"""Steel-furnace smelting column, two furnace stacks sharing one plate belt.
Columns: x=0 ore+coal belt (south) | x=1 inserter | x=2-3 furnace | x=4 inserter | x=5 plate belt (north)
         | x=6 inserter | x=7-8 furnace | x=9 inserter | x=10 ore+coal belt (south)
Each furnace pair is 2 tiles tall. 24 steel furnaces = 1 full yellow belt of ore (15/s) -> 12 rows.
Burner furnaces take coal from the same belt (put coal on one lane, ore on the other).
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from blueprint import Blueprint, N, E, S, W

def build(rows=12, furnace="steel-furnace", belt="transport-belt", ins="inserter"):
    bp = Blueprint(f"Smelting column {rows*2}x {furnace}", game="2.0",
                   description="ore+coal enters at top of x=0 and x=10 going south; plates leave top of x=5 going north")
    h = rows * 2
    bp.belt_line(belt, 0, 0, S, h)
    bp.belt_line(belt, 10, 0, S, h)
    bp.belt_line(belt, 5, h - 1, N, h)
    for r in range(rows):
        y = 2 * r
        bp.add(ins, 1, y, W)          # picks ore from x=0, drops into furnace
        bp.add(furnace, 2, y)
        bp.add(ins, 4, y, W)          # picks plates from furnace, drops on x=5
        bp.add(ins, 6, y, E)          # picks plates from furnace x=7, drops on x=5
        bp.add(furnace, 7, y)
        bp.add(ins, 9, y, E)          # picks ore from x=10
        if r % 3 == 0:                # medium poles in the free tiles of the inserter columns
            bp.add("medium-electric-pole", 4, y + 1)
            bp.add("medium-electric-pole", 6, y + 1)
    bp.connect_poles()
    return bp

if __name__ == "__main__":
    bp = build(int(sys.argv[1]) if len(sys.argv) > 1 else 12)
    print(bp.report()); print(); print(bp.to_string())
