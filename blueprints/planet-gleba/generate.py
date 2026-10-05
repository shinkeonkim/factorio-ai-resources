"""Gleba all-in-one base (lib/planets/gleba.py + lib/base.py): robot-fed cells in one rectangle inside a wall with
laser / gun turrets. blueprint.txt = the whole base; variants/<line>.txt = each line alone; farm tiles for yumako /
jellynut soil (outside the wall, inside the robot network)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.planets import gleba as G
from lib.planets.common import write_planet

if __name__ == "__main__":
    write_planet(G, __file__, "Gleba all-in-one",
                 "Robot-fed: every machine has a requester chest (inputs + nutrients) and a passive provider chest. "
                 "Water at the trunk tops (north-west, offshore pumps). Farms (variants/farm-*.txt) go on yumako / "
                 "jellynut soil within reach of the robot network. Put a few pentapod eggs and nutrients into the "
                 "network to start; turrets take magazines from the network.",
                 [("power", G.power_stack()), ("rocket-silo", G.rocket_stack()), ("landing-pad", G.pad_stack()),
                  ("farm-yumako", G.farm_tile("yumako-seed")), ("farm-jellynut", G.farm_tile("jellynut-seed"))])
