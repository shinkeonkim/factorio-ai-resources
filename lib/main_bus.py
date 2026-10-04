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
# suggested lane allocation for a 3-group (18-lane) starter-to-rocket bus
SUGGESTED = [["iron-plate"] * 4 + ["copper-plate"] * 2,
             ["copper-plate"] * 2 + ["steel-plate", "stone-brick", "electronic-circuit", "electronic-circuit"],
             ["plastic-bar", "advanced-circuit", "coal", "stone", "sulfur", "processing-unit"]]
LANE_PER_MIN = {"yellow": 900, "red": 1800, "blue": 2700, "turbo": 3600}


def segment(bp, groups=3, length=32, tier="yellow", lanes=SUGGESTED, x0=0, y0=0, markers=True):
    """Straight bus segment; optional constant-combinator label at the west end of every lane."""
    belt = TIER[tier][0]
    for g in range(groups):
        for i in range(GROUP):
            y = y0 + PITCH * g + i
            bp.belt_line(belt, x0, y, E, length)
            if markers and lanes and g < len(lanes):
                bp.add_marker(x0 - 1, y, {lanes[g][i]: LANE_PER_MIN[tier]})


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
