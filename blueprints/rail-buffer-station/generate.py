"""Single-item buffer block (rail city block, 1-2 trains): north stop unloads, south stop loads,
24 steel chests in between; train limits follow chest contents. Base: rail book 'Mixed Elev. Cityblock / 3 Car 2 Stations'."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.fbp import *
from lib.rail_city_block import *


def build(ITEM="iron-plate"):
    WAGONS, SLOTS = 2, 40
    base = book_bp([17, 10])
    base["label"] = f"[item={ITEM}] Buffer Block (1-2)"
    base["description"] = (f"Unload stop (north track) -> 24 steel chests -> load stop (south track), item {ITEM}.\n"
                           "Train limits are set from chest contents: unload = free trainloads, load = stored trainloads.")
    ov = Overlay(base, base["label"])
    SX, R1, R2 = 59, 139, 151          # stop x, unload track y, load track y
    BX = 53                            # vertical belt column (beside the locomotive)

    # unload side: north of track 1
    u_chests, u_poles, u_belt, cols = wagon_side(ov, SX, R1, WAGONS, "N", "unload", None)
    ov.belt_line(BELT, min(cols), u_belt, E, BX - min(cols))          # row 134, x=39..52 -> east
    ov.add(BELT, BX, u_belt, S); ov.add(BELT, BX, u_belt + 1, S)       # turn south
    ov.underground(UG, BX, u_belt + 2, S, R1 + 1 - (u_belt + 2))       # under track 1 -> exit at R1+2
    # load side: north of track 2
    l_chests, l_poles, l_belt, _ = wagon_side(ov, SX, R2, WAGONS, "N", "load", None)
    ov.belt_line(BELT, BX, R1 + 3, S, l_belt - (R1 + 3))               # down to the load belt row
    ov.belt_line(BELT, BX, l_belt, W, BX - min(cols) + 1)              # row 146, x=53..39 -> west

    # circuit: chests -> train limits
    red_chain(ov, u_chests + u_poles); red_chain(ov, l_chests + l_poles)
    cap = 2 * len(u_chests) * 48 * STACK.get(ITEM, 100)
    load = WAGONS * SLOTS * STACK.get(ITEM, 100)
    K = ov.add("constant-combinator", 54, 143,
               control_behavior={"sections": {"sections": [{"index": 1, "filters": [
                   {"index": 1, "type": "item", "name": ITEM, "quality": "normal", "comparator": "=", "count": -cap}]}]}})
    A1 = ov.add("arithmetic-combinator", 55, 143, control_behavior={"arithmetic_conditions": {
        "first_signal": {"type": "item", "name": ITEM}, "second_constant": -load, "operation": "/",
        "output_signal": {"type": "virtual", "name": "signal-L"}}},
        player_description="unload limit L = (capacity - stock) / trainload")
    A2 = ov.add("arithmetic-combinator", 55, 145, control_behavior={"arithmetic_conditions": {
        "first_signal": {"type": "item", "name": ITEM}, "second_constant": load, "operation": "/",
        "output_signal": {"type": "virtual", "name": "signal-L"}}},
        player_description="load limit L = stock / trainload")
    P1 = ov.add(MP, 56, 143)
    ov.wire(max(u_poles)[1], P1, "red"); ov.wire(max(l_poles)[1], P1, "red")
    ov.wire(P1, A1, "red", None, "in"); ov.wire(P1, A2, "red", None, "in")
    ov.wire(K, A1, "green", None, "in")
    ov.add("big-electric-pole", 56, 159)          # bridge: platform poles were not on the street grid
    ov.connect_poles()

    stop_u = set_stop(base, {"x": SX, "y": R1 + 2}, f"[item={ITEM}] Drop (buffer)")
    stop_l = set_stop(base, {"x": SX, "y": R2 + 2}, f"[item={ITEM}] Pickup (buffer)")
    n_before = len(base["entities"])
    linked = merge(base, ov)
    base["wires"] += [[A1 + n_before, 4, stop_u, 2], [A2 + n_before, 4, stop_l, 2]]
    stitch_power(base)
    return {"blueprint": base}


if __name__ == "__main__":
    save(build("iron-plate"), __file__)
    save(build("copper-plate"), __file__, "variants/copper-plate.txt")
    save(build("steel-plate"), __file__, "variants/steel-plate.txt")
