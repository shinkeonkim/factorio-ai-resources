"""Dense robot-fed columns — the block community bases build most (base-design.md §3, decoded from the Vulcanus
mall's tungsten-plate columns): machines stacked with no gap rows, the fluid pipe touching their fluid ports
directly, one column for inserters and poles, one column of chests shared by the two mirrored halves.

    x:   0     1 .. s      s+1        s+2         s+3       s+4 .. 2s+3   2s+4
        main | machine  | ins+pole | chest     | ins+pole | machine     | main
             (inputs face the main)   requester / provider shared by both halves

Per machine block of s rows the inserter column holds the input inserter(s) (from the requester chest), the
output inserter (into the provider chest, stopped at ~2 minutes of stock) and a pole. Only recipes with at most
one fluid ingredient and no fluid result fit; everything item-side comes and goes by robot.
As a lib.complex.Stack: the blocks end on row 7 (no cap) and each main has its fluid marker on row 8, so a shelf
street feeds them.
"""
from __future__ import annotations

import math

from lib.complex import Stack
from lib.fbp import N, E, S, W
from lib.fstack import FluidCell, PORTS, ROT, DIRS, _rot_dir, _size, INSERTER, TIERS, rates, _bot_requests


def _facing(machine, side):
    """facing that turns every fluid input port of `machine` towards `side` (W or E); None if impossible"""
    ins = PORTS.get(machine, {}).get("in", [])
    for f in DIRS:
        if all(_rot_dir(d, f) == side for _, _, d in ins):
            return f
    return None


def fits(cell: FluidCell):
    """can this cell's recipe run in a dense column?"""
    return (len(cell.fluids_in) <= 1 and not cell.fluids_out and cell.items_out
            and (not cell.fluids_in or (_facing(cell.machine, W) and _facing(cell.machine, E))))


def _segment(cell: FluidCell, rows: int, tier: str):
    """inserter plan for `rows` blocks of `cell`"""
    s = _size(cell.machine)
    rt = rates(cell)                                       # per machine, per second
    ins = TIERS[tier]["ins"]
    n_in = max(1, math.ceil(sum(rt["in"][i] for i in cell.items_in) / INSERTER[ins] - 1e-9)) if cell.items_in else 0
    if cell.sink == "chest":
        n_in = min(n_in, 1)                                # mall machines idle most of the time
    ins_name = None                                        # tier inserter unless a faster one is needed to fit
    if n_in + 2 > s and cell.items_in:
        ins_name = "bulk-inserter"
        n_in = max(1, math.ceil(sum(rt["in"][i] for i in cell.items_in) / INSERTER[ins_name] - 1e-9))
    capped = n_in + 2 > s
    n_in = min(n_in, s - 2)                                # (capped: the machine runs below full speed)
    pole_row = s // 2                                      # the pole in the middle reaches 3 rows up and down
    free = [r for r in range(s) if r != pole_row]
    return dict(cell=cell, rows=rows, s=s, rt=rt, n_in=n_in, ins_name=ins_name, capped=capped, pole_row=pole_row,
                in_rows=free[:n_in], out_row=free[n_in], out_item=cell.items_out[0],
                out_rate=rt["out"][cell.items_out[0]] * 2 * rows)


def dense_column(segments, tier="mid", name=None, limit=True):
    """One column of several recipes that share the machine size and the fluid (or use none), bottom segment first:
    [(cell, rows), …]. Community foundry columns mix castings like this around one pipe."""
    segs = [_segment(c, r, tier) for c, r in segments if r > 0]
    s = segs[0]["s"]
    fl = segs[0]["cell"].fluids_in[0] if segs[0]["cell"].fluids_in else None
    assert all(g["s"] == s and (g["cell"].fluids_in[0] if g["cell"].fluids_in else None) == fl for g in segs)
    x_main = {W: 0} if fl else {}
    x0 = 1 if fl else 0                                    # west machine's left column
    xi = {W: x0 + s, E: x0 + s + 2}                        # inserter columns
    xc = x0 + s + 1                                        # chest column
    xm = {W: x0, E: x0 + s + 3}                            # machine left columns
    if fl:
        x_main[E] = xm[E] + s
    height = sum(g["rows"] for g in segs) * s

    def build(bp, t):
        tt = TIERS[t]
        y = 8                                              # the lowest block ends on row 7: no empty cap
        for g in segs:
            cell = g["cell"]
            for k in range(g["rows"]):
                y -= s
                top = y
                for side in (W, E):
                    f = _facing(cell.machine, side) if fl else N
                    kw = {} if "furnace" in cell.machine else {"recipe": cell.recipe}
                    bp.add(cell.machine, xm[side], top, f, **kw)
                    pick_chest, pick_mach = (E, W) if side == W else (W, E)
                    lim = {}
                    if cell.limit:                         # e.g. pentapod eggs: inputs only below a stock
                        lim = {"control_behavior": {"connect_to_logistic_network": True, "logistic_condition": {
                            "first_signal": {"name": cell.limit[0]}, "constant": cell.limit[1], "comparator": "<"}}}
                    for j in g["in_rows"]:                 # picks from the chest, drops into the machine
                        bp.add(g["ins_name"] or tt["ins"], xi[side], top + j, pick_chest, **lim)
                    cb = {"control_behavior": {"connect_to_logistic_network": True, "logistic_condition": {
                        "first_signal": {"name": g["out_item"]}, "constant": max(200, int(g["out_rate"] * 120)),
                        "comparator": "<"}}} if limit else {}
                    bp.add(tt["ins"], xi[side], top + g["out_row"], pick_mach, **cb)   # machine -> chest
                    bp.add(tt["pole"], xi[side], top + g["pole_row"])
                for j in g["in_rows"]:
                    bp.add("requester-chest", xc, top + j, request_filters=_bot_requests(cell))
                bp.add("passive-provider-chest", xc, top + g["out_row"])
        if fl:
            per_main = sum(g["rt"]["in"][fl] * g["rows"] for g in segs)
            for side in (W, E):
                for yy in range(8 - height, 8):
                    bp.add("pipe", x_main[side], yy)
                bp.add_marker(x_main[side], 8, {fl: round(per_main * 60)})   # each main fed from the street

    demand = {fl: sum(g["rt"]["in"][fl] * g["rows"] for g in segs)} if fl else {}   # per feed column (main)
    supply = {}
    for g in segs:
        supply[g["out_item"]] = supply.get(g["out_item"], 0) + g["out_rate"]
    st = Stack(name or " + ".join(f"{g['cell'].name} x{2 * g['rows']}" for g in segs) + " (dense)",
               build, tier, [], demand, supply, gap=1)
    st._dense = True
    st._capped = any(g["capped"] for g in segs)
    return st


def dense_stack(cell: FluidCell, rows: int, tier="mid", name=None, limit=True):
    """`rows` machine blocks on each half (2 * rows machines) of one recipe."""
    return dense_column([(cell, rows)], tier, name, limit)


def column_key(cell: FluidCell):
    """cells with the same key can share a dense column"""
    return (_size(cell.machine), cell.fluids_in[0] if cell.fluids_in else None)
