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
