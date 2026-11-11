from datetime import date, timedelta
from pathlib import Path

from shelf_rotation import next_shelf, shelf_ids

ROOT = Path(__file__).resolve().parents[2]


def test_cycle_visits_each_shelf_once():
    shelves = shelf_ids(ROOT / "skills")
    assert len(shelves) == 20
    start = date(2026, 11, 11)
    picked = [next_shelf(shelves, start + timedelta(days=offset)) for offset in range(len(shelves))]
    assert sorted(picked) == sorted(shelves)
    assert len(set(picked)) == len(shelves)


def test_next_day_advances():
    shelves = ["alpha", "beta", "gamma"]
    first = next_shelf(shelves, date(2026, 1, 1))
    second = next_shelf(shelves, date(2026, 1, 2))
    assert first != second
    assert {first, second} <= set(shelves)
