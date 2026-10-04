# 6×6 load balancer (throughput unlimited)

[한국어](01-6x6-balancer.md)

- Source: unknown (standard community design)
- Raw analysis: [data/01-6x6-balancer.md](data/01-6x6-balancer.md)

![6×6 load balancer (throughput unlimited)](images/01-6x6-balancer.webp)

## What it is

Balances 6 input lanes onto 6 output lanes. 18×9, 122 red belts/undergrounds/splitters, no machines or power.
Throughput unlimited: if some outputs back up, everything still flows through the others.

## Against the rules

| Item | Verdict |
|---|---|
| upgrade | ✅ belts only, longest underground gap 4 → same layout from yellow to turbo |
| 6+2 bus | ✅ exactly one bus group wide; smelter output → bus start |
| water | n/a |

## Use

- At the **start of each bus group** (several smelting columns → 6 lanes) and when unloading 6 train lanes onto the bus.
- The string itself is not in the repo (demo-resources is private); the bus kit assumes this balancer in front.
