"""Stackable production cells (the house standard, modelled on the Nilaus green-circuit module).

A cell has a fixed width and a fixed period P (rows). Input belts run north along both edges, the product
belt runs south down the middle; every line enters at the bottom edge and leaves at the top edge in the same
column. Paste the same cell P rows further north and production grows until an input lane runs out.
A cap (base piece) sits under the lowest cell: it turns bus taps into the right belt lanes and lets the
product leave to the south.

Cell layout (west half; the east half is the mirror image around the centre column c):

    x = c-7  outer belt (N)   picked by long-handed inserters (low-rate items, or lane-maker products)
    x = c-6  inner belt (N)   picked by normal inserters
    x = c-5  inserters        row y: inner -> machine, row y+1: machine -> lane, row y+2: outer -> machine
    x = c-4..c-2  machines    one column, 3x3, pitch 4 rows (row 0, 4, 8 … of the cell are gap rows)
    x = c-1  output inserter  machine -> centre belt (only for the cell's product)
    x = c    centre belt (S)  the product

Gap rows hold small/medium poles at c-5, c-1, c+5 and, at c-3, a hand-over inserter that passes an
intermediate straight to the machine above or below. A *lane maker* is a machine whose product goes onto a
belt lane (always the lane away from the machines) so machines further north can take it.

`Cell` is pure data; `build_cell`, `build_cap` and `analyse` do the geometry and the ratio maths, so every
factory in the repository follows the same rules.
"""
from __future__ import annotations

import json
import math
import pathlib
from dataclasses import dataclass, field

from lib.fbp import N, E, S, W

ROOT = pathlib.Path(__file__).resolve().parents[1]
_DATA = ROOT / "skills" / "factorio-blueprint" / "data"
RECIPES = {**json.loads((_DATA / "recipes-space-age.json").read_text())["recipes"],   # quality modules etc.
           **json.loads((_DATA / "recipes-base.json").read_text())["recipes"]}          # base wins where both exist
SPEED = {"assembling-machine-1": 0.5, "assembling-machine-2": 0.75, "assembling-machine-3": 1.25,
         "electric-furnace": 2.0, "steel-furnace": 2.0, "stone-furnace": 1.0, "chemical-plant": 1.0}
LANE = {"transport-belt": 7.5, "fast-transport-belt": 15.0, "express-transport-belt": 22.5,
        "turbo-transport-belt": 30.0}
INSERTER = {"inserter": 0.83, "fast-inserter": 2.31, "bulk-inserter": 2.31, "long-handed-inserter": 1.2}
LH = "long-handed-inserter"

TIERS = {
    "early": dict(belt="transport-belt", ug="underground-belt", am="assembling-machine-1", ins="inserter",
                  pole="small-electric-pole", label={"ko": "초반 (노랑·조립기 1·일반)", "en": "early (yellow, AM1, basic)"}),
    "mid": dict(belt="fast-transport-belt", ug="fast-underground-belt", am="assembling-machine-2",
                ins="fast-inserter", pole="medium-electric-pole",
                label={"ko": "중반 (빨강·조립기 2·고속)", "en": "mid (red, AM2, fast)"}),
    "late": dict(belt="express-transport-belt", ug="express-underground-belt", am="assembling-machine-3",
                 ins="bulk-inserter", pole="medium-electric-pole",
                 label={"ko": "후반 (파랑·조립기 3·벌크)", "en": "late (blue, AM3, bulk)"}),
}


@dataclass
class Cell:
    name: str
    column: list[str]                       # recipes, south -> north (one machine each, both sides)
    inner: tuple                            # (far lane, near lane) item names, None = empty
    outer: tuple | None = None              # same for the outer belt, None = no outer belt
    product: str | None = None              # defaults to the last recipe's result
    machine: dict = field(default_factory=dict)   # recipe -> entity override (e.g. electric-furnace)
    east: list | None = None                # east half's column if it differs (malls); same length as column
    sink: str = "belt"                      # "belt": product onto the centre belt; "chest": every product into a
                                            # chest in the centre column (malls), neighbours may still take it
    water: bool = False                     # water mains at d=10 on both edges; see build_cell
    facing: list | None = None              # per machine (south -> north) N/S; fluid machines that share a water
                                            # row face each other (lower one N, upper one S)

    def half(self, side):
        """This cell as seen from one half (side = -1 west, +1 east)."""
        if side < 0 or not self.east:
            return self
        import dataclasses
        return dataclasses.replace(self, column=list(self.east), east=None)

    @property
    def period(self):
        return 4 * len(self.column)

    @property
    def c(self):
        return 10 if self.water else 7 if self.outer else 6

    @property
    def width(self):
        return 2 * self.c + 1

    def out_item(self, recipe):
        return RECIPES[recipe]["results"][0]["name"]

    @property
    def final(self):
        return self.product or self.out_item(self.column[-1])

    def lanes(self):
        """item -> ('inner'|'outer', 'far'|'near')"""
        out = {}
        for belt, pair in (("inner", self.inner), ("outer", self.outer)):
            if pair:
                for side, item in zip(("far", "near"), pair):
                    if item:
                        out[item] = (belt, side)
        return out

    def makers(self):
        """lane items produced inside the cell"""
        made = {self.out_item(r) for r in self.column + (self.east or [])}
        return {i for i in self.lanes() if i in made}

    def cap_items(self):
        return {i: v for i, v in self.lanes().items() if i not in self.makers()}


def _ingredients(recipe):
    return {x["name"]: x["amount"] for x in RECIPES[recipe]["ingredients"] if x.get("type", "item") == "item"}


def plan(cell: Cell):
    """Per machine: which inserter groups it needs. Raises if an ingredient has no source."""
    lanes = cell.lanes()
    col = cell.column
    jobs = []
    for k, r in enumerate(col):
        j = {"recipe": r, "roles": []}
        for item in _ingredients(r):
            if item in lanes:
                role = lanes[item][0]                       # "inner" / "outer"
                if role not in j["roles"]:
                    j["roles"].append(role)
            elif not [n for n in (k - 1, k + 1) if 0 <= n < len(col) and cell.out_item(col[n]) == item]:
                raise ValueError(f"{cell.name}: {r} needs {item}: not on a lane and no neighbour makes it")
        prod = cell.out_item(r)
        users = [n for n in (k - 1, k + 1) if 0 <= n < len(col) and prod in _ingredients(col[n])]
        if prod in lanes:
            j["roles"].append("lane_" + lanes[prod][0])
        elif cell.sink == "chest":
            j["roles"].append("chest")
            j["roles"] += [("hand", n) for n in users]
        elif prod == cell.final:
            j["roles"].append("centre")
        else:
            if not users:
                raise ValueError(f"{cell.name}: nobody takes {prod} from machine {k}")
            j["roles"] += [("hand", n) for n in users]
        jobs.append(j)
    return jobs


def machine_for(cell, recipe, tier):
    """Entity for a recipe at a tier: per-recipe override, else the tier's assembler — but fluid recipes
    need at least assembling-machine-2."""
    ent = cell.machine.get(recipe, TIERS[tier]["am"])
    if ent == "assembling-machine-1" and "crafting-with-fluid" in RECIPES[recipe].get("categories", []):
        ent = "assembling-machine-2"
    return ent


def water_rows(cell):
    """Gap-row indices k (between machine k and k+1) that carry water: lower machine faces N, upper faces S."""
    f = cell.facing or [N] * len(cell.column)
    return [k for k in range(len(cell.column) - 1) if f[k] == N and f[k + 1] == S] if cell.water else []


def _rate(cell, tier):
    return [SPEED[machine_for(cell, r, tier)] / RECIPES[r]["energy_required"] for r in cell.column]


def _role_load(cell, tier, k, role):
    """items/s through inserter group `role` of machine k when the machine it limits runs at 100 %."""
    col, rate, lanes = cell.column, _rate(cell, tier), cell.lanes()
    r = col[k]
    if role in ("inner", "outer"):
        return rate[k] * sum(a for i, a in _ingredients(r).items() if lanes.get(i, ("",))[0] == role)
    if role in ("centre", "chest") or str(role).startswith("lane_"):
        return rate[k] * RECIPES[r]["results"][0]["amount"]
    n = role[1]                                             # hand-over: limited by the consumer n
    return rate[n] * _ingredients(col[n])[cell.out_item(r)]


def _role_cap(tier, role):
    t = TIERS[tier]
    return INSERTER[LH] if role in ("outer", "lane_outer") else INSERTER[t["ins"]]


def _solve(cell, tier, counts=None):
    """Machine utilisation: finals as fast as possible, intermediates follow demand, everything capped by
    its inserters (counts) when given."""
    col, rate = cell.column, _rate(cell, tier)
    amt = lambda k: RECIPES[col[k]]["results"][0]["amount"]
    jobs = plan(cell)
    limit = [1.0] * len(col)
    if counts:
        for k, j in enumerate(jobs):
            for role in j["roles"]:
                load = _role_load(cell, tier, k, role)
                if load <= 0:
                    continue
                allowed = counts[k][str(role)] * _role_cap(tier, role) / load
                target = role[1] if isinstance(role, tuple) else k
                limit[target] = min(limit[target], allowed)
    if cell.sink == "chest":                               # malls: size every machine for running flat out
        finals = [k for k, j in enumerate(jobs) if "chest" in j["roles"]]
    else:
        finals = [k for k, r in enumerate(col) if cell.out_item(r) == cell.final]
    util = [limit[k] if k in finals else 0.0 for k in range(len(col))]
    for _ in range(30):
        need = {}
        for k, u in enumerate(util):
            for item, a in _ingredients(col[k]).items():
                need[item] = need.get(item, 0) + rate[k] * u * a
        scale = 1.0
        for item, d in need.items():
            prod = [k for k in range(len(col)) if cell.out_item(col[k]) == item]
            if not prod or d <= 0:
                continue
            per = sum(rate[k] * amt(k) * limit[k] for k in prod)
            for k in prod:
                util[k] = min(limit[k], d / sum(rate[q] * amt(q) for q in prod))
            if d > per * 1.0001:
                scale = min(scale, per / d)
        for k in finals:
            util[k] = min(limit[k], util[k] * scale)
    return util


def counts(cell: Cell):
    """Inserters per group (max over tiers of load / capacity, rounded up), clamped to the free slots:
    3 rows beside the machine on the belt side (inner + outer + lane output), 3 at the centre column,
    3 in a gap row for a hand-over."""
    jobs = plan(cell)
    want = [{} for _ in cell.column]
    for tier in TIERS:
        util = _solve(cell, tier)
        for k, j in enumerate(jobs):
            for role in j["roles"]:
                target = role[1] if isinstance(role, tuple) else k
                load = _role_load(cell, tier, k, role) * util[target]
                n = max(1, math.ceil(load / _role_cap(tier, role) - 1e-9))
                want[k][str(role)] = max(want[k].get(str(role), 1), n)
    import itertools
    for k, w in enumerate(want):
        side = [r for r in w if r in ("inner", "outer", "lane_inner", "lane_outer")]
        if sum(w[r] for r in side) > 3:                          # best split of the 3 belt-side slots
            best = max((combo for combo in itertools.product(range(1, 4), repeat=len(side)) if sum(combo) <= 3),
                       key=lambda combo: min(n / w[r] for n, r in zip(combo, side)))
            for n, r in zip(best, side):
                w[r] = n
        for r in w:
            w[r] = min(w[r], 3)
    return want


def build_cell(bp, cell: Cell, tier: str, y0: int):
    """Place one cell with its top row at y0 (rows y0 .. y0+P-1)."""
    t = TIERS[tier]
    c, P = cell.c, cell.period
    gap_used = set()
    chest = {"early": "iron-chest", "mid": "iron-chest", "late": "passive-provider-chest"}[tier]
    for sgn in (-1, 1):                                          # west half, then the mirrored east half
        half = cell.half(sgn)
        if len(half.column) != len(cell.column):
            raise ValueError(f"{cell.name}: both halves need the same number of machines")
        jobs, cnt = plan(half), counts(half)
        X = lambda d: c + sgn * d                                # d = distance from the centre
        from_out, from_in = (W, E) if sgn < 0 else (E, W)        # inserter picks from the outer / inner side
        for y in range(y0, y0 + P):
            bp.add(t["belt"], X(6), y, N)
            if cell.outer:
                bp.add(t["belt"], X(7), y, N)
        for k, j in enumerate(jobs):
            top = y0 + P - 3 - 4 * k                             # machine rows top .. top+2
            r = j["recipe"]
            ent = machine_for(cell, r, tier)
            face = (cell.facing or [N] * len(cell.column))[k]
            bp.add(ent, X(4) if sgn < 0 else X(2), top, face, **({} if "furnace" in ent else {"recipe": r}))
            rows = [top + 1, top, top + 2]                       # belt-side slots, lane output first
            for role in ("lane_inner", "lane_outer", "outer", "inner"):
                for _ in range(cnt[k].get(role, 0)):
                    y = rows.pop(0)
                    name = LH if role in ("outer", "lane_outer") else t["ins"]
                    bp.add(name, X(5), y, from_in if role.startswith("lane") else from_out)
            for i in range(cnt[k].get("centre", 0)):
                bp.add(t["ins"], X(1), [top + 1, top, top + 2][i], from_out)
            if "chest" in j["roles"]:                            # west chest on row top+1, east on top+2
                cy = top + 1 if sgn < 0 else top + 2
                bp.add(t["ins"], X(1), cy, from_out)
                bp.add(chest, c, cy, bar=2)
            for role in j["roles"]:
                if not isinstance(role, tuple):
                    continue
                n = role[1]
                gy = top - 1 if n > k else top + 3               # gap row between the two machines
                if (sgn, gy) in gap_used:
                    raise ValueError(f"{cell.name}: two hand-overs in one gap row")
                gap_used.add((sgn, gy))
                spots = [2] if min(k, n) in water_rows(cell) else [3, 4, 2]     # water row: d=3,4 hold pipes
                for i in range(min(cnt[k][str(role)], len(spots))):
                    bp.add(t["ins"], X(spots[i]), gy, S if n > k else N)   # S = picks from the south
                    if spots[i] == 2 and sgn > 0:                # c+2 is outside the c-1 / c+5 poles' reach
                        bp.add(t["pole"], c + 1, gy)
    if cell.water:                                               # water mains + one tap per shared water row
        for sgn in (-1, 1):
            X = lambda d: c + sgn * d
            out_dir, in_dir = (W, E) if sgn < 0 else (E, W)
            for y in range(y0, y0 + P):
                bp.add("pipe", X(10), y)
            for k in water_rows(cell):
                gy = y0 + P - 4 - 4 * k                          # gap row above machine k
                bp.add("pipe", X(9), gy)
                bp.add("pipe-to-ground", X(8), gy, out_dir)      # above-ground side faces the main
                bp.add("pipe-to-ground", X(4), gy, in_dir)       # surfaces next to the machines' ports
                bp.add("pipe", X(3), gy)                         # feeds the machine below (N) and above (S)
    for g in range(y0, y0 + P, 4):                               # gap rows: poles
        for dx in (-5, -1, 5):
            bp.add(t["pole"], c + dx, g)
    if cell.sink == "belt":
        for y in range(y0, y0 + P):
            bp.add(t["belt"], c, y, S)


def build_cap(bp, cell: Cell, tier: str, rates=None):
    """Base piece, rows 0..7 under the lowest cell (which ends at row -1). Bus taps arrive at row 7,
    markers sit on row 8 (count = per-cell demand per minute at the late tier). The product leaves
    south through the centre column.

    Per side (distance d from the centre): inner belt d=6 starts at row 2 and is side-loaded on row 1 —
    near lane from a column at d=5, far lane from a column further out that runs inward along row 1.
    A fed outer belt (d=7) starts at row 5, is side-loaded on row 4 (far lane from d=8, near lane from the
    inner belt's column d=6 before the inner belt starts) and jumps over row 1 with a 1-tile underground,
    so the inner belt's far-lane feed can pass."""
    t = TIERS[tier]
    c = cell.c
    lanes = cell.cap_items()
    rates = rates or {}
    for dx in (-5, -1, 5):
        bp.add(t["pole"], c + dx, 0)
    if cell.sink == "belt":
        for y in range(0, 8):
            bp.add(t["belt"], c, y, S)
    if cell.water:
        for sgn in (-1, 1):
            for y in range(0, 8):
                bp.add("pipe", c + sgn * 10, y)
            bp.add_marker(c + sgn * 10, 8, {"water": round(rates.get("water", 0))}, )
    get = lambda belt, side: next((i for i, v in lanes.items() if v == (belt, side)), None)
    inner_far, inner_near = get("inner", "far"), get("inner", "near")
    outer_far, outer_near = get("outer", "far"), get("outer", "near")
    outer_fed = bool(outer_far or outer_near)
    for sgn in (-1, 1):
        X = lambda d: c + sgn * d
        inward, outward = (E, W) if sgn < 0 else (W, E)
        marks = []

        def column(x, y_top):
            for y in range(y_top, 8):
                bp.add(t["belt"], x, y, N)

        if inner_far or inner_near:
            for y in (2, 1, 0):
                bp.add(t["belt"], X(6), y, N)
        if inner_near:
            column(X(5), 2)
            bp.add(t["belt"], X(5), 1, outward)
            marks.append((X(5), inner_near))
        if inner_far:
            d0 = 9 if outer_fed else 7
            column(X(d0), 2)
            for d in range(d0, 6, -1):
                bp.add(t["belt"], X(d), 1, inward)
            marks.append((X(d0), inner_far))
        if outer_fed:
            for y in (5, 4, 3):
                bp.add(t["belt"], X(7), y, N)
            bp.add(t["ug"], X(7), 2, N, type="input")
            bp.add(t["ug"], X(7), 0, N, type="output")
            if outer_far:
                column(X(8), 5)
                bp.add(t["belt"], X(8), 4, inward)
                marks.append((X(8), outer_far))
            if outer_near:
                column(X(6), 5)
                bp.add(t["belt"], X(6), 4, outward)
                marks.append((X(6), outer_near))
        for x, item in marks:
            bp.add_marker(x, 8, {item: max(1, round(rates.get(item, 0)))})


def stack(bp, cell: Cell, tier: str, n: int, cap=True, rates=None):
    if cap:
        build_cap(bp, cell, tier, rates)
    for k in range(n):
        build_cell(bp, cell, tier, -cell.period * (k + 1))


# --------------------------------------------------------------------------------------------- analysis
def analyse(cell: Cell, tier: str):
    """Ratios for one cell at one tier with the inserters the layout really has.

    out_per_s (both halves), util per machine, lane_per_side (cap-fed items/s per side), max_cells (stack
    height before the busiest input lane or the product lane of this tier's belt is full), limited (machines
    held back by their inserters)."""
    t = TIERS[tier]
    col = cell.column
    rate = _rate(cell, tier)
    cnt = counts(cell)
    util = _solve(cell, tier, cnt)
    free = _solve(cell, tier)
    finals = [k for k, r in enumerate(col) if cell.out_item(r) == cell.final]
    side_out = sum(rate[k] * util[k] * RECIPES[col[k]]["results"][0]["amount"] for k in finals)
    cap_items = cell.cap_items()
    raw = {}
    for k, u in enumerate(util):
        for item, a in _ingredients(col[k]).items():
            if item in cap_items:
                raw[item] = raw.get(item, 0) + rate[k] * u * a
    fluid = {}
    for k, u in enumerate(util):
        for x in RECIPES[col[k]]["ingredients"]:
            if x.get("type") == "fluid":
                fluid[x["name"]] = fluid.get(x["name"], 0) + rate[k] * u * x["amount"]
    lane = LANE[t["belt"]]
    max_cells = math.floor(min([lane / v for v in raw.values() if v > 0] + [lane / side_out]))
    limited = {col[k]: round(util[k] / free[k], 3) for k in range(len(col)) if free[k] > 0 and util[k] < free[k] * 0.999}
    return {"util": [round(u, 3) for u in util], "out_per_s": 2 * side_out, "lane_per_side": raw,
            "max_cells": max_cells, "limited": limited, "counts": cnt, "fluid_per_side": fluid}
