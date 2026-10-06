# CLAUDE.md — working in factorio-ai-resources

- Design work uses the `factorio-blueprint` skill in `skills/factorio-blueprint/` (installed into
  `~/.claude/skills` by `scripts/install-skills.sh` as a symlink, so edits here are live).
- New blueprint → `python3 tools/new_blueprint.py <id> --title-ko … --title-en …`, write `generate.py`
  using `from lib.fbp import *` and `save(bp, __file__)`, then `python3 tools/build.py <id>`.
- **Factories are stackable cells** (lib/stack.py, specs in lib/cells.py): fixed width × period, inputs run north
  along both edges, the product runs south down the middle, every line enters at the bottom edge and leaves at the
  top edge, so pasting the cell one period further north extends production (model: the Nilaus green-circuit
  module). Each folder ships cap + 3 cells (example), cell-<tier> (snaps to its grid) and cap-<tier>; build.py adds
  the stacking table. Complex products get their intermediates from their own cells, not one big layout.
- **Fluid cells** (lib/fstack.py): one recipe per cell, machines rotated so fluid inputs face the belts and outputs
  face the centre; each input fluid gets its own machine row (pipe-to-ground pairs must never share a row).
- **Planet bases** (lib/base.py + lib/planets/<planet>.py `islands()` / `base()`): one dense rectangle like community
  planet bases (skills/factorio-blueprint/references/base-design.md), never a planet-wide bus. Islands = lines that
  share fluids/intermediates; split islands keep their own fluid producers (no fluid crosses the base). Parts packed
  into shelves with short streets; recipes with ≤1 fluid input run in dense robot-fed columns (lib/dense.py,
  several recipes per column on one pipe); fluid-free robot stacks float into the gaps; robot-fed cells (`bots=True`, or
  `belt_out=True` to keep a by-product on a belt); outputs gated by logistic conditions; self-starting power
  (burner inserters on accumulator charge) + low-power alarm; inputs on the edge (underground/PTG end + marker +
  display panel). Frames: Gleba mines + walls + turrets, Fulgora lightning band, Aquilo heat (lib/heat `check()`
  must be empty), Vulcanus none. Measure with `scripts/study.py` (density, coverage).
- House rules for new factories: horizontal main bus of 6-lane groups + 2 empty rows (`lib/main_bus.py`,
  docs/guides/main-bus-6x2.md); upgrade in place yellow→red→blue with the same layout (underground spans ≤4,
  no long-handed on bottlenecks, small-pole spacing, 2×2 furnaces; docs/guides/upgrade-in-place.md);
  water via Waterfill (mark the inlet, no long water pipes).
- Analysing a blueprint/book: `python3 tools/analyze_blueprint.py <file>` (tiers, upgrade check, I/O); how a design
  works (density, inserter flows, circuits, inputs, power, defence): `skills/factorio-blueprint/scripts/study.py`.
- Every external input gets a constant-combinator marker (`bp.add_marker`), count = per minute.
- Write both `README.md` (Korean) and `README.en.md` (English); keep prose outside the AUTO block.
- Every blueprint's meta.json has a `roadmap` (stages; `research` = recipe names, resolved to technologies by
  build.py from `tech-unlocks.json`, so never type tech names by hand) and `next` (related blueprint ids).
  Variants with `"preview": true` get their own image.
- Shared generator code goes to `lib/`; never commit anything under `third_party/` except its README.
- Rail city-block stations: take rail geometry from the user's book (`third_party/rail-book.txt` via
  `lib/rail_city_block.py`); do not invent rail positions.
- Before committing: `.venv/bin/python tools/build.py --regen` (renders game-sprite previews via FBE; needs
  `pip install -r tools/requirements.txt` + `playwright install chromium`) and make sure validation passes.
