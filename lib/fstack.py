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

# fluid-box connections of a north-facing machine: (x, y) of the port tile relative to the machine centre and the
# direction the connection points, in box order (factorio-data). Box i <-> i-th fluid ingredient / result.
PORTS = {
    "foundry": {"in": [(-1, 2, "S"), (1, 2, "S")], "out": [(-1, -2, "N"), (1, -2, "N")]},
    "cryogenic-plant": {"in": [(-2, 2, "S"), (0, 2, "S"), (2, 2, "S")], "out": [(-2, -2, "N"), (0, -2, "N"), (2, -2, "N")]},
    "chemical-plant": {"in": [(-1, -1, "N"), (1, -1, "N")], "out": [(-1, 1, "S"), (1, 1, "S")]},
    "biochamber": {"in": [(-1, -1, "N"), (1, -1, "N")], "out": [(1, 1, "S"), (-1, 1, "S")]},
    "assembling-machine-2": {"in": [(0, -1, "N")], "out": [(0, 1, "S")]},
    "assembling-machine-3": {"in": [(0, -1, "N")], "out": [(0, 1, "S")]},
    "oil-refinery": {"in": [(-1, 2, "S"), (1, 2, "S")], "out": [(-2, -2, "N"), (0, -2, "N"), (2, -2, "N")]},
    "electromagnetic-plant": {"in": [(-1.5, 0.5, "W"), (1.5, -0.5, "E")], "out": [(0.5, 1.5, "S"), (-0.5, -1.5, "N")]},
    "electric-furnace": {"in": [], "out": []},           # furnaces pick their recipe from the input
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
DIRS = [N, E, S, W]
ROT = {N: lambda x, y: (x, y), E: lambda x, y: (-y, x), S: lambda x, y: (-x, -y), W: lambda x, y: (y, -x)}


def _rot_dir(d, f):
    return DIRS[(DIRS.index(d) + DIRS.index(f)) % 4]


def _size(machine):
    return SIZES[machine]["w"]


@dataclass
class Port:
    kind: str          # "in" | "out"
    fluid: str
    side: str          # "belt" | "centre" | "above" | "below"
    pos: int           # row (belt/centre: machine row 0..s-1) or column (above/below: distance d from the centre)


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
    bots: bool = False               # robot-fed: a requester chest per input inserter instead of belts (Gleba)
    fuel: str | None = None          # burner fuel to request as well (biochambers burn nutrients)
    limit: tuple | None = None       # (item, count): input inserters run only while the network holds < count
    belt_out: bool = False           # robot-fed inputs, but the item product leaves on the centre belt (e.g. stone)

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
    def s(self):
        return _size(self.machine)

    # ---- port layout: facing per half, chosen once
    def layout(self):
        if getattr(self, "_layout", None):
            return self._layout
        P = PORTS[self.machine]
        s = self.s
        off = (s - 1) / 2

        def ports_for(f, sgn):
            belt_dir = W if sgn < 0 else E
            out = []
            for kind, boxes, fluids in (("in", P["in"], self.fluids_in), ("out", P["out"], self.fluids_out)):
                for (x, y, d), fl in zip(boxes, fluids):
                    rx, ry = ROT[f](x, y)
                    rd = _rot_dir(d, f)
                    if rd == belt_dir:
                        side, pos = "belt", int(round(ry + off))
                    elif rd in (E, W):
                        side, pos = "centre", int(round(ry + off))
                    else:
                        col = int(round(rx + off))                    # 0 = west column of the machine
                        side, pos = ("above" if rd == N else "below"), col
                    out.append(Port(kind, fl, side, pos))
            return out

        best = None
        for fw in DIRS:
            for fe in DIRS:
                pw, pe = ports_for(fw, -1), ports_for(fe, 1)
                centre = {p.fluid for p in pw + pe if p.side == "centre"}
                if len(centre) > 1:
                    continue
                bad = False
                for ps in (pw, pe):
                    if any(p.kind == "out" and p.side == "belt" for p in ps):
                        bad = True                                # outputs must reach the centre or a gap row
                    rows = [p.pos for p in ps if p.side == "belt"]
                    if len(rows) != len(set(rows)):
                        bad = True
                    gaps = [p.side for p in ps if p.side in ("above", "below")]
                    if len(set(gaps)) > 1 or len(gaps) > 1:      # one gap port per machine, all on one side
                        bad = True
                if bad:
                    continue
                gap = sum(p.side in ("above", "below") for p in pw + pe)
                cin = sum(p.side == "centre" and p.kind == "in" for p in pw + pe)
                below = sum(p.side == "below" for p in pw + pe)
                score = (gap, cin, below, DIRS.index(fw), DIRS.index(fe))
                if best is None or score < best[0]:
                    best = (score, fw, fe, pw, pe, centre)
        if best is None:
            raise ValueError(f"{self.name}: no machine facing fits its fluid ports")
        _, fw, fe, pw, pe, centre = best
        self._layout = {"facing": {-1: fw, 1: fe}, "ports": {-1: pw, 1: pe},
                        "centre_fluid": next(iter(centre)) if centre else None}
        return self._layout

    @property
    def centre_fluid(self):
        return self.layout()["centre_fluid"]

    @property
    def extra_row(self):
        """1 if a port points below the lowest machine (it gets its own row inside the cell)"""
        return int(any(p.side == "below" for ps in self.layout()["ports"].values() for p in ps))

    @property
    def mains(self):
        """fluids carried by mains outside the belts (both halves use the same columns)"""
        out = []
        for ps in self.layout()["ports"].values():
            for p in ps:
                if p.side != "centre" and p.fluid not in out:
                    out.append(p.fluid)
        return out

    @property
    def centre(self):
        cf = self.centre_fluid
        if cf:
            if self.items_out and self.bots and not self.belt_out:
                return "pipe+chest"                   # items to a provider chest between the two centre pipes
            return "pipe+belt" if self.items_out else "pipe"
        if self.sink == "chest" or (self.bots and not self.belt_out):
            return "chest"
        return "belt" if self.items_out else "none"

    @property
    def period(self):
        return (self.s + 1) * self.n + self.extra_row

    # ---- geometry (distances from the centre column c, measured outwards)
    @property
    def d_port_c(self):
        return 2 if self.centre in ("pipe+belt", "pipe+chest") else 1

    @property
    def d_mach(self):
        return self.d_port_c + 1

    @property
    def d_port_b(self):
        return self.d_mach + self.s

    @property
    def d_inner(self):
        return self.d_port_b + 1

    @property
    def d_outer(self):
        return self.d_inner + 1 if self.outer else None

    def d_entry(self, i):
        return (self.d_outer or self.d_inner) + 1 + 2 * i

    def d_main(self, i):
        return self.d_entry(i) + 1

    def main_of(self, fluid):
        return self.mains.index(fluid)

    @property
    def c(self):
        return self.d_main(len(self.mains) - 1) if self.mains else (self.d_outer or self.d_inner)

    @property
    def width(self):
        return 2 * self.c + 1

    def products(self):
        """[(item, kind, x offset from the stack origin)] leaving at the cap bottom"""
        out = []
        cf = self.centre_fluid
        for fl in self.fluids_out:
            if fl == cf:
                out.append((fl, "fluid", self.c - 1 if self.centre in ("pipe+belt", "pipe+chest") else self.c))
            else:
                out.append((fl, "fluid", self.c - self.d_main(self.main_of(fl))))
        if self.items_out and self.centre in ("belt", "pipe+belt"):
            out.append((self.items_out[0], "item", self.c))
        return out


def _amount(lst, name):
    return next(x.get("amount", 1) * x.get("probability", 1) for x in lst if x["name"] == name)


def _bot_requests(cell):
    want = {i["name"]: 3 * i["amount"] for i in cell.r["ingredients"] if i.get("type") != "fluid"}
    if cell.fuel:
        want[cell.fuel] = want.get(cell.fuel, 0) + 10
    return {"sections": [{"index": 1, "filters": [
        {"index": k + 1, "name": it, "quality": "normal", "comparator": "=", "count": n}
        for k, (it, n) in enumerate(want.items())]}]}


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
        if cell.bots:
            load["inner"] += rt["in"][item]
            continue
        if item not in lanes:
            raise ValueError(f"{cell.name}: {item} is not on a lane")
        load[lanes[item]] += rt["in"][item]
    out_load = sum(rt["out"][i] for i in cell.items_out)
    ports = cell.layout()["ports"].values()
    free_b = min(cell.s - sum(p.side == "belt" for p in ps) for ps in ports)
    free_c = min(cell.s - sum(p.side == "centre" for p in ps) for ps in ports)
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
    L = cell.layout()
    for sgn in (-1, 1):
        X = lambda d: c + sgn * d
        to_belt, to_centre = (W, E) if sgn < 0 else (E, W)            # inserter pickup side / pipe-to-ground facing
        f = L["facing"][sgn]
        ports = L["ports"][sgn]
        for y in range(y0, y0 + P):
            if not cell.bots:
                bp.add(t["belt"], X(cell.d_inner), y, N)
            if cell.outer:
                bp.add(t["belt"], X(cell.d_outer), y, N)
            for i in range(len(cell.mains)):
                bp.add("pipe", X(cell.d_main(i)), y)
        gap_tiles = set()
        for k in range(cell.n):
            top = y0 + P - cell.extra_row - s - (s + 1) * k             # machine rows top .. top+s-1
            left = X(cell.d_mach + s - 1) if sgn < 0 else X(cell.d_mach)
            bp.add(cell.machine, left, top, f, **({} if "furnace" in cell.machine else {"recipe": cell.recipe}))
            used_b, used_c = set(), set()
            for p in ports:
                ent = cell.d_entry(cell.main_of(p.fluid)) if p.side != "centre" else None
                if p.side == "belt":
                    row = top + p.pos
                    used_b.add(row)
                    bp.add("pipe-to-ground", X(cell.d_port_b), row, to_centre)   # surfaces at the machine
                    bp.add("pipe-to-ground", X(ent), row, to_belt)               # next to its main
                elif p.side == "centre":
                    row = top + p.pos
                    used_c.add(row)
                    bp.add("pipe", X(cell.d_port_c), row)                        # touches the centre pipe
                else:                                                            # gap row above / below
                    row = top - 1 if p.side == "above" else top + s
                    d = cell.d_mach + s - 1 - p.pos if sgn < 0 else cell.d_mach + p.pos
                    bp.add("pipe", X(d), row)
                    bp.add("pipe-to-ground", X(d + 1), row, to_centre)
                    bp.add("pipe-to-ground", X(ent), row, to_belt)
                    gap_tiles |= {(d, row), (d + 1, row)}
            free = [top + r for r in range(s) if top + r not in used_b]
            for role, name in (("inner", t["ins"]), ("outer", LH)):
                for _ in range(want.get(role, 0)):
                    row = free.pop(0)
                    extra = {}
                    if cell.bots and cell.limit:
                        extra["control_behavior"] = {"connect_to_logistic_network": True, "logistic_condition": {
                            "first_signal": {"type": "item", "name": cell.limit[0]}, "constant": cell.limit[1],
                            "comparator": "<"}}
                    bp.add(name, X(cell.d_port_b), row, to_belt, **extra)
                    if cell.bots:                                   # its requester chest on the outer side
                        bp.add("requester-chest", X(cell.d_inner), row, request_filters=_bot_requests(cell))
            cfree = [top + r for r in range(s) if top + r not in used_c]
            if cell.centre == "chest":                       # west chest on the first free row, east on the second
                cy = cfree[0] if sgn < 0 else cfree[1]
                bp.add(t["ins"], X(cell.d_port_c), cy, to_belt)
                bp.add(CHEST[tier], c, cy, **({} if cell.bots else {"bar": 4}))
                continue
            if cell.centre == "pipe+chest":                  # long-handed over the pipe into a provider chest
                cy = cfree[0] if sgn < 0 else cfree[-1]
                bp.add(LH, X(cell.d_port_c), cy, to_belt)
                bp.add(CHEST[tier], c, cy)
            if cell.centre in ("belt", "pipe+belt"):
                for _ in range(want.get("out", 0)):
                    name = t["ins"] if cell.centre == "belt" else LH
                    bp.add(name, X(cell.d_port_c), cfree.pop(0), to_belt)       # picks from the machine side
        for k in range(cell.n):                                        # gap row above each machine: poles
            g = y0 + P - cell.extra_row - s - (s + 1) * k - 1
            for d in (cell.d_port_b, cell.d_port_c):
                if (d, g) not in gap_tiles:
                    bp.add(t["pole"], X(d), g)
        if cell.extra_row:
            g = y0 + P - 1
            for d in (cell.d_port_b, cell.d_port_c):
                if (d, g) not in gap_tiles:
                    bp.add(t["pole"], X(d), g)
    for y in range(y0, y0 + P):
        if cell.centre == "belt":
            bp.add(t["belt"], c, y, S)
        elif cell.centre == "pipe":
            bp.add("pipe", c, y)
        elif cell.centre == "pipe+belt":
            bp.add("pipe", c - 1, y); bp.add("pipe", c + 1, y); bp.add(t["belt"], c, y, S)
        elif cell.centre == "pipe+chest":
            bp.add("pipe", c - 1, y); bp.add("pipe", c + 1, y)


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
    if cell.centre_fluid in cell.fluids_in:
        lim.append(PIPE_FLOW / (2 * side_in[cell.centre_fluid]))
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
        pipes = {cell.d_main(i) for i in range(len(cell.mains))}
        for i, fl in enumerate(cell.mains):
            for y in range(rows):
                bp.add("pipe", X(cell.d_main(i)), y)
            if fl in cell.fluids_in:                          # outputs leave here instead (see products())
                bp.add_marker(X(cell.d_main(i)), rows, {fl: round(rates_pm.get(fl, 0))})
        marks = []
        outer_fed = cell.outer and (("outer", "far") in lanes or ("outer", "near") in lanes)
        inner_fed = ("inner", "far") in lanes or ("inner", "near") in lanes
        far_start = max((max(pipes) if pipes else (cell.d_outer or cell.d_inner)) + 1,
                        cell.d_port_b + 3)               # feed columns at least 4 apart (bus taps)

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
                    while k in obstacles or ((k + step) in obstacles and (k + step - d_to) * step <= 0):
                        k += step                            # one underground over obstacles 1 tile apart
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
        near_outer = ("outer", "near") in lanes
        far_outer = ("outer", "far") in lanes
        far_inner = ("inner", "far") in lanes
        F = far_start
        d_of = F + 1                                         # outer far-lane feed column
        d_if = F + 1 + 4 * far_outer                         # inner far-lane feed column
        d_on = F + 1 + 4 * far_outer + 4 * far_inner         # outer near-lane feed column
        if outer_fed:
            for y in (4, 3):
                bp.add(t["belt"], X(cell.d_outer), y, N)
            bp.add(t["belt"], X(cell.d_outer), 5, N)         # dead start, or the curve that brings the near lane
            bp.add(t["ug"], X(cell.d_outer), 2, N, type="input")
            bp.add(t["ug"], X(cell.d_outer), 0, N, type="output")
            if far_outer:
                column(d_of, 5)
                bp.add(t["belt"], X(d_of), 4, inward)
                run_inward(d_of - 1, cell.d_outer + 1, 4)
                marks.append((d_of, lanes[("outer", "far")]))
            if near_outer:
                # the item side-loads onto the right-hand lane of a belt that runs inward on row 5 and curves
                # into the outer belt's start, which puts it on the outer belt's near lane
                bp.add(t["belt"], X(d_on + 1), 5, inward)    # dead start
                column(d_on, 6)
                obstacles = set(pipes) | ({d_of} if far_outer else set()) | ({d_if} if far_inner else set())
                run(d_on, cell.d_outer + 1, 5, obstacles)
                marks.append((d_on, lanes[("outer", "near")]))
        if far_inner:
            column(d_if, 2)
            bp.add(t["belt"], X(d_if), 1, inward)
            run_inward(d_if - 1, cell.d_inner + 1, 1)
            marks.append((d_if, lanes[("inner", "far")]))
        for d, item in marks:
            bp.add_marker(X(d), rows, {item: round(rates_pm.get(item, 0))})
    for y in range(rows):
        if cell.centre == "belt":
            bp.add(t["belt"], c, y, S)
        elif cell.centre == "pipe":
            bp.add("pipe", c, y)
        elif cell.centre == "pipe+belt":
            bp.add("pipe", c - 1, y); bp.add("pipe", c + 1, y); bp.add(t["belt"], c, y, S)
        elif cell.centre == "pipe+chest":
            bp.add("pipe", c - 1, y); bp.add("pipe", c + 1, y)
    cf = cell.centre_fluid
    if cf and cf in cell.fluids_in:                           # the centre pipe is an input: fed from the bus
        bp.add_marker(c - 1 if cell.centre in ("pipe+belt", "pipe+chest") else c, rows, {cf: round(rates_pm.get(cf, 0))})


def stack(bp, cell, tier, n, rates_pm=None):
    build_cap(bp, cell, tier, rates_pm)
    for k in range(n):
        build_cell(bp, cell, tier, -cell.period * (k + 1))


def late_rates(cell):
    a = analyse(cell, "late")
    return {k: v * 60 for k, v in a["in_per_side"].items()}


def join_top(bp, cell: FluidCell, cells: int):
    """Above the top cell: join the two centre pipes (pipe+belt) and both halves of every outer main that carries
    an output, so each line leaves the stack through one column. Outer mains are joined with a pipe-to-ground
    chain (it only connects at its ends, so nothing it passes over mixes in)."""
    yt = -cell.period * cells - 1
    c = cell.c
    if cell.centre in ("pipe+belt", "pipe+chest"):
        for dx in (-1, 0, 1):
            bp.add("pipe", c + dx, yt)
    rows = 0
    for fl in cell.mains:
        if fl not in cell.fluids_out:
            continue
        d = cell.d_main(cell.main_of(fl))
        y = yt - rows
        for k in range(rows + 1):                      # risers above the earlier chains
            bp.add("pipe", c - d, yt - k); bp.add("pipe", c + d, yt - k)
        x = c - d + 1
        while x < c + d:
            end = min(x + 10, c + d - 1)
            bp.add("pipe-to-ground", x, y, W)
            bp.add("pipe-to-ground", end, y, E)
            x = end + 1
        rows += 1


def cap_rows(cell: FluidCell) -> int:
    """fewest cap rows the feeds need: none fed by belt (robot cells) 2, inner belt only 3, outer belt 7"""
    lanes = _lanes(cell)
    if cell.outer and (("outer", "far") in lanes or ("outer", "near") in lanes):
        return 7
    if ("inner", "far") in lanes or ("inner", "near") in lanes:
        return 3
    return 2


def as_stack(cell: FluidCell, cells: int, tier: str = "mid", name=None, compact=False):
    """A lib.complex.Stack for `cells` copies of this fluid cell on its cap (products and demand filled in).
    compact=True (dense bases, lib/base): the cap has only the rows its feeds need (still ending on row 7 with the
    markers on row 8, so lib/complex places it the same way) and no roboports (the base places its own)."""
    from lib.complex import Stack

    def build(bp, t):
        if not compact:
            stack(bp, cell, t, cells, late_rates(cell))
            join_top(bp, cell, cells)
            if cell.bots:                                          # logistic coverage: cap and top of the stack
                bp.add("roboport", cell.c - 2, 2)
                bp.add("roboport", cell.c - 2, -cell.period * cells - 6)
                bp.add(TIERS[t]["pole"], cell.c + 2, -cell.period * cells - 2)
            return
        from lib.fbp import Blueprint
        rows = cap_rows(cell)
        part = Blueprint("cell", game="2.0")
        build_cap(part, cell, t, late_rates(cell), rows=rows)
        for k in range(cells):
            build_cell(part, cell, t, -cell.period * (k + 1))
        join_top(part, cell, cells)
        dy = 8 - rows                                          # cap bottom on row 7, markers on row 8
        for e in part.entities:
            m = part._meta[e["entity_number"]]
            fields = {k: v for k, v in e.items() if k not in ("entity_number", "name", "position", "direction")}
            bp.add(e["name"], m["x"], m["y"] + dy, m["dir"], **fields)

    products = cell.products()
    a = analyse(cell, "late")
    duty = 0.05 if cell.centre == "chest" else 1.0           # mall cells idle once their chests are full
    demand = {k: v * cells * duty for k, v in a["in_per_side"].items()}
    supply = {k: v * cells for k, v in a["out_per_s"].items()}
    return Stack(name or f"{cell.name} x{cells}", build, tier, products, demand, supply, gap=1 if compact else 3)
