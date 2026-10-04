"""Heated, robot-fed stackable cells for Aquilo (every building that freezes has a heat pipe within one tile).

Same port logic, recipes and rates as lib/fstack (a FluidCell with bots=True), but its own columns. West half,
distance d from the centre column c, outwards:

    d = 0              heat pipe (full column)                      shared by both halves
    d = 1              centre main (if the cell has a centre fluid) -> d_port_c = 2, else d_port_c = 1
    d_port_c           centre-side port column: output pipe at the port row, heat pipe elsewhere
    machine            rotated so fluid inputs face outwards and fluid outputs face the centre
    d_pb               port column: pipe-to-ground (fluid in), input / output inserters, heat pipe elsewhere
    d_pb + 1           chests: requester beside the input inserter, passive provider beside the output inserter
    d_pb + 2           heat pipe (full column; every heat-pipe segment of the cell reaches it)
    per input main i:  entry (pipe-to-ground beside the main), main, heat pipe (full column)
Above every machine there are two gap rows: row A is heat pipe across the whole half (it joins every column of a
strip; the strips between fluid mains are joined where each main hops with a pipe-to-ground pair), row B holds
the poles and heat pipe. Items never ride belts:
robots move them (chests do not freeze), so the only freezable things are machines, inserters, pipes,
pipe-to-ground and roboports, all next to heat pipe by construction; lib/heat.check proves it."""
from __future__ import annotations

from lib.fbp import N, E, S, W
from lib.fstack import FluidCell, LH, TIERS, CHEST, slots, _bot_requests

HP = "heat-pipe"


class Geo:
    def __init__(self, cell: FluidCell):
        self.cell = cell
        L = cell.layout()
        self.cf = L["centre_fluid"]
        self.s = cell.s
        self.port_c = 2 if self.cf else 1
        self.mach = self.port_c + 1
        self.pb = self.mach + self.s
        self.chest = self.pb + 1
        self.hp = self.pb + 2
        self.mains = [f for f in cell.mains]
        self.entry = [self.hp + 1 + 3 * i for i in range(len(self.mains))]
        self.main = [e + 1 for e in self.entry]
        self.hpo = [m + 1 for m in self.main]
        self.c = self.hpo[-1] if self.mains else self.hp
        self.width = 2 * self.c + 1
        self.period = (self.s + 2) * cell.n             # two gap rows per machine: heat row A, pole row B


def build_cell(bp, cell: FluidCell, tier: str, y0: int):
    g = Geo(cell)
    t = TIERS[tier]
    c, s, P = g.c, g.s, g.period
    L = cell.layout()
    want, _, _ = slots(cell)
    n_in = max(1, want.get("inner", 1)) if cell.items_in else 0
    for sgn in (-1, 1):
        X = lambda d: c + sgn * d
        to_out, to_c = (W, E) if sgn < 0 else (E, W)       # inserter picks from the outer / the centre side
        f = L["facing"][sgn]
        ports = L["ports"][sgn]
        full = [g.hp] + g.hpo + ([0] if sgn < 0 else [])
        for y in range(y0, y0 + P):
            for d in full:
                bp.add(HP, X(d), y)
        # mains: plain pipe, except one pipe-to-ground hop per machine so heat pipe can cross the main there
        cross = {}                                             # main distance -> [(row, main index)]
        tops = [y0 + P - s - (s + 2) * k for k in range(cell.n)]

        b_rows = {tp - 1 for tp in tops}                       # pole rows: the poles would block the crossing

        def pick(prow, avoid_b=True):
            for r in range(y0 + 1, y0 + P - 1):
                if (r not in b_rows or not avoid_b) and not ({r - 1, r, r + 1} & prow):
                    return r
            raise ValueError(f"{cell.name}: no row for a heat crossing")

        for i, fl in enumerate(g.mains):
            prow = {tp + p.pos for tp in tops for p in ports if p.side == "belt" and p.fluid == fl}
            cross[g.main[i]] = [(pick(prow), i)]
        if g.cf:
            crow = {tp + p.pos for tp in tops for p in ports if p.side == "centre"}
            cross[1] = [(pick(crow, avoid_b=False), None)]          # port_c has no poles: B rows are fine
        mains = list(g.main) + ([1] if g.cf else [])
        for d in mains:
            hops = {r for r, _ in cross.get(d, [])}
            for y in range(y0, y0 + P):
                if y in hops:
                    bp.add(HP, X(d), y)
                elif y + 1 in hops:
                    bp.add("pipe-to-ground", X(d), y, N)          # continues above ground to the north
                elif y - 1 in hops:
                    bp.add("pipe-to-ground", X(d), y, S)
                else:
                    bp.add("pipe", X(d), y)
        cross_entry = {(g.entry[i], r) for d, lst in cross.items() for r, i in lst if i is not None}
        for (d, r) in cross_entry:
            if (X(d), r) not in bp._grid:
                bp.add(HP, X(d), r)                             # heat bridge through the entry column
        for k in range(cell.n):
            top = y0 + P - s - (s + 2) * k
            gap = top - 1
            row_a = top - 2
            left = X(g.mach + s - 1) if sgn < 0 else X(g.mach)
            bp.add(cell.machine, left, top, f, **({} if "furnace" in cell.machine else {"recipe": cell.recipe}))
            used_b, used_c = {}, {}
            for p in ports:
                if p.side == "belt":
                    used_b[top + p.pos] = p
                elif p.side == "centre":
                    used_c[top + p.pos] = p
                else:
                    raise ValueError(f"{cell.name}: gap-row ports are not supported in heated cells")
            for row, p in used_b.items():
                i = g.mains.index(p.fluid)
                bp.add("pipe-to-ground", X(g.pb), row, to_c)          # surfaces at the machine
                bp.add("pipe-to-ground", X(g.entry[i]), row, to_out)  # beside its main
            free = [top + r for r in range(s) if top + r not in used_b]
            # input inserter(s) on the first free rows, the output inserter on the last free row
            ins_rows = free[:n_in] if cell.items_in else []
            out_row = free[-1] if (cell.items_out and free[-1] not in ins_rows) else None
            extra = {}
            if cell.limit:
                extra["control_behavior"] = {"connect_to_logistic_network": True, "logistic_condition": {
                    "first_signal": {"type": "item", "name": cell.limit[0]}, "constant": cell.limit[1], "comparator": "<"}}
            for row in ins_rows:
                bp.add(t["ins"], X(g.pb), row, to_out, **extra)
                bp.add("requester-chest", X(g.chest), row, request_filters=_bot_requests(cell))
            if out_row is not None:
                bp.add(t["ins"], X(g.pb), out_row, to_c)
                bp.add(CHEST[tier], X(g.chest), out_row)
            taken_pb = set(used_b) | set(ins_rows) | ({out_row} if out_row is not None else set())
            for r in range(top, top + s):
                if r not in taken_pb:
                    bp.add(HP, X(g.pb), r)
                if r not in set(ins_rows) | ({out_row} if out_row is not None else set()):
                    bp.add(HP, X(g.chest), r)
            for row in range(top, top + s):                          # centre-side port column
                if row in used_c:
                    bp.add("pipe", X(g.port_c), row)                 # touches the centre main
                else:
                    bp.add(HP, X(g.port_c), row)
            # gap rows above the machine: A = heat pipe across, B = poles + heat pipe
            for d in range(0 if sgn < 0 else 1, c + 1):
                if d in g.main or d in full or (g.cf and d == 1):
                    continue
                for row in (row_a, gap):
                    if (X(d), row) in bp._grid:
                        continue
                    if row == gap and d == g.chest:
                        bp.add(t["pole"], X(d), row)
                    else:
                        bp.add(HP, X(d), row)


def build_cap(bp, cell: FluidCell, tier: str, rates_pm=None, rows=8):
    """Mains, the centre main and the full heat-pipe columns run down to the bottom edge; poles on row 0,
    a roboport (heated) in the middle; markers for the input fluids."""
    g = Geo(cell)
    t = TIERS[tier]
    c = g.c
    rates_pm = rates_pm or {}
    for sgn in (-1, 1):
        X = lambda d: c + sgn * d
        for y in range(rows):
            for d in [g.hp] + g.hpo + ([0] if sgn < 0 else []):
                bp.add(HP, X(d), y)
            for i, d in enumerate(g.main):
                bp.add("pipe", X(d), y)
            if g.cf:
                bp.add("pipe", X(1), y)
        for i, fl in enumerate(g.mains):
            if fl in cell.fluids_in:
                bp.add_marker(X(g.main[i]), rows, {fl: round(rates_pm.get(fl, 0))})
        bp.add(t["pole"], X(g.chest), 0)
        for d in range(g.port_c, g.pb + 1):                         # heat row joining the lowest machine's columns
            bp.add(HP, X(d), 0)
    if g.cf and g.cf in cell.fluids_in:
        bp.add_marker(c - 1, rows, {g.cf: round(rates_pm.get(g.cf, 0))})
    bp.add("roboport", c - g.hp + 2, 2)
    for d in (-2, 2):                                           # joins both halves' poles across the centre
        bp.add(TIERS[tier]["pole"], c + d, 1)


def stack(bp, cell, tier, n, rates_pm=None):
    build_cap(bp, cell, tier, rates_pm)
    for k in range(n):
        build_cell(bp, cell, tier, -Geo(cell).period * (k + 1))


def products(cell):
    g = Geo(cell)
    out = []
    for fl in cell.fluids_out:
        if fl == g.cf:
            out.append((fl, "fluid", g.c - 1))
        else:
            raise ValueError(f"{cell.name}: fluid output {fl} must face the centre")
    return out


def join_top(bp, cell, cells):
    g = Geo(cell)
    yt = -g.period * cells - 1
    if g.cf:
        for dx in (-1, 0, 1):
            bp.add("pipe", g.c + dx, yt)


def as_stack(cell: FluidCell, cells: int, tier="mid", name=None):
    from lib.complex import Stack
    from lib.fstack import analyse, late_rates

    def build(bp, t):
        stack(bp, cell, t, cells, late_rates(cell))
        join_top(bp, cell, cells)

    a = analyse(cell, "late")
    return Stack(name or f"{cell.name} x{cells}", build, tier, products(cell),
                 {k: v * cells for k, v in a["in_per_side"].items()},
                 {k: v * cells for k, v in a["out_per_s"].items()}, gap=4)
