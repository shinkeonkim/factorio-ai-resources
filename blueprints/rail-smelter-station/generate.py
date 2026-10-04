"""Smelter block (rail city block, 1-2 trains): north stop unloads ore, 42 electric furnaces,
south stop loads plates. Base: rail book 'Mixed Elev. Cityblock / 3 Car 2 Stations'."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.fbp import *
from lib.rail_city_block import *


def build(ORE="iron-ore", PLATE=None):
    PLATE = PLATE or ORE.replace("-ore", "-plate")
    WAGONS, EF = 2, "electric-furnace"
    base = book_bp([17, 10])
    base["label"] = f"[item={ORE}] -> [item={PLATE}] Smelter Block (1-2)"
    base["description"] = (f"North stop unloads {ORE}; 42 electric furnaces; south stop loads {PLATE}.\n"
                           "Train limits from chest contents (ore: free trainloads, plates: stored trainloads).")
    ov = Overlay(base, base["label"])
    SX, R1, R2, CX = 59, 139, 151, 53
    WEST_N, EAST_N, ROWS = 9, 12, (100, 112)       # furnaces per half-row, ore-row y of each band

    def band(oy, flow):
        for i in range(WEST_N):
            x = 16 + 4 * i
            ov.add(EF, x, oy + 2); ov.add(FI, x + 1, oy + 1, N); ov.add(FI, x + 1, oy + 5, N); ov.add(MP, x + 3, oy + 3)
        for i in range(EAST_N):
            x = 55 + 4 * i
            ov.add(EF, x, oy + 2); ov.add(FI, x + 1, oy + 1, N); ov.add(FI, x + 1, oy + 5, N); ov.add(MP, x + 3, oy + 3)
        py = oy + 6                                          # plates -> collector from both sides
        ov.belt_line(BELT, 15, py, E, CX - 15)               # x=15..52 -> west lane
        ov.belt_line(BELT, 103, py, W, 103 - CX)             # x=103..54 -> east lane
        if flow == E:                                        # ore row, crossing the collector underground
            ov.belt_line(BELT, 15, oy, E, CX - 1 - 15)       # x=15..51
            ov.underground(UG, CX - 1, oy, E, 1)             # 52 -> 54
            ov.belt_line(BELT, CX + 2, oy, E, 104 - (CX + 2))  # x=55..103
        else:
            ov.belt_line(BELT, 103, oy, W, 103 - (CX + 1))   # x=103..55
            ov.underground(UG, CX + 1, oy, W, 1)             # 54 -> 52
            ov.belt_line(BELT, CX - 2, oy, W, CX - 2 - 15 + 1)  # x=51..15

    band(ROWS[1], E)                                         # lower band first in the ore path
    band(ROWS[0], W)
    ov.add(BELT, 104, ROWS[1], N); ov.belt_line(BELT, 104, ROWS[1] - 1, N, ROWS[1] - ROWS[0] - 1)
    ov.add(BELT, 104, ROWS[0], W)                            # turn into the upper ore row

    # unload ore (north of track 1) -> row 134 westwards -> up x=14 -> lower band ore row
    u_chests, u_poles, u_belt, cols = wagon_side(ov, SX, R1, WAGONS, "N", "unload", None)
    ov.belt_line(BELT, 52, u_belt, W, 52 - 15 + 1)           # x=52..15
    ov.add(BELT, 14, u_belt, N); ov.belt_line(BELT, 14, u_belt - 1, N, u_belt - 1 - ROWS[1])
    ov.add(BELT, 14, ROWS[1], E)

    # plate collector x=53 from the upper plate row down, under track 1, to the load belt
    top = ROWS[0] + 6
    ov.belt_line(BELT, CX, top, S, (R1 - 3) - top)           # y=106..135
    ov.underground(UG, CX, R1 - 3, S, 4)                     # 136 -> 141
    l_chests, l_poles, l_belt, _ = wagon_side(ov, SX, R2, WAGONS, "N", "load", None)
    ov.belt_line(BELT, CX, R1 + 3, S, l_belt - (R1 + 3))
    ov.belt_line(BELT, CX, l_belt, W, CX - min(cols) + 1)

    # power links between bands and down to the station
    for y in (ROWS[0] + 9, ROWS[1] + 11, 130):
        ov.add(MP, 52, y)
    ov.add("big-electric-pole", 56, 159)

    # circuits: ore chests (red) -> unload limit, plate chests (green) -> load limit
    red_chain(ov, u_chests + u_poles)
    for (xa, a), (xb, b) in zip(sorted(l_chests + l_poles), sorted(l_chests + l_poles)[1:]):
        ov.wire(a, b, "green")
    ore_load = WAGONS * 40 * STACK.get(ORE, 50); plate_load = WAGONS * 40 * STACK.get(PLATE, 100)
    ore_cap = len(u_chests) * 48 * STACK.get(ORE, 50)
    K = ov.add("constant-combinator", 54, 143, control_behavior={"sections": {"sections": [{"index": 1, "filters": [
        {"index": 1, "type": "item", "name": ORE, "quality": "normal", "comparator": "=", "count": -ore_cap}]}]}})
    A1 = ov.add("arithmetic-combinator", 55, 143, control_behavior={"arithmetic_conditions": {
        "first_signal": {"type": "item", "name": ORE}, "second_constant": -ore_load, "operation": "/",
        "output_signal": {"type": "virtual", "name": "signal-L"}}}, player_description="ore drop limit = free trainloads")
    A2 = ov.add("arithmetic-combinator", 55, 145, control_behavior={"arithmetic_conditions": {
        "first_signal": {"type": "item", "name": PLATE}, "second_constant": plate_load, "operation": "/",
        "output_signal": {"type": "virtual", "name": "signal-L"}}}, player_description="plate pickup limit = stored trainloads")
    P1 = ov.add(MP, 56, 143)
    ov.wire(max(u_poles)[1], P1, "red"); ov.wire(P1, A1, "red", None, "in"); ov.wire(K, A1, "green", None, "in")
    ov.wire(max(l_poles)[1], A2, "green", None, "in")
    ov.connect_poles()

    stop_u = set_stop(base, {"x": SX, "y": R1 + 2}, f"[item={ORE}] Drop (smelter)")
    stop_l = set_stop(base, {"x": SX, "y": R2 + 2}, f"[item={PLATE}] Pickup")
    n0 = len(base["entities"]); merge(base, ov)
    base["wires"] += [[A1 + n0, 4, stop_u, 2], [A2 + n0, 4, stop_l, 2]]
    stitch_power(base)
    return {"blueprint": base}


if __name__ == "__main__":
    save(build("iron-ore"), __file__)
    save(build("copper-ore", "copper-plate"), __file__, "variants/copper-plate.txt")
