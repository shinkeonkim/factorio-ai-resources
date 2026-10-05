---
name: factorio-blueprint
description: Design Factorio production setups and output importable blueprint strings. Computes recipe ratios (machines, belts, raw inputs) from real game data, lays out entities on a grid with a builder that handles positions/directions/wires/modules, validates overlaps and power coverage, and encodes to the "0eN..." string. Also decodes, explains, studies (how a community design works) and edits existing blueprint strings, and designs dense all-in-one / planet bases and malls the way top community prints do (circuit-gated, self-powered, defended). Use this whenever the user mentions Factorio blueprints, blueprint strings, build ratios, "how many assemblers/furnaces/drills", a factory module (green circuits, science, smelting, mining outpost, oil), a mall or all-in-one / planet base, circuit conditions, Space Age builds, or pastes a string starting with "0eN" — even if they don't say the word "blueprint". Korean triggers too: 팩토리오, 블루프린트, 청사진, 생산 비율, 조립기 몇 대, 설계도 문자열, 몰, 올인원, 행성 기지, 회로 조건.
---

# Factorio Blueprint

Turn a production goal into a blueprint string the player can paste into Factorio (Import string),
or read/modify a string they already have.

Everything lives next to this file:
- `scripts/calc.py` — ratio calculator over the real recipe data (vanilla 2.x or Space Age)
- `scripts/tech.py` — which research unlocks a recipe, its science packs and prerequisite chain (`--plan` merges several)
- `scripts/blueprint.py` — encode/decode, `Blueprint` builder, `validate()`, ASCII preview, CLI
- `scripts/study.py` — how a design works: size, density, inserter flows (direct insertion, robots…),
  circuits used, labelled inputs, power, defence, coarse map. Use it on community prints and on your own output
- `examples/*.py` — validated layouts to start from (green circuits 3:2, smelting column, mining outpost,
  dynamic mall cell with circuits)
- `references/blueprint-format.md` — string/JSON spec, 2.0 vs 1.1 differences, wires, modules, fluid ports
- `references/layout-patterns.md` — game mechanics that break designs + layout patterns
- `references/base-design.md` — how top community all-in-one / planet bases and malls are built (measured)
- `references/circuits.md` — exact 2.0 JSON for circuit / logistic conditions, readers, dynamic recipes, alarms
- `data/` — recipes (extracted from wube/factorio-data 2.1), technology unlocks (`tech-unlocks.json`), entity footprints, machine/belt/pole stats

Use `python3` with absolute paths to these files (`SKILL_DIR` below = this directory).

## Why the tooling matters

Hand-writing blueprint JSON fails in quiet ways: an assembler at an integer position is off-grid,
an inserter facing the wrong way moves items backwards, a 1×2 combinator rotated east has a different
footprint, an inserter row sits outside every pole's supply area. The game either refuses the string or
builds something that silently doesn't work. The builder computes positions from top-left tiles, converts
directions per game version, and `validate()` catches overlaps, unpowered entities, unconnected poles and
unpaired undergrounds — so lean on it rather than writing raw JSON.

## Workflow: designing a new blueprint

### 1. Pin down the goal
Needed: the product, the target rate (per second or per minute), and the game version.
Useful: Space Age or not, machine tier, belt tier, inserter tech, whether inputs come as plates on belts
(the usual assumption) or from ore, and whether to include power poles (default yes).
If the user gave a clear goal, don't interrogate them — pick sensible defaults (Factorio 2.0 vanilla,
assembling-machine-2, yellow belts, plates delivered on belts, medium poles) and state them in the answer.
Ask only when the answer would change the design substantially (e.g. "1.1 or 2.0?" when they paste a
1.1-looking string, or Space Age when they name an SA item).

### 2. Compute ratios
```bash
python3 SKILL_DIR/scripts/calc.py electronic-circuit 10              # 10/s
python3 SKILL_DIR/scripts/calc.py automation-science-pack 60 --per-min --tier 1
python3 SKILL_DIR/scripts/calc.py processing-unit 1 --space-age --machine crafting=assembling-machine-3
python3 SKILL_DIR/scripts/calc.py --recipes-for solid-fuel           # alternatives
python3 SKILL_DIR/scripts/calc.py --show advanced-circuit            # one recipe
```
Options: `--raw a,b` (treat as supplied), `--not-raw` (solve something normally raw), `--recipe ITEM=RECIPE`,
`--prod 0.4` (module productivity, applied only where allowed), `--speed 0.5`, `--json`.
Oil products and uranium isotopes are treated as supplied inputs because they come from multi-output
recipes — size refineries/centrifuges separately with `--show` and simple arithmetic.
Read the machine counts as fractional (6.67 → build 7) and check the belt table: if an input needs more
than one belt, the layout must deliver it from two belts/sides.

### 3. Choose a layout
Read `references/layout-patterns.md` (at least §1 mechanics and the pattern you need). Start from the
closest `examples/*.py` when one fits. **Anything bigger than one module** (a mall, "make everything",
a planet base, an all-in-one) follows "Designing a big base" below instead of chaining modules on a bus. Decide: which belts enter where, lane usage, how many tileable
slices, where poles go. Check inserter throughput against per-machine rates (§1) — this is where
paper-valid designs fail in practice.

### 4. Build with the builder
Write a short Python script (in the working directory or scratch space), e.g.:
```python
import sys; sys.path.insert(0, "SKILL_DIR/scripts")
from blueprint import Blueprint, N, E, S, W

bp = Blueprint("Gear module", game="2.0")             # game="1.1" for old saves
bp.belt_line("transport-belt", 0, 0, E, 9)              # (x,y) = upstream end, then direction, length
for i in range(3):
    x = 3 * i
    bp.add("inserter", x + 1, 1, N)                     # N = picks up from north (the belt)
    bp.add("assembling-machine-2", x, 2, recipe="iron-gear-wheel",
           modules={"speed-module": 2})
    bp.add("inserter", x + 1, 5, N)                     # takes from machine above, drops south
bp.belt_line("transport-belt", 8, 6, W, 9)
bp.add("medium-electric-pole", 2, 1); bp.add("medium-electric-pole", 2, 5)
bp.add("medium-electric-pole", 8, 1); bp.add("medium-electric-pole", 8, 5)
bp.connect_poles()
print(bp.report())       # ASCII map + validation
print(bp.to_string())
```
Key API (details in the module docstring):
- `add(name, x, y, direction=N, modules=None, **fields)` — (x, y) is the **top-left tile**; extra
  fields (`recipe`, `type`, `bar`, `filters`, `quality`, `control_behavior`…) go into the entity JSON.
  Raises `OverlapError` on collisions.
- `add_marker(x, y, {"stone": 1440})` — constant combinator input label (see "Input markers" below).
- `belt_line`, `underground(name, x, y, dir, gap)`, `add_tile`, `wire(a, b, color, a_side, b_side)`,
  `connect_poles()`, `validate()`, `ascii()`, `report()`, `to_dict()`, `to_string()`; `make_book(label, [dicts])`.
- Entity names are 2.0 prototype names (`bulk-inserter`, `requester-chest`, …); unknown names raise
  `KeyError` — look in `data/entity_sizes.json`.

### Input markers (required)
Mark **every external input** with a constant combinator (일정 신호 조합기) so the player can see in-game
what to connect where and how much — the blueprint carries its own documentation:
- One `bp.add_marker(x, y, {item_or_fluid: rate_per_minute})` per input point (each belt start, each
  water pipe inlet, each chest the player must fill). Put it on a free tile directly next to the input
  tile (beside the first belt / pipe), not on the tile where the player's belt or pipe will connect.
- Signal = exactly the item or fluid to supply there (`stone`, `iron-ore`, `water`, …; the type is
  detected automatically). Count = required rate **per minute**, rounded up (calc.py raw input rate × 60,
  split per input point if one resource has several entry points).
- Constant combinators need no power and connect to nothing; they're labels only. Don't wire them.
- Mention the markers in the answer (position + signal + count), and `blueprint.py info` lists them when
  decoding.
Outputs don't need markers unless the user asks. On big bases also put a display panel at each input
(`bp.add_panel(x, y, "scrap", "Input")`, no power needed) — that is how community bases label their edges.

### 5. Verify before answering
- `report()` must say `Validation: OK`. If it lists problems, fix the layout (move/add poles, fix
  overlaps); don't hand over a string with known problems unless you explain each one.
- Trace each item path once on the ASCII map: belt → inserter arrow → machine → inserter arrow → next.
  Arrows on inserters show item flow, so a wrong direction is visible.
- Round-trip: `decode(bp.to_string()) == bp.to_dict()` (cheap sanity check if you edited JSON by hand).

### 6. Answer format
1. One-line summary (what it makes, rate, machine counts).
2. Assumptions (version, tiers, input belts, research such as inserter capacity if relied on).
   List each input with its marker (signal, count/min, location).
3. The ASCII preview in a code block, plus where each belt enters/exits and lane contents.
4. The blueprint string in its own code block, on a single line. If it's very long (> ~4000 chars),
   also write it to a `.txt` file and give the path.
5. Ratio table from calc.py (condensed) when the user asked about rates.
Write the answer in the user's language.

## Designing a big base (mall, all-in-one, planet base)

Community bases that people actually use are not modules strung along a bus. Read `references/base-design.md`
(measured from top factorioprints designs) and follow its checklist:
1. **Study first.** If the user names or pastes reference prints, run `scripts/study.py <file> --map 3` on
   them and say what you take over (shape, inputs, flow mix, circuits). base-design.md §12 shows how to pull
   top-rated prints from factorioprints for analysis (keep their strings out of any repo).
2. **Shape**: one dense rectangle; few inputs, all on the edge, each ending in an underground belt /
   pipe-to-ground with a marker + display panel; waste has a way out (void or exit belt).
3. **Inside**: rows of machines between two belts (4 lanes, long-handed for the far belt), direct insertion
   where one machine feeds one consumer, fluids produced next to their consumers (no fluid main across the
   base). Belts for volume, robots (requester / buffer chests) for the many low-volume items.
4. **Control**: gate every output that can pile up with a logistic condition, crack oil by tank level, burn
   fuel by accumulator charge, add an alarm where the base can starve (`references/circuits.md`). A mall
   that makes dozens of items uses the dynamic-mall cell (`examples/dynamic_mall_cell.py`).
5. **Power and frame**: power that restarts itself (heating towers / turbines gated by accumulators, solar);
   the planet's frame (Gleba mines + walls + turrets with ammo requesters, Fulgora lightning rods +
   accumulators, Aquilo heat pipes everywhere, Vulcanus none — build outside demolisher territory).
6. **Measure your result** with `study.py`: density ≥ 0.3 in the core, direct insertion where recipes chain,
   no empty streets. Write the description the way community prints do: makes / needs (rates) / how to start
   (robots, fuel, seeds, eggs).

## House rules when working in factorio-ai-resources

The repo's `docs/guides/` define how new factories should look; follow them unless the user says otherwise:
- **Main bus** (for a Nauvis-style factory of modules, not for planet bases / malls): horizontal, groups of
  6 lanes separated by 2 empty rows; branches leave north with the kit in `lib/main_bus.py`.
- **Planet bases / malls**: one rectangle per "Designing a big base" above (`lib/base.py` composes one).
- **Upgrade in place**: one layout for early → late — underground spans ≤ 4, no long-handed inserters on
  throughput bottlenecks, pole spacing valid for small poles, 2×2 furnaces, fluid recipes on AM2+.
- **Water**: Waterfill is used; mark the water inlet with a marker instead of long pipes.
- To evaluate an existing print against these rules: `python3 tools/analyze_blueprint.py <file>`.

## Saving into the factorio-ai-resources repo

When the working directory is (or contains) the `factorio-ai-resources` repository, finished blueprints
live there instead of loose files:
1. `python3 tools/new_blueprint.py <id> --title-ko … --title-en … --summary-ko … --summary-en …`
2. Put the builder code in `blueprints/<id>/generate.py` (`from lib.fbp import *`, end with
   `save(bp, __file__)`; variants via `save(obj, __file__, "variants/<name>.txt")`).
3. Fill `meta.json` (outputs, mods, tags) and write the prose sections of both `README.md` (Korean)
   and `README.en.md` (English) outside the AUTO block.
4. `python3 tools/build.py <id>` → validates, renders `images/preview.webp` (+ `detail.webp` for big rail
   blocks) and refreshes the docs and the root catalog. Screenshots: `tools/attach_image.py`.
Shared generator code belongs in `lib/`; third-party inputs in git-ignored `third_party/`.

## Workflow: reading or modifying an existing string

```bash
python3 SKILL_DIR/scripts/blueprint.py info  "<string or file>"   # summary, counts, ASCII map, validation
python3 SKILL_DIR/scripts/study.py "<file>" --top 4 --map 3      # how it works: flows, circuits, inputs, power
python3 SKILL_DIR/scripts/blueprint.py decode "<string>" > bp.json
# edit bp.json (or load with json in Python and modify)
python3 SKILL_DIR/scripts/blueprint.py encode bp.json
```
**Long pasted strings**: write the user's string to a file first and work from the file. If decoding
fails with `incorrect data check` / broken JSON, a character was mangled while copying — run
`blueprint.py repair <file>` (finds and fixes a single wrong base64 character via the zlib checksum)
before asking the user to resend.

**Grid blocks (rail city blocks etc.)**: `scripts/tile.py <string|file> N out.txt` repeats a
`snap-to-grid` blueprint N×N, merging shared border entities and remapping wires. Stacked rails at the
same tile with different directions are normal (crossings/switches) and are kept.

To modify programmatically: `obj = decode(s)`, change `obj["blueprint"]["entities"]`, keep
`entity_number`s consecutive and update `wires` if you renumber, then `validate(obj)` and `encode(obj)`.
Common edits: swap recipe, upgrade tiers (rename `assembling-machine-2` → `-3`, `transport-belt` →
`fast-transport-belt` and the matching underground/splitter), add modules, change label/icons.
Blueprint books (`blueprint_book`) contain `blueprints: [{index, blueprint}]` — `info` walks them.

## Version notes

- Default to **Factorio 2.0** (`game="2.0"`, version 2.0.10.1 stamp). Directions are 0/4/8/12, wires are
  top-level tuples, modules use `in_inventory` insert plans — the builder does this.
- For **1.1** (`game="1.1"`) the builder emits 0/2/4/6 directions, `neighbours`/`connections`, and
  `{"module": count}` items. Several entities were renamed in 2.0 (see blueprint-format.md §10); use the
  1.1 names when targeting 1.1.
- Recipe data is from Factorio 2.1 base / Space Age. A few numbers differ from 1.1 (e.g. Space Age
  adds categories, some recipes changed) — mention this if the user is on 1.1 and exact ratios matter.
- Space Age crafters with built-in +50% productivity (foundry, electromagnetic plant, biochamber) are
  handled by calc.py automatically.

## Scope limits — say so instead of guessing

- Rails, train stations and signals: the 2.0 rail grid has its own position rules; only generate them if
  you copy the exact positions from a user-provided blueprint. When the user wants stations added to a
  rail block, ask them to lay the branch + station track in-game and send it; then add stops, signals,
  chests, inserters and circuits around the given track.
- Circuit logic: the shapes in `references/circuits.md` are decoded from working community prints —
  generate those directly (and the wires). For anything not listed there, generate the entities and wires,
  and ask the user to set the condition in-game or to export an example to decode.
- Modded items/entities: names aren't in `data/`; pass `size=(w, h)` to `add()` if you know the footprint,
  otherwise ask the user for a sample blueprint containing that entity and decode it.
