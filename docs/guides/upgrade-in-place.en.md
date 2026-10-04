# Upgrade-in-place design rules (early → mid → late, same layout)

[한국어](upgrade-in-place.md)

Goal: lay a factory once and move it from early to late game with the **upgrade planner only**, without
changing the layout (e.g. a "Daiso"-style mall, science lines).

## Tiers

| Stage | Belts | Assemblers | Inserters | Poles | Smelting |
|---|---|---|---|---|---|
| early | yellow (15/s) | AM1/AM2 | basic | small | stone furnace |
| mid | red (30/s) | AM2 | fast | medium | steel furnace |
| late | blue/turbo (45/60/s) | AM3 + modules | bulk (stack) | medium | steel → (separate) electric/foundry |

## 1. Only swap things with the same footprint

| Family | Order | Watch out |
|---|---|---|
| belt / underground / splitter | yellow → red → blue → turbo | design **underground spans ≤ 4** (yellow limit) so they still connect after the upgrade |
| assemblers | 1 → 2 → 3 (all 3×3) | AM1 has no fluid input and no modules → fluid-recipe slots start at AM2 |
| inserters | basic → fast → bulk (→ stack in Space Age) | **long-handed has no upgrade**: keep it off throughput-critical spots or reserve room for two |
| poles | small → medium (1×1) | place poles for **small-pole** coverage (5×5 supply, 7.5 reach); substations (2×2) need another layout |
| furnaces | stone → steel (2×2) | electric furnaces (3×3) do not fit the same slot → keep steel-furnace columns; add electric/foundry blocks separately later |

## 2. Ratios survive the upgrade — if everything is upgraded together

When all machines of a block move up one tier together, the machine-count ratios (e.g. cable 3 : circuit 2)
stay correct and output scales uniformly (AM1→AM2 ×1.5, AM2→AM3 ×1.67). Upgrading part of a block just moves
the bottleneck.

## 3. Size belts and inserters for the final tier

- Lay input belts with enough lanes for the late-game rate from the start (half-empty early is fine).
- One inserter (chest-to-chest, no research bonus): basic 0.83/s, fast 2.31/s, bulk 2.31/s × hand size.
  If a machine's late-game I/O exceeds one inserter, reserve a second inserter slot.

## 4. Modules and beacons

Adding beacons (3×3) later changes the layout. Either (a) finish with modules only, or (b) leave beacon
rows empty from the start. Upgradeable blueprints here default to (a).

## 5. Water anywhere (Waterfill)

With the Waterfill mod, water is made next to the factory (water tiles + offshore pump). Blueprints mark
the water inlet with a `water` constant combinator instead of running long water pipes.

## Checklist

- [ ] underground spans ≤ 4
- [ ] no long-handed inserter on a throughput bottleneck
- [ ] pole spacing fits small poles
- [ ] fluid-recipe slots use AM2+
- [ ] furnaces are the 2×2 family (stone/steel)
- [ ] input/output belt lane count sized for the late tier
