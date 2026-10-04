"""Upgradeable green science tile for the 6+2 main bus (one layout, early/mid/late tiers).
Default blueprint = early tier (yellow, AM1, basic inserters, small poles); variants mid and late are the
same layout after an upgrade-planner pass. See lib/science.py."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.fbp import *
from lib.science import green_tile, TIERS

def build(tier):
    bp = Blueprint(f"Green science ({tier}, {TIERS[tier]['rate']}/min)", game="2.0",
                   description="Inputs from bus taps at the bottom edge (markers = late-tier demand/min). Science belt leaves east.")
    green_tile(bp, tier)
    bp.connect_poles()
    return bp

if __name__ == "__main__":
    save(build("early"), __file__)
    for t in ("mid", "late"):
        save(build(t), __file__, f"variants/{t}.txt")
