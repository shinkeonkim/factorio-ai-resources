"""Fulgora all-in-one base (lib/planets/fulgora.py + lib/base.py): one rectangle wrapped in a lightning band.
blueprint.txt = the whole base; variants/<line>.txt = each line alone."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.fbp import Blueprint
from lib.base import lightning_tile
from lib.complex import Stack
from lib.planets import fulgora as F
from lib.planets.common import write_planet, void_sink, robot_silo, TRASH

if __name__ == "__main__":
    tile = Stack("Lightning tile (12x12)", lambda bp, t: lightning_tile(bp, 0, 0), "mid")
    write_planet(F, __file__, "Fulgora all-in-one",
                 "Makes: ~100 electromagnetic science/min, holmium plates, superconductors, supercapacitors, accumulators, EM "
                 "plants, rocket parts. Needs: scrap belts into the west inputs of the scrap shelves, heavy oil at the "
                 "west inputs (offshore pump on the oil ocean). To start: build it in a storm or bring charged accumulators; "
                 "add 150 logistic robots. Sorted outputs stop at ~2 minutes of stock, everything else is voided.",
                 [("lightning-tile", tile), ("scrap-recycling", F.scrap_stack(1)), ("secondary-recycling", F.second_stack()),
                  ("rocket-silo", robot_silo()), ("void", void_sink(TRASH, 4))])
