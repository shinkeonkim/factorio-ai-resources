"""Refined-concrete module shared by refined-concrete-240 and refined-concrete-1200.

Band A (y=0..2): [C B C] x groups + iron furnaces F; bricks go furnace -> concrete AM sideways.
Band B (y=7..9): refined AM R, steel furnaces S, stick AMs K.
Belts: y=-3 ore (E), y=-2 stone (E), y=4 concrete+sticks (W), y=5 plates+steel (W), y=11 output (W).
Water: y=-5 main, east riser, y=13 main for R.
`edge` = x of the west end of the input belts / water main / output belt.
"""
from lib.fbp import N, E, S, W

BELT, PIPE, PTG = "fast-transport-belt", "pipe", "pipe-to-ground"
AM, EF, FI, LI, POLE = ("assembling-machine-2", "electric-furnace", "fast-inserter",
                        "long-handed-inserter", "medium-electric-pole")


def module(bp, groups=7, n_f=6, n_r=8, n_s=4, n_k=2, edge=-1):
    band_a = []
    for _ in range(groups):
        band_a += ["C", "B", "C"]
    band_a += ["F"] * n_f
    for i, kind in enumerate(band_a):
        x = 4 * i
        if kind == "F":                               # iron ore (long) -> plates (long, onto y=5 S lane)
            bp.add(EF, x, 0); bp.add(LI, x + 1, -1, N); bp.add(LI, x + 1, 3, N)
        elif kind == "B":                             # stone (fast) -> bricks to both neighbours
            bp.add(EF, x, 0); bp.add(FI, x + 1, -1, N)
            bp.add(FI, x - 1, 1, E)                   # picks from B, drops into C on the west
            bp.add(FI, x + 3, 1, W)                   # picks from B, drops into C on the east
        else:                                         # concrete AM, water from north via pipe-to-ground
            bp.add(AM, x, 0, recipe="concrete")
            bp.add(PTG, x + 1, -1, S); bp.add(PTG, x + 1, -4, N)
            bp.add(LI, x + 2, -1, N)                  # iron ore
            bp.add(FI, x, 3, N)                       # concrete -> y=4 (S lane)
        bp.add(POLE, x + 3, 2)
    wa = 4 * len(band_a) - 1                          # last band-A column

    band_b = ["R"] * n_r + ["S"] * n_s + ["K"] * n_k
    for i, kind in enumerate(band_b):
        x = 4 * i
        if kind == "R":
            bp.add(AM, x, 7, S, recipe="refined-concrete")
            bp.add(FI, x, 6, N)                       # steel from y=5
            bp.add(LI, x + 1, 6, N); bp.add(LI, x + 2, 6, N)   # concrete + sticks from y=4
            bp.add(FI, x, 10, N)                      # output -> y=11
            bp.add(PTG, x + 1, 10, N); bp.add(PTG, x + 1, 12, S)
        elif kind == "S":
            bp.add(EF, x, 7)
            bp.add(FI, x, 6, N)                       # plates from y=5
            bp.add(FI, x + 1, 6, S)                   # steel -> y=5 (N lane)
        else:
            bp.add(AM, x, 7, recipe="iron-stick")
            bp.add(FI, x, 6, N)                       # plates from y=5
            bp.add(LI, x + 1, 6, S); bp.add(LI, x + 2, 6, S)   # sticks -> y=4 (N lane)
        bp.add(POLE, x + 3, 8)
        if i == 0:
            bp.add(POLE, x - 1, 8)

    last_b = 4 * (len(band_a) - n_f - 2)
    last_c = 4 * (len(band_a) - n_f - 1)
    rb = 4 * n_r - 2
    bp.belt_line(BELT, edge, -3, E, wa - edge)                  # ore, to last F
    bp.belt_line(BELT, edge, -2, E, last_b + 2 - edge)          # stone, to last B
    bp.belt_line(BELT, last_c, 4, W, last_c + 1)                # concrete + sticks
    bp.belt_line(BELT, wa - 1, 5, W, wa)                        # plates + steel
    bp.belt_line(BELT, rb, 11, W, rb + 1 - edge)                # output to x=edge
    xr = wa + 2                                                 # east water riser column
    for x in range(edge, xr + 1):
        bp.add(PIPE, x, -5)
    for y in range(-4, 13):
        bp.add(PIPE, xr, y)
    for x in range(1, xr + 1):
        bp.add(PIPE, x, 13)
    return {"band_a": band_a, "band_b": band_b, "width": xr + 1}
