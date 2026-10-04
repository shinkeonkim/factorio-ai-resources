"""Ratio-perfect electronic circuits: 3 copper-cable AM -> 2 circuit AM by direct insertion.
One slice = 9 tiles wide, 12 tall, makes 3 circuits/s with AM2 (5 /s with AM3).
Belts: y=0 copper plates (east), y=10 iron plates (east), y=11 circuits out (west).
Note: machine->machine fast inserters must move 3 cable/s each; that needs inserter capacity
research (hand size >= 2). Mention this to the user.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from blueprint import Blueprint, N, E, S, W

def slice_(bp, x0, am="assembling-machine-2"):
    for i in range(3):                                   # cable row
        bp.add(am, x0 + 3 * i, 2, recipe="copper-cable")
        bp.add("fast-inserter", x0 + 3 * i + 1, 1, N)    # copper belt -> cable AM
    for i in range(2):                                   # circuit row, offset by 1
        cx = x0 + 1 + 4 * i
        bp.add(am, cx, 6, recipe="electronic-circuit")
        bp.add("fast-inserter", cx, 9, S)                # iron belt (y=10) -> circuit AM
        bp.add("long-handed-inserter", cx + 1, 9, N)     # circuit AM -> out belt (y=11)
        bp.add("long-handed-inserter", cx + 2, 9, N)
    for x in (1, 3, 5, 7):                               # cable -> circuit
        bp.add("fast-inserter", x0 + x, 5, N)
    bp.add("medium-electric-pole", x0 + 2, 1)
    bp.add("medium-electric-pole", x0 + 8, 1)
    bp.add("medium-electric-pole", x0 + 4, 5)
    bp.add("medium-electric-pole", x0 + 4, 9)

def build(slices=2, am="assembling-machine-2"):
    bp = Blueprint(f"Green circuits 3:2 x{slices}", game="2.0",
                   description="copper in y=0 (east), iron in y=10 (east), circuits out y=11 (west)")
    w = 9 * slices
    bp.belt_line("transport-belt", 0, 0, E, w)
    bp.belt_line("transport-belt", 0, 10, E, w)
    bp.belt_line("transport-belt", w - 1, 11, W, w)
    for s in range(slices):
        slice_(bp, 9 * s, am)
    bp.connect_poles()
    return bp

if __name__ == "__main__":
    bp = build(int(sys.argv[1]) if len(sys.argv) > 1 else 2)
    print(bp.report()); print(); print(bp.to_string())
