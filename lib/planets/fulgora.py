"""Fulgora all-in-one complex: scrap -> recyclers + sorters, holmium, electrolyte, superconductors, supercapacitors,
electromagnetic science, rocket, mall, lightning power and protection, and a void for everything left over.

Numbers per electromagnetic science pack (EM plants and foundries +50 % productivity): ~0.93 holmium ore,
2.7 batteries, 1.8 green circuits -> about 93 scrap per pack, so 100 packs/min need ~155 scrap/s: four
scrap stacks of 16 recyclers (2.5 scrap/s each) = 160 scrap/s."""
import dataclasses
import math

from lib.complex import Stack
from lib.fbp import N, E, S, W
from lib.fstack import FluidCell, as_stack, analyse, TIERS as FT
from lib.planets.common import TRASH, recycle_sort_stack, void_sink

BUS_TIER = "blue"
SCRAP_PER_STACK = 40.0          # 16 recyclers x 2.5 scrap/s
SCRAP_OUT = {"iron-gear-wheel": 0.2, "solid-fuel": 0.07, "concrete": 0.06, "ice": 0.05, "steel-plate": 0.04,
             "battery": 0.04, "stone": 0.04, "advanced-circuit": 0.03, "copper-cable": 0.03, "processing-unit": 0.02,
             "low-density-structure": 0.01, "holmium-ore": 0.01}

C = {
    "water": FluidCell("Water (ice melting)", "ice-melting", "chemical-plant", n=2, inner=(None, "ice")),
    "light-oil": FluidCell("Light oil (heavy oil cracking)", "heavy-oil-cracking", "chemical-plant", n=1),
    "holmium-solution": FluidCell("Holmium solution", "holmium-solution", "chemical-plant", n=3,
                                  inner=("stone", "holmium-ore")),
    "holmium-plate": FluidCell("Holmium plate", "holmium-plate", "foundry", n=1),
    "electrolyte": FluidCell("Electrolyte", "electrolyte", "electromagnetic-plant", n=2, inner=(None, "stone")),
    "rocket-fuel": FluidCell("Rocket fuel", "rocket-fuel", "assembling-machine-3", n=2, inner=(None, "solid-fuel")),
    "superconductor": FluidCell("Superconductor", "superconductor", "electromagnetic-plant", n=2,
                                inner=("holmium-plate", "copper-plate"), outer=("plastic-bar", None)),
    "accumulator": FluidCell("Accumulator", "accumulator", "electromagnetic-plant", n=2, inner=("battery", "iron-plate")),
    "supercapacitor": FluidCell("Supercapacitor", "supercapacitor", "electromagnetic-plant", n=2,
                                inner=("holmium-plate", "superconductor"), outer=("electronic-circuit", "battery")),
    "science": FluidCell("Electromagnetic science", "electromagnetic-science-pack", "electromagnetic-plant", n=2,
                         inner=("supercapacitor", "accumulator")),
    # mall (passive provider chests)
    "mall-em-plant": FluidCell("Mall: electromagnetic plant", "electromagnetic-plant", "electromagnetic-plant", n=1,
                               sink="chest", inner=("holmium-plate", "steel-plate"), outer=("processing-unit", "refined-concrete")),
    "iron-stick": FluidCell("Iron sticks", "iron-stick", "assembling-machine-3", n=1, inner=(None, "iron-plate")),
    "refined-concrete": FluidCell("Refined concrete", "refined-concrete", "assembling-machine-3", n=2,
                                  inner=("concrete", "iron-stick"), outer=("steel-plate", None)),
}

SCRAP_SORT = [("holmium-ore", 1), ("battery", 2), ("processing-unit", 1), ("advanced-circuit", 1),
              ("low-density-structure", 1), ("ice", 2), ("stone", 1), ("steel-plate", 1), ("copper-cable", 1),
              ("iron-gear-wheel", 3), ("solid-fuel", 2), ("concrete", 2)]
SECOND_SORT = [("iron-plate", 2), ("copper-plate", 2), ("electronic-circuit", 3), ("plastic-bar", 1),
               ("advanced-circuit", 1), ("steel-plate", 1)]

PLAN = [("water", 1), ("light-oil", 1), ("holmium-solution", 2), ("holmium-plate", 1), ("electrolyte", 2),
        ("rocket-fuel", 1)]
PLAN2 = [("superconductor", 1), ("accumulator", 1), ("supercapacitor", 1), ("science", 2),
         ("iron-stick", 1), ("refined-concrete", 1), ("mall-em-plant", 1)]


def scrap_stack(k, tier="mid"):
    rate = {"scrap": SCRAP_PER_STACK / 2} | {i: SCRAP_PER_STACK * p for i, p in SCRAP_OUT.items()} | {TRASH: 10.0}
    return recycle_sort_stack(f"Scrap recycling + sorting {k}", ["scrap", "scrap"], SCRAP_SORT, 16, tier, rate)


def second_stack(tier="mid"):
    """Gears -> iron, copper cable -> copper, blue circuits -> green (+ red), LDS -> plastic (+ steel, copper)."""
    rate = {"iron-gear-wheel": 6.0, "copper-cable": 3.0, "processing-unit": 1.0, "low-density-structure": 0.5,
            "iron-plate": 6.0, "copper-plate": 2.0, "electronic-circuit": 5.0, "plastic-bar": 0.6,
            "advanced-circuit": 0.5, "steel-plate": 0.3, TRASH: 2.0}
    return recycle_sort_stack("Secondary recycling (iron, copper, green circuits, plastic)",
                              ["iron-gear-wheel", "copper-cable", "processing-unit", "low-density-structure"],
                              SECOND_SORT, 8, tier, rate)


POWER_KW = {"recycler": 180, "electromagnetic-plant": 2000, "foundry": 2500, "chemical-plant": 210,
            "assembling-machine-3": 375, "rocket-silo": 250, "roboport": 50, "fast-inserter": 46, "bulk-inserter": 79,
            "long-handed-inserter": 20}


def power_budget(bp):
    use = sum(POWER_KW.get(e["name"], 0) for e in bp.entities)
    store = sum(5 for e in bp.entities if e["name"] == "accumulator")          # MJ
    return use, store


LINES = PLAN + PLAN2
SPECIAL = [("Scrap shelves ×2", "재활용기 16대 + 12종 분류 블록 2개씩, 고철 초당 80 (서쪽 벨트로 입력)", "two blocks of 16 recyclers + 12-item sorter each, 80 scrap/s (belts from the west)"),
           ("Secondary recycling", "톱니→철, 구리선→구리, 파랑 회로→초록 회로, LDS→플라스틱", "gears→iron, cable→copper, blue→green circuits, LDS→plastic"),
           ("Voids ×4", "넘침 벨트의 모든 것을 재활용기로 없앰", "recyclers destroy everything on the overflow belts"),
           ("Rocket silo", "로봇이 재료를 넣는 사일로; 수출은 화물 요청으로", "robot-fed silo; exports via its cargo requests"),
           ("Lightning band", "단지 둘레 12×12 타일마다 번개 수집기 + 변전소 + 축전지 34 (170 MJ)", "around the base, each 12×12 tile: lightning collector + substation + 34 accumulators (170 MJ)"),
           ("Lightning cover", "코어 안에도 번개 수집기를 36칸 간격으로", "lightning collectors every 36 tiles inside the core too")]


def power_line(bp, lang):
    use, store = power_budget(bp)
    return (f"최대 전력 {use / 1000:,.0f} MW, 축전지 {store:,} MJ (번개는 폭풍 때만 들어옴)." if lang == "ko"
            else f"Peak power {use / 1000:,.0f} MW, accumulators {store:,} MJ (lightning arrives only in storms).")


# ------------------------------------------------------------------------------------- the base (lib/base)
HEIGHT = (24, 30, 36, 44, 52)
EXPORTS = ("electromagnetic-science-pack", "holmium-plate", "supercapacitor", "superconductor")


def bot(key):
    """robot-fed version of a cell (requester / provider chests at each machine, no belt columns)"""
    return dataclasses.replace(C[key], bots=True, inner=(None, None), outer=None)


def overflow_voids(rate, n, tier="mid"):
    per_side = max(2, math.ceil(rate / 16) + 1)
    return [void_sink(TRASH, per_side, tier, f"Void: overflow ({rate:.0f}/s)", rate) for _ in range(n)]


def islands():
    """Scrap island (belts: scrap in, sorted items to provider chests, leftovers into voids; gears and cable go
    straight into the secondary recycler on short belts) and the electromagnetic island, which makes its own water,
    light oil, holmium solution and electrolyte next to the lines that use them."""
    from lib.base import Island
    from lib.planets.common import robot_silo
    em = [("water", 1), ("light-oil", 1), ("holmium-solution", 2), ("holmium-plate", 1), ("electrolyte", 2),
          ("rocket-fuel", 1), ("superconductor", 1), ("accumulator", 1), ("supercapacitor", 1), ("science", 2),
          ("iron-stick", 1), ("refined-concrete", 1), ("mall-em-plant", 1)]
    return [
        Island("Scrap", [], extra=[lambda t, k=k: scrap_stack(k, t) for k in (1, 2, 3, 4)] + [second_stack],
               raw=("scrap",), waste=(TRASH, overflow_voids)),
        Island("Electromagnetic", [(bot(k) if C[k].items_in else C[k], n) for k, n in em]),
        Island("Rocket", [], extra=[robot_silo]),
    ]


def controls(bp):
    from lib.base import power_alarm
    acc = next(e["entity_number"] for e in bp.entities if e["name"] == "accumulator")
    return power_alarm(bp, acc, "Fulgora base: accumulators low (no storm lately?)")


def base(label="Fulgora all-in-one", tier="mid"):
    """Dense rectangle wrapped in a band of lightning tiles (collector + substation + 34 accumulators each) with
    more collectors over the core. Scrap belts and heavy oil enter from the west of their shelves; robots carry
    items between blocks; every sorted output stops at about two minutes of stock, the rest overflows into voids."""
    from lib.base import build_base, field_frame
    return build_base(label, islands(), HEIGHT, frame=field_frame(), tier="blue", controls=controls)
