"""Upgradeable mall (stackable cells): a family of stackable chest cells (lib/cells.py MALL, lib/stack.py).
blueprint.txt = cap + one of each cell (early); variants = each cell and the cap per tier."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.cells import MALL
from lib.stack_bp import write_family

RATES = {'iron-plate': 450, 'steel-plate': 450, 'electronic-circuit': 450}   # marker counts: a mall idles most of the time, so one yellow lane per input is plenty

if __name__ == "__main__":
    write_family(MALL, __file__, RATES)
