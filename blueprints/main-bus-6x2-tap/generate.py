"""Main bus 6+2 branch pieces: take lane N of a 6-lane group north (full lane or half via splitter).
Default = full tap of lane 0; variants for every lane and both kinds. Place over an existing segment
(super-force build replaces the straight belts)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.fbp import *
from lib.main_bus import tap, GROUP, TIER

def build(lane, kind):
    bp = Blueprint(f"Bus tap {kind} lane {lane}", game="2.0",
                   description=f"{kind} tap of lane {lane} (0 = top) of a 6-lane group; branch leaves north.")
    cols = tap(bp, lane, kind, rise=2)
    belt = TIER["yellow"][0]
    for y in range(GROUP):                       # 2 straight belts each side to show / align the bus
        bp.belt_line(belt, cols[0] - 2, y, E, 2)
        if not (kind == "full" and y == lane):
            bp.belt_line(belt, cols[1] + 1, y, E, 2)
    return bp

if __name__ == "__main__":
    save(build(0, "full"), __file__)
    for kind in ("full", "half"):
        for lane in range(GROUP):
            if (kind, lane) != ("full", 0):
                save(build(lane, kind), __file__, f"variants/{kind}-lane{lane}.txt")
