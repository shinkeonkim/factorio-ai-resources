"""Vulcanus all-in-one base (lib/planets/vulcanus.py + lib/base.py): one rectangle of shelves, robots between blocks.
blueprint.txt = the whole base; variants/<line>.txt = each line alone (cap + 1 cell, markers on its inputs)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.planets import vulcanus as V
from lib.planets.common import write_planet, robot_pad, robot_silo

if __name__ == "__main__":
    write_planet(V, __file__, "Vulcanus all-in-one",
                 "Inputs: lava and sulfuric acid at the trunk tops (north-west: offshore pumps on lava, pumpjacks on "
                 "acid geysers); calcite, coal and tungsten ore belts into the south gate. Imports arrive at the "
                 "landing pad; robots carry items between blocks. Keep it outside demolisher territory.",
                 [("power", V.power_stack()), ("raw-intake", V.intake_stack()),
                  ("stone-void", V.stone_sink()), ("landing-pad", robot_pad(V.IMPORTS)), ("rocket-silo", robot_silo())])
