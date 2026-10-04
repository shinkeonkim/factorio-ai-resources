"""Compose a planet complex: a horizontal bus (6-lane groups + 2 gap rows, fluid groups at the bottom) with
stacks of cells standing on its north side, generated as one blueprint.

* Raw lanes start at the west end (x = 0) with a constant-combinator marker: those are the external inputs.
* Each cap input (a marker at the bottom of the stack) is tapped from a lane of that item that starts west of
  it: a splitter tap in the lane's group (the lanes above it dive under), crossings through the groups above
  (all six lanes dive), and the branch rises into the cap's feed column. Fluids climb with pipe-to-ground.
* A stack's products go back to the bus: each centre line runs south through the groups above its lane and
  starts that lane there, so stacks further east can tap it. Place producers west of consumers.
* Overlaps raise (the blueprint builder refuses two entities on one tile), so a layout that composes is free
  of collisions; lane capacity is checked against the stacks' declared demand.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from lib.fbp import Blueprint, N, E, S, W
from lib.main_bus import TIER as BUS_TIER, GROUP, GAP, PITCH

PTG_MAX = 10
LANE_PER_S = {"yellow": 15.0, "red": 30.0, "blue": 45.0, "turbo": 60.0}    # a bus row is a whole belt
FLUID_PER_S = 1200.0


@dataclass
class Stack:
    name: str
    build: callable                     # build(bp, tier): cap rows 0..7 (markers on row 8), cells at y < 0, x = 0
    tier: str
    products: list = field(default_factory=list)   # [(item, "item"|"fluid", x offset from the stack origin)]
    demand: dict = field(default_factory=dict)     # item -> items/s per feed column
    supply: dict = field(default_factory=dict)     # item -> items/s it puts on its lane
    gap: int = 3                        # free columns before the next stack


def _read(stack):
    """Build the stack alone; markers become feed columns, everything else is re-placed later."""
    bp = Blueprint(stack.name, game="2.0")
    stack.build(bp, stack.tier)
    feeds, keep = [], []
    for e in bp.entities:
        m = bp._meta[e["entity_number"]]
        if e["name"] == "constant-combinator":
            f = e["control_behavior"]["sections"]["sections"][0]["filters"][0]
            feeds.append((m["x"], f["name"]))
        else:
            fields = {k: v for k, v in e.items() if k not in ("entity_number", "name", "position", "direction")}
            keep.append((e["name"], m["x"], m["y"], m["dir"], m["w"], m["h"], fields))
    lo = min(k[1] for k in keep)
    hi = max(k[1] + k[4] - 1 for k in keep)
    return keep, feeds, lo, hi


def compose(label, layout, stacks, tier="red", y_bus=0, gap=2, tail=4, ptg_ok=lambda x: True, cover=None,
            fluid_plain=False):
    """cover = (entity, size, spacing): after composing, scatter that entity (e.g. lightning collectors on Fulgora)
    over the whole area on a `spacing` grid, each on the nearest free size x size spot."""
    belt, ug, spl = BUS_TIER[tier]
    bp = Blueprint(label, game="2.0")
    G = [y_bus + PITCH * g for g in range(len(layout))]
    lanes = []
    for g, grp in enumerate(layout):
        for i, item in enumerate(grp["lanes"]):
            if item:
                lanes.append(dict(item=item, g=g, i=i, row=G[g] + i, kind=grp["kind"], src=None, taps=[], load=0.0, supply=None))
    produced = {p[0] for s in stacks for p in s.products}
    for ln in lanes:
        if ln["item"] not in produced:
            ln["src"] = 0
    # ---- stacks
    x = 6                                       # room for the west-end markers and first taps
    placed = []
    cap_bottom = y_bus - gap                    # cap row 7
    for st in stacks:
        ents, feeds, lo, hi = _read(st)
        dx = x - lo
        dy = cap_bottom - 7
        for name, ex, ey, d, w, h, fields in ents:
            bp.add(name, ex + dx, ey + dy, d, **fields)
        placed.append((st, dx, [(fx + dx, item) for fx, item in feeds]))
        if len(placed) > 1:                               # bridge the power gap to the previous stack
            bp.add("medium-electric-pole", x - 1 - st.gap // 2, cap_bottom - 7)
        x = hi + dx + 1 + st.gap
    x_end = x + tail
    # ---- product lanes start at their producer
    sources = []
    for st, dx, _ in placed:
        for item, kind, off in st.products:
            x_out = dx + off
            cand = [ln for ln in lanes if ln["item"] == item and ln["src"] is None]
            if cand:                                       # start a new lane here
                ln = cand[0]
                ln["src"] = x_out
                ln["supply"] = st.supply.get(item, 0)
            else:                                          # join an existing lane (side-load / fluid riser)
                old = [ln for ln in lanes if ln["item"] == item and ln["src"] is not None and ln["src"] < x_out - 3]
                if not old:
                    raise ValueError(f"{st.name}: no bus lane for {item}")
                ln = min(old, key=lambda l: l["supply"] or 0)
                ln["supply"] = (ln["supply"] or 0) + st.supply.get(item, 0)
                if ln["kind"] == "fluid":
                    ln["taps"].append(x_out)              # surfaces there; its riser joins the stack's main
                    continue
            sources.append((ln, x_out))
    # ---- bus planner: per row, merged underground spans and tiles that must stay on the surface
    UGMAX = {"yellow": 4, "red": 6, "blue": 8, "turbo": 10}[tier]
    under = {}                 # row -> list[[a, b]] (entrance a, exit b)
    surf = {}                  # row -> set(x)
    gapcol = set()             # (x, y) of branch tiles in gap rows

    def merged(spans, a, b, surface):
        """spans with [a, b] merged in, or None if too long or it would bury a surface tile"""
        new, keep = [a, b], []
        for t in spans:
            if t[1] >= new[0] and t[0] <= new[1]:              # overlapping: one underground (touching is fine)
                new = [min(new[0], t[0]), max(new[1], t[1])]
            else:
                keep.append(t)
        if new[1] - new[0] - 1 > UGMAX or any(new[0] <= xx <= new[1] for xx in surface):
            return None
        return keep + [new]

    def plan_tap(ln, x, commit):
        """solid tap on lane ln at column x (branch goes north)"""
        g, i, r = ln["g"], ln["i"], ln["row"]
        changes = []
        for l2 in lanes:                                   # lanes above it in its group dive x-2 .. x+1
            if l2["kind"] == "solid" and l2["g"] == g and l2["i"] < i and l2["src"] is not None and l2["src"] < x - 2:
                changes.append(("u", l2["row"], x - 2, x + 1))
        for gg in range(g - 1, -1, -1):                     # crossings above: every lane dives x-1 .. x+1
            for l2 in lanes:
                if l2["kind"] == "solid" and l2["g"] == gg and l2["src"] is not None and l2["src"] < x - 1:
                    changes.append(("u", l2["row"], x - 1, x + 1))
        changes.append(("s", r, x - 2, x + 1))
        if i == 0:
            changes.append(("g", G[g] - 1, x - 1, x - 1))     # splitter top half in the gap row
        return _apply(changes, x, g, commit)

    def plan_source(ln, x, commit):
        g, i, r = ln["g"], ln["i"], ln["row"]
        changes = []
        for gg in range(0, g):
            for l2 in lanes:
                if l2["kind"] == "solid" and l2["g"] == gg and l2["src"] is not None and l2["src"] < x - 1:
                    changes.append(("u", l2["row"], x - 1, x + 1))
        for l2 in lanes:
            if l2["kind"] == "solid" and l2["g"] == g and l2["i"] < i and l2["src"] is not None and l2["src"] < x - 1:
                changes.append(("u", l2["row"], x - 1, x + 1))
        changes.append(("s", r, x, x + 1))
        return _apply(changes, x, g, commit)

    why = []

    def _apply(changes, x, g, commit):
        tmp = {row: [list(t) for t in sp] for row, sp in under.items()}
        for kind, row, a, b in changes:
            if kind == "u":
                res = merged(tmp.get(row, []), a, b, surf.get(row, ()))
                if res is None:
                    why.append(f"row {row}: underground {a}..{b} too long or over surface {sorted(t for t in surf.get(row, ()) if a - 9 <= t <= b + 9)}")
                    return False
                tmp[row] = res
        for kind, row, a, b in changes:
            if kind == "s":
                if any(t[0] <= xx <= t[1] for t in tmp.get(row, []) for xx in range(a, b + 1)):
                    why.append(f"row {row}: surface {a}..{b} inside underground {[t for t in tmp.get(row, []) if t[1] >= a - 2 and t[0] <= b + 2]}")
                    return False
                if any(xx in surf.get(row, ()) for xx in range(a, b + 1)):
                    why.append(f"row {row}: surface {a}..{b} already used")
                    return False
            if kind == "g" and (a, row) in gapcol:
                why.append(f"gap tile ({a},{row}) used"); return False
        branch = [(x, y) for gg in range(0, g) for y in (G[gg] + GROUP, G[gg] + GROUP + 1)] + [(x, G[0] - 1)]
        if any(t in gapcol for t in branch):
            why.append(f"branch column {x} gap rows used"); return False
        if commit:
            under.clear(); under.update(tmp)
            for kind, row, a, b in changes:
                if kind == "s":
                    surf.setdefault(row, set()).update(range(a, b + 1))
                if kind == "g":
                    gapcol.add((a, row))
            gapcol.update(branch)
        return True

    report = {"taps": [], "lanes": lanes, "x_end": x_end}
    for ln, sx in sources:
        if ln["kind"] == "solid" and not plan_source(ln, sx, True):
            raise ValueError(f"product lane {ln['item']} cannot start at x={sx} (crowded bus there)")
    all_feeds = sorted(((fx, item, st) for st, dx, feeds in placed for fx, item in feeds), key=lambda t: t[0])
    for fx, item, st in all_feeds:
        cand = [ln for ln in lanes if ln["item"] == item and ln["src"] is not None and ln["src"] < fx - 3]
        if not cand:
            raise ValueError(f"{st.name}: no bus lane carries {item} west of x={fx}")
        need = st.demand.get(item, 0)
        cand.sort(key=lambda l: l["load"] + need)
        if cand[0]["kind"] == "fluid":
            ln = cand[0]
            if (fx, G[0] - 1) in gapcol:
                raise ValueError(f"{st.name}: fluid riser at x={fx} collides with a branch")
            gapcol.update({(fx, G[0] - 1)} | {(fx, y) for gg in range(len(G)) for y in (G[gg] + GROUP, G[gg] + GROUP + 1)})
        else:
            ln = next((l for l in cand if plan_tap(l, fx, False)), None)
            if ln is None:
                raise ValueError(f"{st.name}: no {item} lane can be tapped at x={fx} without colliding: {why[-len(cand):]}")
            plan_tap(ln, fx, True)
        ln["load"] += need
        ln["taps"].append(fx)
        report["taps"].append((st.name, item, fx, ln["g"], ln["i"]))
    # ---- draw solid lanes from the plan
    for ln in lanes:
        if ln["kind"] != "solid" or ln["src"] is None:
            continue
        r = ln["row"]
        spans = under.get(r, [])
        inside = {xx for a, b in spans for xx in range(a + 1, b)}
        ends = {a: "input" for a, b in spans} | {b: "output" for a, b in spans}
        taps = set(ln["taps"])
        for xx in range(ln["src"], x_end):
            if xx in inside:
                continue
            if xx in ends:
                bp.add(ug, xx, r, E, type=ends[xx]); continue
            if xx + 1 in taps:                          # splitter column
                bp.add(spl, xx, r - 1, E); continue
            bp.add(belt, xx, r, E)
        if ln["src"] == 0:
            bp.add_marker(-1, r, {ln["item"]: 0})
    def column(xx, ya, yb, d):
        for y in range(ya, yb + 1):
            try:
                bp.add(belt, xx, y, d)
            except Exception as e:
                raise ValueError(f"branch x={xx} row {y}: {e}")
    for ln in [l for l in lanes if l["kind"] == "solid"]:
        g, r = ln["g"], ln["row"]
        for fx in ln["taps"]:
            column(fx, G[g], r - 1, N) if r - 1 >= G[g] else None
            if ln["i"] == 0:
                pass
            for gg in range(g - 1, -1, -1):
                column(fx, G[gg], G[gg] + GROUP + GAP - 1, N)
            column(fx, cap_bottom + 1, G[0] - 1, N)
    for ln, sx in sources:
        if ln["kind"] != "solid":
            continue
        g, r = ln["g"], ln["row"]
        column(sx, cap_bottom + 1, G[0] - 1, S)
        for gg in range(0, g):
            column(sx, G[gg], G[gg] + GROUP + GAP - 1, S)
        column(sx, G[g], r - 1, S)
    # ---- fluid lanes
    fl = [l for l in lanes if l["kind"] == "fluid" and l["src"] is not None]
    for ln in fl:
        others = [l2 for l2 in fl if l2["g"] == ln["g"] and l2["i"] > ln["i"]]
        avoid = {t for l2 in others for t in l2["taps"]} | {l2["src"] for l2 in others if l2["src"]}
        _fluid_line(bp, ln, x_end, avoid, G, cap_bottom, fluid_plain)
        if ln["src"] == 0:
            bp.add_marker(-1, ln["row"], {ln["item"]: 0})
    cap = {"solid": LANE_PER_S[tier], "fluid": FLUID_PER_S}
    report["warnings"] = [f"lane {l['item']} (group {l['g']}, row {l['i']}): demand {l['load']:.1f}/s > {cap[l['kind']]:.0f}/s"
                          for l in lanes if l["load"] > cap[l["kind"]] * 1.0001]
    report["warnings"] += [f"lane {l['item']} (group {l['g']}, row {l['i']}): supply {l['supply']:.1f}/s > {cap[l['kind']]:.0f}/s"
                           for l in lanes if l["supply"] and l["supply"] > cap[l["kind"]] * 1.0001]
    # power spine along the caps' top row: medium poles at most 7 apart, on free tiles
    y_sp = cap_bottom - 7
    last = -99
    for xx in range(-1, x_end + 1):
        if xx - last >= 7:
            for cand in range(xx, last, -1):
                if (cand, y_sp) not in bp._grid:
                    bp.add("medium-electric-pole", cand, y_sp)
                    last = cand
                    break
    if cover:
        name, size, spacing = cover
        ys = [k[1] for k in bp._grid]
        y_lo, y_hi = min(ys), max(ys)
        placed_cover = 0
        for gy in range(y_lo, y_hi + spacing, spacing):
            for gx in range(0, x_end + spacing, spacing):
                spot = None
                for rad in range(0, 10):
                    for dx in range(-rad, rad + 1):
                        for dy in (-rad, rad) if abs(dx) != rad else range(-rad, rad + 1):
                            x0, y0 = gx + dx, gy + dy
                            if all((x0 + i, y0 + j) not in bp._grid for i in range(size) for j in range(size)):
                                spot = (x0, y0); break
                        if spot: break
                    if spot: break
                if spot:
                    bp.add(name, *spot); placed_cover += 1
        report["cover"] = placed_cover
    report["lane_use"] = [(l["item"], l["g"], l["i"], l["src"], len(l["taps"]), round(l["load"], 2), l["supply"]) for l in lanes]
    return bp, report


def _fluid_line(bp, ln, x_end, avoid, G, cap_bottom, plain=False):
    """plain=True: a plain pipe all along (only when no other line is on a neighbouring row, e.g. Aquilo, where
    pipe-to-ground costs 150 kW of heat each); risers stay pipe-to-ground, which only connect at their open end."""
    r = ln["row"]
    pts = [ln["src"]] + sorted(t for t in ln["taps"] if t > ln["src"])
    for k, p in enumerate(pts):
        bp.add("pipe", p, r)
        if k > 0 or ln["src"] != 0:
            _fluid_vertical(bp, p, ln, G, cap_bottom)
    if plain:
        stops = set(pts)
        for x in range(pts[0] + 1, x_end):
            if x not in stops and (x, r) not in bp._grid:
                bp.add("pipe", x, r)
        return
    for a, b in zip(pts, pts[1:] + [x_end]):
        xx = a + 1                                       # pairs: W-facing at xx ... E-facing at end
        while xx < b - 1:
            if xx in avoid:
                raise ValueError(f"fluid line {ln['item']}: column {xx} is needed by a lower line's riser")
            end = min(xx + PTG_MAX, b - 1)
            while end > xx + 1 and (end in avoid or (end + 1 < b - 1 and end + 1 in avoid)):
                end -= 1
            bp.add("pipe-to-ground", xx, r, W)
            bp.add("pipe-to-ground", end, r, E)
            xx = end + 1


def _fluid_vertical(bp, x, ln, G, cap_bottom):
    """surfaced pipe at (x, lane row) <-> the cap above the bus: pipe-to-ground hops through every group"""
    g, r = ln["g"], ln["row"]
    if r > G[g]:
        bp.add("pipe-to-ground", x, r - 1, S)
        bp.add("pipe-to-ground", x, G[g] - 1, N)
    else:
        bp.add("pipe", x, G[g] - 1)
    for gg in range(g - 1, -1, -1):
        bp.add("pipe-to-ground", x, G[gg] + GROUP, S)
        bp.add("pipe-to-ground", x, G[gg] - 1, N)
    for y in range(cap_bottom + 1, G[0] - 1):
        bp.add("pipe", x, y)
