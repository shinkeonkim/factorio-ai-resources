"""Vulcanus all-in-one complex: lava -> molten metals -> castings, tungsten, metallurgic science, mall items,
water/steam, power, rocket and imports. Every production line is a stack of lib/fstack fluid cells standing on
one planet bus (lib/complex.compose)."""
import dataclasses
import math

from lib.fstack import FluidCell, as_stack, analyse

C = {
    # raw processing
    "molten-iron": FluidCell("Molten iron", "molten-iron-from-lava", "foundry", n=1, inner=(None, "calcite")),
    "molten-copper": FluidCell("Molten copper", "molten-copper-from-lava", "foundry", n=1, inner=(None, "calcite")),
    "steam": FluidCell("Steam (acid neutralisation)", "acid-neutralisation", "chemical-plant", n=1, inner=(None, "calcite")),
    "water": FluidCell("Water (steam condensation)", "steam-condensation", "chemical-plant", n=2),
    # castings
    "iron-plate": FluidCell("Iron plates", "casting-iron", "foundry", n=1),
    "copper-plate": FluidCell("Copper plates", "casting-copper", "foundry", n=1),
    "steel-plate": FluidCell("Steel", "casting-steel", "foundry", n=1),
    "iron-gear-wheel": FluidCell("Gears", "casting-iron-gear-wheel", "foundry", n=1),
    "iron-stick": FluidCell("Iron sticks", "casting-iron-stick", "foundry", n=1),
    # tungsten + science
    "carbon": FluidCell("Carbon", "carbon", "chemical-plant", n=3, inner=(None, "coal")),
    "tungsten-carbide": FluidCell("Tungsten carbide", "tungsten-carbide", "assembling-machine-3", n=2,
                                  inner=("carbon", "tungsten-ore")),
    "tungsten-plate": FluidCell("Tungsten plate", "tungsten-plate", "foundry", n=2, inner=(None, "tungsten-ore")),
    "science": FluidCell("Metallurgic science", "metallurgic-science-pack", "foundry", n=1,
                         inner=("tungsten-plate", "tungsten-carbide")),
    # oil -> lubricant, rocket LDS
    "heavy-oil": FluidCell("Heavy oil (simple coal liquefaction)", "simple-coal-liquefaction", "oil-refinery", n=1,
                           inner=("calcite", "coal")),
    "lubricant": FluidCell("Lubricant", "lubricant", "chemical-plant", n=1),
    "low-density-structure": FluidCell("Low density structure", "casting-low-density-structure", "foundry", n=1,
                                       inner=(None, "plastic-bar")),
    # mall (products into passive provider chests)
    "mall-foundry": FluidCell("Mall: foundry", "foundry", "foundry", n=1, sink="chest",
                              inner=("tungsten-carbide", "steel-plate"), outer=("electronic-circuit", "refined-concrete")),
    "mall-big-drill": FluidCell("Mall: big mining drill", "big-mining-drill", "foundry", n=1, sink="chest",
                                inner=("tungsten-carbide", "electric-mining-drill"),
                                outer=("electric-engine-unit", "advanced-circuit")),
    "mall-turbo-belt": FluidCell("Mall: turbo belt", "turbo-transport-belt", "foundry", n=1, sink="chest",
                                 inner=("tungsten-plate", "express-transport-belt")),
    "mall-turbo-underground": FluidCell("Mall: turbo underground", "turbo-underground-belt", "foundry", n=1, sink="chest",
                                        inner=("tungsten-plate", "express-underground-belt")),
    "mall-turbo-splitter": FluidCell("Mall: turbo splitter", "turbo-splitter", "foundry", n=1, sink="chest",
                                     inner=("tungsten-plate", "express-splitter"), outer=("processing-unit", None)),
}

BUS_TIER = "blue"
IMPORTS = ["electronic-circuit", "advanced-circuit", "processing-unit", "electric-engine-unit", "electric-mining-drill",
           "refined-concrete", "express-transport-belt", "express-underground-belt", "express-splitter", "plastic-bar",
           "rocket-fuel"]

PLAN = [   # (cell key, stacked cells) west -> east: producers before consumers
    ("molten-iron", 3), ("molten-copper", 3), ("molten-copper", 3),
    ("heavy-oil", 1), ("lubricant", 1),
    ("carbon", 3), ("tungsten-carbide", 3), ("tungsten-plate", 5),
    ("iron-plate", 2), ("steel-plate", 2),
    ("science", 5), ("low-density-structure", 1),
    ("mall-foundry", 1), ("mall-big-drill", 1), ("mall-turbo-belt", 1), ("mall-turbo-underground", 1),
    ("mall-turbo-splitter", 1),
]


def balance(plan=PLAN, tier="late"):
    """items/s supplied vs demanded by the plan (both halves, all cells)."""
    sup, dem = {}, {}
    for key, n in plan:
        a = analyse(C[key], tier)
        for k, v in a["out_per_s"].items():
            sup[k] = sup.get(k, 0) + v * n
        for k, v in a["in_per_side"].items():
            dem[k] = dem.get(k, 0) + 2 * v * n
    return {k: (round(sup.get(k, 0), 2), round(dem.get(k, 0), 2)) for k in sorted(set(sup) | set(dem))}


# ------------------------------------------------------------------------------------------- special stacks
from lib.complex import Stack
from lib.fbp import N, E, S, W
from lib.fstack import stack as fstack, late_rates, TIERS as FT
from lib.planets.common import void_sink


def power_stack(turbine_cols=8, turbines_per_col=8, tier="mid", bots=False):
    """Acid neutralisation (2 chemical plants, 4,000 steam/s at 500 C) under a field of steam turbines.
    Steam rises up the centre pipe into a header; each column is a chain of turbines (their ports pass steam
    through vertically). 64 turbines x 5.82 MW = 372 MW. Inputs: calcite (belt, or a requester chest when
    bots=True) and sulfuric acid (main)."""
    cell = dataclasses.replace(C["steam"], bots=True, inner=(None, None), outer=None) if bots else C["steam"]

    def build(bp, t):
        fstack(bp, cell, t, 1, late_rates(cell))
        c = cell.c
        top = -cell.period - 1                     # first row above the cell
        bp.add("pipe", c, top)                     # riser; the row above it is the header
        hy = top - 1
        half = turbine_cols // 2
        xs = [c + 4 * (j - half) + 2 for j in range(turbine_cols)]
        for x in range(min(xs), max(xs) + 1):
            bp.add("pipe", x, hy)
        for x in xs:
            for k in range(turbines_per_col):
                bp.add("steam-turbine", x - 1, hy - 5 * (k + 1))
        for x in xs + [min(xs) - 4]:
            for k in range(0, turbines_per_col * 5 + 1, 6):
                bp.add(FT[t]["pole"], x + 2, hy - 1 - k)
        bp.add(FT[t]["pole"], c - 2, top)          # joins the field to the cell's poles

    return Stack("Power: acid neutralisation + 64 turbines", build, tier, [],
                 {k: v for k, v in {**{"calcite": late_rates(cell).get("calcite", 0) / 60},
                                    **{"sulfuric-acid": late_rates(cell).get("sulfuric-acid", 0) / 60}}.items()})


def stone_sink(recyclers_per_side=7, tier="mid", name="Stone sink (recyclers)"):
    """Voids stone with recyclers (stone recycles into itself 25 % of the time); see common.void_sink."""
    return void_sink("stone", recyclers_per_side, tier, name)


POWER_KW = {"foundry": 2500, "assembling-machine-3": 375, "chemical-plant": 210, "oil-refinery": 420, "recycler": 180,
            "rocket-silo": 250, "roboport": 50, "fast-inserter": 46, "bulk-inserter": 79, "stack-inserter": 133,
            "long-handed-inserter": 20, "cargo-landing-pad": 0}


def power_budget(bp):
    """peak electric draw of the complex (kW) and the turbines' output (kW)."""
    use = sum(POWER_KW.get(e["name"], 0) for e in bp.entities)
    gen = sum(5820 for e in bp.entities if e["name"] == "steam-turbine")
    return use, gen


SPECIAL = [("Raw intake (south gate)", "방해석·석탄·텅스텐 광석 벨트 → 공급 상자", "calcite, coal, tungsten ore belts → provider chests"),
           ("Power", "산 중화 화학 공장 2대 + 증기 터빈 64대 (372 MW)", "2 acid-neutralisation plants + 64 steam turbines (372 MW)"),
           ("Stone voids ×3", "용암 선반의 돌 벨트 끝, 재활용기 14대씩", "on the lava shelf's stone belts, 14 recyclers each"),
           ("Landing pad", "수입품 11종 → 로봇 네트워크", "11 imports → the robot network"),
           ("Rocket silo", "로봇이 재료를 넣는 사일로; 수출은 화물 요청으로", "robot-fed silo; exports via its cargo requests")]


def power_line(bp, lang):
    use, gen = power_budget(bp)
    return (f"최대 전력 {use / 1000:,.0f} MW / 발전 {gen / 1000:,.0f} MW." if lang == "ko"
            else f"Peak power {use / 1000:,.0f} MW / generated {gen / 1000:,.0f} MW.")


# ------------------------------------------------------------------------------------- the base (lib/base)
HEIGHT = (24, 30, 36, 44, 52)
LINES = PLAN


def stone_voids(rate, n, tier="mid"):
    """one recycler void per stone belt (`rate` stone/s each)"""
    per_side = max(2, math.ceil(rate / 16) + 1)                 # a recycler with its two inserters takes ~8 stone/s
    return [void_sink("stone", per_side, tier, f"Stone void ({rate:.0f}/s)", rate) for _ in range(n)]


def solar_bootstrap(tier="mid"):
    """Restart kit: 8 solar panels (4x output on Vulcanus) and 4 accumulators power the acid-neutralisation
    plants when the turbines are cold; the first accumulator also drives the low-power alarm."""
    def build(bp, t):
        for i in range(4):
            for j in range(2):
                bp.add("solar-panel", 3 * i, -3 * (j + 1) - 1)
        for i in range(4):
            bp.add("accumulator", 2 * i + 1, -10)
        bp.add(FT[t]["pole"], 0, -11); bp.add(FT[t]["pole"], 6, -1)
    return Stack("Solar restart kit", build, tier, [], {}, gap=1)


def intake_stack(tier="mid"):
    """south gate: calcite / coal / tungsten ore belts unloaded into provider chests (rates from the lines)"""
    from lib.planets.common import ingress_stack, raw_demand
    cell = C["steam"]
    raw = raw_demand(__import__(__name__, fromlist=["x"]), set(RAW), {"calcite": late_rates(cell).get("calcite", 0) / 60})
    return ingress_stack(raw, tier)


RAW = ("calcite", "coal", "tungsten-ore")


def bot(key, belt_out=False):
    """robot-fed version of a cell: a requester chest at every input inserter and a provider chest for the output,
    no belt columns (base-design.md §4: robots for the many low-volume items). belt_out keeps the item product on
    the centre belt (molten metals: their stone rides a belt into the voids)."""
    return dataclasses.replace(C[key], bots=True, inner=(None, None), outer=None, belt_out=belt_out)


def islands():
    """Each island makes the fluids it uses next to their consumers (base-design.md §3). Robots feed every
    machine; molten metals send their stone along a belt into voids in the same island."""
    from lib.base import Island
    from lib.planets.common import robot_pad, robot_silo
    stone = ("stone", stone_voids)
    mall = ["mall-foundry", "mall-big-drill", "mall-turbo-belt", "mall-turbo-underground", "mall-turbo-splitter"]
    return [
        Island("Iron castings", [(bot("molten-iron", True), 2), (bot("iron-plate"), 2), (bot("steel-plate"), 2),
                                 (bot("tungsten-plate"), 5)], waste=stone),
        Island("Metallurgic science", [(bot("molten-copper", True), 6), (bot("molten-iron", True), 1),
                                       (bot("carbon"), 3), (bot("tungsten-carbide"), 3), (bot("science"), 5),
                                       (bot("low-density-structure"), 1)], waste=stone),
        Island("Mall", [(bot("molten-iron", True), 1), (bot("heavy-oil"), 1), (C["lubricant"], 1)] + [(bot(k), 1) for k in mall],
               waste=stone),
        Island("Power", [], extra=[lambda t: power_stack(16, 4, tier=t, bots=True), solar_bootstrap]),
        Island("Rocket", [], extra=[robot_silo, lambda t: robot_pad(IMPORTS, t)]),
    ]


def controls(bp):
    from lib.base import power_alarm
    acc = next(e["entity_number"] for e in bp.entities if e["name"] == "accumulator")
    return power_alarm(bp, acc, "Vulcanus base: power low (check calcite / sulfuric acid)")


def base(label="Vulcanus all-in-one", tier="mid"):
    """Dense rectangle: island shelves (iron castings, metallurgic science, mall, power, rocket) with their own
    molten metals and stone voids; ores through the south gate, lava / sulfuric acid from the west per shelf.
    No frame: demolishers never attack — keep the base outside their territories."""
    from lib.base import build_base
    return build_base(label, islands(), HEIGHT, frame=None, tier="blue", gates=[intake_stack(tier)], controls=controls)
