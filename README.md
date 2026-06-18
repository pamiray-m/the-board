# The Board 🧭

**Convene a panel of expert archetypes to pressure-test any decision — and get a clear `PROCEED` / `CONCERN` / `BLOCK` verdict with reasons.**

The Board is an open-source [Claude](https://claude.com/claude-code) skill. When you face a
judgment call — *should we build this? ship this? fund this? kill this?* — it convenes a panel
of opinionated expert **archetypes**, has each one review the decision from its own lens, and
aggregates their votes into a single, honest verdict.

> The board is made of **composite advisory archetypes** — *The Strategist, The CFO, The Safety
> Reviewer, The Contrarian,* and friends. **It never impersonates real, named people.** That's a
> deliberate design choice: you get the diversity of perspective without putting words in any real
> person's mouth.

---

## Why

Most AI assistants give you one confident answer. Important decisions deserve **structured
disagreement**. The Board makes the strongest version of a decision survive the strongest
objections — a pre-mortem, a red-team, and a go/no-go in one pass.

## The archetypes

| Archetype | Lens |
|---|---|
| The Frontier Scientist | Genuine novelty & technical depth |
| The Ruthless Operator | Execution & go-to-market repeatability |
| The Research Skeptic | Technical feasibility & method soundness |
| The Safety & Alignment Reviewer | Risk, misuse, reversibility |
| The CFO | Unit economics & capital discipline |
| The Strategist | Timing, competition, moat, second-order effects |
| The Systems Architect | Scalability, reliability, technical debt |
| The Product Truth-Teller | Real user demand & value |
| The Legal & Compliance Counsel | Regulatory, IP, liability, privacy |
| The Growth Lead | Distribution & acquisition |
| The Customer Advocate | End-user experience & trust |
| The Contrarian | Pre-mortem & steelman the failure |

## Install

Drop the skill into your Claude Code skills directory:

```bash
git clone https://github.com/<your-org>/the-board.git
mkdir -p ~/.claude/skills
cp -R the-board ~/.claude/skills/the-board
```

Claude will discover it automatically and invoke it when you ask for a decision review,
a second opinion, a pre-mortem, or a go/no-go. You can also just ask: *"Get the board's take on X."*

## Use it directly (CLI)

The skill works through three deterministic helpers — the reasoning is done by the model, the
routing and tallying by the script:

```bash
# 1. See the panel + each archetype's doctrine for a decision
python3 scripts/board.py panel --decision venture --topic "Launch a paid tier in Q3"

# 2. (the model produces one verdict per archetype as JSON — see SKILL.md)

# 3. Aggregate the verdicts into the board's call
python3 scripts/board.py aggregate --file verdicts.json

# List every archetype
python3 scripts/board.py roster
```

**Decision types:** `general` (default) · `venture` · `technical` · `launch` · `risk` · `all`
(aliases like `gtm`, `architecture`, `safety` work too).

**Aggregation rules (deterministic):** any `BLOCK` → BLOCK · strict majority `CONCERN`-or-worse
→ CONCERN · otherwise PROCEED. Confidence is the mean of member confidences.

## Customize

This is your board. Add archetypes to [`data/archetypes.json`](data/archetypes.json) or new panels
to [`data/routing.json`](data/routing.json) to fit your org. One rule we'd ask you to keep:
**archetypes, not real people.**

## Tests

```bash
python3 -m pytest tests/ -q
```

## License

MIT — see [LICENSE](LICENSE).

---

*The Board is an open-source skill from [AOS-1](https://aos-1.com) — an operating system for
trustworthy, governed AI. Multi-perspective decision review is the same discipline AOS-1 applies
to autonomous agents in production. Questions: support@aos-1.com*
