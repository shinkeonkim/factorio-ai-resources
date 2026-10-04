"""Empty rail city block tiled 2x2 (182x182 cells -> 364x364 snap grid).
Shared border streets are merged and power wires remapped. Input: third_party/empty-block.txt."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.fbp import *
import tile

if __name__ == "__main__":
    tile.SRC = decode(third_party("empty-block.txt").read_text())["blueprint"]
    tile.CELL = tile.SRC["snap-to-grid"]["x"]
    obj, same_spot = tile.tile(2)
    save(obj, __file__)
