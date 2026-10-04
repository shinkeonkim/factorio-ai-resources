"""Every stackable cell in the repository (specs only; geometry and maths live in lib/stack.py).

inner = (far lane, near lane) of the belt next to the inserters, outer = the belt behind it (long-handed).
"far" is the lane away from the machines: lane makers drop there, so cap-fed items go on the near lane
whenever a maker shares the belt.
"""
from lib.stack import Cell

CELLS = {
    # --- science -----------------------------------------------------------------------------------------
    "red": Cell("Red science", ["automation-science-pack", "iron-gear-wheel", "automation-science-pack"],
                inner=("iron-plate", "copper-plate")),
    "green": Cell("Green science",
                  ["iron-gear-wheel", "transport-belt", "logistic-science-pack", "inserter", "logistic-science-pack"],
                  inner=("iron-gear-wheel", "iron-plate"), outer=("transport-belt", "electronic-circuit")),
    "military": Cell("Military science", ["military-science-pack"] * 3,
                     inner=("piercing-rounds-magazine", "grenade"), outer=("stone-wall", None)),
    "blue": Cell("Chemical science", ["chemical-science-pack"] * 3,
                 inner=("engine-unit", "advanced-circuit"), outer=("sulfur", None)),
    "purple": Cell("Production science", ["production-science-pack"] * 3,
                   inner=("rail", "electric-furnace"), outer=("productivity-module", None)),
    "yellow": Cell("Utility science", ["utility-science-pack"] * 3,
                   inner=("low-density-structure", "processing-unit"), outer=("flying-robot-frame", None)),
    # --- intermediates for the sciences above ------------------------------------------------------------
    "piercing": Cell("Piercing rounds", ["piercing-rounds-magazine", "firearm-magazine", "piercing-rounds-magazine"],
                     inner=("iron-plate", "copper-plate"), outer=("steel-plate", None)),
    "grenade": Cell("Grenades", ["grenade"] * 3, inner=("coal", "iron-plate")),
    "wall": Cell("Stone walls", ["stone-wall"], inner=("stone-brick", None)),
    "rail": Cell("Rails", ["rail", "iron-stick", "rail"], inner=("stone", "steel-plate"), outer=("iron-plate", None)),
    "electric-furnace": Cell("Electric furnaces", ["electric-furnace"] * 3,
                             inner=("steel-plate", "stone-brick"), outer=("advanced-circuit", None)),
    "productivity-module": Cell("Productivity modules", ["productivity-module"] * 3,
                                inner=("advanced-circuit", "electronic-circuit")),
    "robot-frame": Cell("Flying robot frames", ["flying-robot-frame"] * 3,
                        inner=("battery", "electronic-circuit"), outer=("electric-engine-unit", "steel-plate")),
}

# --- malls: products into chests (sink="chest"); each half has its own items; one lane set per mall --------
_MALL = dict(inner=("iron-gear-wheel", "iron-plate"), outer=("steel-plate", "electronic-circuit"), sink="chest")
MALL = [   # stack in this order: the first cell makes the gear lane for everything above it
    Cell("Mall: gears & belts", ["iron-gear-wheel", "transport-belt", "underground-belt"],
         east=["iron-gear-wheel", "transport-belt", "splitter"], **_MALL),
    Cell("Mall: inserters & assemblers", ["long-handed-inserter", "inserter", "fast-inserter"],
         east=["assembling-machine-2", "assembling-machine-1", "electric-mining-drill"], **_MALL),
    Cell("Mall: pipes & logistics", ["pipe", "pipe-to-ground", "radar"],
         east=["steel-chest", "repair-pack", "rail-signal"], **_MALL),
    Cell("Mall: trains & fluids", ["pipe", "engine-unit", "locomotive"],
         east=["storage-tank", "fluid-wagon", "pipe"], **_MALL),
]
_MOD = dict(inner=("advanced-circuit", "electronic-circuit"), outer=("processing-unit", None), sink="chest")
MODULE_MALL = [
    Cell("Modules: speed & efficiency", ["speed-module", "speed-module-2"],
         east=["efficiency-module", "efficiency-module-2"], **_MOD),
    Cell("Modules: productivity & quality", ["productivity-module", "productivity-module-2"],
         east=["quality-module", "quality-module-2"], **_MOD),
]
