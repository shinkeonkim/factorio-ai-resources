"""Mining provider block (rail city block, 1-2 trains): 64 electric drills -> collector -> load chests.
Base: rail book 'Mixed Elev. Cityblock / 3 Car 1 Station'."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.fbp import *
from lib.rail_city_block import *


def build(ORE="iron-ore"):
    WAGONS = 2
    base = book_bp([17, 11])
    base["label"] = f"[item={ORE}] Mining Block (1-2)"
    base["description"] = (f"Place on a {ORE} patch. 64 electric drills (~32/s) -> collector -> 12 steel chests -> 1-2 train.\n"
                           "Train limit = stored trainloads (circuit).")
    ov = Overlay(base, base["label"])
    SX, R = 59, 151
    CX = 53                                         # collector column, flows south

    drills = 0
    for y0 in (30, 70):
        drills += drill_band(ov, 25, y0, 4, E)      # west field x=25..52 -> side-loads collector west lane
        drills += drill_band(ov, 55, y0, 4, W)      # east field x=55..82 -> east lane
        ov.add(BELT, CX + 1, y0 + 3, W)             # bridge the 1-tile gap to the collector
    ov.belt_line(BELT, CX, 30, S, 145 - 30 + 1 - 1)  # x=53, y=30..144
    ov.add(BELT, CX, 145, S)
    chests, poles, belt_row, cols = wagon_side(ov, SX, R, WAGONS, "N", "load", None)
    ov.belt_line(BELT, CX, belt_row, W, CX - min(cols) + 1)    # y=146, x=53..39
    for y in range(38, 143, 8):                                 # power spine beside the collector
        ov.add(MP, CX + 1, y)
    ov.add("big-electric-pole", 56, 159)
    A, stop, load = provider_limit(ov, base, ORE, WAGONS, (chests, poles), (55, 143), {"x": SX, "y": R + 2},
                                   f"[item={ORE}] Pickup")
    red_chain(ov, chests + poles)
    ov.connect_poles()
    n0 = len(base["entities"])
    merge(base, ov)
    base["wires"].append([A + n0, 4, stop, 2])
    stitch_power(base)
    return {"blueprint": base}


if __name__ == "__main__":
    save(build("iron-ore"), __file__)
    save(build("copper-ore"), __file__, "variants/copper-ore.txt")
    save(build("stone"), __file__, "variants/stone.txt")
    save(build("coal"), __file__, "variants/coal.txt")
