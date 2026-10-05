# Circuit and logistic control — exact 2.0 JSON shapes

Every shape below was decoded from community blueprints that work in game (Fulgora Starter, Fulgora Mall,
Gleba Base (Mall+All), Vulcanus MALL; 2026-10). Pass the dict as `control_behavior=` (or the other named field)
to `Blueprint.add`. Wire with `bp.wire(a, b, "red"|"green", a_side, b_side)`; side is `None` for chests,
machines, inserters, poles and constant combinators, `"in"`/`"out"` for arithmetic / decider / selector
combinators (2.0 connector ids: 1 red, 2 green, 3 red output, 4 green output; 5 copper).

Signals: `{"name": "iron-plate"}` (item; `"type": "item"` may be given), `{"type": "fluid", "name": "water"}`,
`{"type": "virtual", "name": "signal-A"}`, `signal-each`, `signal-everything`, `signal-anything`, recipes
`{"type": "recipe", "name": "ice-melting"}`. Comparators: `"<" ">" "=" "≥" "≤" "≠"`.

## Contents
1. Enable / disable on a condition
2. Logistic-network conditions (no wires)
3. Reading machines, chests, belts, power
4. Requests from the circuit
5. The dynamic mall
6. Combinators
7. Alarms, panels, lamps
8. Filters from the circuit

## 1. Enable / disable on a condition (wired)

Inserter (any kind), belt, pump, power switch, machine:
```json
"control_behavior": {"circuit_enabled": true,
  "circuit_condition": {"first_signal": {"name": "piercing-rounds-magazine"}, "constant": 500, "comparator": "<"}}
```
- ammo inserter runs while magazines < 500 (Gleba turret ring);
- fuel inserter into a heating tower runs while accumulator charge `signal-A` < 50 (Fulgora Mall, Gleba);
- refinery / chemical plant runs while a tank is low: `{"type": "fluid", "name": "heavy-oil"}` < 5000;
- pump runs while a tank is full enough: `water` > 10000;
- power switch: `{"circuit_enabled": true, "circuit_condition": {...}}` plus top-level `"switch_state": false`.

Chests: `{"circuit_condition_enabled": false}` is what the game writes for a plain chest that only reads.

## 2. Logistic-network conditions (no wires needed)

```json
"control_behavior": {"connect_to_logistic_network": true,
  "logistic_condition": {"first_signal": {"name": "electronic-circuit"}, "constant": 2000, "comparator": "<"}}
```
Output inserter of a mall line: stop at 2000 in the network. Machines take the same
`logistic_condition` (decoded: electric furnace stops when the network holds > 1000 iron plates).
This is the cheapest anti-pile-up tool: use it on every mall output and on anything that can spoil.

## 3. Reading machines, chests, belts, power

| entity | control_behavior | gives |
|---|---|---|
| assembler / foundry / EM plant | `{"read_contents": true, "include_in_crafting": false}` | contents |
| assembler | `{"read_ingredients": true}` (with `set_recipe`) | the current recipe's ingredients |
| biochamber | `{"read_contents": true, "read_fuel": true}` | contents + nutrients |
| recycler | `{"read_contents": true}` | contents |
| chest | default when wired | contents (no field needed) |
| belt | `{"circuit_read_hand_contents": true, "circuit_contents_read_mode": 1}` (1 hold, 2 pulse) | items on the belt |
| inserter | `{"circuit_read_hand_contents": true, "circuit_hand_read_mode": 1}` | hand |
| accumulator | `{"output_signal": {"type": "virtual", "name": "signal-A"}}` | charge % |
| heating tower | `{"read_temperature": true, "temperature_signal": {"type": "virtual", "name": "signal-T"}}` | °C |
| roboport | `{"read_robot_stats": true}` or `{"read_items_mode": 2}` | robots / network contents |
| turret | `{"read_ammo": true}` | ammo |

Machines also take network selection when they both read and are set:
`"input_networks": {"red": true, "green": false}, "output_networks": {"red": false, "green": true}`.

## 4. Requests from the circuit

Requester chest whose requests come from the wire (dynamic mall):
```json
"control_behavior": {"set_requests": true, "read_contents": false, "circuit_condition_enabled": false}
```
Requester chest that only requests while a condition holds (Gleba nutrients):
```json
"control_behavior": {"circuit_condition_enabled": true,
  "circuit_condition": {"first_signal": {"name": "nutrients"}, "constant": 20, "comparator": "<"}}
```
Static requests (2.0) — `request_filters`, optionally `"request_from_buffers": true` and per-filter
`"import_from": "nauvis"` (planet to import from when the chest is on a platform / pad):
```json
"request_filters": {"sections": [{"index": 1, "filters": [
  {"index": 1, "name": "processing-unit", "quality": "normal", "comparator": "=", "count": 20}]}],
  "request_from_buffers": true}
```
Cargo landing pad: `{"set_requests": true, "read_contents": false}` lets a circuit set its orbit requests.

## 5. The dynamic mall

See `examples/dynamic_mall_cell.py` (validated) and `references/base-design.md` §6.
```
assembler:  {"input_networks": {"red": true, "green": false}, "output_networks": {"red": false, "green": true},
             "set_recipe": true, "read_ingredients": true}
decider:    {"decider_conditions": {"conditions": [{"first_signal": {"type": "virtual", "name": "signal-each"},
             "constant": 0, "comparator": "<"}], "outputs": [{"signal": {"type": "virtual", "name": "signal-each"},
             "copy_count_from_input": false}]}}
arithmetic: {"arithmetic_conditions": {"first_signal": {"type": "virtual", "name": "signal-each"},
             "second_constant": 4, "operation": "*", "output_signal": {"type": "virtual", "name": "signal-each"}}}
constant:   wanted items with NEGATIVE counts (-target) in "sections"
requester:  {"set_requests": true}
```
Wires: buffer chests + constant (green) → decider input; decider output (red) → assembler; assembler (green)
→ arithmetic input; arithmetic output (green) → requester.
The community decoded form omits `"constant": 0, "comparator": "<"` (those are the defaults); writing them
explicitly is equivalent and clearer.

## 6. Combinators

Arithmetic: `{"arithmetic_conditions": {"first_signal": …, "second_constant": 4 | "second_signal": …,
"operation": "*" | "/" | "+" | "-" | "%" | "^" | "<<" | ">>" | "AND" | "OR" | "XOR", "output_signal": …}}`
(optional `first_signal_networks: {"red": true, "green": false}`).
Decider: `{"decider_conditions": {"conditions": [{…, "comparator": "<"}, …], "outputs": [{"signal": …,
"copy_count_from_input": true | false}], "else_outputs": []}}`.
Selector (quality transfer, decoded from a Fulgora quality build):
`{"operation": "quality-transfer", "select_quality_from_signal": true, "quality_source_signal": {"name": "ice"},
"quality_destination_signal": {"type": "recipe", "name": "ice-melting"}}`.
Constant: `{"sections": {"sections": [{"index": 1, "filters": [{"index": 1, "name": …, "quality": "normal",
"comparator": "=", "count": …}]}]}}` — also the input markers of this skill (`add_marker`).

## 7. Alarms, panels, lamps

Programmable speaker with a map alert:
```json
{"control_behavior": {"circuit_condition": {"first_signal": {"name": "uranium-fuel-cell"}, "constant": 16, "comparator": "<"},
   "circuit_parameters": {"signal_value_is_pitch": false, "stop_playing_sounds": false, "instrument_id": 0, "note_id": 1}},
 "parameters": {"playback_volume": 1, "playback_mode": "local", "allow_polyphony": false, "volume_controlled_by_signal": false},
 "alert_parameters": {"show_alert": true, "show_on_map": true, "icon_signal_id": {"name": "uranium-fuel-cell"},
   "alert_message": "Need more fuel cells"}}
```
Display panel (labels inputs; with a condition it becomes a status light):
```json
{"control_behavior": {"parameters": [{"condition": {"first_signal": {"type": "virtual", "name": "signal-dot"},
   "constant": 1, "comparator": "≠"}, "icon": {"name": "agricultural-science-pack"}, "text": "Science Production Offline"}]},
 "always_show": true, "show_in_chart": true}
```
A plain label needs only `"text": "Input scrap", "icon": {"name": "scrap"}, "always_show": true` (top-level).
Lamp: `{"circuit_enabled": true, "circuit_condition": {…}, "use_colors": true, "rgb_signal": {"type":
"virtual", "name": "signal-green"}}` with `"color": {"r": 1, "g": 1, "b": 1, "a": 1}, "always_on": true`.

## 8. Filters from the circuit

Inserter filters set by the wire (quality sorting, mixed-belt sorting):
`{"circuit_set_filters": true}` plus `"use_filters": true` and a starting `filters` list; a stack inserter
may carry `"override_stack_size": 16`. Static filters by quality list one entry per quality:
`{"index": 2, "name": "low-density-structure", "quality": "uncommon", "comparator": "="}`.
