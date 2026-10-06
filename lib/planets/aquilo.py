"""Aquilo all-in-one complex: ammonia ocean -> ammonia + ice, lithium, fluoroketone, cryogenic science, rocket fuel,
ice platforms, fusion power cells — robot-fed cells (chests do not freeze), fluids in heated pipes, and
heat pipes beside every building that freezes (lib/heat.py fills and checks them)."""
from lib.complex import Stack
from lib.fbp import N, E, S, W
from lib.fstack import FluidCell, TIERS as FT
from lib import hstack, heat as _heat

BUS_TIER = "blue"


def _cryo(name, recipe, n, **kw):
    return FluidCell(name, recipe, "cryogenic-plant", n=n, bots=True, **kw)


def _chem(name, recipe, n, **kw):
    return FluidCell(name, recipe, "chemical-plant", n=n, bots=True, **kw)


C = {
    "ammonia": _chem("Ammonia + ice (separation)", "ammoniacal-solution-separation", 2),
    "water": _chem("Water (ice melting)", "ice-melting", 2),
    "lithium": _cryo("Lithium", "lithium", 1),
    "lithium-plate": FluidCell("Lithium plate", "lithium-plate", "electric-furnace", n=2, bots=True),
    "solid-fuel": _chem("Solid fuel (ammonia + crude oil)", "solid-fuel-from-ammonia", 2),
    "fluoroketone": _cryo("Fluoroketone (hot)", "fluoroketone", 1),
    "cooling": _cryo("Fluoroketone cooling", "fluoroketone-cooling", 1),
    "science": _cryo("Cryogenic science", "cryogenic-science-pack", 2),
    "rocket-fuel": _chem("Rocket fuel (ammonia)", "ammonia-rocket-fuel", 2),
    "ice-platform": FluidCell("Ice platform", "ice-platform", "assembling-machine-3", n=2, bots=True),
    "fusion-cell": _cryo("Fusion power cell", "fusion-power-cell", 1),
}


FUEL = "rocket-fuel"
# sized from the power block up: ~55 MW of turbines need ~560 water/s = 28 ice/s melted (8 water cells); the heating
# towers burn ~30 rocket fuel/min (2 rocket-fuel cells, 480 solid fuel/min); 6 separation cells give ~58 ice/s and
# ~576 ammonia/s, a little under what the lines draw, so ammonia never backs up and stalls the ice
LINES = [("ammonia", 6), ("water", 8), ("lithium", 3), ("lithium-plate", 2), ("solid-fuel", 2), ("fluoroketone", 1),
         ("cooling", 2), ("science", 4), ("rocket-fuel", 2), ("ice-platform", 1), ("fusion-cell", 1)]
def power_stack(units=2, tier="mid"):
    """Heating towers burning ammonia rocket fuel -> heat exchangers -> turbines; the same heat-pipe network keeps
    the whole complex warm (lib/heat fills and checks it). Water from the bus."""
    from lib.planets.gleba import power_stack as _ps
    st = _ps(units, tier)
    inner = st.build

    def build(bp, t):
        inner(bp, t)
        for e in bp.entities:                                   # burn rocket fuel instead of spoilage / jellynut
            if e["name"] == "requester-chest":
                e["request_filters"] = {"sections": [{"index": 1, "filters": [
                    {"index": 1, "name": FUEL, "quality": "normal", "comparator": "=", "count": 20}]}]}
    st.build = build
    st.name = f"Power + heat: {units} heating towers"
    st.demand = {"water": 700.0}       # steam for the ~70 MW the complex draws; the rest of the heat keeps it warm
    return st


def rocket_stack(tier="mid"):
    from lib.planets.gleba import rocket_stack as _rs
    st = _rs(tier); st.name = "Rocket silo (robot-fed)"
    return st


def pad_stack(tier="mid"):
    from lib.planets.gleba import pad_stack as _pad
    return _pad(("holmium-plate", "processing-unit", "low-density-structure"), tier)


CELL_STACK = hstack.as_stack
CELL_GEO = hstack.Geo

POWER_KW = {"cryogenic-plant": 1500, "chemical-plant": 210, "electric-furnace": 180, "assembling-machine-3": 375,
            "rocket-silo": 250, "roboport": 50, "fast-inserter": 46}


def power_budget(bp):
    use = sum(POWER_KW.get(e["name"], 0) for e in bp.entities)
    gen = sum(5820 for e in bp.entities if e["name"] == "steam-turbine")
    return use, gen


def power_line(bp, lang):
    use, gen = power_budget(bp)
    load = _heat.load_kw(bp) / 1000
    return (f"최대 전력 {use / 1000:,.0f} MW / 터빈 {gen / 1000:,.0f} MW, 보온 열 {load:,.1f} MW." if lang == "ko"
            else f"Peak power {use / 1000:,.0f} MW / turbines {gen / 1000:,.0f} MW, heating load {load:,.1f} MW.")


SPECIAL = [("Power + heat", "가열탑 3기(암모니아 로켓 연료, 열 300 MW) → 열교환기 12 → 터빈 24; 같은 열 배관이 단지 전체를 데움",
            "3 heating towers (ammonia rocket fuel, 300 MW of heat) → 12 exchangers → 24 turbines; the same heat pipes warm the whole base"),
           ("Rocket silo", "로봇이 재료를 넣는 사일로", "robot-fed silo"),
           ("Landing pad", "홀뮴 판·파랑 회로·LDS 수입", "imports holmium plates, blue circuits, LDS")]


# ------------------------------------------------------------------------------------- the base (lib/base)
HEIGHT = 40


def islands():
    """One heated island (split into parts that each make their own ammonia, water and fluoroketone) with the
    power block, and the rocket / landing pad (no fluids, so they fill gaps)."""
    from lib.base import Island
    return [
        Island("Aquilo", [(C[k], n) for k, n in LINES], extra=[lambda t: power_stack(3, t)],
               make=lambda c, n, t: hstack.as_stack(c, n, t)),
        Island("Rocket", [], extra=[rocket_stack, pad_stack]),
    ]


def controls(bp):
    from lib.base import power_alarm
    acc = next(e["entity_number"] for e in bp.entities if e["name"] == "accumulator")
    return power_alarm(bp, acc, "Aquilo base: power low (heating towers need rocket fuel)")


def warm(bp):
    _heat.fill(bp)
    _heat.prune(bp)
    problems = _heat.check(bp)
    if problems:
        raise SystemExit("Aquilo heating: " + "; ".join(problems))
    return round(_heat.load_kw(bp) / 1000, 1)


def base(label="Aquilo all-in-one", tier="mid"):
    """Dense heated rectangle: robot-fed heated cells, plain-pipe streets (every pipe-to-ground costs 150 kW of
    heat), raw fluids (ammoniacal solution, lithium brine, fluorine, crude oil) from the west of each shelf, three
    heating towers that restart by themselves; at the end lib/heat fills heat pipe beside everything that freezes
    and checks it."""
    from lib.base import build_base
    return build_base(label, islands(), HEIGHT, frame=None, tier="blue", finish=warm, controls=controls, plain=True)
