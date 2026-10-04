"""Fulgora all-in-one complex: scrap -> recyclers + sorters, holmium, electrolyte, superconductors, supercapacitors,
electromagnetic science, rocket, mall, lightning power and protection, and a void for everything left over.

Numbers per electromagnetic science pack (EM plants and foundries +50 % productivity): ~0.93 holmium ore,
2.7 batteries, 1.8 green circuits -> about 93 scrap per pack, so 100 packs/min need ~155 scrap/s: four
scrap stacks of 16 recyclers (2.5 scrap/s each) = 160 scrap/s."""
from lib.complex import Stack
from lib.fbp import N, E, S, W
from lib.fstack import FluidCell, as_stack, analyse, TIERS as FT
from lib.planets.common import TRASH, recycle_sort_stack, rocket_stack, void_sink  # noqa: F401

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

LAYOUT = [
    {"kind": "solid", "lanes": ["scrap", "scrap", "scrap", "scrap", "holmium-ore", "battery"]},
    {"kind": "solid", "lanes": ["ice", "stone", "processing-unit", "advanced-circuit", "low-density-structure", "solid-fuel"]},
    {"kind": "solid", "lanes": ["concrete", "steel-plate", "iron-gear-wheel", "copper-cable", TRASH, "rocket-fuel"]},
    {"kind": "solid", "lanes": ["iron-plate", "copper-plate", "electronic-circuit", "plastic-bar", "holmium-plate", "superconductor"]},
    {"kind": "solid", "lanes": ["accumulator", "supercapacitor", "electromagnetic-science-pack", "iron-stick", "refined-concrete", None]},
    {"kind": "fluid", "lanes": ["heavy-oil", "heavy-oil", "water", "light-oil", "holmium-solution", "electrolyte"]},
]

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


def lightning_field(cols=4, rows=3, tier="mid"):
    """Lightning power + protection: tiles of 12x12, each a lightning collector (catches strikes within 25 tiles,
    stores 1 GJ, 40 % efficient), a substation and 34 accumulators (5 MJ each, 170 MJ per tile)."""
    def build(bp, t):
        for i in range(cols):
            for j in range(rows):
                x0, y0 = 12 * i, -12 * (j + 1) - 1
                bp.add("substation", x0 + 6, y0 + 6)
                bp.add("lightning-collector", x0, y0)
                for ax in range(0, 12, 2):
                    for ay in range(0, 12, 2):
                        if (ax, ay) in ((0, 0), (6, 6)):
                            continue
                        bp.add("accumulator", x0 + ax, y0 + ay)
        bp.add("medium-electric-pole", 6, 0)

    return Stack(f"Lightning power ({cols * rows} collectors, {cols * rows * 34} accumulators)", build, tier, [], {}, gap=4)


def stacks(tier="mid"):
    s = [lightning_field(tier=tier)]
    s += [scrap_stack(k + 1, tier) for k in range(4)]
    s += [as_stack(C[k], n, tier) for k, n in PLAN]
    s += [second_stack(tier)]
    s += [as_stack(C[k], n, tier) for k, n in PLAN2]
    s += [rocket_stack(["electromagnetic-science-pack", "holmium-plate", "supercapacitor", "superconductor"], tier=tier)]
    s += [void_sink(TRASH, 7, tier, "Void: overflow 1", 20.0), void_sink(TRASH, 7, tier, "Void: overflow 2", 20.0)]
    return s


POWER_KW = {"recycler": 180, "electromagnetic-plant": 2000, "foundry": 2500, "chemical-plant": 210,
            "assembling-machine-3": 375, "rocket-silo": 250, "roboport": 50, "fast-inserter": 46, "bulk-inserter": 79,
            "long-handed-inserter": 20}


def power_budget(bp):
    use = sum(POWER_KW.get(e["name"], 0) for e in bp.entities)
    store = sum(5 for e in bp.entities if e["name"] == "accumulator")          # MJ
    return use, store


LINES = PLAN + PLAN2
COVER = ("lightning-collector", 2, 36)       # lightning protection everywhere (collector range 25)
SPECIAL = [("Lightning power", "번개 수집기 12 + 축전지 408 (2 GJ) + 변전소", "12 lightning collectors + 408 accumulators (2 GJ) + substations"),
           ("Scrap recycling + sorting ×4", "재활용기 16대씩(고철 초당 40), 12종 분류 + 넘침 줄", "16 recyclers each (40 scrap/s), sorts 12 items + an overflow lane"),
           ("Secondary recycling", "톱니→철, 구리선→구리, 파랑 회로→초록 회로, LDS→플라스틱", "gears→iron, cable→copper, blue→green circuits, LDS→plastic"),
           ("Rocket silo", "로켓 부품(고철의 파랑 회로·LDS + 로켓 연료) + 수출 상자", "rocket parts (blue circuits and LDS from scrap + rocket fuel) + export chests"),
           ("Void ×2", "넘침 줄의 모든 것을 재활용기로 없앰", "recyclers destroy everything on the overflow lane"),
           ("Lightning cover", "단지 전체에 번개 수집기를 36칸 간격으로 (보호 반경 25)", "lightning collectors every 36 tiles over the whole complex (range 25)")]


def power_line(bp, lang):
    use, store = power_budget(bp)
    return (f"최대 전력 {use / 1000:,.0f} MW, 축전지 {store:,} MJ (번개는 폭풍 때만 들어옴)." if lang == "ko"
            else f"Peak power {use / 1000:,.0f} MW, accumulators {store:,} MJ (lightning arrives only in storms).")
