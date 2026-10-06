"""Aquilo all-in-one base (lib/planets/aquilo.py + lib/base.py): heated robot-fed cells (lib/hstack.py) in one
rectangle, fluids in plain-pipe trunks, heating-tower power whose heat pipes also keep every building warm
(lib/heat.py fills and checks them). blueprint.txt = the whole base; variants/<line>.txt = each line alone (cap + 1 cell, its own heat pipes)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.planets import aquilo as A
from lib.planets.common import write_planet

if __name__ == "__main__":
    write_planet(A, __file__, "Aquilo all-in-one",
                 "Makes: ~96 cryogenic science/min, lithium plates, ice platforms, fusion power cells, ammonia rocket fuel. "
                 "Needs: ammoniacal solution, lithium brine, fluorine and crude oil at the west inputs of each shelf, "
                 "imports (holmium plates, blue circuits, LDS) via the landing pad. To start: rocket fuel in the heating "
                 "towers' chests, 100 logistic robots; everything that freezes has heat pipe beside it.",
                 [("power", A.power_stack()), ("rocket-silo", A.rocket_stack()), ("landing-pad", A.pad_stack())])
