# Layout patterns and mechanics

Read this before designing a layout. Coordinates are top-left tiles as used by `Blueprint.add`
(+x east, +y south). ASCII matches `render_ascii`: belts `^>v<`, inserters show item flow `↑→↓←`
(long-handed `⇑⇒⇓⇐`), `+` pole, `=` pipe, letters = machines.

Every layout in §3–§5 is a runnable, validated script in `examples/` — start from the closest one.

## Contents
1. Mechanics that break designs if you get them wrong
2. Choosing a layout shape
3. Direct insertion chain — `examples/green_circuits_3to2.py`
4. Smelting column — `examples/smelting_column.py`
5. Mining outpost — `examples/mining_outpost.py`
6. Assembler row between belts (generic)
7. Fluid machines
8. Beacons
9. Power poles
10. Train stations (wagon geometry, train-limit circuits)
11. Tileable designs

## 1. Mechanics

**Inserters** — `direction` = the side it picks up from; it drops on the opposite side.
Regular reach 1; long-handed reach 2 (it skips the adjacent tile on both sides, which lets one inserter
row serve a belt that is one tile further away). They need power (except burner inserters).
Base throughput (no research): inserter ≈ 0.83 items/s, long-handed ≈ 1.2/s, fast/bulk ≈ 2.31/s.
Machine→machine and machine→belt transfers rise with "inserter capacity bonus" research — say so when a
design depends on it.

**Belt lanes** — every belt has two lanes. An inserter puts items on the **far lane** (seen from the
inserter); it picks from either lane. Side-loading (a belt pointing into the side of another) fills only
the near lane — the standard way to put two items on one belt. State lane assignments in the response.

**Belt turns** — a belt whose only input comes from its side becomes a curve; a belt pointing into the
side of a belt that already has a straight input side-loads. Keep I/O belts straight; let the user hook up
their bus at a clearly stated end.

**Undergrounds** — `Blueprint.underground(name, x, y, dir, gap)`; max gap 4/6/8/10 tiles
(yellow/red/blue/turbo). Use to cross belts or pass under pole rows.

**Splitters** — 2 tiles wide perpendicular to travel. North-facing at top-left (x, y) covers (x, y) and
(x+1, y).

**Furnaces** choose their recipe from the input — never set `recipe` on furnaces. Assemblers, chemical
plants, refineries and Space Age crafters need `recipe`.

**Mining drills** drop output on the tile just outside the middle of their facing edge.

**Power** — every electric entity's footprint must overlap a pole's supply square. Inserter rows on the
far side of a 3×3 machine row are the usual casualty. `validate()` catches this; fix by adding a pole in a
free tile of that inserter row.

## 2. Choosing a shape

| situation | shape |
|---|---|
| intermediate consumed by exactly one next step (cable→circuit, gear→red science) | direct insertion (§3) |
| plates from ore | smelting column (§4) |
| ore patch | mining outpost (§5) |
| one recipe fed from a bus | assembler row between belts (§6) |
| fluid recipes | §7 |
| whole chain (e.g. red science from plates) | stack modules vertically, joined by straight belts; or one row with direct insertion |

Size the build with `calc.py` first; build one tileable slice and repeat it.

## 3. Direct insertion — green circuits 3:2 (`examples/green_circuits_3to2.py`)

Copper cable: 2 per 0.5 s; circuit eats 3 cable per 0.5 s → 3 cable machines per 2 circuit machines.
Circuit row is offset one tile so each cable machine touches a circuit machine through a row-5 inserter
(the middle cable machine feeds both).

```
>>>>>>>>>>>>>>>>>>   y=0  copper plates →
.↓+.↓..↓+.↓+.↓..↓+   y=1  fast inserters (dir N) + poles
A1AA1AA1AA1AA1AA1A   y=2-4 copper-cable AMs at x=0,3,6 (+9 per slice)
AAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAA
.↓.↓+↓.↓..↓.↓+↓.↓.   y=5  fast inserters cable→circuit at x=1,3,5,7
.A2A.A2A..A2A.A2A.   y=6-8 electronic-circuit AMs at x=1,5
.AAA.AAA..AAA.AAA.
.AAA.AAA..AAA.AAA.
.↑⇓⇓+↑⇓⇓..↑⇓⇓+↑⇓⇓.   y=9  fast inserter dir S (iron in), 2 long-handed dir N (circuits out, skip y=10)
>>>>>>>>>>>>>>>>>>   y=10 iron plates →
<<<<<<<<<<<<<<<<<<   y=11 circuits ←
```
Slice = 9 wide, 3 circuits/s with AM2 (5/s with AM3). Note: each cable→circuit inserter must move up to
3 cable/s, which needs capacity research (hand size ≥ 2) or AM2-level speeds will be inserter-capped.

Before committing to a direct-insertion ratio, compute both sides with real crafting times: e.g. with
AM3 a module-2 assembler eats 4 module-1 per 24 s (10/min) while a module-1 assembler makes one per 12 s
(5/min) → two tier-1 machines per tier-2 machine ([T1][T2][T1]), not the other way round.

## 4. Smelting column (`examples/smelting_column.py`)

```
v→F1→^←F1←v     x=0 ore+coal belt ↓ | x=1 inserter W | x=2-3 steel furnace | x=4 inserter W | x=5 plates ↑
v.FF+^+FF.v     | x=6 inserter E | x=7-8 furnace | x=9 inserter E | x=10 ore+coal belt ↓
v→F1→^←F1←v     poles in the free tile under the plate-side inserters every 3 rows
v.FF.^.FF.v
```
Burner furnaces take coal from the same belt (coal on one lane, ore on the other). Stone furnace speed 1,
steel 2: one yellow belt of ore (15/s) feeds 48 stone or 24 steel furnaces (iron/copper plate: 3.2 s).
Electric furnaces (3×3, speed 2) use the same pattern with 3-tile row pitch.

## 5. Mining outpost (`examples/mining_outpost.py`)

```
D1D.D1DD1D.D1DD1D.D1D     drills dir S at y=0 (output at y=3)
DDD+DDDDDD+DDDDDD+DDD     medium pole between each pair: drill x, pole x+3, drill x+4 (pitch 7)
DDD.DDDDDD.DDDDDD.DDD
>>>>>>>>>>>>>>>>>>>>>     shared belt y=3
D1D.D1DD1D.D1DD1D.D1D     drills dir N at y=4
DDD+DDDDDD+DDDDDD+DDD
DDD.DDDDDD.DDDDDD.DDD
```
0.5 ore/s per electric drill (uranium 0.25/s and needs sulfuric acid). 30 drills ≈ one yellow belt.

## 6. Assembler row between belts

```
>>>>>>>>>>>>   y=0  input belt (may carry two items, one per lane)
.↓+.↓+.↓+...   y=1  input inserters dir N at machine middle column, poles in the free tiles
A1AA1AA1A...   y=2-4 assemblers at x=0,3,6,…
AAAAAAAAA...
AAAAAAAAA...
.↓+.↓+.↓+...   y=5  output inserters dir N
<<<<<<<<<<<<   y=6  output belt
```
Two input belts on the same side: y=0 item A, y=1 item B, y=2 = long-handed (dir N, reaches y=0) +
regular inserter (dir N, reaches y=1), machines at y=3. More than two solid inputs: feed from both sides,
or use a two-item belt on each side.

## 7. Fluid machines

- Pipes join every adjacent pipe / fluid port. Two fluids must never touch; cross with pipe-to-ground.
- Chemical plant (dir N): fluid inputs at the north edge (columns x+0 and x+2), outputs at the south edge
  (x+0, x+2). Solid I/O through inserters on the east/west sides or the middle columns.
- Oil refinery (dir N): inputs on the south edge (x+1, x+3); outputs on the north edge (x+0, x+2, x+4).
- AM2/AM3 fluid recipe (dir N): fluid in at north-middle, fluid out at south-middle.
- Rotating the machine rotates the ports clockwise. Details in blueprint-format.md §6.
- After building fluid layouts, trace each pipe network by hand and list which fluid each carries.

## 8. Beacons (2.0)

Beacon 3×3, distribution efficiency 1.5, reaches machines overlapping its 9×9 area (3 tiles out).
With n beacons affecting one machine, each beacon's effect is scaled by 1/√n. Common: rows of AM3 with a
beacon row above and below. Beacons accept speed/efficiency modules only (`modules={"speed-module-3": 2}`).

## 9. Power poles

| pole | supply square | wire reach | rule of thumb |
|---|---|---|---|
| small | 5×5 | 7.5 | every 5–6 tiles |
| medium | 7×7 | 9 | one per two 3×3 machines, in each inserter row that needs it |
| substation | 18×18 | 18 | 18-tile grid |
| big | 4×4 | 32 | transmission only |

Put poles in free tiles of inserter rows. Always call `connect_poles()` then `validate()`.

## 10. Train stations (wagon geometry)

Verified on community 2.0 blueprints: a train stops with the **front of the locomotive at the stop's
centre line**. For a stop centred at x=S facing **west** (train heading west, stop on the north side of
the track) the locomotive covers tile columns S..S+5 and cargo wagon k covers S+7k..S+7k+5; mirror for
east-facing (loco S-6..S-1, wagon k S-7k-6..S-7k-1). Each vehicle is 6 tiles with a 1-tile gap. Wagon
rows = the two tile rows of the straight rail (rail centre y=R → rows R-1, R).
- 6 inserters per wagon side, in the row next to the track; the gap columns (between wagons) are the
  natural place for poles and for an underground belt crossing the track.
- Unloading: inserter picks FROM the wagon side; loading: picks from the chest/belt side.
- Inserters dropping onto a belt fill only its far lane → an unloading belt fed from one side carries
  ≤15/s (fast). Use both sides or two belts for more.
- Train limit from stock: chests chained with one wire colour → arithmetic `item / trainload → L` →
  stop (`set_trains_limit`). For "free space" use a constant combinator with `item = -capacity` on the
  other colour and divide by `-trainload`.
- Rail grids/city blocks: never invent rail geometry; take station tracks from the user's blueprint book
  and only add stops' settings, chests, inserters, belts, poles and circuits around them.

## 11. Tileable designs

- Write `slice(bp, x0)` and loop it; make full-length straight I/O belts outside the loop.
- Check the seam between two slices (a 2-slice build) — overlaps and power gaps show up there.
- Report which end each belt enters/leaves and what lane carries what.
