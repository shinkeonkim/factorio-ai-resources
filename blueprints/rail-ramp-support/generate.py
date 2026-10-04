"""Rail ramp + rail support factory (Space Age / elevated rails). Low rate, steel-limited.
Band A (y=0..2):  6 iron furnaces, ore from y=-2, plates -> y=4 (south lane).
y=4: plates (S lane) + stone (N lane, side-loaded at the west end).
Band B (y=6..8):  6 steel furnaces | iron-stick AM -> rail AM -> rail-ramp AM -> chest | rail-support AM -> chest
y=10: steel (from steel furnaces)   y=11: refined concrete (input)"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.fbp import *

BELT, AM, EF, FI, LI, POLE, CHEST = ("fast-transport-belt", "assembling-machine-2", "electric-furnace",
                                     "fast-inserter", "long-handed-inserter", "medium-electric-pole", "steel-chest")
bp = Blueprint("Rail ramp + support", game="2.0", icons=["rail-ramp", "rail-support"],
               description="West inputs: y=-2 iron ore, y=3 stone, y=11 refined concrete. Products in chests.")

# ---- band A: iron furnaces ----
for i in range(6):
    x = 4 * i
    bp.add(EF, x, 0); bp.add(FI, x + 1, -1, N); bp.add(FI, x + 1, 3, N)
    bp.add(POLE, x + 3, 2)

# ---- band B ----
for i in range(6):                                     # steel furnaces
    x = 4 * i
    bp.add(EF, x, 6); bp.add(FI, x + 1, 5, N)          # plates from y=4
    bp.add(FI, x + 1, 9, N)                            # steel -> y=10
    bp.add(POLE, x + 3, 8)
bp.add(AM, 24, 6, recipe="iron-stick");  bp.add(FI, 25, 5, N)       # plates from y=4
bp.add(FI, 27, 7, W)                                                # sticks -> rail AM
bp.add(AM, 28, 6, recipe="rail");        bp.add(FI, 29, 5, N)       # stone from y=4 (N lane)
bp.add(FI, 29, 9, S)                                                # steel from y=10
bp.add(FI, 31, 7, W)                                                # rails -> ramp AM
bp.add(AM, 32, 6, recipe="rail-ramp")
bp.add(FI, 32, 9, S); bp.add(LI, 34, 9, S)                          # steel y=10, refined concrete y=11
bp.add(FI, 35, 7, W); bp.add(CHEST, 36, 7, bar=2)                        # ramp -> chest
bp.add(AM, 38, 6, recipe="rail-support")
bp.add(FI, 38, 9, S); bp.add(LI, 40, 9, S)                          # steel y=10, refined concrete y=11
bp.add(FI, 41, 7, W); bp.add(CHEST, 42, 7, bar=2)                        # support -> chest
for gx in (27, 31, 37, 41):
    bp.add(POLE, gx, 8)

# ---- belts ----
bp.belt_line(BELT, -1, -2, E, 23)                      # iron ore x=-1..21
bp.add(BELT, -2, 4, E)                                 # dead start so the stone side-loads
bp.belt_line(BELT, -1, 4, E, 31)                       # plates + stone x=-1..29
bp.belt_line(BELT, -3, 3, E, 2); bp.add(BELT, -1, 3, S)   # stone in -> north lane of y=4
bp.belt_line(BELT, 0, 10, E, 39)                       # steel x=0..38
bp.belt_line(BELT, -1, 11, E, 42)                      # refined concrete x=-1..40

# ---- input markers (per minute) ----
bp.add_marker(-1, -1, {"iron-ore": 225})
bp.add_marker(-3, 4, {"stone": 4})
bp.add_marker(-1, 12, {"refined-concrete": 160})

bp.connect_poles()
save(bp, __file__)
