"""Refined concrete 20/s (1200/min): 5 stacked copies of the 240/min module + west-side manifold.
Inputs (all fast belts):
  top-left:    x=-3 stone A (feeds modules 1-3, 24/s), x=-6 iron ore (all modules, 22/s), x=-8 water pipe
  bottom-left: x=-3 stone B (feeds modules 4-5, 16/s, flows north)
  output:      x=-11 bottom (refined concrete 20/s; modules 1-3 east lane, 4-5 west lane)"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.fbp import *
from lib.refined_concrete import module as _module

GROUPS, N_F, N_R, N_S, N_K = 7, 6, 8, 4, 2
MODULES, PITCH, STONE_A = 5, 19, 3
BELT, PIPE, PTG = "fast-transport-belt", "pipe", "pipe-to-ground"
UG, SPL = "fast-underground-belt", "fast-splitter"
AM, EF, FI, LI, POLE = "assembling-machine-2", "electric-furnace", "fast-inserter", "long-handed-inserter", "medium-electric-pole"

class Shifted:
    """Proxy that shifts every placement by dy (lets the module code stay in local coordinates)."""
    def __init__(self, bp, dy): self.bp, self.dy = bp, dy
    def add(self, name, x, y, *a, **k): return self.bp.add(name, x, y + self.dy, *a, **k)
    def belt_line(self, name, x, y, d, n): return self.bp.belt_line(name, x, y + self.dy, d, n)

def module(bp):
    _module(bp, GROUPS, N_F, N_R, N_S, N_K, edge=0)

bp = Blueprint("Refined concrete 1200/min", game="2.0",
               description="Top-left: stone A (x=-3), iron ore (x=-6), water (x=-8). Bottom-left: stone B (x=-3, north), output (x=-11, south).")
dys = [PITCH * k for k in range(MODULES)]
for dy in dys:
    module(Shifted(bp, dy))

TOP = -8
# ---- iron ore column x=-6 (south), splitter per module, branch under stone column ----
prev = TOP
for i, dy in enumerate(dys):
    bp.belt_line(BELT, -6, prev, S, dy - 4 - prev)
    bp.add(SPL, -6, dy - 4, S)
    bp.add(BELT, -5, dy - 3, E)                       # curve from splitter
    bp.underground(UG, -4, dy - 3, E, 2)              # under stone column + branch -> (-1, dy-3)
    prev = dy - 3
# ---- stone A column x=-3 (south) for modules 0..STONE_A-1 ----
prev = TOP
for dy in dys[:STONE_A]:
    bp.belt_line(BELT, -3, prev, S, dy - 6 - prev)
    bp.add(SPL, -3, dy - 6, S)
    bp.belt_line(BELT, -2, dy - 5, S, 3)
    bp.add(BELT, -2, dy - 2, E); bp.add(BELT, -1, dy - 2, E)   # curve into stone belt at x=0
    prev = dy - 5
# ---- stone B column x=-3 (north) for remaining modules, fed from the bottom ----
bottom = dys[-1] + 15
prev = bottom
for dy in reversed(dys[STONE_A:]):
    bp.belt_line(BELT, -3, prev, N, prev - (dy + 1))
    bp.add(SPL, -3, dy + 1, N)
    bp.add(BELT, -2, dy, N); bp.add(BELT, -2, dy - 1, N)
    bp.add(BELT, -2, dy - 2, E); bp.add(BELT, -1, dy - 2, E)
    prev = dy
# ---- water column x=-8, pipe-to-ground into each module's main ----
for y in range(TOP, dys[-1] - 4):
    bp.add(PIPE, -8, y)
for dy in dys:
    bp.add(PTG, -7, dy - 5, W); bp.add(PTG, -1, dy - 5, E)
# ---- output column x=-11 (south) ----
for i, dy in enumerate(dys):
    y = dy + 11
    bp.underground(UG, -1, y, W, 2)                   # -> exit (-4, y)
    bp.underground(UG, -5, y, W, 3)                   # -> exit (-9, y), under ore + water columns
    if i < STONE_A:
        bp.add(BELT, -10, y, W)                       # side-load onto east lane
    else:
        bp.underground(UG, -10, y, W, 1)              # under the output column -> (-12, y)
        bp.add(BELT, -13, y, N); bp.add(BELT, -13, y - 1, E); bp.add(BELT, -12, y - 1, E)  # west lane
bp.belt_line(BELT, -11, 10, S, bottom - 10 + 1)

# ---- input markers: constant combinators, signal = what to supply, count = per minute ----
n_a, n_b = STONE_A, MODULES - STONE_A
bp.add_marker(-2, TOP, {"stone": 8 * 60 * n_a})            # right of stone A belt start
bp.add_marker(-5, TOP, {"iron-ore": 4.4 * 60 * MODULES})   # right of iron ore belt start
bp.add_marker(-9, TOP, {"water": 145 * 60 * MODULES})      # left of water pipe start
bp.add_marker(-2, bottom, {"stone": 8 * 60 * n_b})         # right of stone B belt start (bottom)
for dy in dys[:-1]:
    bp.add(POLE, 35, dy + 12)                         # bridge pole to the next module
bp.connect_poles()
save(bp, __file__)
