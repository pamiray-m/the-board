#!/usr/bin/env python3
"""
The Board — a multi-archetype advisory panel for any decision.

Deterministic helpers for a skill-driven workflow:

  1. board.py roster
        List every archetype (composite advisory lenses — NOT real people).

  2. board.py panel --decision <type> --topic "..."
        Resolve the right panel for a decision and print each archetype's
        doctrine + the exact verdict JSON it must emit. The calling agent then
        adopts each doctrine and produces a verdict.

  3. board.py aggregate --file verdicts.json   (or pipe JSON on stdin)
        Deterministically combine member verdicts into one board verdict:
          - any BLOCK            -> overall BLOCK
          - >50% CONCERN-or-worse -> overall CONCERN
          - otherwise            -> overall PROCEED
        confidence = mean of member confidences.

Pure standard library. No network, no API key — the reasoning is the agent's;
this script only routes and tallies.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from statistics import mean
from typing import Any

_DATA = Path(__file__).resolve().parent.parent / "data"

VERDICTS = ("PROCEED", "CONCERN", "BLOCK")
_SEVERITY = {"PROCEED": 0, "CONCERN": 1, "BLOCK": 2}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load(name: str) -> dict[str, Any]:
    with (_DATA / name).open() as f:
        return json.load(f)


def _archetypes() -> dict[str, dict[str, Any]]:
    data = _load("archetypes.json")
    return {a["id"]: a for a in data["archetypes"]}


def _routing() -> dict[str, Any]:
    return _load("routing.json")


def resolve_panel(decision: str) -> tuple[str, list[str]]:
    """Return (panel_key, [archetype_ids]) for a decision type.

    'all' / 'full' convenes every archetype. Unknown types fall back to the
    default panel. Aliases (e.g. 'gtm' -> 'launch') are honoured.
    """
    routing = _routing()
    key = (decision or "").strip().lower()
    if key in ("all", "full", "everyone"):
        return "all", list(_archetypes().keys())
    key = routing.get("aliases", {}).get(key, key)
    panels = routing["panels"]
    if key not in panels:
        key = routing["default"]
    return key, list(panels[key]["members"])


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_roster(_args) -> int:
    arch = _archetypes()
    print("# The Board — archetype roster\n")
    for a in arch.values():
        print(f"- **{a['name']}** (`{a['id']}`) — {a['lens']}")
    print(f"\n{len(arch)} archetypes. Composite advisory lenses — not real individuals.")
    return 0


def cmd_panel(args) -> int:
    arch = _archetypes()
    panel_key, ids = resolve_panel(args.decision)
    topic = args.topic or "(no topic provided)"

    if args.format == "json":
        out = {
            "decision_type": panel_key,
            "topic": topic,
            "members": [
                {k: arch[i][k] for k in ("id", "name", "lens", "doctrine", "focus_questions")}
                for i in ids
            ],
            "verdict_schema": _VERDICT_SCHEMA,
        }
        print(json.dumps(out, indent=2))
        return 0

    print(f"# Board consultation — panel: {panel_key}")
    print(f"\n**Decision under review:** {topic}\n")
    print(
        "Adopt EACH archetype below in turn. Reason strictly from its doctrine "
        "and focus questions, then emit one verdict object per archetype in the "
        "schema shown at the end. Be specific to the decision — no boilerplate.\n"
    )
    for n, i in enumerate(ids, 1):
        a = arch[i]
        print(f"## {n}. {a['name']}  (`{a['id']}`)")
        print(f"*Lens: {a['lens']}*\n")
        print(a["doctrine"])
        print("\nFocus questions:")
        for q in a["focus_questions"]:
            print(f"  - {q}")
        print()
    print("---\n## Verdict schema (one object per archetype)\n")
    print("```json")
    print(json.dumps(_VERDICT_SCHEMA, indent=2))
    print("```")
    print(
        "\nThen run: `python3 scripts/board.py aggregate --file verdicts.json` "
        "(a JSON array of the objects above) to get the board's overall verdict."
    )
    return 0


def cmd_aggregate(args) -> int:
    raw = Path(args.file).read_text() if args.file else sys.stdin.read()
    try:
        verdicts = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"error: input is not valid JSON: {exc}", file=sys.stderr)
        return 2
    if isinstance(verdicts, dict) and "verdicts" in verdicts:
        verdicts = verdicts["verdicts"]
    if not isinstance(verdicts, list) or not verdicts:
        print("error: expected a non-empty JSON array of verdict objects", file=sys.stderr)
        return 2

    try:
        result = aggregate(verdicts)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(result, indent=2))
        return 0

    print(f"# Board verdict: {result['overall']}  (confidence {result['confidence']})\n")
    c = result["counts"]
    print(f"Tally — PROCEED: {c['PROCEED']}  CONCERN: {c['CONCERN']}  BLOCK: {c['BLOCK']}  "
          f"({result['member_count']} members)\n")
    for m in result["members"]:
        line = f"- {m.get('member', '?')}: **{m['verdict']}** ({m.get('confidence', 0):.2f})"
        if m.get("reasoning"):
            line += f" — {m['reasoning']}"
        print(line)
    if result["key_risks"]:
        print("\n**Key risks:**")
        for r in result["key_risks"]:
            print(f"  - {r}")
    if result["key_conditions"]:
        print("\n**Conditions to revisit:**")
        for k in result["key_conditions"]:
            print(f"  - {k}")
    return 0


# ---------------------------------------------------------------------------
# Aggregation (pure, deterministic)
# ---------------------------------------------------------------------------

_VERDICT_SCHEMA = {
    "member": "<archetype id, e.g. strategist>",
    "verdict": "PROCEED | CONCERN | BLOCK",
    "confidence": "0.0-1.0",
    "reasoning": "one or two sentences, specific to the decision",
    "key_risk": "the single biggest risk this archetype sees (or empty)",
    "key_condition": "what would change this verdict (or empty)",
}


def _norm_verdict(v: str) -> str:
    u = (v or "").strip().upper()
    if u not in VERDICTS:
        raise ValueError(f"invalid verdict {v!r}; must be one of {VERDICTS}")
    return u


def aggregate(verdicts: list[dict[str, Any]]) -> dict[str, Any]:
    """Combine member verdicts into one board verdict. Deterministic."""
    if not verdicts:
        raise ValueError("no verdicts to aggregate")

    norm: list[dict[str, Any]] = []
    confidences: list[float] = []
    for v in verdicts:
        verdict = _norm_verdict(v.get("verdict", ""))
        try:
            conf = float(v.get("confidence", 0.0))
        except (TypeError, ValueError):
            conf = 0.0
        conf = max(0.0, min(1.0, conf))
        confidences.append(conf)
        norm.append({
            "member": v.get("member") or v.get("name") or "?",
            "verdict": verdict,
            "confidence": conf,
            "reasoning": (v.get("reasoning") or "").strip(),
            "key_risk": (v.get("key_risk") or "").strip(),
            "key_condition": (v.get("key_condition") or "").strip(),
        })

    n = len(norm)
    counts = {k: sum(1 for m in norm if m["verdict"] == k) for k in VERDICTS}
    concern_or_worse = counts["CONCERN"] + counts["BLOCK"]

    if counts["BLOCK"] > 0:
        overall = "BLOCK"
    elif concern_or_worse * 2 > n:   # strict majority
        overall = "CONCERN"
    else:
        overall = "PROCEED"

    key_risks = [m["key_risk"] for m in norm if m["verdict"] != "PROCEED" and m["key_risk"]]
    key_conditions = [m["key_condition"] for m in norm if m["verdict"] != "PROCEED" and m["key_condition"]]

    return {
        "overall": overall,
        "confidence": round(mean(confidences), 2) if confidences else 0.0,
        "member_count": n,
        "counts": counts,
        "key_risks": key_risks,
        "key_conditions": key_conditions,
        "members": norm,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="The Board — multi-archetype advisory panel.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("roster", help="List all archetypes.")

    p_panel = sub.add_parser("panel", help="Print the panel + doctrines for a decision.")
    p_panel.add_argument("--decision", "-d", default="general",
                         help="Decision type: general|venture|technical|launch|risk|all (aliases ok).")
    p_panel.add_argument("--topic", "-t", default="", help="The decision being reviewed.")
    p_panel.add_argument("--format", "-f", choices=["md", "json"], default="md")

    p_agg = sub.add_parser("aggregate", help="Combine member verdicts into a board verdict.")
    p_agg.add_argument("--file", help="Path to a JSON array of verdicts (default: stdin).")
    p_agg.add_argument("--format", "-f", choices=["md", "json"], default="md")

    args = parser.parse_args(argv)
    return {"roster": cmd_roster, "panel": cmd_panel, "aggregate": cmd_aggregate}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
