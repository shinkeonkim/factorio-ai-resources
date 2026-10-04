"""Gleba all-in-one complex (lib/planets/gleba.py): robot-fed cells, water bus, heating-tower power, defence ring.
blueprint.txt = the whole complex; variants/<line>.txt = each line alone; farm tiles for yumako / jellynut soil."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.planets import gleba as G
from lib.planets.common import write_planet

if __name__ == "__main__":
    write_planet(G, __file__, "Gleba all-in-one",
                 "Robot-fed: every machine has a requester chest (inputs + nutrients) and a passive provider chest. "
                 "Water from offshore pumps at the west markers. Farms (variants/farm-*.txt) go on yumako / jellynut "
                 "soil inside the robot network. Put a few pentapod eggs and nutrients into the network to start.",
                 [("power", G.power_stack()), ("rocket-silo", G.rocket_stack()), ("landing-pad", G.pad_stack()),
                  ("farm-yumako", G.farm_tile("yumako-seed")), ("farm-jellynut", G.farm_tile("jellynut-seed"))],
                 post=G.defend)
