"""Module mall tier 1-2 (stackable cells): a family of stackable chest cells (lib/cells.py MODULE_MALL, lib/stack.py).
blueprint.txt = cap + one of each cell (early); variants = each cell and the cap per tier."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.cells import MODULE_MALL
from lib.stack_bp import write_family

RATES = {'advanced-circuit': 450, 'electronic-circuit': 450, 'processing-unit': 450}   # marker counts: a mall idles most of the time, so one yellow lane per input is plenty

if __name__ == "__main__":
    write_family(MODULE_MALL, __file__, RATES)
