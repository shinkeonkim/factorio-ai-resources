# Tileable nuclear reactor

[한국어](06-nuclear.md)

- Source: unknown
- Raw analysis: [data/06-nuclear.md](data/06-nuclear.md)

![Tileable nuclear reactor](images/06-nuclear.webp)

## What it is

A 380×15 tileable nuclear plant. Description: **N sets → 480 + 640×(N−1) MW**. A 2×2 reactor core in the
middle (neighbour bonus) with heat pipes, heat exchangers and turbines stretching both ways.
Fuel by red belt + 8 bulk inserters; 42 medium poles + 16 substations; 4,230 floor tiles.

## Against the rules

| Item | Verdict |
|---|---|
| upgrade | reactors have no tiers → "upgrading" = tiling more sets sideways, no layout change ✅ |
| water | ✅ **ideal for Waterfill**: water + offshore pumps beside the exchanger rows, no long water pipes |
| 6+2 bus | fuel cells come by their own belt/train, not the bus |

## Notes

- 640 MW per extra set matches the neighbour-bonus math of a 4-reactor block.
- Whether a spent-cell return path exists should be checked in game.
