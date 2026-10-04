"""Main bus kit: horizontal bus (flows east) in groups of 6 lanes separated by 2 empty rows.

Coordinates of one group: lanes on rows 0..5 (lane 0 = top), branches leave towards the north (row -1).
Group g of a multi-group bus sits at rows 8g .. 8g+5; rows 8g+6, 8g+7 stay empty.

Tier-independence: every underground here spans at most 2 tiles, inside the yellow underground limit
(4), so the same layout keeps working after an upgrade-planner pass yellow -> red -> blue -> turbo.
"""
from lib.fbp import N, E, S, W

TIER = {"yellow": ("transport-belt", "underground-belt", "splitter"),
        "red": ("fast-transport-belt", "fast-underground-belt", "fast-splitter"),
        "blue": ("express-transport-belt", "express-underground-belt", "express-splitter"),
        "turbo": ("turbo-transport-belt", "turbo-underground-belt", "turbo-splitter")}
GROUP, GAP = 6, 2
PITCH = GROUP + GAP
# House bus (top -> bottom). Solid groups first, the fluid group last (bottom) so solid branches never
# cross fluid lines; fluid branches climb through the 2-row gaps with pipe-to-ground hops.
LAYOUT = [
    {"kind": "solid", "lanes": ["iron-plate"] * 6},
    {"kind": "solid", "lanes": ["copper-plate"] * 6},
    {"kind": "solid", "lanes": ["electronic-circuit"] * 2 + ["advanced-circuit"] * 2 + ["processing-unit"] * 2},
    {"kind": "solid", "lanes": ["steel-plate"] * 2 + ["plastic-bar"] * 2 + ["stone", "stone-brick"]},
    {"kind": "solid", "lanes": ["coal", "sulfur", "battery", "engine-unit", "electric-engine-unit", "low-density-structure"]},
    {"kind": "fluid", "lanes": ["petroleum-gas", "light-oil", "heavy-oil", "lubricant", "sulfuric-acid", "water"]},
]
SUGGESTED = [g["lanes"] for g in LAYOUT if g["kind"] == "solid"]
LANE_PER_MIN = {"yellow": 900, "red": 1800, "blue": 2700, "turbo": 3600}
FLUID_PER_MIN = 60000          # label only: a pipe-to-ground chain carries ~1,000+/s over these lengths
PTG_SPAN = 10                  # pipe-to-ground max distance; a pair covers x .. x+10 (9 tiles between)
PERIOD = PTG_SPAN + 1          # chain period: [W-facing at x] ... [E-facing at x+10], next pair at x+11


def group_row(g):
    return PITCH * g


def fluid_chain(bp, y, x0, length):
    """Horizontal pipe-to-ground chain on row y from x0 (inclusive) over `length` tiles (multiple of PERIOD).
    Neighbouring chains do not connect: pipe-to-ground only joins on its single above-ground side."""
    for j in range(length // PERIOD):
        a = x0 + PERIOD * j
        bp.add("pipe-to-ground", a, y, W)                 # above-ground side faces west (joins the previous pair)
        bp.add("pipe-to-ground", a + PTG_SPAN, y, E)


def segment(bp, length=33, tier="yellow", layout=LAYOUT, x0=0, y0=0, markers=True):
    """Bus segment for `layout` (default: the house bus). Solid groups: belts; fluid group: ptg chains.
    A constant-combinator label sits at the west end of every lane (count = lane capacity per minute)."""
    belt = TIER[tier][0]
    for g, grp in enumerate(layout):
        for i, item in enumerate(grp["lanes"]):
            y = y0 + PITCH * g + i
            if grp["kind"] == "solid":
                bp.belt_line(belt, x0, y, E, length)
                count = LANE_PER_MIN[tier]
            else:
                # no plain inlet pipe: stacked plain pipes would join all fluid lines. Feed each line with a
                # pipe-to-ground facing east at x0 (its underground passes under the label).
                fluid_chain(bp, y, x0 + 1, length - length % PERIOD)
                count = FLUID_PER_MIN
            if markers:
                bp.add_marker(x0 - 1, y, {item: count})


def fluid_tap(bp, line, x=0, y0=0, rise=True):
    """Bring fluid line `line` (0..5) of the fluid group (rows y0..y0+5) up to the gap row above it.
    The line surfaces at column x (ptg E at x-1, pipe at x, ptg W at x+1 re-pair with the chain);
    lines above it are underground at x, so a pipe-to-ground hop climbs to row y0-1 (facing north),
    ready for fluid_crossing() pieces in the groups above."""
    r = y0 + line
    bp.add("pipe-to-ground", x - 1, r, E)
    bp.add("pipe", x, r)
    bp.add("pipe-to-ground", x + 1, r, W)
    if line == 0:
        bp.add("pipe", x, y0 - 1)
    else:
        bp.add("pipe-to-ground", x, r - 1, S)             # joins the pipe below, goes underground north
        bp.add("pipe-to-ground", x, y0 - 1, N)


def fluid_crossing(bp, x=0, y0=0):
    """A fluid branch passes north through one 6-lane group (lanes y0..y0+5): pipe-to-ground from the
    first gap row below (y0+6, facing south) to the last gap row above (y0-1, facing north)."""
    bp.add("pipe-to-ground", x, y0 + GROUP, S)
    bp.add("pipe-to-ground", x, y0 - 1, N)


def dive(bp, ug, rows, x_in, x_out, x_before=None, belt=None):
    """Lanes on `rows` pass under columns x_in+1 .. x_out-1 (entrance x_in, exit x_out)."""
    for y in rows:
        bp.add(ug, x_in, y, E, type="input")
        bp.add(ug, x_out, y, E, type="output")


def tap(bp, lane, kind="full", tier="yellow", x=0, y0=0, rise=1):
    """Branch `lane` (0..5) of one group north at column x.
    full: the whole lane turns north (the lane ends here).
    half: a splitter sends half north, half continues east.
    Lanes above the tapped one dive under the branch column(s); lanes below pass straight.
    The branch belt continues `rise` tiles above the group (row y0-1 ...)."""
    belt, ug, spl = TIER[tier]
    r = y0 + lane
    above = [y0 + i for i in range(lane)]
    below = [y0 + i for i in range(lane + 1, GROUP)]
    if kind == "full":
        cols = (x - 1, x + 1)
        dive(bp, ug, above, x - 1, x + 1)
        bp.add(belt, x - 1, r, E)
        bp.add(belt, x, r, N)                                   # curve: lane turns north
        start = r - 1
    else:
        cols = (x - 2, x + 1)
        dive(bp, ug, above, x - 2, x + 1)
        bp.add(belt, x - 2, r, E)
        bp.add(spl, x - 1, r - 1, E)                            # splitter spans rows r-1 (branch) and r
        bp.add(belt, x, r, E); bp.add(belt, x + 1, r, E)        # lane continues
        bp.add(belt, x, r - 1, N)                               # branch turns north
        start = r - 2
    for y in range(start, y0 - 1 - rise, -1):
        bp.add(belt, x, y, N)
    for y in below:
        bp.belt_line(belt, cols[0], y, E, cols[1] - cols[0] + 1)
    return cols


def crossing(bp, tier="yellow", x=0, y0=0, rise=1):
    """A branch coming from a lower group passes north through this group: all 6 lanes dive at column x."""
    belt, ug, _ = TIER[tier]
    dive(bp, ug, [y0 + i for i in range(GROUP)], x - 1, x + 1)
    for y in range(y0 + GROUP + GAP - 1, y0 - 1 - rise, -1):
        bp.add(belt, x, y, N)
