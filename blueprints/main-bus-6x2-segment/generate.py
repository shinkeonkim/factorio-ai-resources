"""Main bus straight segment: 3 groups x 6 lanes, 2 empty rows between groups, 32 tiles long, flowing east.
Every lane starts with a constant-combinator label (suggested allocation, count = lane capacity per minute)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.fbp import *
from lib.main_bus import segment

def build(tier):
    bp = Blueprint(f"Main bus 6+2 segment ({tier})", game="2.0",
                   description="3 groups x 6 lanes, 2 empty rows between groups (branch corridors). Flows east.")
    segment(bp, groups=3, length=32, tier=tier)
    return bp

if __name__ == "__main__":
    save(build("yellow"), __file__)
    for t in ("red", "blue", "turbo"):
        save(build(t), __file__, f"variants/{t}.txt")
