"""Upgradeable mall: two streets of 20 items each, fed by bus branches (redesign of the 'Daiso' malls).
Default blueprint = logistics street at the early tier; variants: power street, and mid/late of both.
See lib/mall.py for the street layout and the cell lists."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.fbp import *
from lib.mall import street, STREETS

def build(name, tier):
    bp = Blueprint(f"Mall: {STREETS[name]['title']} ({tier})", game="2.0",
                   description="Inputs from bus taps at the bottom edge (markers capped at one yellow lane). "
                               "Products go into chests limited to 2 slots.")
    street(bp, name, tier)
    bp.connect_poles()
    return bp

if __name__ == "__main__":
    save(build("logistics", "early"), __file__)
    for name, tier in (("logistics", "mid"), ("logistics", "late"),
                       ("power-fluids-trains", "early"), ("power-fluids-trains", "mid"),
                       ("power-fluids-trains", "late")):
        save(build(name, tier), __file__, f"variants/{name}-{tier}.txt")
