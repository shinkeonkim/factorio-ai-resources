"""Flying robot frames: stackable cell (see lib/cells.py["robot-frame"] and lib/stack.py).
blueprint.txt = cap + 3 cells (early); variants = one cell and the cap per tier."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.cells import CELLS
from lib.stack_bp import write_all

if __name__ == "__main__":
    write_all(CELLS["robot-frame"], __file__)
