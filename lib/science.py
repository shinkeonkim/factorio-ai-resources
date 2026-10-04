"""Upgradeable science tiles (red, green) for the 6+2 main bus.

One layout, three tiers (same footprint, upgrade planner only):

    tier   belts   assemblers   inserters   poles    output per tile
    early  yellow  AM1          basic       small     60/min
    mid    red     AM2          fast        medium    90/min
    late   blue    AM3          bulk        medium   150/min

Geometry of a tile (x grows east, y grows south):
    y=0      science belt -> flows east, leaves at the east end (towards the labs)
    y=1      output inserters
    y=2..4   science assemblers (pitch 3)
    y=5      input inserters
    y=6      feed belt (two lanes, see each tile)
    y>=7     intermediate cluster at the west end + input belts
Inputs arrive from the south (bus taps) on branch columns that end at the bottom edge, each with a
constant-combinator marker; counts are the late-tier (AM3) demand per minute.
Every underground spans ≤ 1 tile, no long-handed inserters.
"""
from lib.fbp import N, E, S, W

TIERS = {
    "early": {"belt": "transport-belt", "ug": "underground-belt", "am": "assembling-machine-1",
              "ins": "inserter", "pole": "small-electric-pole", "rate": 60},
    "mid": {"belt": "fast-transport-belt", "ug": "fast-underground-belt", "am": "assembling-machine-2",
            "ins": "fast-inserter", "pole": "medium-electric-pole", "rate": 90},
    "late": {"belt": "express-transport-belt", "ug": "express-underground-belt", "am": "assembling-machine-3",
             "ins": "bulk-inserter", "pole": "medium-electric-pole", "rate": 150},
}
BOTTOM = 15          # branch columns start at this row (connect the bus taps here)


def _column_up(bp, t, x, y_from, y_to):
    """belt going north from y_from (south) to y_to (inclusive)"""
    for y in range(y_from, y_to - 1, -1):
        bp.add(t["belt"], x, y, N)


def _science_row(bp, t, n, recipe):
    """n science assemblers on y=2..4 with output to y=0 and input from the y=6 feed belt."""
    for k in range(n):
        x = 3 * k
        bp.add(t["am"], x, 2, recipe=recipe)
        bp.add(t["ins"], x + 1, 1, S)       # picks from the machine (south), drops on the science belt
        bp.add(t["ins"], x + 1, 5, S)       # picks from the feed belt (south), drops into the machine
        if k % 2 == 0:                      # poles in the free tiles of both inserter rows (small-pole spacing)
            bp.add(t["pole"], x + 2, 1)
            bp.add(t["pole"], x + 2, 5)
    bp.belt_line(t["belt"], 0, 0, E, 3 * n + 1)      # science belt, one tile past the last machine


def red_tile(bp, tier="early"):
    """Red science: 10 x automation-science-pack + 1 gear assembler.
    Feed belt y=6: north lane = gears (inserted from the south), south lane = copper (side-loaded)."""
    t = TIERS[tier]
    n = 10
    _science_row(bp, t, n, "automation-science-pack")
    bp.belt_line(t["belt"], -8, 6, E, 8 + 3 * n)     # feed belt x=-8 .. 3n-1
    # gear assembler under the feed belt start
    bp.add(t["am"], -7, 8, recipe="iron-gear-wheel")
    bp.add(t["ins"], -6, 7, S); bp.add(t["ins"], -5, 7, S)       # gears -> feed belt (north lane)
    bp.add(t["ins"], -7, 11, S); bp.add(t["ins"], -6, 11, S)     # iron -> gear assembler
    # iron: branch column x=-9 from the bottom, turns east under the gear assembler
    _column_up(bp, t, -9, BOTTOM, 13)
    bp.add(t["belt"], -9, 12, E); bp.belt_line(t["belt"], -8, 12, E, 3)
    # copper: branch column x=-2, side-loads the feed belt from the south (south lane)
    _column_up(bp, t, -2, BOTTOM, 7)
    bp.add(t["pole"], -4, 9); bp.add(t["pole"], -4, 12); bp.add(t["pole"], -1, 3); bp.add(t["pole"], -8, 11)
    bp.add_marker(-10, BOTTOM, {"iron-plate": 300})
    bp.add_marker(-1, BOTTOM, {"copper-plate": 150})


def green_tile(bp, tier="early"):
    """Green science: 12 x logistic-science-pack, 1 inserter AM, 1 belt AM, 2 gear AMs.
    Feed belt y=6: north lane = inserters (from the south cluster), south lane = belts (north cluster).
    North cluster (y=2..4, x<0): gear B -> belt assembler, iron from the y=0 stub belt.
    South cluster (y=8..10, x<0): gear A -> inserter assembler, iron + circuits from the y=12 belt."""
    t = TIERS[tier]
    n = 12
    _science_row(bp, t, n, "logistic-science-pack")
    bp.belt_line(t["belt"], -6, 6, E, 6 + 3 * n)     # feed belt x=-6 .. 3n-1
    # north cluster
    bp.add(t["am"], -10, 2, recipe="iron-gear-wheel")
    bp.add(t["am"], -6, 2, recipe="transport-belt")
    bp.add(t["ins"], -7, 3, W)                       # gear B (west) -> belt assembler
    bp.add(t["ins"], -9, 1, N); bp.add(t["ins"], -5, 1, N)          # iron from y=0 stub
    bp.add(t["ins"], -5, 5, N)                       # belts -> feed belt (south lane)
    # south cluster
    bp.add(t["am"], -10, 8, recipe="iron-gear-wheel")
    bp.add(t["am"], -6, 8, recipe="inserter")
    bp.add(t["ins"], -7, 9, W)                       # gear A (west) -> inserter assembler
    bp.add(t["ins"], -5, 7, S)                       # inserters -> feed belt (north lane)
    bp.add(t["ins"], -9, 11, S)                      # iron -> gear A
    bp.add(t["ins"], -6, 11, S); bp.add(t["ins"], -4, 11, S)        # iron + circuits -> inserter AM
    # y=12 belt (iron south lane, circuits north lane), dead start at x=-14
    bp.add(t["belt"], -14, 12, E); bp.belt_line(t["belt"], -13, 12, E, 10)
    _column_up(bp, t, -13, BOTTOM, 13)                                  # iron A side-loads from the south
    _column_up(bp, t, -15, BOTTOM, 12)                                  # circuits: up, east, then south
    bp.add(t["belt"], -15, 11, E); bp.add(t["belt"], -14, 11, E); bp.add(t["belt"], -13, 11, S)
    # iron B: column x=-12 crosses the y=12 belt underground, then runs north to the y=0 stub
    _column_up(bp, t, -12, BOTTOM, 14)
    bp.add(t["ug"], -12, 13, N, type="input"); bp.add(t["ug"], -12, 11, N, type="output")
    _column_up(bp, t, -12, 10, 1)
    bp.add(t["belt"], -12, 0, E); bp.belt_line(t["belt"], -11, 0, E, 7)   # stub x=-11..-5
    for x, y in ((-10, 1), (-11, 5), (-7, 5), (-7, 7), (-3, 9), (-11, 9), (-3, 3), (-2, 12), (-8, 11)):
        bp.add(t["pole"], x, y)
    bp.add_marker(-14, BOTTOM, {"iron-plate": 450})
    bp.add_marker(-16, BOTTOM, {"electronic-circuit": 150})
    bp.add_marker(-11, BOTTOM, {"iron-plate": 225})
