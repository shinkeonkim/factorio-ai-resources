"""Gleba all-in-one complex, robot-fed: everything here spoils, so no item sits on a belt. Every machine has a
requester chest (inputs, plus nutrients to burn in biochambers) and a passive provider chest (outputs, spoilage
included); logistic robots do all the item moving. Only water comes in pipes.

Spoilage is fuel (250 kJ), so the heating towers that power the complex are also its spoilage sink. Pentapod
eggs hatch into enemies when they spoil (15 min): the egg machines only take inputs while the network holds
fewer than 40 eggs, so eggs never pile up.

Sized for ~600 agricultural science/min: one science biochamber makes 0.75 packs/s (4 s, speed 2, +50 %)."""
from lib.complex import Stack
from lib.fbp import N, E, S, W
from lib.fstack import FluidCell, as_stack, TIERS as FT

BUS_TIER = "blue"
NUT = "nutrients"


def _bio(name, recipe, n, **kw):
    return FluidCell(name, recipe, "biochamber", n=n, bots=True, fuel=NUT, **kw)


C = {
    "yumako-processing": _bio("Yumako processing", "yumako-processing", 3),
    "jellynut-processing": _bio("Jellynut processing", "jellynut-processing", 1),
    "bioflux": _bio("Bioflux", "bioflux", 3),
    "nutrients": _bio("Nutrients", "nutrients-from-bioflux", 1),
    "eggs": _bio("Pentapod eggs", "pentapod-egg", 3, limit=("pentapod-egg", 40)),
    "science": _bio("Agricultural science", "agricultural-science-pack", 2),
    "iron-bacteria": _bio("Iron bacteria", "iron-bacteria", 1),
    "iron-cultivation": _bio("Iron bacteria cultivation", "iron-bacteria-cultivation", 2),
    "iron-plate": FluidCell("Iron plates (bacteria ore)", "iron-plate", "electric-furnace", n=2, bots=True),
    "magazine": FluidCell("Firearm magazines", "firearm-magazine", "assembling-machine-3", n=1, bots=True),
    "carbon": _bio("Carbon (burnt spoilage)", "burnt-spoilage", 2),
    "carbon-fiber": _bio("Carbon fiber", "carbon-fiber", 2),
    "rocket-fuel": _bio("Rocket fuel (jelly)", "rocket-fuel-from-jelly", 2),
}

SCALE = 2           # the line counts below are for ~300 agricultural science/min; the base builds twice that
LINES = [(k, n * SCALE) for k, n in [
    ("yumako-processing", 1), ("jellynut-processing", 1), ("bioflux", 1), ("nutrients", 1), ("eggs", 2),
    ("science", 2), ("iron-bacteria", 1), ("iron-cultivation", 1), ("iron-plate", 1), ("magazine", 1),
    ("carbon", 1), ("carbon-fiber", 1), ("rocket-fuel", 1)]]


def power_stack(units=2, tier="mid"):
    """Heating towers -> heat exchangers -> steam turbines, stacked. One unit: a heating tower (burns spoilage and
    jellynut from a requester chest), a heat-pipe row under 4 heat exchangers (water passes from one exchanger to
    the next), two turbines on each exchanger. Water comes up the main on the east edge.
    Self-starting (base-design.md §7): the fuel goes in through a burner inserter (it needs no electricity, so a
    dead base restarts as soon as fuel arrives), enabled only while the accumulator beside it is below 90 %."""
    def build(bp, t):
        f = FT[t]
        main = 20
        P = 14
        for y in range(0, 8):
            bp.add("pipe", main, y)
        bp.add_marker(main, 8, {"water": 0})
        bp.add(f["pole"], 2, 0)
        for k in range(units):
            yh = -2 - P * k                                     # heat-pipe row
            for y in range(yh - P + 2, yh + 2):
                bp.add("pipe", main, y)
            bp.add("heating-tower", 0, yh - 1)
            ins = bp.add("burner-inserter", -1, yh, W, control_behavior={          # fuel from the chest west of it
                "circuit_enabled": True, "circuit_condition": {
                    "first_signal": {"type": "virtual", "name": "signal-A"}, "constant": 90, "comparator": "<"}})
            acc = bp.add("accumulator", -3, yh - 3, control_behavior={"output_signal": {"type": "virtual", "name": "signal-A"}})
            bp.wire(acc, ins, "red")
            bp.add("requester-chest", -2, yh, request_filters={"sections": [{"index": 1, "filters": [
                {"index": 1, "name": "spoilage", "quality": "normal", "comparator": "=", "count": 200},
                {"index": 2, "name": "jellynut", "quality": "normal", "comparator": "=", "count": 50}]}]})
            for x in range(3, main - 1):
                bp.add("heat-pipe", x, yh)
            for j in range(4):
                ex = 3 + 4 * j
                bp.add("heat-exchanger", ex, yh - 2, N)          # 3x2, heat in at the bottom centre
                bp.add("steam-turbine", ex, yh - 7, N)
                bp.add("steam-turbine", ex, yh - 12, N)
                gx = ex + 3                                      # gap column: water link + poles
                bp.add("pipe", gx, yh - 1)
                bp.add(f["pole"], gx, yh - 4); bp.add(f["pole"], gx, yh - 10)
            bp.add(f["pole"], 1, yh - 3)

    return Stack(f"Power: {units} heating towers, {8 * units} turbines", build, tier, [], {"water": 103.0 * 4 * units}, gap=4)   # 103 water/s per exchanger


def rocket_stack(tier="mid"):
    """Rocket silo fed by robots (requester chests for its three ingredients); its cargo requests take the
    exports (agricultural science, bioflux, carbon fiber) straight from the network."""
    def build(bp, t):
        f = FT[t]
        bp.add("rocket-silo", 0, -12)
        for k, item in enumerate(["processing-unit", "low-density-structure", "rocket-fuel"]):
            x = 1 + 3 * k
            bp.add(f["ins"], x, -3, S)
            bp.add("requester-chest", x, -2, request_filters={"sections": [{"index": 1, "filters": [
                {"index": 1, "name": item, "quality": "normal", "comparator": "=", "count": 20}]}]})
        bp.add(f["pole"], 2, -2); bp.add(f["pole"], 10, -4)
        bp.add("roboport", 11, -10)
    return Stack("Rocket silo (robot-fed)", build, tier, [], {}, gap=4)


def farm_tile(tower_seed="yumako-seed", tier="mid"):
    """One agricultural tower (plants within 3 growth cells = 21x21 tiles): seeds from a requester chest, harvest
    into a passive provider chest. Place it on yumako (or jellynut) soil inside the robot network; tile every 22."""
    def build(bp, t):
        f = FT[t]
        bp.add("agricultural-tower", 0, 0)
        bp.add(f["ins"], 3, 1, W)                               # harvest -> provider (picks from the tower)
        bp.add("passive-provider-chest", 4, 1)
        bp.add(f["ins"], -1, 1, W)                              # seeds -> tower (picks from the chest)
        bp.add("requester-chest", -2, 1, request_filters={"sections": [{"index": 1, "filters": [
            {"index": 1, "name": tower_seed, "quality": "normal", "comparator": "=", "count": 10}]}]})
        bp.add(f["pole"], 1, 3)
    return Stack(f"Farm tile ({tower_seed.split('-')[0]})", build, tier, [], {})


def pad_stack(imports=("processing-unit", "low-density-structure"), tier="mid"):
    """Cargo landing pad in the robot network: it requests the imports from orbit and robots take them from it."""
    def build(bp, t):
        bp.add("cargo-landing-pad", 0, -10, request_filters={"sections": [{"index": 1, "filters": [
            {"index": k + 1, "name": it, "quality": "normal", "comparator": "=", "count": 200}
            for k, it in enumerate(imports)]}]})
        bp.add("roboport", 9, -8)
        bp.add(FT[t]["pole"], 8, -3)
    return Stack("Landing pad (robot network)", build, tier, [], {}, gap=4)


POWER_KW = {"biochamber": 500, "electric-furnace": 180, "assembling-machine-3": 375, "rocket-silo": 250,
            "roboport": 50, "fast-inserter": 46, "bulk-inserter": 79, "agricultural-tower": 200}


def power_budget(bp):
    use = sum(POWER_KW.get(e["name"], 0) for e in bp.entities)
    gen = sum(5820 for e in bp.entities if e["name"] == "steam-turbine")
    return use, gen


def power_line(bp, lang):
    use, gen = power_budget(bp)
    return (f"최대 전력 {use / 1000:,.0f} MW / 터빈 {gen / 1000:,.0f} MW (가열탑 연료가 충분할 때)." if lang == "ko"
            else f"Peak power {use / 1000:,.0f} MW / turbines {gen / 1000:,.0f} MW (with enough heating-tower fuel).")


SPECIAL = [("Power ×2", "가열탑 2기 → 열교환기 8 → 터빈 16씩 (연료: 부패물·젤리넛)", "2 heating towers → 8 heat exchangers → 16 turbines each (fuel: spoilage, jellynut)"),
           ("Rocket silo", "로봇이 재료를 넣는 사일로; 수출은 화물 요청으로", "robot-fed silo; exports via its cargo requests"),
           ("Landing pad", "파랑 회로·LDS 수입", "imports blue circuits and LDS"),
           ("Defence ring", "돌벽 2겹 + 4칸마다 레이저 포탑, 세 번째마다 기관총 포탑(탄창 요청 상자)", "two rows of stone wall + a laser turret every 4 tiles, every third a gun turret with a magazine requester")]


# ------------------------------------------------------------------------------------- the base (lib/base)
HEIGHT = 34


def islands():
    from lib.base import Island
    L = dict(LINES)
    cells = lambda *keys: [(C[k], L[k]) for k in keys]
    return [
        Island("Fruit processing", cells("yumako-processing", "jellynut-processing", "bioflux", "nutrients")),
        Island("Eggs and science", cells("eggs", "science")),
        Island("Bacteria iron", cells("iron-bacteria", "iron-cultivation", "iron-plate", "magazine")),
        Island("Carbon and fuel", cells("carbon", "carbon-fiber", "rocket-fuel")),
        Island("Power", [], extra=[lambda t: power_stack(tier=t)] * SCALE),
        Island("Rocket", [], extra=[rocket_stack, lambda t: pad_stack(tier=t)]),
    ]


def controls(bp):
    from lib.base import power_alarm
    acc = next(e["entity_number"] for e in bp.entities if e["name"] == "accumulator")
    return power_alarm(bp, acc, "Gleba base: power low (heating towers need spoilage / jellynut)")


def base(label="Gleba all-in-one", tier="mid"):
    """Dense rectangle inside two rows of land mines, two rows of stone wall and a turret row (laser turrets, gun
    turrets on magazine requesters); robot-fed cells grouped by island, heating-tower power that restarts by itself,
    silo and landing pad inside. Water enters from the west per shelf (offshore pumps)."""
    from lib.base import build_base, defence_frame
    return build_base(label, islands(), HEIGHT, frame=defence_frame(mines=2), tier="blue", controls=controls)
