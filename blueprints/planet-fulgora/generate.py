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
                 "Inputs: scrap belts from the west into the two bottom shelves (big mining drills on scrap), heavy oil "
                 "at its trunk top (north-west, offshore pump on the oil ocean). A band of lightning collectors and "
                 "accumulators around the base powers and protects it; robots carry items between blocks.",
                 [("lightning-tile", tile), ("scrap-recycling", F.scrap_stack(1)), ("secondary-recycling", F.second_stack()),
                  ("rocket-silo", robot_silo()), ("void", void_sink(TRASH, 4))])
