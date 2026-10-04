"""Vulcanus all-in-one complex: lava -> molten metals -> castings, tungsten, metallurgic science, mall items,
water/steam, power, rocket and imports. Every production line is a stack of lib/fstack fluid cells standing on
one planet bus (lib/complex.compose)."""
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

LAYOUT = [
    {"kind": "solid", "lanes": ["calcite", "coal", "tungsten-ore", "tungsten-ore", "carbon", "tungsten-carbide"]},
    {"kind": "solid", "lanes": ["tungsten-plate", "metallurgic-science-pack", "iron-plate", "steel-plate", "low-density-structure", None]},
    {"kind": "solid", "lanes": ["stone", "stone", "stone", None, None, None]},
    {"kind": "solid", "lanes": IMPORTS[:6]},
    {"kind": "solid", "lanes": IMPORTS[6:] + [None]},
    {"kind": "fluid", "lanes": ["lava", "lava", "sulfuric-acid", "molten-iron", "molten-copper", "molten-copper"]},
    {"kind": "fluid", "lanes": ["heavy-oil", "lubricant", None, None, None, None]},
]

PLAN = [   # (cell key, stacked cells) west -> east: producers before consumers
    ("molten-iron", 3), ("molten-copper", 3), ("molten-copper", 3),
    ("heavy-oil", 1), ("lubricant", 1),
    ("carbon", 3), ("tungsten-carbide", 3), ("tungsten-plate", 4),
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


def stacks(plan=PLAN, tier="mid"):
    """landing pad, power, every planned line, rocket silo, stone sink (west -> east)."""
    return ([landing_pad_stack(IMPORTS, tier), power_stack(tier=tier)]
            + [as_stack(C[k], n, tier) for k, n in plan]
            + [rocket_stack(tier=tier)] + [stone_sink(tier=tier, name=f"Stone sink {k + 1}") for k in range(3)])


# ------------------------------------------------------------------------------------------- special stacks
from lib.complex import Stack
from lib.fbp import N, E, S, W
from lib.fstack import stack as fstack, late_rates, TIERS as FT
from lib.planets.common import void_sink, landing_pad_stack as _pad, rocket_stack as _rocket


def power_stack(turbine_cols=8, turbines_per_col=8, tier="mid"):
    """Acid neutralisation (2 chemical plants, 4,000 steam/s at 500 C) under a field of steam turbines.
    Steam rises up the centre pipe into a header; each column is a chain of turbines (their ports pass steam
    through vertically). 64 turbines x 5.82 MW = 372 MW. Inputs: calcite (belt) and sulfuric acid (main)."""
    cell = C["steam"]

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


def landing_pad_stack(imports, tier="mid", count=200):
    return _pad(imports, tier, count)


def rocket_stack(exports=("metallurgic-science-pack", "tungsten-carbide", "tungsten-plate", "iron-plate"), tier="mid"):
    return _rocket(list(exports), tier=tier)


POWER_KW = {"foundry": 2500, "assembling-machine-3": 375, "chemical-plant": 210, "oil-refinery": 420, "recycler": 180,
            "rocket-silo": 250, "roboport": 50, "fast-inserter": 46, "bulk-inserter": 79, "stack-inserter": 133,
            "long-handed-inserter": 20, "cargo-landing-pad": 0}


def power_budget(bp):
    """peak electric draw of the complex (kW) and the turbines' output (kW)."""
    use = sum(POWER_KW.get(e["name"], 0) for e in bp.entities)
    gen = sum(5820 for e in bp.entities if e["name"] == "steam-turbine")
    return use, gen


SPECIAL = [("Power", "산 중화 화학 공장 2대 + 증기 터빈 64대 (372 MW)", "2 acid-neutralisation plants + 64 steam turbines (372 MW)"),
           ("Landing pad", "수입품 11종 → 버스 줄", "11 imports → bus lanes"),
           ("Rocket silo", "로켓 부품(수입 파랑 회로·주조 LDS·수입 로켓 연료) + 수출 상자", "rocket parts (imported blue circuits, cast LDS, imported rocket fuel) + export chests"),
           ("Stone sinks ×3", "재활용기 14대씩, 돌 줄마다 하나", "14 recyclers each, one per stone lane")]


def power_line(bp, lang):
    use, gen = power_budget(bp)
    return (f"최대 전력 {use / 1000:,.0f} MW / 발전 {gen / 1000:,.0f} MW." if lang == "ko"
            else f"Peak power {use / 1000:,.0f} MW / generated {gen / 1000:,.0f} MW.")
