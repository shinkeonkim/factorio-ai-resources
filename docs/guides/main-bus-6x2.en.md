# Main bus 6+2 guide

[한국어](main-bus-6x2.md)

Factories in this repository assume a **horizontal main bus**: resources travel in groups of 6 lanes with
2 empty rows between groups.

```
          ↑ branch (to a factory)   ↑ branch
..........^......................^..........   ← 2 empty rows: branch belts, underground ends, poles
..........^......................^..........
>>>>>>>>>U^u>>>>>>>>>>>>>>>>>>>>>^..........   ┐
>>>>>>>>>U^u>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   │
>>>>>>>>>>^>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   │ group of 6 (lanes 0-5 from the top)
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   │
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   │
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   ┘
............................................   ← 2 empty rows
............................................
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   next group ...
```

## Why 6 + 2

- Six lanes hold one family per group (e.g. iron ×4 + copper ×2); the two empty rows hold branch belts,
  underground ends, poles and lamps.
- More lanes per width than the common "4 + 2" bus. The catch: crossing a whole group underground needs a
  6-tile span, which **yellow undergrounds (max 4) cannot do**. So this kit never jumps a group; at a
  branch column the other lanes **dive only 1-2 tiles**. The same layout works for every tier.

## Kit

| Piece | Use |
|---|---|
| [Segment](../../blueprints/main-bus-6x2-segment/README.en.md) | the 6 groups above (5 solid + 1 fluid), 33 tiles, lane labels |
| [Tap](../../blueprints/main-bus-6x2-tap/README.en.md) | one lane north: full / half (splitter), lanes 0-5, fluid lines 0-5 |
| [Crossing](../../blueprints/main-bus-6x2-crossing/README.en.md) | a branch from a lower group passes through a group (belt / fluid) |

### Making a branch

1. Pick the column, super-force build (Shift+click) the tap piece for the lane over the group.
2. Put a crossing piece on the same column of every group above it.
3. The branch leaves above the top group into the factory. Keep 4-6 tiles between branches.

## This repository's bus (6 groups, top → bottom)

| Group | lanes 0-5 | Note |
|---|---|---|
| 1 | iron ×6 | |
| 2 | copper ×6 | |
| 3 | green ×2, red ×2, blue circuits ×2 | |
| 4 | steel ×2, plastic ×2, stone, stone brick | |
| 5 | coal, sulfur, battery, engine, electric engine, low density structure | late-tech intermediates |
| 6 | **fluids**: petroleum, light oil, heavy oil, lubricant, sulfuric acid, water | pipe-to-ground chains; water optional with Waterfill |

- 46 rows in total. Most-used groups are on top so branches cross fewer groups.
- The fluid group is **at the bottom**: solid branches only go up, so they never cross fluid lines.

### Fluid lines

- Each fluid line is a **pipe-to-ground chain** (a pair every 10 tiles). Pipe-to-ground connects only on its
  single above-ground side, so six chains can sit side by side without mixing.
- **Fluid tap** (`fluid-line*` in the [tap pieces](../../blueprints/main-bus-6x2-tap/README.en.md)): surfaces one
  line inside a span (2-8 tiles into a pair) and climbs to the gap row above the group.
- **Crossing a group** (`fluid` variant of the [crossing piece](../../blueprints/main-bus-6x2-crossing/README.en.md)):
  one pipe-to-ground pair from the first gap row below to the last gap row above. Stacked group by group,
  **the two gap rows are where consecutive pairs meet**.

```
  ...P...   ← gap row below the next group: next crossing (south-facing)
  ...P...   ← gap row above this group: crossing top (north-facing)
  >>>>>>>   ┐
  >>>>>>>   │ 6-lane group (passed underground)
  >>>>>>>   ┘
  ...P...   ← gap row below: crossing bottom (south-facing)
  ...P...   ← top of the crossing of the group below
```

- With Waterfill, **water is made next to the factory**; the water line is a spare.
- Put the most demanded branches first (west). Splitters always halve, so downstream factories only fill
  after upstream ones are saturated.

## Upgrading

Swap belts, undergrounds and splitters with the upgrade planner; lanes keep their place. Per lane:
yellow 900/min, red 1,800, blue 2,700, turbo 3,600.

## Sources

- Nilaus Base-In-A-Book bus pieces (Full line / Half line, 4-lane groups) — see [07 Nilaus](../demo-analysis/07-nilaus-base-in-a-book.en.md)
- [Factorio Main Bus Guide (factoriocalculator.blog)](https://factoriocalculator.blog/factorio-main-bus/), [Steam guide: How to Build a Main Bus](https://steamcommunity.com/sharedfiles/filedetails/?id=754378586)
