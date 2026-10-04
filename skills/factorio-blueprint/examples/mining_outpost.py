"""Electric-mining-drill outpost: two drill rows facing a shared belt.
Drills come in pairs around a 1-tile pole column: drill x, pole x+3, drill x+4 (pitch 7). The 1-tile gap is still mined
because each drill mines a 5x5 area around its 3x3 body.
Belt at y=3 runs east; drills above face S, drills below face N. 0.5 ore/s per drill
(30 drills ≈ 1 yellow belt).
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from blueprint import Blueprint, N, E, S, W

def build(pairs=3, belt="transport-belt"):
    bp = Blueprint(f"Mining outpost {pairs*4} drills", game="2.0",
                   description="ore exits east end of belt row y=3")
    w = pairs * 7
    bp.belt_line(belt, 0, 3, E, w)
    for p in range(pairs):
        x = 7 * p
        for dx in (0, 4):
            bp.add("electric-mining-drill", x + dx, 0, S)
            bp.add("electric-mining-drill", x + dx, 4, N)
        bp.add("medium-electric-pole", x + 3, 1)
        bp.add("medium-electric-pole", x + 3, 5)
    bp.connect_poles()
    return bp

if __name__ == "__main__":
    bp = build(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
    print(bp.report()); print(); print(bp.to_string())
