# Contributing to The Board

Thanks for helping make The Board better! Contributions are very welcome —
especially **new archetypes, new decision panels, and translations**.

## The one rule

**Archetypes, not real people.** The board is composed of *composite advisory
lenses* (The Strategist, The CFO, …). Please never add a member that impersonates
a real, named individual — it's a deliberate design choice for integrity and to
keep the project clean to use and share. PRs that add real-person personas will be
declined.

## Quick start

```bash
git clone https://github.com/pamiray-m/the-board.git
cd the-board
python3 -m pytest tests/ -q     # everything should pass before you start
```

No dependencies — standard library only. Python 3.8+.

## Add an archetype

Edit [`data/archetypes.json`](data/archetypes.json) and add an object to `archetypes`:

```json
{
  "id": "the_ethicist",
  "name": "The Ethicist",
  "lens": "Fairness, harm, and who is affected",
  "doctrine": "You weigh who is helped and who is harmed... PROCEED when ... CONCERN when ... BLOCK when ...",
  "focus_questions": ["Who bears the downside?", "Is the harm consented and reversible?", "..."]
}
```

Guidelines:
- `id` is lowercase `snake_case` and unique.
- `name` starts with **"The "** (it's an archetype).
- `doctrine` is 3–5 sentences, opinionated and *distinct* from the others, and should
  state when this lens votes PROCEED / CONCERN / BLOCK.
- Add the new `id` to at least one panel in [`data/routing.json`](data/routing.json).

## Add a decision panel

Edit [`data/routing.json`](data/routing.json) — add an entry under `panels` (5-ish
members that genuinely disagree), and optional `aliases` that route to it.

## Run the checks

```bash
python3 -m pytest tests/ -q
```

The test suite guards the invariants (every panel references a valid archetype, the
"no real people" rule, and the aggregation math). Please add a test if you add behavior.

## Open a PR

1. Fork → branch → change → `pytest`.
2. Keep the diff focused (one archetype/panel/feature per PR is ideal).
3. Describe *why* the lens is distinct and what it catches that the others miss.

New to the project? Look for issues labeled **`good first issue`** — they're scoped to
be a clean first contribution.
