"""Main bus 6+2 crossing piece: a branch from a lower group passes north through a full 6-lane group
(all six lanes dive under one column). Stack it on every group between the tap and the factory."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.fbp import *
from lib.main_bus import crossing, fluid_crossing, GROUP, TIER

if __name__ == "__main__":
    bp = Blueprint("Bus crossing (6 lanes)", game="2.0",
                   description="All 6 lanes dive under the branch column; branch enters from the gap below, leaves north.")
    crossing(bp, rise=1)
    belt = TIER["yellow"][0]
    for y in range(GROUP):
        bp.belt_line(belt, -3, y, E, 2); bp.belt_line(belt, 2, y, E, 2)
    save(bp, __file__)
    fp = Blueprint("Bus fluid crossing (6 lanes)", game="2.0",
                   description="A fluid branch passes under one 6-lane group: pipe-to-ground from the gap row below to the gap row above.")
    fluid_crossing(fp)
    for y in range(GROUP):
        fp.belt_line(belt, -2, y, E, 5)
    save(fp, __file__, "variants/fluid.txt")
