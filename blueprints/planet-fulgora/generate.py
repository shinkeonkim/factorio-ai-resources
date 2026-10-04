"""Fulgora all-in-one complex (lib/planets/fulgora.py): one bus, every production line as a stack of cells.
blueprint.txt = the whole complex; variants/<line>.txt = each line alone."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.planets import fulgora as F
from lib.planets.common import write_planet, void_sink, TRASH

if __name__ == "__main__":
    write_planet(F, __file__, "Fulgora all-in-one",
                 "Markers on the west end = raw inputs: scrap (big mining drills on scrap) and heavy oil (offshore pumps "
                 "on the oil ocean). Lightning collectors protect and power the whole complex.",
                 [("lightning-power", F.lightning_field()), ("scrap-recycling", F.scrap_stack(1)),
                  ("secondary-recycling", F.second_stack()),
                  ("rocket-silo", F.rocket_stack(["electromagnetic-science-pack", "holmium-plate", "supercapacitor",
                                                  "superconductor"])),
                  ("void", void_sink(TRASH))])
