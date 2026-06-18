"""Tests for The Board — routing + verdict aggregation (the deterministic core)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import board  # noqa: E402


# ---------------------------------------------------------------------------
# Data integrity
# ---------------------------------------------------------------------------

def test_no_real_person_impersonation_in_data():
    """Guard the core design promise: archetypes only, never named individuals."""
    arch = board._archetypes()
    assert len(arch) >= 8
    for a in arch.values():
        assert a["name"].startswith("The "), f"{a['name']} should be an archetype, not a person"
        assert a["doctrine"] and a["focus_questions"]


def test_routing_panels_reference_valid_archetypes():
    arch = board._archetypes()
    routing = board._routing()
    for key, panel in routing["panels"].items():
        for mid in panel["members"]:
            assert mid in arch, f"panel {key} references unknown archetype {mid}"


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------

def test_resolve_known_panel():
    key, ids = board.resolve_panel("venture")
    assert key == "venture"
    assert "frontier_scientist" in ids and "cfo" in ids


def test_alias_resolves():
    key, _ = board.resolve_panel("gtm")
    assert key == "launch"


def test_unknown_decision_falls_back_to_default():
    key, ids = board.resolve_panel("banana")
    assert key == "general"
    assert ids


def test_all_convenes_full_board():
    key, ids = board.resolve_panel("all")
    assert key == "all"
    assert set(ids) == set(board._archetypes().keys())


def test_resolve_is_case_insensitive():
    assert board.resolve_panel("VENTURE")[0] == "venture"


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def _v(verdict, conf=0.8, member="m", risk="", cond=""):
    return {"member": member, "verdict": verdict, "confidence": conf,
            "reasoning": "r", "key_risk": risk, "key_condition": cond}


def test_all_proceed_is_proceed():
    r = board.aggregate([_v("PROCEED"), _v("PROCEED"), _v("PROCEED")])
    assert r["overall"] == "PROCEED"
    assert r["counts"] == {"PROCEED": 3, "CONCERN": 0, "BLOCK": 0}


def test_any_block_is_block():
    r = board.aggregate([_v("PROCEED"), _v("PROCEED"), _v("BLOCK")])
    assert r["overall"] == "BLOCK"


def test_strict_majority_concern_is_concern():
    # 3 of 5 concern -> strict majority -> CONCERN
    r = board.aggregate([_v("CONCERN"), _v("CONCERN"), _v("CONCERN"), _v("PROCEED"), _v("PROCEED")])
    assert r["overall"] == "CONCERN"


def test_tie_concern_is_not_majority():
    # 2 of 4 concern -> not a strict majority -> PROCEED
    r = board.aggregate([_v("CONCERN"), _v("CONCERN"), _v("PROCEED"), _v("PROCEED")])
    assert r["overall"] == "PROCEED"


def test_confidence_is_mean():
    r = board.aggregate([_v("PROCEED", 0.6), _v("PROCEED", 0.8)])
    assert r["confidence"] == 0.7


def test_key_risks_only_from_dissenters():
    r = board.aggregate([
        _v("PROCEED", risk="should-not-appear"),
        _v("CONCERN", risk="real-risk"),
    ])
    assert r["key_risks"] == ["real-risk"]


def test_invalid_verdict_raises():
    with pytest.raises(ValueError):
        board.aggregate([_v("MAYBE")])


def test_confidence_clamped():
    r = board.aggregate([_v("PROCEED", 5.0), _v("PROCEED", -2.0)])
    # clamped to [0,1] -> mean(1.0, 0.0) = 0.5
    assert r["confidence"] == 0.5


def test_aggregate_accepts_wrapped_object():
    # {"verdicts": [...]} is unwrapped by the CLI; aggregate itself takes the list.
    r = board.aggregate([_v("PROCEED")])
    assert r["member_count"] == 1


# ---------------------------------------------------------------------------
# CLI smoke
# ---------------------------------------------------------------------------

def test_cli_roster(capsys):
    assert board.main(["roster"]) == 0
    out = capsys.readouterr().out
    assert "The Strategist" in out


def test_cli_panel_json(capsys):
    assert board.main(["panel", "--decision", "venture", "--topic", "X", "--format", "json"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["decision_type"] == "venture"
    assert len(out["members"]) == 5


def test_cli_aggregate_stdin(capsys, monkeypatch):
    payload = json.dumps([_v("PROCEED"), _v("BLOCK")])
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO(payload))
    assert board.main(["aggregate", "--format", "json"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["overall"] == "BLOCK"
