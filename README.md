<h1 align="center">The Board 🧭</h1>

<p align="center">
  <b>Convene a panel of expert archetypes to pressure-test any decision —<br>
  and get a clear <code>PROCEED</code> / <code>CONCERN</code> / <code>BLOCK</code> verdict with reasons.</b>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/Claude-skill-8A63D2" alt="Claude skill">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/deps-stdlib%20only-brightgreen" alt="stdlib only">
  <a href="https://github.com/pamiray-m/the-board/stargazers"><img src="https://img.shields.io/github/stars/pamiray-m/the-board?style=social" alt="Stars"></a>
</p>

---

Most AI assistants hand you **one confident answer**. Important decisions deserve **structured
disagreement**. The Board is an open-source [Claude](https://claude.com/claude-code) skill that
spins up a panel of opinionated expert *archetypes*, has each one review your decision from its
own lens, and aggregates their votes into a single, honest call — a pre-mortem, a red-team, and a
go/no-go in one pass.

> The board is made of **composite advisory archetypes** — *The Strategist, The CFO, The Safety
> Reviewer, The Contrarian,* and friends. **It never impersonates real, named people.** That's a
> deliberate choice: the diversity of perspective, none of the likeness problems.

## See it in action

> **You:** *"Get the board's take: should we rewrite our monolith as microservices?"*

```
# Board verdict: BLOCK  (confidence 0.73)

Tally — PROCEED: 0  CONCERN: 4  BLOCK: 1  (5 members)

- frontier_scientist:  CONCERN (0.70) — Microservices aren't novel — the real question is whether
                                        your scaling pain demands them or you're chasing fashion.
- research_skeptic:    CONCERN (0.72) — Sound only if boundaries are clear; otherwise you trade fast
                                        in-process calls for slow network calls and distributed debugging.
- systems_architect:   CONCERN (0.75) — A big-bang rewrite is the highest-risk path — huge operational
                                        burden before proving any value.
- safety_reviewer:     CONCERN (0.68) — A full rewrite is hard to reverse; risk a multi-quarter stall.
- contrarian:          BLOCK   (0.80) — Pre-mortem: a year later it's 70% done, both systems run in
                                        parallel, velocity cratered — and the "scaling problem" was one
                                        unindexed query.

Conditions to revisit:
  - Name the specific scaling limit the monolith cannot meet.
  - Use a strangler-fig: extract incrementally behind the live system.
  - First prove the bottleneck is architectural, not a few hot paths.
```

One dissent (`BLOCK`) is enough to gate the call — and you get the *why*, the risks, and the
conditions that would turn it into a `PROCEED`.

## Why

- **Kills false confidence** — opposed lenses surface the risk the cheerleader misses.
- **Built-in pre-mortem** — The Contrarian steelmans the failure *before* you commit.
- **One honest verdict** — deterministic aggregation, not vibes: any `BLOCK` → BLOCK; majority
  `CONCERN` → CONCERN; else PROCEED.

## Install

```bash
git clone https://github.com/pamiray-m/the-board.git
mkdir -p ~/.claude/skills && cp -R the-board ~/.claude/skills/the-board
```

That's it. Claude auto-discovers the skill and invokes it whenever you ask for a decision review,
a second opinion, a pre-mortem, or a go/no-go — or just say *"get the board's take on X."*

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

The right subset is convened automatically per decision type (`general` · `venture` · `technical`
· `launch` · `risk` · `all`).

## Use it directly (CLI)

The skill works through three small, dependency-free helpers — the *reasoning* is the model's, the
*routing and tallying* are the script's:

```bash
# 1. See the panel + each archetype's doctrine for a decision
python3 scripts/board.py panel --decision venture --topic "Launch a paid tier in Q3"

# 2. (the model produces one verdict per archetype as JSON — see SKILL.md)

# 3. Aggregate the verdicts into the board's call
python3 scripts/board.py aggregate --file verdicts.json

# List every archetype
python3 scripts/board.py roster
```

## Customize

This is *your* board. Add archetypes in [`data/archetypes.json`](data/archetypes.json) or new
panels in [`data/routing.json`](data/routing.json) to fit your org. One rule we'd ask you to keep:
**archetypes, not real people.**

## Tests

```bash
python3 -m pytest tests/ -q
```

## License

MIT — see [LICENSE](LICENSE). PRs welcome: new archetypes, panels, and translations especially.

---

<p align="center">
  <i>The Board is an open-source skill from <a href="https://aos-1.com">AOS-1</a> — an operating
  system for trustworthy, governed AI.<br>Multi-perspective decision review is the same discipline
  AOS-1 applies to autonomous agents in production. · support@aos-1.com</i>
</p>
