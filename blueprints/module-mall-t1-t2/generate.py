"""Module mall: speed / efficiency / productivity / quality, tiers 1 and 2. Inputs from main bus.
Per type one group [T1][T2][T1] (AM3): a T2 eats 10 T1/min, one T1 makes 5/min, so two T1 feed the
T2 in the middle sideways; T1 surplus goes to its own chest (limited to 1 stack).
Belts (west -> east): y=-3 green (N lane) + blue (S lane), y=-2 red (both lanes)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.fbp import *

TYPES = ["speed", "efficiency", "productivity", "quality"]
BELT, AM, FI, LI, POLE, CHEST = ("fast-transport-belt", "assembling-machine-3", "fast-inserter",
                                 "long-handed-inserter", "medium-electric-pole", "steel-chest")
bp = Blueprint("Module mall T1-T2", game="2.0", icons=["speed-module-2", "efficiency-module-2",
               "productivity-module-2", "quality-module-2"],
               description="West inputs: y=-4 green circuit, y=-2 processing unit, y=0 advanced circuit. Products in chests (y=4).")

x = 0
for t in TYPES:
    for kind in ("T1", "T2", "T1"):
        if kind == "T1":
            bp.add(AM, x, 0, recipe=f"{t}-module")
            bp.add(FI, x, -1, N)                       # advanced circuit (y=-2)
            bp.add(LI, x + 1, -1, N)                   # electronic circuit (y=-3, north lane)
            bar = 1                                    # keep only 1 stack so T2 gets the rest
        else:
            bp.add(AM, x, 0, recipe=f"{t}-module-2")
            bp.add(FI, x, -1, N)                       # advanced circuit (y=-2)
            bp.add(LI, x + 1, -1, N)                   # processing unit (y=-3, south lane)
            bp.add(FI, x - 1, 1, W)                    # T1 on the west -> T2
            bp.add(FI, x + 3, 1, E)                    # T1 on the east -> T2
            bar = 2
        bp.add(FI, x + 1, 3, N)                        # product -> chest
        bp.add(CHEST, x + 1, 4, bar=bar)
        bp.add(POLE, x + 3, 2)
        x += 4
end = x - 2                                            # last machine column used by inserters

# ---- bus belts ----
bp.add(BELT, -3, -3, E)                                # dead start so both side-loads work
bp.belt_line(BELT, -2, -3, E, end + 3)                 # green + blue merge belt, x=-2..end
bp.belt_line(BELT, -1, -2, E, end + 2)                 # red, x=-1..end
# green: enters from west at y=-4, side-loads onto the north lane
bp.belt_line(BELT, -4, -4, E, 2); bp.add(BELT, -2, -4, S)
# processing unit: enters from west at y=-2, side-loads onto the south lane
bp.belt_line(BELT, -4, -2, E, 2); bp.add(BELT, -2, -2, N)
# advanced circuit: enters from west at y=0, turns north into the red belt
bp.belt_line(BELT, -4, 0, E, 3); bp.add(BELT, -1, 0, N); bp.add(BELT, -1, -1, N)
bp.add(POLE, -1, 2)

# ---- input markers (per minute, all machines running) ----
n = len(TYPES)
bp.add_marker(-4, -3, {"electronic-circuit": 50 * n})    # 2 x T1 x 25/min
bp.add_marker(-4, -1, {"processing-unit": 12.5 * n})      # T2 x 12.5/min
bp.add_marker(-4, 1, {"advanced-circuit": 62.5 * n})      # 2 x 25 + 12.5

bp.connect_poles()
save(bp, __file__)
