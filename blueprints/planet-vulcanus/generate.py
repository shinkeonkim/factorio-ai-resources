"""Vulcanus all-in-one base (lib/planets/vulcanus.py + lib/base.py): one rectangle of shelves, robots between blocks.
blueprint.txt = the whole base; variants/<line>.txt = each line alone (cap + 1 cell, markers on its inputs)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.planets import vulcanus as V
from lib.planets.common import write_planet, robot_pad, robot_silo

if __name__ == "__main__":
    write_planet(V, __file__, "Vulcanus all-in-one",
                 "Makes: ~360 metallurgic science/min, iron / steel / tungsten plates, tungsten carbide, LDS, a mall (foundries, "
                 "big drills, turbo belts). Needs: lava and sulfuric acid at the west inputs of each shelf (offshore pumps / "
                 "pumpjacks), calcite + coal + tungsten ore into the south gate (rates on the markers), imports via the landing "
                 "pad. To start: power is self-starting from the solar kit; add 150 logistic robots. Build outside demolisher "
                 "territory.",
                 [("power", V.power_stack()), ("raw-intake", V.intake_stack()),
                  ("stone-void", V.stone_sink()), ("landing-pad", robot_pad(V.IMPORTS)), ("rocket-silo", robot_silo())])
