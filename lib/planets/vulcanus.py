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
    """Voids stone: a stone belt runs north between two columns of recyclers. Each recycler takes stone with
    two inserters and drops its 25 % self-recycling leftover out of its front (the tile above its left column)
    onto a short belt that side-loads back into the stone belt. Recycler speed 0.5, self-recycling 0.5/16 s,
    so one recycler handles up to 16 stone/s (the two inserters set the real rate). Needs the recycling
    research (Fulgora); until then stone collects in the chest at the top."""
    def build(bp, t):
        f = FT[t]
        c = 4
        for y in range(0, 8):                                    # cap: feed column from the bus
            bp.add(f["belt"], c, y, N)
        bp.add_marker(c, 8, {"stone": 0})
        bp.add(f["pole"], c - 1, 0)
        for k in range(recyclers_per_side):
            r = -5 * (k + 1)                                     # return belt row r, recyclers r+1 .. r+4
            for y in range(r, r + 5):
                bp.add(f["belt"], c, y, N)
            # west recycler (cols c-3, c-2), east recycler (cols c+2, c+3)
            bp.add("recycler", c - 3, r + 1, N)
            bp.add("recycler", c + 2, r + 1, N)
            for y in (r + 2, r + 3):
                bp.add(f["ins"], c - 1, y, E)                    # picks from the stone belt (east of it)
                bp.add(f["ins"], c + 1, y, W)
            for x in (c - 3, c - 2, c - 1):
                bp.add(f["belt"], x, r, E)                       # leftovers back into the stone belt
            for x in (c + 2, c + 1):
                bp.add(f["belt"], x, r, W)
            bp.add(f["pole"], c - 1, r + 4); bp.add(f["pole"], c + 1, r + 4)
        top = -5 * recyclers_per_side - 1
        bp.add(f["ins"], c, top, S)                              # overflow into a buffer chest
        bp.add("steel-chest", c, top - 1)
        bp.add(f["pole"], c + 1, top)

    return Stack(name, build, tier, [], {"stone": 30.0})


def _requests(items, count):
    return {"sections": [{"index": 1, "filters": [
        {"index": i + 1, "name": it, "quality": "normal", "comparator": "=", "count": count} for i, it in enumerate(items)]}]}


def landing_pad_stack(imports, tier="mid", count=200):
    """Imports: the cargo landing pad requests `imports` from orbit; logistic bots carry each item to its own
    requester chest, which an inserter empties onto a column running down to the bus, where that column
    starts the item's lane. Columns are 4 apart so the bus taps never collide."""
    def build(bp, t):
        f = FT[t]
        xs = [1 + 4 * k for k in range(len(imports))]
        for x, item in zip(xs, imports):
            bp.add("requester-chest", x, -3, request_filters=_requests([item], count))
            bp.add(f["ins"], x, -2, N)                         # picks from the chest above
            for y in range(-1, 8):
                bp.add(f["belt"], x, y, S)
        for x in xs[::2]:
            bp.add(f["pole"], x + 1, -2)
        mid = xs[len(xs) // 2]
        bp.add("cargo-landing-pad", mid - 4, -14, request_filters=_requests(imports, count * 2))
        bp.add("roboport", mid + 6, -10)
        bp.add(f["pole"], mid + 5, -5); bp.add(f["pole"], mid + 5, -11)

    xs = [1 + 4 * k for k in range(len(imports))]
    return Stack("Landing pad (imports)", build, tier, [(it, "item", x) for it, x in zip(imports, xs)],
                 {}, {it: 15.0 for it in imports}, gap=4)


def rocket_stack(exports=("metallurgic-science-pack", "tungsten-carbide", "tungsten-plate", "iron-plate"), tier="mid"):
    """Rocket silo fed from the bus: processing units, low density structures and rocket fuel go in through
    the bottom edge (one rocket part = one of each, 3 s). Exports from the bus go into passive provider
    chests beside it; the silo's cargo requests pull them in with logistic bots."""
    ings = ["processing-unit", "low-density-structure", "rocket-fuel"]

    def build(bp, t):
        f = FT[t]
        bp.add("rocket-silo", 0, -12)
        for k, item in enumerate(ings):
            x = 1 + 4 * k
            for y in range(-2, 8):
                bp.add(f["belt"], x, y, N)
            bp.add(f["ins"], x, -3, S)                        # belt end -> silo
            bp.add_marker(x, 8, {item: 20})
        for k, item in enumerate(exports):
            x = 13 + 4 * k
            for y in range(-2, 8):
                bp.add(f["belt"], x, y, N)
            bp.add(f["ins"], x, -3, S)
            bp.add("passive-provider-chest", x, -4)
            bp.add_marker(x, 8, {item: 60})
        for x in (3, 7, 11, 15, 19, 23):
            bp.add(f["pole"], x, -2)
        bp.add("roboport", 14, -12)
        bp.add(f["pole"], 11, -6)

    return Stack("Rocket silo + exports", build, tier, [], {i: 0.4 for i in ings} | {e: 1.0 for e in exports}, gap=4)


POWER_KW = {"foundry": 2500, "assembling-machine-3": 375, "chemical-plant": 210, "oil-refinery": 420, "recycler": 180,
            "rocket-silo": 250, "roboport": 50, "fast-inserter": 46, "bulk-inserter": 79, "stack-inserter": 133,
            "long-handed-inserter": 20, "cargo-landing-pad": 0}


def power_budget(bp):
    """peak electric draw of the complex (kW) and the turbines' output (kW)."""
    use = sum(POWER_KW.get(e["name"], 0) for e in bp.entities)
    gen = sum(5820 for e in bp.entities if e["name"] == "steam-turbine")
    return use, gen
