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


# ---------------------------------------------------------------------------------------------------
# Rows built with lib/rowkit.Kit (blue, yellow, military). Long-handed inserters appear only where the
# per-machine rate stays far below 1.2/s at the late tier, so they never limit an upgraded tile.
# ---------------------------------------------------------------------------------------------------
from lib.rowkit import Kit

LH = "long-handed-inserter"


def _row_top(bp, t, n, recipe, y=2, x0=0, far=True, north_long=False):
    """Machines on y..y+2; output up to y-2; fast in from y+4 (belt y+4), long in from y+5 (belt y+5)."""
    for k in range(n):
        x = x0 + 3 * k
        bp.add(t["am"], x, y, recipe=recipe)
        bp.add(t["ins"], x + 1, y - 1, S)                 # output -> belt y-2
        bp.add(t["ins"], x + 1, y + 3, S)                 # fast in <- belt y+4
        if far:
            bp.add(LH, x + 2, y + 3, S)                   # long in <- belt y+5
        if north_long:
            bp.add(LH, x, y - 1, N)                       # long in <- belt y-3
        if k % 2 == 0 or k == n - 1:
            bp.add(t["pole"], x + 2 if not north_long else x + 2, y - 1)
            bp.add(t["pole"], x, y + 3)


def _row_bottom(bp, t, n, recipe, y, x0=0, out=True):
    """Machines on y..y+2; fast in from belt y-2, long in from belt y-3; output down to belt y+4."""
    for k in range(n):
        x = x0 + 3 * k
        bp.add(t["am"], x, y, recipe=recipe)
        bp.add(t["ins"], x + 1, y - 1, N)                 # fast in <- belt y-2
        bp.add(LH, x + 2, y - 1, N)                       # long in <- belt y-3
        if out:
            bp.add(t["ins"], x + 1, y + 3, N)             # output -> belt y+4
        if k % 2 == 0 or k == n - 1:
            bp.add(t["pole"], x, y - 1)
            if out:
                bp.add(t["pole"], x, y + 3)


def blue_tile(bp, tier="early"):
    """Chemical science: 2 rows x 12 assemblers around two shared belts. All inputs come from the bus
    (engines, red circuits, sulfur). y=6 [engine N | red S] is the near belt of the top row and the far
    belt of the bottom row; y=7 [sulfur] the other way round. Both rows put science on one belt:
    the top row on y=0 (north lane), the bottom row on y=13 which returns to y=0 (south lane)."""
    t = TIERS[tier]
    n = 12
    _row_top(bp, t, n, "chemical-science-pack")
    _row_bottom(bp, t, n, "chemical-science-pack", 9)
    bottom = 16
    kit = Kit(bp, t["belt"], t["ug"], bottom)
    kit.feed(6, -9, 3 * n - 1, south_item=("advanced-circuit", 225), north_item=("engine-unit", 150))
    kit.feed(7, -4, 3 * n - 1, south_item=("sulfur", 75))
    kit.belt(0, 0, 3 * n + 3)                             # science belt y=0, leaves east
    kit.belt(13, 0, 3 * n)                                # bottom row output
    kit.render()
    xr = 3 * n + 1                                        # return column: up and side-load y=0 (south lane)
    for y in range(13, 0, -1):
        bp.add(t["belt"], xr, y, N)


def yellow_tile(bp, tier="early"):
    """Utility science: 14 utility assemblers fed directly from 14 robot-frame assemblers below them (1:1).
    Utility: LDS + blue circuits by long-handed from y=-1. Frames: e-engine + battery (y=10, fast),
    steel + green circuits (y=11, long). All from the bus."""
    t = TIERS[tier]
    n = 14
    for k in range(n):
        x = 3 * k
        bp.add(t["am"], x, 2, recipe="utility-science-pack")
        bp.add(t["am"], x, 6, recipe="flying-robot-frame")
        bp.add(t["ins"], x + 1, 1, S)                     # utility -> science belt
        bp.add(LH, x, 1, N)                               # LDS + blue <- y=-1
        bp.add(t["ins"], x + 1, 5, S)                     # frame -> utility (direct)
        bp.add(t["ins"], x + 1, 9, S)                     # e-engine + battery <- y=10
        bp.add(LH, x + 2, 9, S)                           # steel + green <- y=11
        if k % 2 == 0 or k == n - 1:
            bp.add(t["pole"], x + 2, 1); bp.add(t["pole"], x + 2, 5); bp.add(t["pole"], x, 9)
    bottom = 14
    kit = Kit(bp, t["belt"], t["ug"], bottom)
    kit.feed(-1, -24, 3 * n - 1, south_item=("processing-unit", 100), north_item=("low-density-structure", 150))
    kit.feed(11, -16, 3 * n - 1, south_item=("electronic-circuit", 150), north_item=("steel-plate", 50))
    kit.feed(10, -8, 3 * n - 1, south_item=("battery", 100), north_item=("electric-engine-unit", 50))
    kit.belt(0, 0, 3 * n + 1)
    kit.render()
    bp.add(t["pole"], -2, 3); bp.add(t["pole"], -2, 8)


def military_tile(bp, tier="early"):
    """Military science: 10 science assemblers.
       north: walls by long-handed from y=-1 (3 wall assemblers west of it, bricks from y=-7)
       south: piercing rounds (fast, y=6 north lane) + grenades (long, y=7)
    Piercing: 3 assemblers with 2 firearm-magazine assemblers between them (direct insertion);
    firearm iron from the y=6 south lane, piercing steel + copper from y=12.
    Grenades: 8 assemblers, coal (fast, y=13) + iron (long, y=14)."""
    t = TIERS[tier]
    n = 10
    for k in range(n):
        x = 3 * k
        bp.add(t["am"], x, 2, recipe="military-science-pack")
        bp.add(t["ins"], x + 1, 1, S)                     # -> science belt
        bp.add(LH, x, 1, N)                               # walls <- y=-1
        bp.add(t["ins"], x + 1, 5, S)                     # piercing <- y=6
        bp.add(LH, x + 2, 5, S)                           # grenades <- y=7
        if k % 2 == 0 or k == n - 1:
            bp.add(t["pole"], x + 2, 1); bp.add(t["pole"], x, 5)
    ng = 8
    for k in range(ng):                                   # grenades
        x = 3 * k
        bp.add(t["am"], x, 9, recipe="grenade")
        bp.add(t["ins"], x + 1, 8, S)                     # -> y=7
        bp.add(t["ins"], x + 1, 12, S)                    # coal <- y=13
        bp.add(LH, x + 2, 12, S)                          # iron <- y=14
        if k % 2 == 0 or k == ng - 1:
            bp.add(t["pole"], x, 8); bp.add(t["pole"], x, 12)
    # 3 wall assemblers (north-west), each 2 brick inserters (5 bricks/s at the early tier), output onto y=-1
    for x in (-14, -11, -8):
        bp.add(t["am"], x, -5, recipe="stone-wall")
        bp.add(t["ins"], x + 1, -2, N)                    # -> walls belt y=-1
        bp.add(t["ins"], x, -6, N); bp.add(t["ins"], x + 2, -6, N)   # bricks <- y=-7
        bp.add(t["pole"], x + 1, -6)
    for px in (-12, -8, -3):
        bp.add(t["pole"], px, -2)
    # piercing cluster (south-west): P F P F P, pitch 4. Firearm needs 4 iron per magazine, so each firearm
    # assembler takes iron with three inserters (2 iron/s at the early tier).
    P, F = "piercing-rounds-magazine", "firearm-magazine"
    cells = [(P, -20), (F, -16), (P, -12), (F, -8), (P, -4)]
    for recipe, x in cells:
        bp.add(t["am"], x, 8, recipe=recipe)
        if recipe == P:
            bp.add(t["ins"], x + 1, 7, S)                 # -> y=6 north lane
            bp.add(t["ins"], x + 1, 11, S)                # steel + copper <- y=12
        else:
            for ix in (x, x + 1, x + 2):
                bp.add(t["ins"], ix, 7, N)                # iron <- y=6 south lane
    for (ra, xa), (rb, xb) in zip(cells, cells[1:]):      # firearm -> neighbouring piercing
        bp.add(t["ins"], xa + 3, 9, W if ra == F else E)
    for x, y in ((-17, 7), (-13, 7), (-9, 7), (-5, 7), (-18, 11), (-14, 11), (-10, 11), (-6, 11), (-2, 11)):
        bp.add(t["pole"], x, y)
    bottom = 17
    kit = Kit(bp, t["belt"], t["ug"], bottom)
    kit.feed(-7, -36, -6, south_item=("stone-brick", 750))
    kit.belt(-1, -14, 3 * n - 1)                          # walls belt (fed by the wall assemblers)
    kit.feed(6, -30, 3 * n - 1, south_item=("iron-plate", 600))
    kit.feed(12, -25, -2, south_item=("copper-plate", 150), north_item=("steel-plate", 38))
    kit.feed(13, -10, 23, south_item=("coal", 750))
    kit.feed(14, -6, 23, south_item=("iron-plate", 375))
    kit.belt(7, 0, 3 * n - 1)                             # grenade belt
    kit.belt(0, 0, 3 * n + 1)                             # science belt
    kit.render()


def purple_tile(bp, tier="early"):
    """Production science: 14 science assemblers. Per 3 packs: 30 rails, 1 electric furnace, 1 prod module.
       y=0  science belt                      y=2..4  science row (fast <- y=6 rails, long <- y=7)
       y=6  rails, both lanes                 y=7     [modules N | furnaces S]
       y=9..11 modules x=3..32 (-> y=7 N lane, red|green <- y=13) and furnaces x<0 (-> own belt on y=7,
               which drops to y=8 and side-loads the main y=7 at x=1, S lane; steel|brick <- y=13 by two inserters, red <- y=14 by long-handed)
       y=21..23 rail row R S R R S R R S R (pitch 4). Stick assemblers hand sticks sideways to both
               neighbours; rails go up onto y=19, split in two segments: the west one turns into the start
               of y=6 (north lane), the east one side-loads it (south lane), so rails fill both lanes.
               Rails take steel|stone from y=25, sticks take iron from y=26 with three long-handed.
    Rates (late): rails 25/s, furnaces 4 x AM at 83 %, modules 10, sticks 3, rails 6 (83 %)."""
    t = TIERS[tier]
    n = 14
    _row_top(bp, t, n, "production-science-pack")
    # modules under the science row
    nm = 10
    for k in range(nm):
        x = 3 + 3 * k
        bp.add(t["am"], x, 9, recipe="productivity-module")
        bp.add(t["ins"], x + 1, 8, S)                     # -> y=7 north lane
        bp.add(t["ins"], x + 1, 12, S)                    # red + green <- y=13
        if k % 2 == 0 or k == nm - 1:
            bp.add(t["pole"], x, 8); bp.add(t["pole"], x, 12)
    # electric furnaces (west), pitch 4, poles in the gaps
    for x in (-19, -15, -11, -7):
        bp.add(t["am"], x, 9, recipe="electric-furnace")
        bp.add(t["ins"], x + 1, 8, S)                     # -> y=8 belt
        bp.add(t["ins"], x, 12, S); bp.add(t["ins"], x + 1, 12, S)   # steel + bricks <- y=13
        bp.add(LH, x + 2, 12, S)                          # red circuits <- y=14
    for x in (-20, -16, -12, -8, -4):
        bp.add(t["pole"], x, 10)
    # rail row
    R, St = "rail", "iron-stick"
    x0 = -66
    cells = [(r, x0 + 4 * i) for i, r in enumerate((R, St, R, R, St, R, R, St, R))]
    for recipe, x in cells:
        bp.add(t["am"], x, 21, recipe=recipe)
        if recipe == R:
            bp.add(t["ins"], x + 1, 20, S)                # -> y=19
            bp.add(t["ins"], x, 24, S); bp.add(t["ins"], x + 1, 24, S)   # steel + stone <- y=25
        else:
            for ix in (x, x + 1, x + 2):
                bp.add(LH, ix, 24, S)                     # iron <- y=26
    for (ra, xa), (rb, xb) in zip(cells, cells[1:]):
        if St in (ra, rb):
            bp.add(t["ins"], xa + 3, 22, W if ra == St else E)
    for g in [x0 - 1] + [x + 3 for _, x in cells]:
        bp.add(t["pole"], g, 20); bp.add(t["pole"], g, 24)
    for x in (-26, -20, -14, -8):                         # power bridge rail row -> furnaces
        bp.add(t["pole"], x, 16)

    bottom = 28
    kit = Kit(bp, t["belt"], t["ug"], bottom)
    xa = x0 + 4 * 4 + 3                                   # gap between cell 4 and 5: west rails segment turns up
    kit.belt(19, x0 - 1, xa - 1)
    kit.column(xa, 7, 19); kit.tile(xa, 6, E)             # -> start of y=6 (north lane)
    kit.belt(19, xa + 1, -4)
    kit.column(-3, 7, 19)                                 # -> side-loads y=6 (south lane)
    kit.belt(6, xa + 1, 3 * n - 1)
    kit.belt(7, 0, 3 * n - 1)
    kit.belt(7, -20, -6); kit.tile(-5, 7, S); kit.tile(-5, 8, E)   # furnaces: down, east under the rails
    kit.belt(8, -4, 0); kit.tile(1, 8, N)                 # column, side-load y=7 (south lane)
    kit.belt(0, 0, 3 * n + 1)
    kit.feed(13, -23, -5, south_item=("steel-plate", 500), north_item=("stone-brick", 500))
    kit.feed(14, -19, -5, south_item=("advanced-circuit", 250))
    kit.feed(13, -1, 3 + 3 * nm - 1, south_item=("electronic-circuit", 250), north_item=("advanced-circuit", 250))
    kit.feed(25, -70, x0 + 4 * 8 + 2, south_item=("steel-plate", 750), north_item=("stone", 750))
    kit.feed(26, -67, x0 + 4 * 8 + 2, south_item=("iron-plate", 375))
    kit.render()
