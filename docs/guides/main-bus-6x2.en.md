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
| [Segment](../../blueprints/main-bus-6x2-segment/README.en.md) | 6 lanes × 3 groups, 32 tiles, lane label combinators |
| [Tap](../../blueprints/main-bus-6x2-tap/README.en.md) | one lane north: full / half (splitter), lanes 0-5 |
| [Crossing](../../blueprints/main-bus-6x2-crossing/README.en.md) | a branch from a lower group passes through a group |

### Making a branch

1. Pick the column, super-force build (Shift+click) the tap piece for the lane over the group.
2. Put a crossing piece on the same column of every group above it.
3. The branch leaves above the top group into the factory. Keep 4-6 tiles between branches.

## Suggested lanes (3 groups, 18 lanes)

| Group | lanes 0-5 |
|---|---|
| 1 | iron ×4, copper ×2 |
| 2 | copper ×2, steel, stone brick, green circuits ×2 |
| 3 | plastic, red circuits, coal, stone, sulfur, blue circuits |

- Fluids (water, crude, petroleum, lubricant, sulfuric acid) stay off the bus in pipes. With Waterfill,
  **make water next to the factory that needs it**.
- Put the most demanded branches first (west). Splitters always halve, so downstream factories only fill
  after upstream ones are saturated.

## Upgrading

Swap belts, undergrounds and splitters with the upgrade planner; lanes keep their place. Per lane:
yellow 900/min, red 1,800, blue 2,700, turbo 3,600.

## Sources

- Nilaus Base-In-A-Book bus pieces (Full line / Half line, 4-lane groups) — see [07 Nilaus](../demo-analysis/07-nilaus-base-in-a-book.en.md)
- [Factorio Main Bus Guide (factoriocalculator.blog)](https://factoriocalculator.blog/factorio-main-bus/), [Steam guide: How to Build a Main Bus](https://steamcommunity.com/sharedfiles/filedetails/?id=754378586)
