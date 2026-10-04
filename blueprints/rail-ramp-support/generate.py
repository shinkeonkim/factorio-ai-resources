"""Rail ramps & supports as a stackable chest cell (lib/cells.py RAMPS, lib/stack.py).
blueprint.txt = cap + one cell (early); variants = the cell and the cap per tier."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.cells import RAMPS
from lib.stack_bp import write_family

RATES = {"steel-plate": 450, "refined-concrete": 450, "rail": 450}   # chest cell: one yellow lane each is plenty

if __name__ == "__main__":
    write_family(RAMPS, __file__, RATES)
