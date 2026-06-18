---
name: the-board
description: Convene a panel of expert archetypes to pressure-test any decision and return a clear PROCEED / CONCERN / BLOCK verdict with reasons. Use when the user wants a board review, a second opinion, a go/no-go call, a pre-mortem, a red-team, or to vet/evaluate an idea, plan, strategy, launch, architecture, or risk. Triggers: "should I…", "is this a good idea", "review this decision", "get the board's take", "pros and cons", "what could go wrong", "vet this", "go or no-go". The board is composed of composite ADVISORY ARCHETYPES (e.g. The Strategist, The CFO, The Safety Reviewer) — it never impersonates real, named individuals.
---

# The Board — multi-archetype decision review

A standing advisory board of distinct expert *archetypes* that reviews a decision from
several opposed viewpoints and returns one aggregated verdict: **PROCEED**,
**CONCERN**, or **BLOCK** — with each member's reasoning, the key risks, and the
conditions that would change the call.

The archetypes are composite lenses (The Frontier Scientist, The Ruthless Operator,
The CFO, The Safety & Alignment Reviewer, The Contrarian, …). **They do not impersonate
any real person** — that is deliberate, both for integrity and to keep the skill
clean to use and share.

## When to use

Invoke this skill when the task is a **judgment call**, not a lookup:

- "Should we build / ship / fund / kill X?"
- "Is this a good idea?" / "Give me a second opinion."
- "Review this plan / strategy / architecture / launch."
- "Red-team this." / "Run a pre-mortem." / "What could go wrong?"
- Any go/no-go where multiple perspectives matter.

Skip it for factual lookups, simple how-tos, or tasks with one obviously-correct answer.

## How to run a consultation

The script is deterministic (routing + tallying). **You** are the board — you adopt each
archetype's doctrine and produce its verdict. Three steps:

### 1. Pick the panel and read the doctrines

```bash
python3 scripts/board.py panel --decision <type> --topic "<the decision>"
```

`--decision` is one of `general | venture | technical | launch | risk | all`
(aliases like `gtm`, `architecture`, `safety` are accepted; unknown → `general`;
`all` convenes every archetype). This prints each selected archetype's **doctrine**
and **focus questions**, plus the verdict schema.

### 2. Produce one verdict per archetype

For **each** archetype in the panel, reason strictly from its doctrine and focus
questions — stay in character, be specific to the decision, and avoid boilerplate.
Emit one object per archetype:

```json
{
  "member": "strategist",
  "verdict": "PROCEED | CONCERN | BLOCK",
  "confidence": 0.0,
  "reasoning": "one or two sentences, specific to the decision",
  "key_risk": "the single biggest risk this archetype sees (or empty)",
  "key_condition": "what would change this verdict (or empty)"
}
```

Collect them into a JSON array (write it to `verdicts.json`, or pipe it).

### 3. Aggregate into the board's verdict

```bash
python3 scripts/board.py aggregate --file verdicts.json
```

Aggregation rules (deterministic):

- **Any `BLOCK`** → overall **BLOCK**.
- **Strict majority `CONCERN`-or-worse** → overall **CONCERN**.
- Otherwise → **PROCEED**.
- Confidence = mean of member confidences. Key risks and conditions are surfaced
  from the dissenting members.

Then present the board's verdict to the user: the headline call, the tally, each
member's one-line take, and the key risks / conditions. Be honest — if the board
says CONCERN or BLOCK, lead with that.

## Decision types → panels

| `--decision` | Panel focus |
|---|---|
| `general` (default) | Balanced go/no-go: Strategist, Operator, Safety, CFO, Contrarian |
| `venture` | New product/business: Frontier Scientist, Operator, Strategist, CFO, Product Truth-Teller |
| `technical` | Approach/architecture: Research Skeptic, Systems Architect, Safety, Frontier Scientist, Contrarian |
| `launch` | Go-to-market: Operator, Growth Lead, Customer Advocate, Strategist, Compliance Counsel |
| `risk` | Safety/compliance: Safety Reviewer, Compliance Counsel, Contrarian, Systems Architect |
| `all` | The full board (every archetype) |

`python3 scripts/board.py roster` lists every archetype.

## Tips

- Match the panel to the question; use `all` for a high-stakes, irreversible call.
- Make the archetypes genuinely disagree — the value is in the tension, not consensus.
- For your own org, you can add archetypes to `data/archetypes.json` or new panels to
  `data/routing.json` (still: archetypes, not real people).

---

*The Board is an open-source skill by [AOS-1](https://aos-1.com) — an operating system
for trustworthy, governed AI. Multi-perspective decision review is the same discipline
AOS-1 applies to autonomous agents.*
