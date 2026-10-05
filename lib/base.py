"""Planet base: one compact rectangle, the way community planet bases are built (no planet-wide bus).

    frame (per planet: wall + turret rows, accumulator / lightning field, nothing)
    ┌──────────────────────────────────────────────┐
    │ shelf N   stacks of cells … silo, landing pad │   each shelf = a row of stacks standing on a short
    │ ─ street N (its own fluids, a few raw belts) ─│   street (lib/complex.compose) that carries only the
    │ …                                             │   fluids that shelf uses and, where needed, raw belts
    │ shelf 1   power, raw processing …             │
    │ ─ street 1 ────────────────────────────────── │
    └──────────────────────────────────────────────┘

* Every fluid lane of every shelf starts at the west edge, where a vertical trunk per fluid joins the same fluid in
  all shelves (producers feed their own lane, so a fluid made in one shelf reaches the others). Raw fluids enter at
  the bottom of their trunk.
* Lines are split into stacks of equal height and packed into shelves tallest-first (strip packing), so the
  rectangle stays full.
* Items move between blocks by robots: `robotize` gives every block input a requester chest feeding its belt
  column and every block output a passive provider chest at the end of its column, so belts stay inside blocks.
  Items listed as street lanes (e.g. scrap) stay on belts.
* A roboport grid and the power poles cover the whole rectangle; `power_fix` adds a pole beside anything unpowered.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, replace

from lib.complex import Stack, compose
from lib.fbp import Blueprint, N, E, S, W, ROOT, POLES
from lib.fstack import INSERTER, TIERS as FT

_REC = json.loads((ROOT / "skills/factorio-blueprint/data/recipes-space-age.json").read_text())["recipes"]
FLUIDS = {i["name"] for r in _REC.values() for i in r.get("ingredients", []) + r.get("results", []) if i.get("type") == "fluid"}
FLUIDS |= {"lava", "ammoniacal-solution", "fluorine", "lithium-brine", "crude-oil", "heavy-oil", "water", "steam"}
TRASH_SIGNAL = "signal-T"


@dataclass
class Shelf:
    stacks: list
    solid: tuple = ()                   # raw belt lanes kept in this shelf's street (e.g. scrap, stone)
    layout: list = None                 # computed by auto_layout when None
    owners: int = None                  # only the first `owners` stacks use the solid lanes (default: all)
    dry: bool = False                   # only stacks without fluids may join (raw belts enter across the west edge)

    def street(self):
        return self.layout if self.layout is not None else auto_layout(self.stacks, self.solid)


def _lanes(layout):
    return {i for g in layout for i in g["lanes"] if i}


def _depth(rate, ins):
    return max(1, min(4, math.ceil(rate / INSERTER[ins] - 1e-9)))


def robotize(st: Stack, keep=frozenset(), ins="bulk-inserter"):
    """Inputs and outputs of `st` by robots, except items in `keep` (street lanes) and fluids.

    input  (marker at (x, 8)):  belt column continues south to row 8+k-1, k inserters beside it drop onto it from
                                k requester chests (k from the column's demand)
    output (product column x):  belt continues south, k inserters take from it into passive provider chests
    The adapters sit east of the column, or west if that side is taken. Returns the wrapped Stack and its depth."""
    keep = set(keep)
    outs = [(it, x) for it, kind, x in st.products if kind == "item" and it not in keep]
    depth = 1
    for it, _ in outs:
        depth = max(depth, _depth(st.supply.get(it, 0), ins))

    def build(bp, t):
        st.build(bp, t)
        feeds, fluid_cols = [], set()
        for e in list(bp.entities):
            if e["name"] != "constant-combinator":
                continue
            m = bp._meta[e["entity_number"]]
            f = e["control_behavior"]["sections"]["sections"][0]["filters"][0]
            if f["name"] in FLUIDS or f["name"] in keep:
                fluid_cols.add(m["x"])
                continue
            feeds.append((e["entity_number"], m["x"], f["name"]))
        bp.remove([n for n, _, _ in feeds])
        reserved = fluid_cols | {x for it, kind, x in st.products if kind != "item" or it in keep}
        tb = FT[t]["belt"]

        def side(x, k):
            for sgn in (1, -1):
                cols = (x + sgn, x + 2 * sgn)
                if any(c in reserved for c in cols):
                    continue
                if all((c, 8 + j) not in bp._grid for c in cols for j in range(k)):
                    return sgn
            return None                                    # no room beside it: chest straight below instead

        req = lambda item: {"sections": [{"index": 1, "filters": [
            {"index": 1, "name": item, "quality": "normal", "comparator": "=", "count": 100}]}]}
        cols = sorted([(x, item, "in") for _, x, item in feeds] + [(x, item, "out") for item, x in outs])
        plan = {}
        for x, item, kind in cols:                         # side adapters first (they need two free columns)
            k = _depth((st.demand if kind == "in" else st.supply).get(item, 0), ins)
            sgn = side(x, k)
            plan[x] = (sgn, k)
            reserved.add(x)
            if sgn:
                reserved.update({x + sgn, x + 2 * sgn})
        for x, item, kind in cols:
            sgn, k = plan[x]
            if sgn is None:
                d = N if kind == "in" else S
                bp.add(tb, x, 8, d)
                if kind == "in":
                    bp.add(ins, x, 9, S)                   # picks from the chest below, drops on the belt
                    bp.add("requester-chest", x, 10, request_filters=req(item))
                else:
                    bp.add(ins, x, 9, N)                   # picks from the belt end above
                    bp.add("passive-provider-chest", x, 10)
                continue
            for j in range(k):
                bp.add(tb, x, 8 + j, N if kind == "in" else S)
                if kind == "in":
                    bp.add(ins, x + sgn, 8 + j, E if sgn > 0 else W)      # picks from the chest, drops on the belt
                    bp.add("requester-chest", x + 2 * sgn, 8 + j, request_filters=req(item))
                else:
                    bp.add(ins, x + sgn, 8 + j, W if sgn > 0 else E)      # picks from the belt, drops in the chest
                    bp.add("passive-provider-chest", x + 2 * sgn, 8 + j)

    new = replace(st, build=build, products=[p for p in st.products if not (p[1] == "item" and p[0] not in keep)])
    d_in = max([_depth(v, ins) for k, v in st.demand.items() if k not in FLUIDS and k not in keep] + [1])
    new._depth = max(depth, d_in, 3)
    return new


def _paste(dst, src, dx, dy):
    for e in src.entities:
        m = src._meta[e["entity_number"]]
        fields = {k: v for k, v in e.items() if k not in ("entity_number", "name", "position", "direction")}
        dst.add(e["name"], m["x"] + dx, m["y"] + dy, m["dir"], **fields)


def bbox(bp):
    xs = [x for x, _ in bp._grid]; ys = [y for _, y in bp._grid]
    return min(xs), min(ys), max(xs), max(ys)


def stack_size(st):
    """(width incl. its gap, height) of a stack as compose places it"""
    from lib.complex import _read
    ents, feeds, lo, hi = _read(st)
    ys = [e[2] for e in ents] + [e[2] + e[5] - 1 for e in ents]
    return hi - lo + 1 + st.gap, max(ys) - min(ys) + 1


def split_line(cell, n, height, make, tier="mid"):
    """A line of n cells as stacks no taller than `height` (as even as possible)."""
    h1 = stack_size(make(cell, 1, tier))[1]
    h2 = stack_size(make(cell, 2, tier))[1]
    per = h2 - h1
    m = max(1, (height - (h1 - per)) // per) if per > 0 else n
    k = math.ceil(n / m)
    sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
    return [make(cell, s, tier) for s in sizes if s]


_FL = {}


def fluids_of(st):
    """fluids the stack takes or makes (cached per stack object)"""
    if id(st) not in _FL:
        from lib.complex import _read
        _, feeds, _, _ = _read(st)
        _FL[id(st)] = ({i for _, i in feeds if i in FLUIDS} | {p[0] for p in st.products if p[1] == "fluid"}, st)
    return _FL[id(st)][0]


def wet(st):
    """does the stack take or make a fluid?"""
    return bool(fluids_of(st))


def pack(stacks, width, start=()):
    """First-fit decreasing height into shelves of at most `width` tiles; `start` = [(used width, [stacks], dry)] of
    shelves that already hold something (they are filled first). Returns lists of stacks (bottom first)."""
    items = sorted(((stack_size(s), i, s) for i, s in enumerate(stacks)), key=lambda t: (-t[0][1], t[1]))
    shelves = [[u, list(lst), dry] for u, lst, dry in start]
    for (w, h), _, st in items:
        for sh in shelves:
            if sh[0] + w <= width and not (sh[2] and wet(st)):
                sh[0] += w; sh[1].append(st); break
        else:
            shelves.append([6 + 4 + w, [st], False])
    return [sh[1] for sh in shelves]


def compose_base(label, shelves, tier="blue", street_gap=1, ins="bulk-inserter"):
    """Shelves bottom → top into one rectangle, fluids joined by trunks at the west edge. Returns (bp, info)."""
    bp = Blueprint(label, game="2.0")
    y_top = None
    rows = []                                   # (fluid, y, load, supply)
    widths = []
    for sh in shelves:
        layout = sh.street()
        keep = _lanes(layout)
        own = len(sh.stacks) if sh.owners is None else sh.owners
        stacks = [robotize(s, keep if i < own else keep - _lanes([{"lanes": list(sh.solid)}]), ins)
                  for i, s in enumerate(sh.stacks)]
        gap = max(getattr(s, "_depth", 1) for s in stacks) + 2
        part, rep = compose(label, layout, stacks, tier=tier, gap=gap, fluid_plain=True, fluid_west=True)
        if rep["warnings"]:
            raise ValueError("; ".join(rep["warnings"]))
        x0, y0, x1, y1 = bbox(part)
        dy = 0 if y_top is None else (y_top - street_gap - 1 - y1)
        _paste(bp, part, 0, dy)
        rows += [(f, r + dy, ld, sp) for f, r, ld, sp in rep["fluid_rows"]]
        widths.append(rep["x_end"])
        y_top = y0 + dy
    raw = trunks(bp, rows)
    return bp, {"widths": widths, "raw": raw, "fluid_rows": rows}


def _trunk_x(k):
    """trunk columns: banks of five (x = -3, -5, … -11), then a two-column relay gap, then the next bank"""
    return -3 - 2 * (k % 5) - 11 * (k // 5)


def _connect_lane(bp, y, k):
    """lane end at (0, y) → trunk k: pipe at -1, then pipe-to-ground hops under the trunks in between (a hop spans
    one bank; consecutive hops meet back to back in the relay gap)."""
    xt = _trunk_x(k)
    bp.add("pipe", -1, y)
    if k == 0:
        bp.add("pipe", -2, y)
        return
    start = -2
    bank = k // 5
    for b in range(bank + 1):
        last = b == bank
        end = xt + 1 if last else -12 - 11 * b          # exit: beside the trunk, or the relay gap's east column
        if end == start:                                 # trunk right beside the relay: a plain pipe joins them
            bp.add("pipe", start, y)
            return
        bp.add("pipe-to-ground", start, y, E)
        bp.add("pipe-to-ground", end, y, W)
        start = end - 1
        if last:
            return


def trunks(bp, rows):
    """Vertical pipes west of the shelves joining every shelf's lane of the same fluid (more than one trunk when the
    lanes' total load needs it). Fluids nobody produces enter at the top of their trunk (the north edge stays free
    of raw belts, which come from the west into the bottom shelves). Returns {fluid: [(trunk x, top y)]}."""
    from lib.complex import FLUID_PER_S
    by = {}
    for f, y, ld, sp in rows:
        by.setdefault(f, []).append((y, ld, sp))
    out = {}
    k = 0
    for f, lst in by.items():
        load = sum(l for _, l, _ in lst)
        made = sum(s for _, _, s in lst) > 0
        n = max(1, math.ceil(load / FLUID_PER_S - 1e-9))
        if len(lst) < 2 and made:
            continue                                     # produced and used in one shelf only: no trunk needed
        for g in [lst[i::n] for i in range(n)]:
            if not g:
                continue
            xt = _trunk_x(k)
            ys = sorted(y for y, _, _ in g)
            for y in ys:
                _connect_lane(bp, y, k)
            for y in range(ys[0], ys[-1] + 1):
                if (xt, y) not in bp._grid:
                    bp.add("pipe", xt, y)
            if not made:
                out.setdefault(f, []).append((xt, ys[0]))
            k += 1
    return out


def place_gates(bp, gates, tier="mid"):
    """Gate blocks (e.g. raw-ore intake) below the core, side by side from the west: their input markers end up on
    the south edge, where extend_inputs leads them out through the frame."""
    if not gates:
        return
    x0, y0, x1, y1 = bbox(bp)
    x = 8
    for st in gates:
        part = Blueprint(st.name, game="2.0")
        st.build(part, st.tier)
        gx0, gy0, gx1, gy1 = bbox(part)
        _paste(bp, part, x - gx0, y1 + 2 - gy0)
        x += gx1 - gx0 + 1 + st.gap


def extend_inputs(bp, raw, depth, tier="mid"):
    """Lead every external input out through the frame: raw fluid trunks run north and end in a marker; markers on
    the south edge (gates) get a belt / pipe southwards, markers on the west edge (raw belt lanes) a belt
    westwards. Call before the frame so the frame leaves gaps for them."""
    belt = FT[tier]["belt"]
    y_top = bbox(bp)[1]
    for f, ends in raw.items():
        for xt, y in ends:
            for yy in range(y - 1, y_top - depth - 1, -1):
                if (xt, yy) not in bp._grid:
                    bp.add("pipe", xt, yy)
            bp.add_marker(xt, y_top - depth - 1, {f: 0})
    y_bot = bbox(bp)[3]
    for e in list(bp.entities):
        if e["name"] != "constant-combinator":
            continue
        m = bp._meta[e["entity_number"]]
        sig = e["control_behavior"]["sections"]["sections"][0]["filters"][0]
        if m["x"] == -1:                                  # raw lane of a shelf street, entering from the west
            bp.remove([e["entity_number"]])
            for xx in range(-1, -1 - depth, -1):
                bp.add(belt, xx, m["y"], E)
            bp.add_marker(-1 - depth, m["y"], {sig["name"]: sig.get("count", 0)})
        elif m["y"] >= y_bot - 1 and sig["name"] not in FLUIDS:   # gate input on the south edge
            bp.remove([e["entity_number"]])
            for yy in range(m["y"], m["y"] + depth):
                bp.add(belt, m["x"], yy, N)
            bp.add_marker(m["x"], m["y"] + depth, {sig["name"]: sig.get("count", 0)})


# ------------------------------------------------------------------------------------- grid services
def _free(bp, x, y, w, h):
    return all((x + i, y + j) not in bp._grid for i in range(w) for j in range(h))


def _spot(bp, gx, gy, w, h, rmax=12):
    for rad in range(rmax + 1):
        for dx in range(-rad, rad + 1):
            for dy in ((-rad, rad) if abs(dx) != rad else range(-rad, rad + 1)):
                if _free(bp, gx + dx, gy + dy, w, h):
                    return gx + dx, gy + dy
    return None


def roboports(bp, spacing=40, box=None):
    """A roboport near every grid point (logistic area 50 x 50, so a 40 grid leaves slack for displaced spots)."""
    x0, y0, x1, y1 = box or bbox(bp)
    have = [(bp._meta[e["entity_number"]]["x"], bp._meta[e["entity_number"]]["y"]) for e in bp.entities if e["name"] == "roboport"]
    n = 0
    for gy in range(y0 + spacing // 2, y1 + spacing // 2, spacing):
        for gx in range(x0 + spacing // 2, x1 + spacing // 2, spacing):
            if any(abs(hx - gx) < spacing // 2 and abs(hy - gy) < spacing // 2 for hx, hy in have):
                continue
            s = _spot(bp, gx, gy, 4, 4)
            if s:
                bp.add("roboport", *s); have.append(s); n += 1
    return n


def _electric(bp):
    from blueprint import type_of, _ELECTRIC_TYPES, _NOT_ELECTRIC
    return [e for e in bp.entities if type_of(e["name"]) in _ELECTRIC_TYPES and e["name"] not in _NOT_ELECTRIC]


def power_fix(bp, pole="medium-electric-pole"):
    """A pole beside every electric entity that no pole covers, then a chain joining every pole group."""
    sup = POLES[pole]["supply"]
    poles = [e for e in bp.entities if e["name"] in POLES]

    def covered(m):
        for p in poles:
            pm = bp._meta[p["entity_number"]]
            s = POLES[p["name"]]["supply"]
            cx, cy = pm["x"] + pm["w"] / 2, pm["y"] + pm["h"] / 2
            if m["x"] < cx + s and m["x"] + m["w"] > cx - s and m["y"] < cy + s and m["y"] + m["h"] > cy - s:
                return True
        return False

    added = 0
    for e in _electric(bp):
        m = bp._meta[e["entity_number"]]
        if covered(m):
            continue
        r = int(sup)
        best = None
        for x in range(m["x"] - r, m["x"] + m["w"] + r):
            for y in range(m["y"] - r, m["y"] + m["h"] + r):
                if (x, y) not in bp._grid:
                    d = abs(x - (m["x"] + m["w"] / 2)) + abs(y - (m["y"] + m["h"] / 2))
                    if best is None or d < best[0]:
                        best = (d, x, y)
        if best is None:
            raise ValueError(f"no room for a pole beside {e['name']} at ({m['x']},{m['y']})")
        num = bp.add(pole, best[1], best[2])
        poles.append(bp._ent(num) if hasattr(bp, "_ent") else bp.entities[-1])
        added += 1
    return added


def link_poles(bp, pole="medium-electric-pole"):
    """Join pole groups that are out of reach of each other with a chain of poles over free tiles (BFS)."""
    from collections import deque
    reach = POLES[pole]["reach"]
    step = int(reach)
    while True:
        ps = [e for e in bp.entities if e["name"] in POLES]
        pos = {e["entity_number"]: (e["position"]["x"], e["position"]["y"], POLES[e["name"]]["reach"]) for e in ps}
        # groups by reach
        seen, groups = set(), []
        for n in pos:
            if n in seen:
                continue
            g, q = [], [n]; seen.add(n)
            while q:
                a = q.pop(); g.append(a)
                ax, ay, ar = pos[a]
                for b, (bx, by, br) in pos.items():
                    if b not in seen and math.dist((ax, ay), (bx, by)) <= min(ar, br):
                        seen.add(b); q.append(b)
            groups.append(g)
        if len(groups) <= 1:
            return
        groups.sort(key=len, reverse=True)
        main, other = groups[0], groups[1]
        d, a, b = min((math.dist(pos[i][:2], pos[j][:2]), i, j) for i in other for j in main)
        (ax, ay), (bx, by) = pos[a][:2], pos[b][:2]
        last = (ax, ay)
        steps = max(1, math.ceil(d / (reach - 2)))
        for i in range(1, steps):
            px, py = ax + (bx - ax) * i / steps, ay + (by - ay) * i / steps
            cand = sorted(((math.dist((px, py), (x + .5, y + .5)), x, y)
                           for x in range(int(px) - 3, int(px) + 4) for y in range(int(py) - 3, int(py) + 4)
                           if (x, y) not in bp._grid and math.dist(last, (x + .5, y + .5)) <= reach - 0.1))
            if not cand:
                raise ValueError(f"cannot join pole groups near ({px:.0f},{py:.0f})")
            _, x, y = cand[0]
            bp.add(pole, x, y)
            last = (x + .5, y + .5)


# ------------------------------------------------------------------------------------------ frames
def wall_and_turrets(bp, box=None, margin=4, spacing=4, gun_every=3, walls=2, ammo="firearm-magazine", tier="mid"):
    """Defence ring (Gleba): `walls` rows of stone wall outside a row of turrets every `spacing` tiles — laser
    turrets, and every `gun_every`-th a gun turret with an inserter and a requester chest for `ammo` on its inner
    side — with medium poles between them. Anything already crossing the ring (input pipes / belts) leaves a gap."""
    ins = FT[tier]["ins"]
    x0, y0, x1, y1 = box or bbox(bp)
    tx0, ty0, tx1, ty1 = x0 - margin - 2, y0 - margin - 2, x1 + margin, y1 + margin       # turret row (2x2)
    spots = [(x, ty0, "N") for x in range(tx0, tx1 + 1, spacing)] + [(x, ty1, "S") for x in range(tx0, tx1 + 1, spacing)]
    spots += [(tx0, y, "W") for y in range(ty0 + spacing, ty1, spacing)] + [(tx1, y, "E") for y in range(ty0 + spacing, ty1, spacing)]
    n = 0
    for k, (x, y, side) in enumerate(spots):
        if not _free(bp, x, y, 2, 2):
            continue
        if k % gun_every == 0:
            # inserter + chest on the inner side, picking from the chest and dropping into the turret
            ix, iy, d, cx, cy = {"N": (x, y + 2, S, x, y + 3), "S": (x, y - 1, N, x, y - 2),
                                 "W": (x + 2, y, E, x + 3, y), "E": (x - 1, y, W, x - 2, y)}[side]
            if _free(bp, ix, iy, 1, 1) and _free(bp, cx, cy, 1, 1):
                bp.add("gun-turret", x, y)
                bp.add(ins, ix, iy, d)
                bp.add("requester-chest", cx, cy, request_filters={"sections": [{"index": 1, "filters": [
                    {"index": 1, "name": ammo, "quality": "normal", "comparator": "=", "count": 50}]}]})
                n += 1
                continue
        bp.add("laser-turret", x, y)
        n += 1
        px, py = (x + 2, y) if side in "NS" else (x, y + 2)
        if _free(bp, px, py, 1, 1):
            bp.add("medium-electric-pole", px, py)
    wn = 0
    for w in range(walls):
        a0, b0, a1, b1 = tx0 - 2 - w, ty0 - 2 - w, tx1 + 3 + w, ty1 + 3 + w
        ring = [(x, b0) for x in range(a0, a1 + 1)] + [(x, b1) for x in range(a0, a1 + 1)]
        ring += [(a0, y) for y in range(b0 + 1, b1)] + [(a1, y) for y in range(b0 + 1, b1)]
        for x, y in ring:
            if (x, y) not in bp._grid:
                bp.add("stone-wall", x, y); wn += 1
    return n, wn


def field_ring(bp, tile, size=12, rings=1, margin=2, box=None):
    """A band of `tile(bp, x, y)` blocks (size x size) all around the rectangle (Fulgora: accumulators +
    lightning collector + substation per tile). Returns the number of tiles placed."""
    x0, y0, x1, y1 = box or bbox(bp)
    n = 0
    for r in range(rings):
        ax0 = x0 - margin - size * (r + 1)
        ay0 = y0 - margin - size * (r + 1)
        nx = math.ceil((x1 + margin + 1 + size * r - ax0) / size)      # tiles from the west band to the east band
        ny = math.ceil((y1 + margin + 1 + size * r - ay0) / size)
        for i in range(nx + 1):
            for j in range(ny + 1):
                if i in (0, nx) or j in (0, ny):
                    x, y = ax0 + size * i, ay0 + size * j
                    if _free(bp, x, y, size, size):
                        tile(bp, x, y); n += 1
    return n


def auto_layout(stacks, solid=()):
    """Street for one shelf: a lane per fluid the shelf uses (more lanes when one pipe is not enough), two per
    6-row group so no two lanes touch (plain pipes, and the lane starts at the west edge never touch), plus the
    solid lanes given (raw belts such as scrap). No fluids and no solids: no street at all."""
    from lib.complex import _read, FLUID_PER_S
    need, made = {}, []
    for st in stacks:
        _, feeds, _, _ = _read(st)
        for _, item in feeds:
            if item in FLUIDS:
                need[item] = need.get(item, 0) + st.demand.get(item, 0)
        made += [p[0] for p in st.products if p[1] == "fluid"]
    fl = []
    for item in list(dict.fromkeys(made + list(need))):
        fl += [item] * max(1, math.ceil(need.get(item, 0) / FLUID_PER_S - 1e-9))
    groups = []
    for i in range(0, len(solid), 6):
        groups.append({"kind": "solid", "lanes": (list(solid[i:i + 6]) + [None] * 6)[:6]})
    for i in range(0, len(fl), 2):
        chunk = fl[i:i + 2]
        groups.append({"kind": "fluid", "lanes": [chunk[0], None, None, chunk[1] if len(chunk) > 1 else None, None, None]})
    return groups


def shelf_width(sh):
    return 10 + sum(stack_size(s)[0] for s in sh.stacks)


def plan_shelves(stacks, aspect=1.4, fixed=(), street=8):
    """Pack stacks into shelves, trying widths around the square root of the total area and keeping the one that
    wastes least (empty shelf ends) while staying near `aspect` (width / height). `fixed` are Shelf objects that
    must exist (e.g. one with raw belt lanes); they come first, at the bottom, and are filled up with other stacks."""
    sizes = {id(s): stack_size(s) for s in list(stacks) + [x for f in fixed for x in f.stacks]}
    area = sum(w * h for w, h in sizes.values())
    w_min = max([w for w, _ in sizes.values()]) + 10
    w_fix = max([shelf_width(f) for f in fixed] + [0])
    start = [(shelf_width(f), f.stacks, f.dry) for f in fixed]
    best = None
    lo = max(w_min, w_fix, int(math.sqrt(area * aspect) * 0.7))
    for width in range(lo, max(int(math.sqrt(area * aspect) * 1.6), lo) + 2, 2):
        shelves = pack(stacks, width, start)
        used = [10 + sum(sizes[id(s)][0] for s in sh) for sh in shelves]
        hs = [max(sizes[id(s)][1] for s in sh) + 6 + 8 * math.ceil(len(set().union(*map(fluids_of, sh))) / 2)
              for sh in shelves]
        W, H = max(used), sum(hs)
        waste = sum((W - u) * h for u, h in zip(used, hs)) + sum(
            (h - street - sizes[id(s)][1]) * sizes[id(s)][0] for sh, h in zip(shelves, hs) for s in sh)
        score = waste + abs(math.log(W / H / aspect)) * area * 0.5
        if best is None or score < best[0]:
            best = (score, shelves)
    out = []
    for i, g in enumerate(best[1]):
        out.append(Shelf(g, fixed[i].solid, owners=len(fixed[i].stacks), dry=fixed[i].dry) if i < len(fixed) else Shelf(g))
    return out


def build_base(label, stacks, frame=None, fixed=(), aspect=1.4, tier="blue", robot_spacing=40, post=None, gates=(),
               finish=None):
    """The whole base: shelves → rectangle → raw inputs led out through the frame → roboports and poles over the
    core → frame(bp, core_box) (returns its thickness) → poles for everything. Returns (bp, info)."""
    shelves = plan_shelves(stacks, aspect, fixed)
    bp, info = compose_base(label, shelves, tier)
    place_gates(bp, gates)
    core = bbox(bp)
    info["core"] = core
    thick = frame.thickness if frame else 0
    extend_inputs(bp, info["raw"], thick + 2)
    roboports(bp, robot_spacing, core)
    if post:
        post(bp)
    if frame:
        info["frame"] = frame(bp, core)
    power_fix(bp)
    link_poles(bp)
    if finish:
        info["finish"] = finish(bp)
    bp.connect_poles()
    info["shelves"] = [[s.name for s in sh.stacks] for sh in shelves]
    return bp, info


class Frame:
    """A ring around the core: `build(bp, core_box)`; `thickness` tiles outside the core box."""
    def __init__(self, build, thickness):
        self.build, self.thickness = build, thickness

    def __call__(self, bp, core):
        return self.build(bp, core)


def plan_shelves(stacks, aspect=1.4, fixed=(), street=8):
    """Pack stacks into shelves, trying widths around the square root of the total area and keeping the one that
    wastes least (empty shelf ends) while staying near `aspect` (width / height). `fixed` are Shelf objects that
    must exist (e.g. one with raw belt lanes); they come first, at the bottom, and are filled up with other stacks."""
    sizes = {id(s): stack_size(s) for s in list(stacks) + [x for f in fixed for x in f.stacks]}
    area = sum(w * h for w, h in sizes.values())
    w_min = max([w for w, _ in sizes.values()]) + 10
    w_fix = max([shelf_width(f) for f in fixed] + [0])
    start = [(shelf_width(f), f.stacks, f.dry) for f in fixed]
    best = None
    lo = max(w_min, w_fix, int(math.sqrt(area * aspect) * 0.7))
    for width in range(lo, max(int(math.sqrt(area * aspect) * 1.6), lo) + 2, 2):
        shelves = pack(stacks, width, start)
        used = [10 + sum(sizes[id(s)][0] for s in sh) for sh in shelves]
        hs = [max(sizes[id(s)][1] for s in sh) + 6 + 8 * math.ceil(len(set().union(*map(fluids_of, sh))) / 2)
              for sh in shelves]
        W, H = max(used), sum(hs)
        waste = sum((W - u) * h for u, h in zip(used, hs)) + sum(
            (h - street - sizes[id(s)][1]) * sizes[id(s)][0] for sh, h in zip(shelves, hs) for s in sh)
        score = waste + abs(math.log(W / H / aspect)) * area * 0.5
        if best is None or score < best[0]:
            best = (score, shelves)
    out = []
    for i, g in enumerate(best[1]):
        out.append(Shelf(g, fixed[i].solid, owners=len(fixed[i].stacks), dry=fixed[i].dry) if i < len(fixed) else Shelf(g))
    return out


def build_base(label, stacks, frame=None, fixed=(), aspect=1.4, tier="blue", robot_spacing=40, post=None, gates=(),
               finish=None):
    """The whole base: shelves → rectangle → raw inputs led out through the frame → roboports and poles over the
    core → frame(bp, core_box) (returns its thickness) → poles for everything. Returns (bp, info)."""
    shelves = plan_shelves(stacks, aspect, fixed)
    bp, info = compose_base(label, shelves, tier)
    place_gates(bp, gates)
    core = bbox(bp)
    info["core"] = core
    thick = frame.thickness if frame else 0
    extend_inputs(bp, info["raw"], thick + 2)
    roboports(bp, robot_spacing, core)
    if post:
        post(bp)
    if frame:
        info["frame"] = frame(bp, core)
    power_fix(bp)
    link_poles(bp)
    if finish:
        info["finish"] = finish(bp)
    bp.connect_poles()
    info["shelves"] = [[s.name for s in sh.stacks] for sh in shelves]
    return bp, info


class Frame:
    """A ring around the core: `build(bp, core_box)`; `thickness` tiles outside the core box."""
    def __init__(self, build, thickness):
        self.build, self.thickness = build, thickness

    def __call__(self, bp, core):
        return self.build(bp, core)


def defence_frame(**kw):
    """wall_and_turrets as a Frame (thickness: margin + turret + gap + walls)"""
    margin, walls = kw.get("margin", 4), kw.get("walls", 2)
    return Frame(lambda bp, core: wall_and_turrets(bp, core, **kw), margin + 2 + 2 + walls)


def scatter(bp, name, size, spacing, box):
    """`name` (size x size) on the nearest free spot to every point of a `spacing` grid over `box`"""
    x0, y0, x1, y1 = box
    n = 0
    for gy in range(y0 + spacing // 2, y1 + 1, spacing):
        for gx in range(x0 + spacing // 2, x1 + 1, spacing):
            sp = _spot(bp, gx, gy, size, size, 10)
            if sp:
                bp.add(name, *sp); n += 1
    return n


def lightning_tile(bp, x0, y0):
    """12 x 12: a lightning collector (catches strikes within its range, 1 GJ buffer), a substation and 34
    accumulators (5 MJ each)"""
    bp.add("lightning-collector", x0, y0)
    bp.add("substation", x0 + 6, y0 + 6)
    for ax in range(0, 12, 2):
        for ay in range(0, 12, 2):
            if (ax, ay) not in ((0, 0), (6, 6)):
                bp.add("accumulator", x0 + ax, y0 + ay)


def field_frame(rings=1):
    """Fulgora: a band of lightning tiles all around the core, plus collectors scattered over the core so every
    building is protected (lightning hits the tallest / nearest rod within range)."""
    def build(bp, core):
        n = field_ring(bp, lightning_tile, 12, rings, 2, core)
        c = scatter(bp, "lightning-collector", 2, 36, core)
        x0, y0, x1, y1 = core                    # pole ring in the gap: joins the band's substations to the core
        ring = [(x, y0 - 1) for x in range(x0 - 1, x1 + 2, 7)] + [(x, y1 + 1) for x in range(x0 - 1, x1 + 2, 7)]
        ring += [(x0 - 1, y) for y in range(y0 - 1, y1 + 2, 7)] + [(x1 + 1, y) for y in range(y0 - 1, y1 + 2, 7)]
        for x, y in ring:
            if (x, y) not in bp._grid:
                bp.add("medium-electric-pole", x, y)
        return n, c
    return Frame(build, 12 * rings + 2)
