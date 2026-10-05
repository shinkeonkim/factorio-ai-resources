"""Aquilo all-in-one base (lib/planets/aquilo.py + lib/base.py): heated robot-fed cells (lib/hstack.py) in one
rectangle, fluids in plain-pipe trunks, heating-tower power whose heat pipes also keep every building warm
(lib/heat.py fills and checks them). blueprint.txt = the whole base; variants/<line>.txt = each line alone (cap + 1 cell, its own heat pipes)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.planets import aquilo as A
from lib.planets.common import write_planet

if __name__ == "__main__":
    write_planet(A, __file__, "Aquilo all-in-one",
                 "Robot-fed and heated: every building that freezes has a heat pipe within one tile, joined to the "
                 "heating towers of the power block. Fluids at the trunk tops (north-west: offshore pump on the "
                 "ammonia ocean, pumpjacks on crude oil / lithium brine / fluorine vents). Put rocket fuel into the network "
                 "to start the heating towers; the landing pad imports holmium plates, blue circuits and LDS.",
                 [("power", A.power_stack()), ("rocket-silo", A.rocket_stack()), ("landing-pad", A.pad_stack())])
