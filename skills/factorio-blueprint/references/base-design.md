# Dense all-in-one bases (planet bases, malls, "make everything" factories)

How the community builds the bases people actually use. Measured with `scripts/study.py` on top-rated
factorioprints designs (2026-10): Space Ghost "Vulcanus MALL from ores" (-OL_rvijZDQI7WVI8mxG), Space Ghost
"Fulgora blueprint book. All in" (-OUf5gju1G_1O_K38VLl), Nir Adar / Jepakazol "Fulgora Starter" (-OO5V-wUkdrkhAji7y5m),
Jepakazol "Gleba Base (Mall+All)" (-OFa_ZWh1hQypFqucMTy), "Fulgora Mall" (-OX4QBKmwEZ6dIBJY5C5), plus the
"… all production, no mods" planet bases. Read this before designing anything bigger than one module.

## Contents
1. What they measure like
2. Shape: one dense rectangle, labelled inputs
3. Inside: rows between belts, direct insertion, local fluids
4. Belts for volume, robots for variety
5. Circuits that make it self-regulating
6. The dynamic mall (one assembler, many recipes)
7. Power that starts itself
8. Defence in layers (Gleba-style)
9. Modules, beacons, tiers
10. What the description tells the player
11. Checklist
12. Researching more designs

## 1. What they measure like

| design | size | entities | density | machines | inserter flows | circuits |
|---|---|---:|---:|---:|---|---|
| Vulcanus MALL basic (77 items, belts only) | 164×90 | 6,476 | **0.44** | 356 (62 beacons) | belt→machine 47 %, machine→belt 29 %, **machine→machine 11 %**, →provider 6 % | assembler / inserter / chem-plant / refinery / pump enable conditions |
| Vulcanus MALL extended (115 items) | 188×92 | 7,308 | 0.42 | 427 | belt→machine 44 %, machine→belt 30 %, machine→machine 9 %, requester→machine 2 % (24 rare inputs) | + inserters on logistic conditions |
| Fulgora Starter (60 SPM, everything Fulgora makes) | 72×50 | 1,041 | 0.29 | 93 | belt→machine 43 %, machine→buffer 11 %, machine→machine 7 %, requester→machine 6 % | **dynamic mall**, 59 gated inserters, recycler read |
| Fulgora Mall (4-planet tech) | 224×110 | 7,458 | 0.30 | 365 | belt→machine 50 %, chest→belt 11 %, machine→buffer 8 %, machine→machine 5 % | dynamic mall, self-powered heating towers, alarms |
| Gleba Base (Mall + All) | 218×168 | 8,915 | 0.24 (incl. defence) | 276 | belt→machine 30 %, machine→belt 23 %, machine→machine 10 %, requester→turret 9 % | 1,037 filter inserters, nutrient/fuel gating, alarms |
| *this repo's first planet bases (for contrast)* | 264×201 | 9,376 | **0.18** | 147 | requester→belt 14 %, belt→provider 13 %, machine→machine 0 % | markers only |
| *this repo, island generator (lib/base.py, 2026-10)* | 145×98 (Gleba) – 287×211 (Aquilo) | 3k–19k | 0.10–0.31 (coverage 0.19–0.38) | 109–159 | requester→machine dominant | stock limits, burner fuel on accumulator, alarm |

Tile coverage (share of tiles under an entity, `study.py`) is the fairer number when machines are big:
the references cover **0.55–0.82** of their area. A generator that stands blocks on fluid streets tops out near
0.35; reaching the references needs hand-designed dense blocks (foundries around a shared pipe, two-belt rows).

Targets for a new dense base: **density ≥ 0.3** in the core, **direct insertion ≥ 5 %** of inserters wherever
recipes chain, and circuit gating on every output that can pile up.

## 2. Shape: one dense rectangle, labelled inputs

- **No planet-wide bus.** One rectangle (aspect 1.3–2) holds everything. Malls are rows of small production
  islands joined by short belts. Power and defence go around the edge, never through the middle.
- **Few, labelled inputs on the edge.** The player connects 2–9 things: "deliver resources to the underground
  belts and pipes" (Vulcanus mall: lava, calcite, coal, tungsten ore, sulfuric acid, plus stone *out*),
  "2 stacked belts of scrap" + heavy oil (Fulgora), "1200/min of each fruit **from any side**" + water (Gleba).
  Every input point carries a **display panel** with the item icon and text such as "Input scrap" (this repo:
  `add_marker` constant combinators do the same job; add a display panel too when the base is big).
- **Inputs end in an underground belt or pipe-to-ground at the boundary**, so the player's line plugs straight
  in. Gleba accepts fruit at all four corners: a ring belt picks it up wherever it arrives.
- Waste has an exit too: Vulcanus stone leaves on its own belts ("remove the stone from the factory"), and
  Fulgora overflow goes to recycler voids inside the base.

## 3. Inside: rows between belts, direct insertion, local fluids

- **Production row** = a line of machines with a belt above and a belt below (4 lanes of ingredients).
  Inner inserters for the near belt, long-handed inserters reach the far belt. The output goes back onto a lane
  or straight into the next machine.
- **Direct insertion chains** for intermediates that never need a belt: gears → engines, cable → circuits,
  casting → next casting. About 1 inserter in 10 moves machine→machine.
- **Fluids are made where they are used.** The Vulcanus mall has 18 *molten-iron-from-lava* foundries spread
  over its islands rather than one molten-iron plant with long pipes. Fulgora has ice-melting next to each
  holmium-solution plant. Long fluid mains are rare; a fluid crosses at most one island.
- **Short belt segments, many splitters/undergrounds**: belts weave between islands (undergrounds are 10–20 % of
  belt entities). Items do not travel the whole base; each island takes what it needs from the nearest lane.
- **Recycler rows** (Fulgora): recyclers on both sides of the scrap belt, outputs onto a mixed belt that loops
  through **filter inserters** into chests (buffer / passive provider) — sorting by filter, not by splitters.

## 4. Belts for volume, robots for variety

- High-volume flows stay on belts: scrap, ore, plates, fruit, stone. Gleba fruit runs on belts too; robots only
  carry seeds and science. (Delivering fruit by robot "needs more bots and power".)
- Robots carry **many low-volume items**: mall ingredients that are needed by only one machine, ammunition
  for turrets, modules, rocket parts and silo cargo. Requester chests feed machines or a short belt;
  **buffer chests** collect sorted output (Fulgora Starter: 48 buffers) so it is both stored and available.
- The robot network is local (one roboport grid over the rectangle) and needs only 50–150 robots.

## 5. Circuits that make it self-regulating

Exact JSON shapes for all of these are in `references/circuits.md`.

| purpose | how | seen in |
|---|---|---|
| stop overproduction of a mall item | output inserter enabled by the **logistic network count** (`connect_to_logistic_network` + `logistic_condition`, e.g. electronic-circuit < 2000) | every mall |
| stop a machine instead | assembler / furnace `circuit_enabled` or `logistic_condition` (iron-plate > 1000) | Vulcanus, Fulgora |
| oil cracking balance | refinery / chem plant enabled while a tank is low (heavy-oil < 5000, lubricant < 20000); pump enabled when a tank is full enough | Vulcanus mall |
| burn fuel only when needed | accumulator outputs charge as `signal-A`; burner/fuel inserters into heating towers run while A < 50 | Fulgora Mall, Gleba |
| spoilage / eggs (Gleba) | inserters enabled while nutrients < N; requester only while network nutrients < 20; biochamber `read_contents` + `read_fuel` | Gleba |
| alarms | programmable speaker + display panel on a condition (water < 9000, fuel cells < 16, "Science Production Offline") | Gleba, Fulgora |
| recycler sorting | filter inserters, `circuit_set_filters` from a selector/decider when sorting by quality | Fulgora quality builds |
| overflow | belt `circuit_read_hand_contents` / `circuit_contents_read_mode` to count, splitter priority to the void | Fulgora |

## 6. The dynamic mall (one assembler, many recipes)

Used by both Fulgora builds and the Gleba base to make dozens of building items with a few assemblers:

```
buffer chests (contents, green) ─┐
constant combinator (wanted: item = -target, green) ─┤→ decider "each < 0 → each = 1" ─red→ assembler
                                                                  set_recipe (red in), read_ingredients (green out)
assembler ingredients (green out) → arithmetic "each × 4 → each" → requester chest set_requests
```
- Stock minus target is negative for every item that is short; the decider passes those; the assembler
  **sets its recipe** from the circuit signal, **reads its ingredients**, and the arithmetic × 4 turns them
  into requests on the requester chest beside it. When the item is restocked the signal disappears and the
  assembler switches to the next missing item.
- Output goes into the buffer chests that are read by the same network.
- Wiring (2.0 connector ids): chest/assembler/constant use 1 (red) / 2 (green); combinator input 1/2,
  output 3/4. The JSON is in `references/circuits.md` §5.

## 7. Power that starts itself

- **Self-powered**: Fulgora Mall (30 heating towers, 88 turbines, 428 accumulators, 26 lightning collectors) and
  Gleba (22 towers, 39 turbines, 372 solar panels, 214 accumulators) carry their own heating towers → heat
  exchangers → turbines, with
  burner inserters gated by accumulator charge, plus a solar/accumulator band so the base can restart from
  nothing ("easily re-start when it has resources").
- Vulcanus: acid neutralisation → 500 °C steam → turbines (one block of 900+ turbines in the science book).
- Fulgora: lightning rods over the base + accumulator field; heating towers as backup.

## 8. Defence in layers (Gleba-style)

Outside → inside: a field of **land mines** (551), **stone walls** (1,279 + 16 gates), **turret rows** (321 laser,
81 rocket for big stompers, 31 tesla to slow them, 15 gun turrets on requester chests, 27 artillery fed by
requesters), a power ring (solar + accumulators), then the factory. Turret ammo
inserters are gated by stock (magazines < 500). Walls stop only where input belts / pipes enter.

## 9. Modules, beacons, tiers

- Productivity modules in the machines that allow them (≈ 1 per 2 machines), speed modules in beacons around
  the expensive lines only (the Vulcanus mall has 62 beacons for 356 machines; science books are fully
  beaconed), efficiency modules in recyclers and turbines' support machines.
- The same layout ships in several tiers (red/AM2, blue/AM3, green/foundry): only names change, so the
  player upgrades in place.

## 10. What the description tells the player

Every good print says, in a few lines: what it makes (and SPM), tech required, **inputs and their rates**,
how to start (connect power, add 50–150 logistic robots, put rocket fuel / spoilage / one egg in, "remove the
stone"), and what is optional ("remove the beacons until you can supply 1200 fruit/min"). Put the same in
`bp.description` and in the README.

## 11. Checklist

- [ ] one rectangle; inputs only on the edge, each labelled (marker + panel), ending in underground/PTG
- [ ] density ≥ 0.3 in the core; no tile-long empty streets except where pipes/belts must run
- [ ] fluids produced next to their consumers (no fluid main crossing the whole base)
- [ ] direct insertion wherever an intermediate feeds a single consumer
- [ ] high-volume on belts, low-volume by robots; buffers for sorted output
- [ ] every pile-up point gated (logistic condition / circuit condition); waste has a void
- [ ] power that restarts itself; accumulators to gate fuel
- [ ] frame per planet: Gleba mines + walls + turrets, Fulgora lightning rods + accumulators, Aquilo heat,
      Vulcanus none (build outside demolisher territory)
- [ ] description: makes / needs / how to start

## 12. Researching more designs

factorioprints exposes its data as JSON (strings stay out of this repo — analyse them in a scratch dir):
```bash
curl -s 'https://facorio-blueprints.firebaseio.com/blueprintSummaries.json?orderBy="numberOfFavorites"&limitToLast=3000' > sums.json
curl -s 'https://facorio-blueprints.firebaseio.com/blueprints/<id>.json' > bp.json   # .blueprintString, .descriptionMarkdown
python3 SKILL_DIR/scripts/study.py <file with the string> --top 4 --map 3
```
