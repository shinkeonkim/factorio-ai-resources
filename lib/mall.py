"""Upgradeable mall streets (redesign of the user's 'Daiso' malls for the 6+2 bus).

A street is two rows of assembler cells facing two shared belts (4 lanes):

    y=-2   chests (north row)              x = 4*k, pitch 4: assembler 3 wide + 1 gap column
    y=-1   output inserters                gap column: poles above/below, a sideways inserter in the
    y=0..2 north row                       middle row when a cell hands its product to a neighbour
    y=3    inserters: near (x+1), long-handed far (x+2), feeder output (x)
    y=4    belt  [lane N | lane S]
    y=5    belt  [lane N | lane S]
    y=6    inserters (south row)
    y=7..9 south row
    y=10   output inserters
    y=11   chests

The north row's near belt is y=4 and its far belt y=5; the south row the other way round. Long-handed
inserters are fine here: a mall cell needs a few items per second at most.

A *feeder* cell makes an intermediate that is not on the bus (gears, pipes) and drops it onto the
lane the street reserves for it, instead of into a chest. A north-row feeder fills y=4 south lane,
a south-row feeder y=5 north lane; feeders sit at the west end so the product flows past every cell.

Bus lanes come up from the bottom edge with lib/rowkit (y=4 north item, y=5 both items).
Upgrade in place: belts/inserters/assemblers/poles follow lib.science.TIERS; chests go iron -> passive
provider (same footprint). Every chest is limited to 2 slots (`bar`) so the mall does not hoard.
"""
import json
import pathlib

from lib.fbp import N, E, S, W
from lib.rowkit import Kit
from lib.science import TIERS, LH

RECIPES = json.loads((pathlib.Path(__file__).resolve().parents[1] / "skills" / "factorio-blueprint" / "data"
                      / "recipes-base.json").read_text())["recipes"]
CHEST = {"early": "iron-chest", "mid": "iron-chest", "late": "passive-provider-chest"}
PITCH = 4
LANE_CAP = 450                                            # per-minute marker cap: one yellow-belt lane
SPEED = {"assembling-machine-1": 0.5, "assembling-machine-2": 0.75, "assembling-machine-3": 1.25}

# Streets: lanes (y, side) -> item, and the cells of each row from west to east.
# A cell is a recipe name; "<" / ">" after it means: hand the product to the west / east neighbour too.
STREETS = {
    "logistics": {
        "title": "logistics & mining",
        "lanes": {(4, "N"): "iron-plate", (4, "S"): "iron-gear-wheel", (5, "N"): "electronic-circuit",
                  (5, "S"): "steel-plate"},
        "feeders": {"iron-gear-wheel": "north"},
        "north": ["iron-gear-wheel*", "iron-gear-wheel*", "underground-belt", "transport-belt<>", "splitter",
                  "long-handed-inserter", "inserter<>", "fast-inserter", "pipe-to-ground", "pipe<"],
        "south": ["repair-pack", "steel-chest", "assembling-machine-2", "assembling-machine-1<",
                  "electric-mining-drill", "radar", "rail-signal", "rail-chain-signal", "iron-chest",
                  "firearm-magazine"],
    },
    "power-fluids-trains": {
        "title": "power, fluids & trains",
        "lanes": {(4, "N"): "iron-plate", (4, "S"): "iron-gear-wheel", (5, "N"): "pipe",
                  (5, "S"): "steel-plate"},
        "feeders": {"iron-gear-wheel": "north", "pipe": "south"},
        "north": ["iron-gear-wheel*", "steam-engine", "offshore-pump", "pipe-to-ground", "fluid-wagon",
                  "storage-tank<", "cargo-wagon", "burner-inserter", "transport-belt", "flamethrower"],
        "south": ["pipe*", "pipe*", "pump", "engine-unit<>", "car", "engine-unit>", "pump", "steel-chest",
                  "iron-chest", "light-armor"],
    },
}


def _parse(cell):
    feeder = cell.endswith("*")
    name = cell.rstrip("*<>")
    return name, feeder, "<" in cell, ">" in cell


def check(street):
    """Every ingredient must be on a lane or handed over by a neighbour. Returns a list of problems."""
    st = STREETS[street]
    lane_items = set(st["lanes"].values())
    bad = []
    for row in ("north", "south"):
        cells = [_parse(c) for c in st[row]]
        for i, (name, feeder, west, east) in enumerate(cells):
            got = set(lane_items)
            if i > 0 and cells[i - 1][3]:
                got.add(cells[i - 1][0])
            if i + 1 < len(cells) and cells[i + 1][2]:
                got.add(cells[i + 1][0])
            need = {x["name"] for x in RECIPES[name]["ingredients"]}
            if need - got:
                bad.append(f"{row}[{i}] {name}: missing {sorted(need - got)}")
    return bad


def street(bp, name, tier="early"):
    t = TIERS[tier]
    st = STREETS[name]
    problems = check(name)
    if problems:
        raise ValueError("; ".join(problems))
    lanes = st["lanes"]
    where = {}                                            # item -> (belt y, lane side)
    for (y, side), item in lanes.items():
        where[item] = (y, side)
    chest = CHEST[tier]
    # toward = direction that picks from the street side (input row) / from the assembler (output row)
    rows = {"north": dict(am=0, ins=3, out=-1, chest=-2, mid=1, near=4, far=5, toward=S, away=N),
            "south": dict(am=7, ins=6, out=10, chest=11, mid=8, near=5, far=4, toward=N, away=S)}
    demand = {}                                           # bus item -> items/s at full speed
    n = max(len(st["north"]), len(st["south"]))
    for row, r in rows.items():
        cells = [_parse(c) for c in st[row]]
        for i, (recipe, feeder, west, east) in enumerate(cells):
            x = PITCH * i
            bp.add(t["am"], x, r["am"], recipe=recipe)
            rec = RECIPES[recipe]
            need = {k["name"]: k["amount"] for k in rec["ingredients"]}
            crafts = SPEED[t["am"]] / rec["energy_required"]
            # belts this cell must reach
            belts = set()
            for item, amt in need.items():
                if item in where:
                    belts.add(where[item][0])
                    if item not in st["feeders"]:
                        demand[item] = demand.get(item, 0) + crafts * amt
            # inserters: near belt at x+1 (picks from the belt side), far belt long-handed at x+2
            if r["near"] in belts:
                bp.add(t["ins"], x + 1, r["ins"], r["toward"])
            if r["far"] in belts:
                bp.add(LH, x + 2, r["ins"], r["toward"])
            if feeder:                                    # picks from the assembler, drops on the street
                bp.add(t["ins"], x, r["ins"], r["away"])
            else:
                bp.add(t["ins"], x + 1, r["out"], r["toward"])   # picks from the assembler
                bp.add(chest, x + 1, r["chest"], bar=2)
            if east:
                bp.add(t["ins"], x + 3, r["mid"], W)      # picks from this cell (west), drops east
            if west:
                bp.add(t["ins"], x - 1, r["mid"], E)      # picks from this cell (east), drops west
        for g in range(-1, PITCH * len(cells), PITCH):
            for y in (r["ins"], r["out"]):
                bp.add(t["pole"], g, y)
    # bus lanes: y=4 north item only (its south lane is the gear feeder), y=5 per street
    bottom = 14
    kit = Kit(bp, t["belt"], t["ug"], bottom)
    xe = PITCH * n - 2
    # a mall idles most of the time (chests are capped), so markers ask for at most one yellow lane
    rate = lambda item: min(LANE_CAP, max(1, round(demand.get(item, 0) * 60)))
    y4n, y5n, y5s = lanes[(4, "N")], lanes[(5, "N")], lanes[(5, "S")]
    kit.feed(4, -4, xe, north_item=(y4n, rate(y4n)))
    if y5n in st["feeders"]:
        kit.feed(5, -10, xe, south_item=(y5s, rate(y5s)))
    else:
        kit.feed(5, -10, xe, south_item=(y5s, rate(y5s)), north_item=(y5n, rate(y5n)))
    kit.render()
    return demand
