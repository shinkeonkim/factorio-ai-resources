"""Big rail city block 2x2: one 364x364 block with an EMPTY interior.

Only the perimeter streets exist: the 1x1 block's corner intersections are copied to the four corners and
the edges between them are long straight streets (same rail/signal/support/pole pattern as the 1x1's
straight sections). Snap grid 364, same absolute offset as the 1x1, so it lines up with 1x1 blocks.
Input: third_party/empty-block.txt."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.fbp import *
from lib.rail_city_block import big_block

if __name__ == "__main__":
    src = decode(third_party("empty-block.txt").read_text())["blueprint"]
    save({"blueprint": big_block(src, 2)}, __file__)
