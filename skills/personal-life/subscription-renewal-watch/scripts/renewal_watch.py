#!/usr/bin/env python3
"""Project renewals from a charge CSV. Does not contact a bank."""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

# gap days, inclusive, then the multiplier for one latest amount
WINDOWS = (
    ("weekly", 6, 8, 52),
    ("monthly", 27, 33, 12),
    ("yearly", 360, 370, 1),
)
CADENCES = {name for name, _low, _high, _mult in WINDOWS}


def fail(message: str) -> None:
    raise SystemExit(message)


def parse_date(value: str, row_number: int) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        fail(f"row {row_number} date must be YYYY-MM-DD")


def parse_amount(value: str, row_number: int) -> Decimal:
    if value == "":
        fail(f"row {row_number} is missing an amount")
    try:
        amount = Decimal(value)
    except InvalidOperation:
        fail(f"row {row_number} amount must be a plain decimal")
    return amount.quantize(Decimal("0.01"))


def plain(value: str, row_number: int, label: str) -> str:
    if "\t" in value or "\n" in value or "\r" in value:
        fail(f"row {row_number} {label} must be one line")
    return value


def median_lower(gaps: list[int]) -> int:
    ordered = sorted(gaps)
    return ordered[(len(ordered) - 1) // 2]


def cadence_for(gap: int) -> tuple[str, int] | None:
    for name, low, high, multiplier in WINDOWS:
        if low <= gap <= high:
            return name, multiplier
    return None


def money(amount: Decimal) -> str:
    return f"{amount:.2f}"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python3 scripts/renewal_watch.py <csv>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    grouped: dict[str, list[tuple[date, Decimal, str]]] = defaultdict(list)
    rows = 0
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        if not {"date", "merchant", "amount"} <= fields:
            fail("csv needs date, merchant, and amount columns")
        for index, row in enumerate(reader, start=2):
            date_raw = (row.get("date") or "").strip()
            merchant = plain((row.get("merchant") or "").strip(), index, "merchant")
            amount_raw = (row.get("amount") or "").strip()
            if date_raw == "" and merchant == "" and amount_raw == "":
                continue
            if merchant == "":
                fail(f"row {index} is missing a merchant")
            if date_raw == "":
                fail(f"row {index} is missing a date")
            grouped[merchant.casefold()].append(
                (parse_date(date_raw, index), parse_amount(amount_raw, index), merchant)
            )
            rows += 1

    reports = []
    charges = 0
    for key in sorted(grouped):
        events_raw = grouped[key]
        display = events_raw[0][2]
        by_day: dict[date, Decimal] = {}
        for when, amount, _shown in events_raw:
            by_day[when] = (by_day.get(when, Decimal("0.00")) + amount).quantize(Decimal("0.01"))
        events = sorted(by_day.items())
        charges += len(events)
        count = len(events)
        last_day, last_amount = events[-1]
        changed = "yes" if len({amount for _day, amount in events}) > 1 else "no"
        gap_text = "n/a"
        nxt = "n/a"
        projected = "no"
        annualized: Decimal | str = "skipped"
        if count < 2:
            cadence = "unknown"
        else:
            gaps = [(events[i][0] - events[i - 1][0]).days for i in range(1, count)]
            gap = median_lower(gaps)
            gap_text = str(gap)
            found = cadence_for(gap)
            if found is None:
                cadence = "irregular"
            else:
                cadence, multiplier = found
                if last_amount > 0:
                    annualized = (last_amount * multiplier).quantize(Decimal("0.01"))
                    nxt = (last_day + timedelta(days=gap)).isoformat()
                    projected = "yes"
        reports.append(
            (display, count, last_day, last_amount, cadence, gap_text, annualized, nxt, projected, changed)
        )

    numbers = [item[6] for item in reports if isinstance(item[6], Decimal)]
    total = sum(numbers, Decimal("0.00")).quantize(Decimal("0.01"))
    skipped = sum(1 for item in reports if item[6] == "skipped")
    recurring = sum(1 for item in reports if item[4] in CADENCES)
    lines = [
        f"rows={rows}",
        f"charges={charges}",
        f"merchants={len(reports)}",
        f"recurring={recurring}",
        f"annualized_total={money(total)}",
        f"annualized_skipped={skipped}",
        "merchant\tcount\tlast\tlast_amount\tcadence\tgap_days\tannualized\tnext\tprojected\tamount_changed",
    ]
    for display, count, last_day, last_amount, cadence, gap_text, annualized, nxt, projected, changed in reports:
        shown = annualized if isinstance(annualized, str) else money(annualized)
        lines.append(
            "\t".join(
                [
                    display,
                    str(count),
                    last_day.isoformat(),
                    money(last_amount),
                    cadence,
                    gap_text,
                    shown,
                    nxt,
                    projected,
                    changed,
                ]
            )
        )
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
