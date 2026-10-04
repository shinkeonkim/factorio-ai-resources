"""Stackable fluid cells: one recipe per cell, machines in a column on both halves, fluids through the cell.

Same rules as lib/stack.py (fixed width x period, every line enters at the bottom edge and leaves at the top
edge, the next cell pasted one period north continues all of them), but for foundries, chemical plants,
cryogenic plants, biochambers and assemblers running fluid recipes.

West half, from the outside in (the east half is the mirror image around the centre column c):

    fluid mains        vertical pipes, one per input fluid; each main has a free column on its inner side
                       where a pipe-to-ground surfaces next to it
    outer belt (N)     long-handed inserters (optional)
    inner belt (N)     normal inserters
    port column        per machine row: an inserter, or the pipe-to-ground that feeds a fluid port
    machine            rotated so its fluid inputs face the belts and its outputs face the centre
    centre column(s)   "belt" (item product, flows S) | "pipe" (fluid product) |
                       "pipe+belt" (fluid product in two pipes beside an item belt for a byproduct, e.g. stone)

Every input fluid enters on its own machine row, so two pipe-to-ground pairs never share a row (that is
what would let them pair with each other). Rows between machines hold the poles (medium poles: a 5-tall
machine needs the 3.5-tile reach).
Port offsets come from wube/factorio-data (base + space-age entities): fluid box i <-> i-th fluid
ingredient / result of the recipe.
"""
from __future__ import annotations

import json
import math
import pathlib
from dataclasses import dataclass

from lib.fbp import N, E, S, W

ROOT = pathlib.Path(__file__).resolve().parents[1]
_DATA = ROOT / "skills" / "factorio-blueprint" / "data"
RECIPES = {**json.loads((_DATA / "recipes-space-age.json").read_text())["recipes"]}
MACHINES = json.loads((_DATA / "machines.json").read_text())["crafters"]
SIZES = json.loads((_DATA / "entity_sizes.json").read_text())

# fluid-box connection tiles for a north-facing machine, offset from its centre, box order (factorio-data)
PORTS = {
    "foundry": {"in": [(-1, 2), (1, 2)], "out": [(-1, -2), (1, -2)]},
    "cryogenic-plant": {"in": [(-2, 2), (0, 2), (2, 2)], "out": [(-2, -2), (0, -2), (2, -2)]},
    "chemical-plant": {"in": [(-1, -1), (1, -1)], "out": [(-1, 1), (1, 1)]},
    "biochamber": {"in": [(-1, -1), (1, -1)], "out": [(1, 1), (-1, 1)]},
    "assembling-machine-2": {"in": [(0, -1)], "out": [(0, 1)]},
    "assembling-machine-3": {"in": [(0, -1)], "out": [(0, 1)]},
    "oil-refinery": {"in": [(-1, 2), (1, 2)], "out": [(-2, -2), (0, -2), (2, -2)]},
}
SPEED = {k: v["speed"] for k, v in MACHINES.items()}
PROD = {k: v.get("base_productivity", 0) for k, v in MACHINES.items()}
LANE = {"fast-transport-belt": 15.0, "express-transport-belt": 22.5, "turbo-transport-belt": 30.0}
INSERTER = {"fast-inserter": 2.31, "bulk-inserter": 4.0, "stack-inserter": 6.0, "long-handed-inserter": 1.2}
PIPE_FLOW = 1200.0      # per main, conservative for long pipes (2.0 fluid segments)
LH = "long-handed-inserter"

TIERS = {   # planets come after Nauvis: red belts and medium poles at the earliest
    "mid": dict(belt="fast-transport-belt", ug="fast-underground-belt", ins="fast-inserter", pole="medium-electric-pole",
                label={"ko": "중반 (빨강·고속)", "en": "mid (red, fast)"}),
    "late": dict(belt="express-transport-belt", ug="express-underground-belt", ins="bulk-inserter",
                 pole="medium-electric-pole", label={"ko": "후반 (파랑·벌크)", "en": "late (blue, bulk)"}),
    "end": dict(belt="turbo-transport-belt", ug="turbo-underground-belt", ins="stack-inserter", pole="medium-electric-pole",
                label={"ko": "최종 (터보·스택)", "en": "endgame (turbo, stack)"}),
}

CHEST = {"mid": "passive-provider-chest", "late": "passive-provider-chest", "end": "passive-provider-chest"}
ROT = {N: lambda x, y: (x, y), E: lambda x, y: (-y, x), S: lambda x, y: (-x, -y), W: lambda x, y: (y, -x)}


def _size(machine):
    s = SIZES[machine]
    return s["w"]


@dataclass
class FluidCell:
    name: str
    recipe: str
    machine: str
    n: int = 2                       # machines per half
    inner: tuple = (None, None)      # (far, near) lane items
    outer: tuple | None = None
    tiers: tuple = ("mid", "late", "end")
    sink: str = "belt"               # "chest": item product into a chest in the centre column (mall cells)

    # ---- recipe facts
    @property
    def r(self):
        return RECIPES[self.recipe]

    @property
    def fluids_in(self):
        return [i["name"] for i in self.r["ingredients"] if i.get("type") == "fluid"]

    @property
    def fluids_out(self):
        return [o["name"] for o in self.r["results"] if o.get("type") == "fluid"]

    @property
    def items_in(self):
        return [i["name"] for i in self.r["ingredients"] if i.get("type") != "fluid"]

    @property
    def items_out(self):
        return [o["name"] for o in self.r["results"] if o.get("type") != "fluid"]

    @property
    def centre(self):
        if self.sink == "chest" and not self.fluids_out:
            return "chest"
        if self.fluids_out and self.items_out:
            return "pipe+belt"
        return "pipe" if self.fluids_out else "belt"

    @property
    def s(self):
        return _size(self.machine)

    @property
    def period(self):
        return (self.s + 1) * self.n

    # ---- geometry (distances from the centre column c, measured outwards)
    @property
    def d_port_c(self):                 # column between machine and centre
        return 2 if self.centre == "pipe+belt" else 1

    @property
    def d_mach(self):                   # machine spans d_mach .. d_mach+s-1
        return self.d_port_c + 1

    @property
    def d_port_b(self):                 # belt-side port / inserter column
        return self.d_mach + self.s

    @property
    def d_inner(self):
        return self.d_port_b + 1

    @property
    def d_outer(self):
        return self.d_inner + 1 if self.outer else None

    def d_entry(self, i):               # pipe-to-ground beside main i
        base = (self.d_outer or self.d_inner) + 1
        return base + 2 * i

    def d_main(self, i):
        return self.d_entry(i) + 1

    @property
    def c(self):
        return self.d_main(len(self.fluids_in) - 1) if self.fluids_in else (self.d_outer or self.d_inner)

    @property
    def width(self):
        return 2 * self.c + 1

    def facing(self, sgn):
        """Rotation that points the input edge at the belt side (west for sgn=-1)."""
        ports = PORTS[self.machine]
        want = -1 if sgn < 0 else 1                     # x direction of the belt side
        for f in (N, E, S, W):
            xs = [ROT[f](x, y)[0] for x, y in ports["in"]]
            if all(math.copysign(1, x) == want and abs(x) > self.s / 2 - 1 for x in xs):
                return f
        raise ValueError(f"{self.machine}: cannot face its inputs sideways")

    def port_rows(self, sgn):
        """input box i -> row offset from the machine's top row; output box i -> row offset."""
        f = self.facing(sgn)
        half = self.s // 2
        ins = [ROT[f](x, y)[1] + half for x, y in PORTS[self.machine]["in"]]
        outs = [ROT[f](x, y)[1] + half for x, y in PORTS[self.machine]["out"]]
        return ins, outs


def _amount(lst, name):
    return next(x.get("amount", 1) * x.get("probability", 1) for x in lst if x["name"] == name)


def rates(cell: FluidCell):
    """per machine at 100 %: crafts/s, item/fluid in and out per second (base productivity included)."""
    cr = SPEED[cell.machine] / cell.r["energy_required"]
    p = 1 + PROD.get(cell.machine, 0)
    return {"crafts": cr,
            "in": {i["name"]: cr * i["amount"] for i in cell.r["ingredients"]},
            "out": {o["name"]: cr * p * o.get("amount", 1) * o.get("probability", 1) for o in cell.r["results"]}}


def slots(cell: FluidCell):
    """Inserters per machine on the belt side (inner, outer) and the centre side (out), sized for the
    fastest tier and clamped to the rows the fluid ports leave free."""
    rt = rates(cell)
    lanes = {}
    for belt, pair in (("inner", cell.inner), ("outer", cell.outer)):
        for item in (pair or ()):
            if item:
                lanes[item] = belt
    load = {"inner": 0.0, "outer": 0.0}
    for item in cell.items_in:
        if item not in lanes:
            raise ValueError(f"{cell.name}: {item} is not on a lane")
        load[lanes[item]] += rt["in"][item]
    out_load = sum(rt["out"][i] for i in cell.items_out)
    free_b = cell.s - len(cell.fluids_in)
    free_c = cell.s - len(cell.fluids_out)
    want = {}
    for t in cell.tiers:
        ins = TIERS[t]["ins"]
        want["inner"] = max(want.get("inner", 0), math.ceil(load["inner"] / INSERTER[ins] - 1e-9) if load["inner"] else 0)
        want["outer"] = max(want.get("outer", 0), math.ceil(load["outer"] / INSERTER[LH] - 1e-9) if load["outer"] else 0)
        want["out"] = max(want.get("out", 0), math.ceil(out_load / (INSERTER[ins] if cell.centre in ("belt", "chest") else INSERTER[LH]) - 1e-9)
                          if out_load else 0)
    if cell.centre == "chest":
        want["out"] = 1                                   # a mall chest only needs one
    while want["inner"] + want["outer"] > free_b:
        k = "inner" if want["inner"] >= want["outer"] else "outer"
        want[k] -= 1
    want["out"] = min(want["out"], free_c)
    return want, load, out_load


def build_cell(bp, cell: FluidCell, tier: str, y0: int):
    t = TIERS[tier]
    c, s, P = cell.c, cell.s, cell.period
    want, _, _ = slots(cell)
    for sgn in (-1, 1):
        X = lambda d: c + sgn * d
        to_belt, to_centre = (W, E) if sgn < 0 else (E, W)            # inserter pickup side
        f = cell.facing(sgn)
        in_rows, out_rows = cell.port_rows(sgn)
        for y in range(y0, y0 + P):
            bp.add(t["belt"], X(cell.d_inner), y, N)
            if cell.outer:
                bp.add(t["belt"], X(cell.d_outer), y, N)
            for i in range(len(cell.fluids_in)):
                bp.add("pipe", X(cell.d_main(i)), y)
        for k in range(cell.n):
            top = y0 + P - s - (s + 1) * k                             # machine rows top .. top+s-1
            left = X(cell.d_mach + s - 1) if sgn < 0 else X(cell.d_mach)
            bp.add(cell.machine, left, top, f, recipe=cell.recipe)
            used = set()
            for i, fl in enumerate(cell.fluids_in):                   # one fluid per row
                row = top + in_rows[i]
                used.add(row)
                bp.add("pipe-to-ground", X(cell.d_port_b), row, to_centre)   # surfaces at the machine
                bp.add("pipe-to-ground", X(cell.d_entry(i)), row, to_belt)    # next to its main
            free = [top + r for r in range(s) if top + r not in used]
            for role, name in (("inner", t["ins"]), ("outer", LH)):
                for _ in range(want.get(role, 0)):
                    bp.add(name, X(cell.d_port_b), free.pop(0), to_belt)
            # centre side
            out_used = set()
            for i, fl in enumerate(cell.fluids_out):
                row = top + out_rows[i]
                out_used.add(row)
                bp.add("pipe", X(cell.d_port_c), row)                  # touches the centre main
            cfree = [top + r for r in range(s) if top + r not in out_used]
            if cell.centre == "chest":                       # west chest on the first free row, east on the second
                cy = cfree[0] if sgn < 0 else cfree[1]
                bp.add(t["ins"], X(cell.d_port_c), cy, to_belt)
                bp.add(CHEST[tier], c, cy, bar=4)
                continue
            for _ in range(want.get("out", 0)):
                name = t["ins"] if cell.centre == "belt" else LH
                bp.add(name, X(cell.d_port_c), cfree.pop(0), to_belt)     # picks from the machine side
        for k in range(cell.n):                                        # gap row above each machine: poles
            g = y0 + P - s - (s + 1) * k - 1
            for d in (cell.d_port_b, cell.d_port_c):
                bp.add(t["pole"], X(d), g)
    for y in range(y0, y0 + P):
        if cell.centre == "belt":
            bp.add(t["belt"], c, y, S)
        elif cell.centre == "pipe":
            bp.add("pipe", c, y)
        elif cell.centre == "pipe+belt":
            bp.add("pipe", c - 1, y); bp.add("pipe", c + 1, y); bp.add(t["belt"], c, y, S)


def analyse(cell: FluidCell, tier: str):
    """Per cell (both halves) at 100 %: output, inputs per side, max cells for this tier's lanes and the
    conservative pipe limit."""
    t = TIERS[tier]
    rt = rates(cell)
    want, load, out_load = slots(cell)
    # inserter-limited utilisation
    caps = []
    if load["inner"]:
        caps.append(want["inner"] * INSERTER[t["ins"]] / load["inner"])
    if load["outer"]:
        caps.append(want["outer"] * INSERTER[LH] / load["outer"])
    if out_load:
        caps.append(want["out"] * (INSERTER[t["ins"]] if cell.centre == "belt" else INSERTER[LH]) / out_load)
    u = min([1.0] + caps)
    n = cell.n
    side_in = {k: v * u * n for k, v in rt["in"].items()}
    out = {k: v * u * n * 2 for k, v in rt["out"].items()}
    lane = LANE[t["belt"]]
    lim = []
    for k, v in side_in.items():
        lim.append((PIPE_FLOW if k in cell.fluids_in else lane) / v)
    for k, v in out.items():
        lim.append((PIPE_FLOW if k in cell.fluids_out else 2 * lane) / v)
    return {"util": u, "out_per_s": out, "in_per_side": side_in, "max_cells": math.floor(min(lim))}


# ------------------------------------------------------------------------------------------------- cap
def _lanes(cell):
    out = {}
    for belt, pair in (("inner", cell.inner), ("outer", cell.outer)):
        if pair:
            for side, item in zip(("far", "near"), pair):
                if item:
                    out[(belt, side)] = item
    return out


def build_cap(bp, cell: FluidCell, tier: str, rates_pm=None, rows=8):
    """Base piece under the lowest cell (rows 0 .. rows-1, markers on row `rows`).

    * fluid mains and the centre product line run straight down to the bottom edge
    * inner belt: dead start on row 2, side-loaded on row 1 (near lane from the port column, far lane from a
      feed that comes from beyond the mains and goes underground under every pipe it crosses)
    * outer belt (if fed): dead start on row 5, side-loaded on row 4, 1-tile underground over row 1"""
    t = TIERS[tier]
    c = cell.c
    rates_pm = rates_pm or {}
    lanes = _lanes(cell)
    for sgn in (-1, 1):
        X = lambda d: c + sgn * d
        inward, outward = (E, W) if sgn < 0 else (W, E)
        for d in (cell.d_port_b, cell.d_port_c):
            bp.add(t["pole"], X(d), 0)
        pipes = {cell.d_main(i) for i in range(len(cell.fluids_in))}
        for i, fl in enumerate(cell.fluids_in):
            for y in range(rows):
                bp.add("pipe", X(cell.d_main(i)), y)
            bp.add_marker(X(cell.d_main(i)), rows, {fl: round(rates_pm.get(fl, 0))})
        marks = []
        outer_fed = cell.outer and (("outer", "far") in lanes or ("outer", "near") in lanes)
        inner_fed = ("inner", "far") in lanes or ("inner", "near") in lanes
        far_start = (max(pipes) if pipes else (cell.d_outer or cell.d_inner)) + 1

        def column(d, y_top):
            for y in range(y_top, rows):
                bp.add(t["belt"], X(d), y, N)

        def run(d_from, d_to, y, obstacles):
            """belt along row y from distance d_from to d_to (either direction), underground under every
            obstacle column; the tile at d_to points at the belt it side-loads."""
            step = -1 if d_to < d_from else 1
            way = inward if step < 0 else outward
            d = d_from
            while (d - d_to) * step <= 0:
                nxt = d + step
                if nxt in obstacles and (nxt - d_to) * step <= 0:
                    k = nxt
                    while k in obstacles:
                        k += step
                    bp.add(t["ug"], X(d), y, way, type="input")
                    bp.add(t["ug"], X(k), y, way, type="output")
                    d = k + step
                    continue
                bp.add(t["belt"], X(d), y, way)
                d += step

        def run_inward(d_from, d_to, y):
            run(d_from, d_to, y, set(pipes))

        if inner_fed:
            for y in (2, 1, 0):
                bp.add(t["belt"], X(cell.d_inner), y, N)
        if ("inner", "near") in lanes:
            column(cell.d_port_b, 2)
            bp.add(t["belt"], X(cell.d_port_b), 1, outward)
            marks.append((cell.d_port_b, lanes[("inner", "near")]))
        if outer_fed:
            for y in (5, 4, 3):
                bp.add(t["belt"], X(cell.d_outer), y, N)
            bp.add(t["ug"], X(cell.d_outer), 2, N, type="input")
            bp.add(t["ug"], X(cell.d_outer), 0, N, type="output")
            if ("outer", "near") in lanes:                 # from under the machines, 4 columns from the
                dn = cell.d_port_b - 4                       # inner feed, underground under it
                if dn < 2:
                    raise ValueError(f"{cell.name}: no room for the outer belt's near-lane feed")
                column(dn, 5)
                run(dn, cell.d_inner, 4, {cell.d_port_b} if ("inner", "near") in lanes else set())
                marks.append((dn, lanes[("outer", "near")]))
            if ("outer", "far") in lanes:
                d0 = far_start
                column(d0 + 1, 5)
                bp.add(t["belt"], X(d0 + 1), 4, inward)
                run_inward(d0, cell.d_outer + 1, 4)
                marks.append((d0 + 1, lanes[("outer", "far")]))
        if ("inner", "far") in lanes:
            d0 = far_start + (4 if outer_fed and ("outer", "far") in lanes else 0)
            column(d0 + 1, 2)
            bp.add(t["belt"], X(d0 + 1), 1, inward)
            run_inward(d0, cell.d_inner + 1, 1)
            marks.append((d0 + 1, lanes[("inner", "far")]))
        for d, item in marks:
            bp.add_marker(X(d), rows, {item: round(rates_pm.get(item, 0))})
    for y in range(rows):
        if cell.centre == "belt":
            bp.add(t["belt"], c, y, S)
        elif cell.centre == "pipe":
            bp.add("pipe", c, y)
        elif cell.centre == "pipe+belt":
            bp.add("pipe", c - 1, y); bp.add("pipe", c + 1, y); bp.add(t["belt"], c, y, S)


def stack(bp, cell, tier, n, rates_pm=None):
    build_cap(bp, cell, tier, rates_pm)
    for k in range(n):
        build_cell(bp, cell, tier, -cell.period * (k + 1))


def late_rates(cell):
    a = analyse(cell, "late")
    return {k: v * 60 for k, v in a["in_per_side"].items()}


def as_stack(cell: FluidCell, cells: int, tier: str = "mid", name=None):
    """A lib.complex.Stack for `cells` copies of this fluid cell on its cap (products and demand filled in)."""
    from lib.complex import Stack

    def build(bp, t):
        stack(bp, cell, t, cells, late_rates(cell))
        if cell.centre == "pipe+belt":                         # join both halves' product mains on top
            yt = -cell.period * cells - 1
            for dx in (-1, 0, 1):
                bp.add("pipe", cell.c + dx, yt)

    if cell.centre == "pipe+belt":
        products = [(cell.fluids_out[0], "fluid", cell.c - 1), (cell.items_out[0], "item", cell.c)]
    elif cell.centre == "pipe":
        products = [(cell.fluids_out[0], "fluid", cell.c)]
    elif cell.centre == "belt":
        products = [(cell.items_out[0], "item", cell.c)]
    else:
        products = []
    a = analyse(cell, "late")
    duty = 0.05 if cell.centre == "chest" else 1.0           # mall cells idle once their chests are full
    demand = {k: v * cells * duty for k, v in a["in_per_side"].items()}
    supply = {k: v * cells for k, v in a["out_per_s"].items()}
    return Stack(name or f"{cell.name} x{cells}", build, tier, products, demand, supply)
