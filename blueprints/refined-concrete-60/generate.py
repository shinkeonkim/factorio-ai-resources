"""Refined concrete 60/min from stone + iron ore + water (Factorio 2.0).
Fast belts, electric furnaces, assembling-machine-2, fast inserters (long-handed where 2-tile reach needed).
All inputs/outputs on the WEST edge."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.fbp import *

BELT, PIPE, PTG = "fast-transport-belt", "pipe", "pipe-to-ground"
AM, EF, FI, LI, POLE = "assembling-machine-2", "electric-furnace", "fast-inserter", "long-handed-inserter", "medium-electric-pole"
bp = Blueprint("Refined concrete 60/min", game="2.0",
               description="West edge: y=-5 water, y=-3 iron ore, y=-2 stone (in) / y=11 refined concrete (out)")

# ---- band A (y=0..2): F1 F2 C1 B1 C2 B2 C3, pitch 4 ----
A = [("F", 0), ("F", 4), ("C", 8), ("B", 12), ("C", 16), ("B", 20), ("C", 24)]
for kind, x in A:
    if kind == "F":                                   # iron furnace: ore (long, y=-3) -> plates (long -> y=5)
        bp.add(EF, x, 0)
        bp.add(LI, x + 1, -1, N)
        bp.add(LI, x + 1, 3, N)
    elif kind == "B":                                 # brick furnace: stone (fast, y=-2); bricks go sideways
        bp.add(EF, x, 0)
        bp.add(FI, x + 1, -1, N)
        bp.add(FI, x - 1, 1, E)                       # picks from B (east), drops into AM on west
        bp.add(FI, x + 3, 1, W)                       # picks from B (west), drops into AM on east
    else:                                             # concrete AM, water from north
        bp.add(AM, x, 0, recipe="concrete")
        bp.add(PTG, x + 1, -1, S); bp.add(PTG, x + 1, -4, N)
        bp.add(LI, x + 2, -1, N)                      # iron ore from y=-3
        bp.add(FI, x, 3, N)                           # concrete -> y=4 (south lane)
for gx in (3, 7, 11, 15, 19, 23, 27):
    bp.add(POLE, gx, 2)

# ---- belts / pipes between and around bands ----
bp.belt_line(BELT, -1, -3, E, 28)                     # iron ore  x=-1..26
bp.belt_line(BELT, -1, -2, E, 24)                     # stone     x=-1..22
bp.belt_line(BELT, 8, 4, E, 27)                       # concrete (S lane) + sticks (N lane) x=8..34
bp.belt_line(BELT, 0, 5, E, 35)                       # plates (S lane) + steel (N lane)   x=0..34
bp.belt_line(BELT, 34, 11, W, 36)                     # refined concrete out x=34..-1
for x in range(-1, 37):
    bp.add(PIPE, x, -5)                               # water main 1
for y in range(-4, 13):
    bp.add(PIPE, 36, y)                               # east riser to water main 2
for x in range(28, 37):
    bp.add(PIPE, x, 13)                               # water main 2

# ---- band B (y=7..9): S K R1 R2 ----
bp.add(EF, 8, 7)                                      # steel furnace
bp.add(FI, 8, 6, N)                                   # plates from y=5
bp.add(FI, 9, 6, S)                                   # steel -> y=5 (north lane)
bp.add(AM, 12, 7, recipe="iron-stick")
bp.add(FI, 12, 6, N)                                  # plates from y=5
bp.add(LI, 14, 6, S)                                  # sticks -> y=4 (north lane)
for x in (28, 32):
    bp.add(AM, x, 7, S, recipe="refined-concrete")    # facing S: water port on south side
    bp.add(FI, x, 6, N)                               # steel from y=5
    bp.add(LI, x + 1, 6, N); bp.add(LI, x + 2, 6, N)  # concrete + sticks from y=4
    bp.add(FI, x, 10, N)                              # output -> y=11
    bp.add(PTG, x + 1, 10, N); bp.add(PTG, x + 1, 12, S)
for gx in (11, 15, 27, 31, 35):
    bp.add(POLE, gx, 8)


# ---- input markers (constant combinators, count = per minute) ----
bp.add_marker(-1, -6, {"water": 1800})
bp.add_marker(-1, -4, {"iron-ore": 66})
bp.add_marker(-1, -1, {"stone": 120})

bp.connect_poles()
save(bp, __file__)
