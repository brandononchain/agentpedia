"""Tokenizer parity and the serve gate."""

import json
from pathlib import Path

from brain_text import servable, tokenize

ROOT = Path(__file__).resolve().parents[2]


def test_tokenizer_matches_locked_cases():
    cases = json.loads((ROOT / "tools" / "tests" / "brain_tokens.json").read_text(encoding="utf-8"))
    for case in cases:
        assert tokenize(case["in"]) == case["out"]


def test_on_hold_and_grade_f_are_not_servable():
    audit = {"grade": "A", "status": "passed"}
    assert servable(audit, "active", "sha256:abc")
    assert not servable({"grade": "F", "status": "on-hold"}, "on-hold", "sha256:abc")
    assert not servable({"grade": "A", "status": "on-hold"}, "active", "sha256:abc")
    assert not servable({"grade": "A", "status": "passed"}, "withheld", "sha256:abc")
    assert not servable({"grade": "A", "status": "passed"}, "revoked", "sha256:abc")
    assert not servable({"grade": "A", "status": "warning"}, "active", "")
    assert servable({"grade": "D", "status": "warning"}, "active", "sha256:abc")
