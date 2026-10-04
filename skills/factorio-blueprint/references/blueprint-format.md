# Factorio blueprint string format (2.0 and 1.1)

Sources: Factorio wiki "Blueprint string format", lua-api.factorio.com (BlueprintEntity, BlueprintWire,
BlueprintInsertPlan), wube/factorio-data prototypes, real 2.0 blueprint strings from the Draftsman test-suite.

## Contents
1. String encoding
2. Top-level objects (blueprint, book)
3. Coordinates and positions
4. Directions (2.0 vs 1.1) and what "direction" means per entity
5. Entity fields you will actually use
6. Fluid connection sides per machine
7. Wires (copper / red / green)
8. Modules and item requests
9. Version numbers
10. 1.1 ↔ 2.0 differences cheat-sheet

## 1. String encoding

```
string = "0" + base64( zlib_deflate( utf8(json), level 9 ) )
decode = zlib_inflate( base64_decode( string[1:] ) )
```
- The leading `0` is a format version byte (always `0` through 2.x).
- Factorio 2.0 also imports raw, uncompressed JSON pasted into the import box.
- Shell: `echo "$s" | cut -c2- | base64 -d | zlib-flate -uncompress`
- `scripts/blueprint.py encode|decode|info` does this for you.

## 2. Top-level objects

Exactly one key at the root: `blueprint`, `blueprint_book`, `upgrade_planner` or `deconstruction_planner`.

```json
{"blueprint": {
  "item": "blueprint",
  "label": "Green circuits 3:2",
  "description": "optional text",
  "icons": [{"signal": {"name": "electronic-circuit"}, "index": 1}],
  "entities": [ ... ],
  "tiles": [{"name": "refined-concrete", "position": {"x": 0, "y": 0}}],
  "wires": [[1, 5, 2, 5]],
  "snap-to-grid": {"x": 8, "y": 8},          // optional
  "absolute-snapping": true,                // optional
  "version": 562949954076673
}}
```
- `icons`: 1–4 entries, `index` 1-based. In 2.0 `signal.type` is optional and defaults to `"item"`;
  use `"type": "fluid"`, `"virtual"`, `"recipe"`, `"entity"` for other kinds. In 1.1 `type` is required.
- A blueprint with zero entities and zero tiles cannot be imported.

Blueprint book:
```json
{"blueprint_book": {"item": "blueprint-book", "label": "Mall", "active_index": 0,
  "blueprints": [{"index": 0, "blueprint": {...}}, {"index": 1, "blueprint": {...}}],
  "version": 562949954076673}}
```

## 3. Coordinates and positions

- +x = east, +y = south. Units = tiles. The origin is arbitrary; the game recentres on import.
- `position` is the **centre** of the entity. For an entity of footprint w×h whose top-left tile is (tx, ty):
  `x = tx + w/2`, `y = ty + h/2`.
  - 1×1 (belt, inserter, pole, pipe, chest): centre at `.5` (e.g. 3.5, 7.5)
  - 2×2 (stone/steel furnace, big pole, substation): centre on integers
  - 3×3 (assemblers, drills, beacons, chem plant): `.5`
  - 5×5 (refinery, foundry): `.5`; 4×4 (EM plant, roboport): integers
  - non-square (splitter 2×1, pump 1×2, combinators 1×2, boiler 3×2, steam engine 3×5): the
    footprint is rotated with the direction — width/height swap for east/west.
- Tiles use the integer **top-left** of the tile, not the centre.
- Rails (2.0) live on a 2×2 rail grid with special centres; avoid generating rails unless asked and
  then copy positions from an in-game blueprint.

`scripts/blueprint.py` builder takes top-left tile coordinates and computes centres and rotated
footprints, which removes the most common source of broken blueprints.

## 4. Directions

| | N | E | S | W |
|---|---|---|---|---|
| 2.0 (16-way `defines.direction`) | 0 | 4 | 8 | 12 |
| 1.1 (8-way) | 0 | 2 | 4 | 6 |

`direction` is omitted when it is north (0).

What direction means:
- **transport-belt / underground-belt / splitter / loader**: the direction items travel.
  Underground pairs: both halves have the same direction (travel direction); entrance has
  `"type": "input"`, exit `"type": "output"`.
- **inserters**: the side the inserter **picks up from**; it drops on the opposite side.
  Prototype: `pickup_position = {0,-1}`, `insert_position = {0,1.2}` for a north-facing inserter.
  So an inserter with direction N takes from the tile north of it and puts into the tile south.
  Long-handed: pickup 2 tiles away, drop 2 tiles away (`{0,-2}` → `{0,2.2}`).
  - Belt above, machine below → `N`. Machine above, belt below → `N` as well (items still move N→S).
  - Machine above, items must go up into it from a belt below → `S`.
- **assembling machines / chemical plants / refineries**: direction only rotates fluid connections
  (matters for fluid recipes). Furnaces/most solid-only machines: leave north.
- **mining drills**: output drop point is in front (direction side), one tile outside the edge centre.
- **offshore pump**: direction = which way the output pipe points (away from the water, roughly).
- **pumps**: direction = flow direction.

## 5. Entity fields

Always: `entity_number` (1..n, unique, referenced by wires), `name`, `position`.

| field | where | example |
|---|---|---|
| `direction` | rotatable entities | `4` |
| `recipe` | assembling machines, chem plants, refineries… (not furnaces – they auto-select) | `"copper-cable"` |
| `recipe_quality` | 2.0 quality recipes | `"rare"` |
| `quality` | any entity (2.0) | `"uncommon"` |
| `type` | underground-belt / loader: `"input"` or `"output"` | |
| `input_priority`, `output_priority` | splitter: `"left"`/`"right"` | |
| `filter` | splitter filter item (2.0: `{"name": "iron-plate"}`; 1.1: `"iron-plate"`) | |
| `filters` | inserters/loaders filter list: `[{"index":1,"name":"coal"}]` (2.0 adds `"comparator":"="`, `"quality"`) | |
| `use_filters` | 2.0 inserters: `true` to enable the filter list | |
| `bar` | chests: slot limit | `10` |
| `items` | module/fuel requests (see §8) | |
| `request_filters` | requester/buffer chests (2.0 uses `{"sections":[{"index":1,"filters":[{"index":1,"name":"iron-plate","count":100,"comparator":"=","quality":"normal"}]}]}`) | |
| `control_behavior` | circuit settings; copy from an in-game export when possible | |
| `station`, `manual_trains_limit` | train stops | |

Constant combinator (2.0) — used by this skill as input markers (`Blueprint.add_marker`):
```json
{"name": "constant-combinator", "control_behavior": {"sections": {"sections": [
  {"index": 1, "filters": [{"index": 1, "type": "item", "name": "stone", "quality": "normal",
                            "comparator": "=", "count": 1440}]}]}}}
```
`type` is `"item"`, `"fluid"` or `"virtual"`. 1.1 format: `"control_behavior": {"filters": [{"index": 1,
"signal": {"type": "item", "name": "stone"}, "count": 1440}]}`.

Train stop with circuit train limit (2.0, from a real community blueprint):
```json
{"name": "train-stop", "station": "[item=iron-plate] Pickup",
 "control_behavior": {"set_trains_limit": true, "trains_limit_signal": {"type": "virtual", "name": "signal-L"}}}
```
Arithmetic combinator: `{"arithmetic_conditions": {"first_signal": {"type": "item", "name": "iron-plate"},
"second_constant": 8000, "operation": "/", "output_signal": {"type": "virtual", "name": "signal-L"}}}`
(optional `first_signal_networks: {"red": true, "green": false}`). Decider: `{"decider_conditions":
{"conditions": [{"first_signal": ..., "constant" | "second_signal": ..., "comparator": "<"}], "outputs":
[{"signal": ..., "copy_count_from_input": true}]}}`. Wire combinator inputs with connector 1/2, outputs 3/4.

When unsure about a rarely-used field, generate the entity without it and tell the user to set it in-game,
or ask the user to export a sample blueprint from their game and decode it to copy the exact shape.

## 6. Fluid connection sides (direction = north, from factorio-data 2.1)

Rotate everything clockwise for E/S/W. Offsets are from the machine centre; the pipe goes in the tile just
outside that edge.

| machine | inputs | outputs |
|---|---|---|
| assembling-machine-2/3 (fluid recipe) | north edge centre (0,-1) → pipe tile at y-2 | south edge centre (0,+1) |
| chemical-plant 3×3 | north edge, x = -1 and +1 | south edge, x = -1 and +1 |
| oil-refinery 5×5 | south edge, x = -1 and +1 (water / crude) | north edge, x = -2, 0, +2 (heavy, light, petroleum in recipe order) |
| foundry 5×5 | south edge, x = -1 and +1 | north edge, x = -1 and +1 |
| cryogenic-plant 5×5 | south edge, x = -2, 0, +2 | north edge, x = -2, 0, +2 |
| electromagnetic-plant 4×4 | two fluid boxes with pass-through ports on all four sides (input W/E at (-1.5,0.5)/(1.5,-0.5), output S/N at (0.5,1.5)/(-0.5,-1.5)) | — |

Which fluid enters which port follows the order of fluid ingredients in the recipe. Keep fluid layouts
simple and say clearly in the response which pipe carries what.

`pipe-to-ground`: `direction` = the side of its normal (above-ground) connection; the underground
connection goes out the opposite side. A pair spanning a gap going east is therefore: west piece
direction **W**, east piece direction **E** (they face away from each other). `max_underground_distance = 10`; keep the gap ≤ 9 tiles to be safe.
Adjacent plain `pipe`s always connect to each other — two different fluids must never touch; use
pipe-to-ground to cross.

## 7. Wires

2.0: a top-level `wires` array of 4-tuples
`[source_entity_number, source_connector, target_entity_number, target_connector]`.

| connector (`defines.wire_connector_id`) | value |
|---|---|
| circuit_red / combinator_input_red | 1 |
| circuit_green / combinator_input_green | 2 |
| combinator_output_red | 3 |
| combinator_output_green | 4 |
| pole_copper / power_switch_left_copper | 5 |
| power_switch_right_copper | 6 |

Example: two poles with copper + red + green: `[[1,5,2,5],[1,1,2,1],[1,2,2,2]]`.

Copper wires between poles should be included: build them with `Blueprint.connect_poles()`.

1.1: per-entity `neighbours: [ids]` (copper) and
`connections: {"1": {"red": [{"entity_id": 2}], "green": [...]}, "2": {...}}`
(`"2"` = combinator output side, `circuit_id: 2` marks the far side's output).

## 8. Modules and item requests

2.0 (`BlueprintInsertPlan`):
```json
"items": [{"id": {"name": "productivity-module-3", "quality": "normal"},
           "items": {"in_inventory": [{"inventory": 4, "stack": 0}, {"inventory": 4, "stack": 1}]}}]
```
Module inventory index: assembling-machine/furnace/rocket-silo (crafter_modules) = 4, mining-drill = 2,
lab = 3, beacon = 1. Each `in_inventory` entry is one slot; add `"count": n` for stacks of fuel/ammo.

1.1: `"items": {"productivity-module-3": 4}`.

## 9. Versions

`version = major<<48 | minor<<32 | patch<<16 | build`
- `562949954076673` = 2.0.10.1 (safe default for 2.x)
- `281479278886912` = 1.1.110.0
A blueprint stamped with a version **newer** than the player's game may be refused; older is migrated.
`blueprint.py version 2.0.28` converts.

## 10. 1.1 → 2.0 cheat-sheet

| topic | 1.1 | 2.0 |
|---|---|---|
| directions | 0,2,4,6 | 0,4,8,12 |
| wires | `connections`/`neighbours` on entities | top-level `wires` tuples |
| modules | `{"name": count}` | `BlueprintInsertPlan` list |
| icon signal type | required | optional (defaults item) |
| filter-inserter / stack-inserter | separate entities | `inserter`… with `use_filters`; `stack-inserter`→`bulk-inserter` (SA adds a new `stack-inserter`) |
| logistic chests | `logistic-chest-requester` … | `requester-chest`, `passive-provider-chest`, `active-provider-chest`, `storage-chest`, `buffer-chest` |
| rails | `straight-rail`, `curved-rail` (8 dirs) | new rail set (`straight-rail`, `curved-rail-a/b`, `half-diagonal-rail`); old ones appear as `legacy-*` |
| new entities | — | `selector-combinator`, `display-panel`, quality, SA buildings |
