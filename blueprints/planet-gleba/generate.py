"""Gleba all-in-one base (lib/planets/gleba.py + lib/base.py): robot-fed cells in one rectangle inside a wall with
laser / gun turrets. blueprint.txt = the whole base; variants/<line>.txt = each line alone; farm tiles for yumako /
jellynut soil (outside the wall, inside the robot network)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.planets import gleba as G
from lib.planets.common import write_planet

if __name__ == "__main__":
    write_planet(G, __file__, "Gleba all-in-one",
                 "Makes: ~600 agricultural science/min, bioflux, nutrients, carbon fiber, rocket fuel, bacteria iron, "
                 "magazines for its own turrets. Needs: water at the west inputs (offshore pumps), yumako + jellynut from "
                 "the farm tiles (variants/farm-*.txt, inside the robot network). To start: 150 logistic robots, 2000 "
                 "spoilage or some rocket fuel for the heating towers, nutrients, one pentapod egg.",
                 [("power", G.power_stack()), ("rocket-silo", G.rocket_stack()), ("landing-pad", G.pad_stack()),
                  ("farm-yumako", G.farm_tile("yumako-seed")), ("farm-jellynut", G.farm_tile("jellynut-seed"))])
