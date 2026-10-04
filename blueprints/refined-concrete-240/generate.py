"""Refined concrete 240/min (4/s) from stone + iron ore + water (Factorio 2.0).
One long module (lib/refined_concrete.py): 14 concrete AM, 8 refined AM, 2 stick AM, 17 electric furnaces.
All inputs/outputs on the WEST edge."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.fbp import *
from lib.refined_concrete import module

bp = Blueprint("Refined concrete 240/min", game="2.0",
               description="West edge: y=-5 water, y=-3 iron ore, y=-2 stone (in) / y=11 refined concrete (out)")
module(bp, edge=-1)
bp.add_marker(-1, -6, {"water": 8700})
bp.add_marker(-1, -4, {"iron-ore": 264})
bp.add_marker(-1, -1, {"stone": 480})
bp.connect_poles()
save(bp, __file__)
