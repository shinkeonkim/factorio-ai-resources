"""Planet base: one dense rectangle, built the way the top community bases are
(skills/factorio-blueprint/references/base-design.md).

    frame (per planet: mines / walls / turrets, lightning band, heat, or nothing)
    ┌──────────────────────────────────────────────────────────┐
 →  │ shelf: island part │ island part │ post │ island part …  │   each island makes its own fluids
 →  │ ── street: this shelf's fluids + short belts ──────────── │   (lava → molten iron → castings, …)
 →  │ …                                                        │   and keeps its internal items on belts
    └──────────────────────────────────────────────────────────┘
 →  inputs only on the edge: raw fluids / belts from the west per shelf, ores through gates on the south edge,
    each ending in an underground pair with a display panel and a marker (count = per minute)

* **Islands**: a group of lines that share fluids and intermediates (molten iron + its castings, carbon +
  tungsten carbide, …). An island too wide for a shelf is split into parts that each carry their own producers,
  so fluids never cross the base. Items made and used only inside one island stay on short street belts
  (no robot round trip); everything else leaves through a provider chest and arrives through a requester chest.
* **Dense**: compact caps, one-tile gaps, roboport posts between blocks instead of roboports on every stack,
  shelves packed tallest-first at the width that wastes least.
* **Self-regulating**: every provider-chest output stops while the network holds about two minutes of it
  (logistic condition), by-products (stone, overflow) ride belts into voids on the same shelf.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, replace

from lib.complex import Stack, compose, _read
from lib.fbp import Blueprint, N, E, S, W, ROOT, POLES
from lib.fstack import INSERTER, TIERS as FT

_REC = json.loads((ROOT / "skills/factorio-blueprint/data/recipes-space-age.json").read_text())["recipes"]
FLUIDS = {i["name"] for r in _REC.values() for i in r.get("ingredients", []) + r.get("results", []) if i.get("type") == "fluid"}
FLUIDS |= {"lava", "ammoniacal-solution", "fluorine", "lithium-brine", "crude-oil", "heavy-oil", "water", "steam"}
LANE = 45.0                   # items/s on one street belt (blue)


# ------------------------------------------------------------------------------------------------ islands
@dataclass
class Island:
    """Lines that share fluids / intermediates. `lines` = [(FluidCell, cells)] producers first; `extra` = stack
    factories (tier -> Stack) handed out to the parts in turn; `waste` = (item, sink(rate_per_lane, lanes, tier) ->
    [Stack]) for a
    by-product that rides a street belt into voids in the same part (stone, recycler overflow); `raw` = raw items
    that enter this island's shelf on belts from the west (scrap). When an island is split, every part gets at
    least one cell of each fluid-producing line, so each part makes its own fluids."""
    name: str
    lines: list
    extra: list = field(default_factory=list)
    waste: tuple = None
    raw: tuple = ()              # raw items that arrive on street belts from the west (scrap), lanes sized per part
    make: callable = None


@dataclass
class Part:
    island: Island
    stacks: list
    lanes: tuple                 # solid lanes this part needs in its street (waste, raw, internal items)
    keep: set                    # items that stay on belts for this part's stacks


def _feeds(st):
    if id(st) not in _FEEDS:
        _, feeds, _, _ = _read(st)
        _FEEDS[id(st)] = ([i for _, i in feeds], st)
    return _FEEDS[id(st)][0]


_SIZE, _FEEDS = {}, {}


def stack_size(st):
    """(width incl. its gap, height) of a stack as compose places it (cached per stack object)"""
    if id(st) not in _SIZE:
        ents, feeds, lo, hi = _read(st)
        ys = [e[2] for e in ents] + [e[2] + e[5] - 1 for e in ents]
        _SIZE[id(st)] = (hi - lo + 1 + st.gap, max(ys) - min(ys) + 1, st)
    return _SIZE[id(st)][:2]


def split_line(cell, n, height, make, tier="mid", max_cells=None):
    """A line of n cells as stacks no taller than `height` and of at most `max_cells` cells (as even as possible)."""
    h1 = stack_size(make(cell, 1, tier))[1]
    h2 = stack_size(make(cell, 2, tier))[1]
    per = h2 - h1
    m = max(1, (height - (h1 - per)) // per) if per > 0 else n
    if max_cells:
        m = max(1, min(m, max_cells))
    k = math.ceil(n / m)
    sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
    return [make(cell, s, tier) for s in sizes if s]


def island_parts(isl: Island, k, height, tier, outside):
    """Split an island into k self-sufficient parts. `outside` = items consumed by other islands."""
    from lib.fstack import as_stack
    make = isl.make or (lambda c, n, t: as_stack(c, n, t, compact=True))
    parts = []
    for i in range(k):
        stacks = []
        counts = []
        for li, (cell, n) in enumerate(isl.lines):            # remainders rotate, so single cells spread out
            counts.append(n // k + (1 if (i - li) % k < n % k else 0))
        fluid_maker = [bool(cell.fluids_out and not cell.items_out) for cell, _ in isl.lines]
        mine = [f(tier) for j, f in enumerate(isl.extra) if j % k == i]
        consumed = {x for st in mine for x in _feeds(st) if x in FLUIDS}
        for (cell, n), ni, fm in zip(isl.lines, counts, fluid_maker):
            if ni and not fm:
                consumed |= set(cell.fluids_in)
        grow = True
        while grow:                                         # producers of producers (heavy oil -> lubricant)
            grow = False
            for (cell, n), fm in zip(isl.lines, fluid_maker):
                if fm and set(cell.fluids_out) & consumed and not set(cell.fluids_in) <= consumed:
                    consumed |= set(cell.fluids_in); grow = True
        for idx, ((cell, n), ni, fm) in enumerate(zip(isl.lines, counts, fluid_maker)):
            if fm:                                          # every part makes the fluids its own lines use
                ni = max(1, ni) if set(cell.fluids_out) & consumed else 0
            cap = None
            if isl.waste:                                   # one by-product belt must carry a whole stack's waste
                one = make(cell, 1, tier).supply.get(isl.waste[0], 0)
                cap = int(LANE // one) if one > 0 else None
            if ni:
                stacks += split_line(cell, ni, height, make, tier, cap)
        stacks += mine
        lanes = []
        for item in isl.raw:
            rate = sum(s.demand.get(item, 0) * _feeds(s).count(item) for s in stacks)
            if rate > 0:
                lanes += [item] * max(1, math.ceil(rate / LANE - 1e-9))
        if isl.waste:
            item, sink = isl.waste
            makers = [s for s in stacks if s.supply.get(item, 0) > 0]
            rate = sum(s.supply[item] for s in makers)
            if makers:
                n = max(len(makers), math.ceil(rate / LANE - 1e-9))   # one lane (and one void) per maker
                stacks += sink(rate / n, n, tier)
                lanes += [item] * n
        made, used = {}, {}
        for s in stacks:
            for it, kind, _ in s.products:
                if kind == "item":
                    made[it] = made.get(it, 0) + s.supply.get(it, 0)
            for it in _feeds(s):
                if it not in FLUIDS:
                    used[it] = used.get(it, 0) + s.demand.get(it, 0)
        internal = [it for it in made if it in used and it not in outside and it not in lanes and it not in isl.raw]
        for it in internal:
            lanes += [it] * max(1, math.ceil(max(made[it], used[it]) / LANE - 1e-9))
        if not stacks:
            continue
        parts.append(Part(isl, stacks, tuple(lanes), set(lanes)))
    return parts


def consumers_outside(islands):
    """item -> set of island names that consume it"""
    from lib.fstack import as_stack
    users = {}
    for isl in islands:
        make = isl.make or (lambda c, n, t: as_stack(c, n, t, compact=True))
        stacks = [make(c, 1, "mid") for c, _ in isl.lines] + [f("mid") for f in isl.extra]
        for s in stacks:
            for it in _feeds(s):
                users.setdefault(it, set()).add(isl.name)
    return users


# ------------------------------------------------------------------------------------------ robots
def _depth(rate, ins):
    return max(1, min(4, math.ceil(rate / INSERTER[ins] - 1e-9)))


def _limit(item, rate):
    """stop an output while the network holds about two minutes of it"""
    return {"connect_to_logistic_network": True, "logistic_condition": {
        "first_signal": {"name": item}, "constant": max(200, int(rate * 120)), "comparator": "<"}}


def robotize(st: Stack, keep=frozenset(), ins="bulk-inserter", gate=True):
    """Inputs and outputs of `st` by robots, except items in `keep` (street lanes) and fluids.

    input  (marker at (x, 8)):  belt column continues south, k inserters beside it drop onto it from k requester
                                chests (k from the column's demand); or one chest straight below when the sides are
                                taken
    output (product column x):  belt continues south, k inserters take from it into passive provider chests; each
                                stops while the network holds ~2 minutes of the item (gate=True)
    The stack keeps no roboports of its own (the base places posts)."""
    keep = set(keep)
    outs = [(it, x) for it, kind, x in st.products if kind == "item" and it not in keep]

    def build(bp, t):
        st.build(bp, t)
        bp.remove([e["entity_number"] for e in bp.entities if e["name"] == "roboport"])
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
            return None

        req = lambda item: {"sections": [{"index": 1, "filters": [
            {"index": 1, "name": item, "quality": "normal", "comparator": "=", "count": 100}]}]}
        cols = sorted([(x, item, "in") for _, x, item in feeds] + [(x, item, "out") for item, x in outs])
        plan = {}
        for x, item, kind in cols:
            k = _depth((st.demand if kind == "in" else st.supply).get(item, 0), ins)
            sgn = side(x, k)
            plan[x] = (sgn, k)
            reserved.add(x)
            if sgn:
                reserved.update({x + sgn, x + 2 * sgn})
        for x, item, kind in cols:
            sgn, k = plan[x]
            cb = {"control_behavior": _limit(item, st.supply.get(item, 0))} if (kind == "out" and gate) else {}
            if sgn is None:
                bp.add(tb, x, 8, N if kind == "in" else S)
                if kind == "in":
                    bp.add(ins, x, 9, S)                   # picks from the chest below, drops on the belt
                    bp.add("requester-chest", x, 10, request_filters=req(item))
                else:
                    bp.add(ins, x, 9, N, **cb)             # picks from the belt end above
                    bp.add("passive-provider-chest", x, 10)
                continue
            for j in range(k):
                bp.add(tb, x, 8 + j, N if kind == "in" else S)
                if kind == "in":
                    bp.add(ins, x + sgn, 8 + j, E if sgn > 0 else W)
                    bp.add("requester-chest", x + 2 * sgn, 8 + j, request_filters=req(item))
                else:
                    bp.add(ins, x + sgn, 8 + j, W if sgn > 0 else E, **cb)
                    bp.add("passive-provider-chest", x + 2 * sgn, 8 + j)

    new = replace(st, build=build, products=[p for p in st.products if not (p[1] == "item" and p[0] not in keep)],
                  gap=1)
    d_out = max([_depth(st.supply.get(it, 0), ins) for it, _ in outs] + [0])
    item_feeds = [i for i in _feeds(st) if i not in FLUIDS and i not in keep]
    d_in = max([_depth(st.demand.get(i, 0), ins) for i in item_feeds] + [0])
    new._depth = max(d_out, d_in, 3) if (outs or item_feeds) else 0
    return new


def post_stack(height, tier="mid"):
    """Roboport post between blocks: a roboport half-way up the shelf and a pole column down to the cap row."""
    y_r = -max(4, height // 2)

    def build(bp, t):
        bp.add("roboport", 0, y_r)
        for y in range(6, y_r + 4, -6):
            bp.add(FT[t]["pole"], 1, y)
        if (1, y_r + 4) not in bp._grid:
            bp.add(FT[t]["pole"], 1, y_r + 4)
    return Stack("Roboport post", build, tier, [], {}, gap=1)


# ----------------------------------------------------------------------------------------- composing
def auto_layout(stacks, solid=(), plain=False):
    """Street for one shelf: the solid lanes given, then a lane per fluid the shelf uses (more when one pipe is not
    enough), six per 6-row group as pipe-to-ground runs, or two per group as plain pipes that never touch
    (plain=True, for Aquilo where every pipe-to-ground costs heat). Nothing to carry: no street."""
    from lib.complex import FLUID_PER_S
    need, made = {}, []
    for st in stacks:
        for item in _feeds(st):
            if item in FLUIDS:
                need[item] = need.get(item, 0) + st.demand.get(item, 0)
        made += [p[0] for p in st.products if p[1] == "fluid"]
    fl = []
    for item in list(dict.fromkeys(made + list(need))):
        fl += [item] * max(1, math.ceil(need.get(item, 0) / FLUID_PER_S - 1e-9))
    groups = []
    for i in range(0, len(solid), 6):
        groups.append({"kind": "solid", "lanes": (list(solid[i:i + 6]) + [None] * 6)[:6]})
    if not plain:
        for i in range(0, len(fl), 6):
            groups.append({"kind": "fluid", "lanes": (fl[i:i + 6] + [None] * 6)[:6]})
        return groups
    for i in range(0, len(fl), 2):
        chunk = fl[i:i + 2]
        groups.append({"kind": "fluid", "lanes": [chunk[0], None, None, chunk[1] if len(chunk) > 1 else None, None, None]})
    return groups


def _paste(dst, src, dx, dy):
    for e in src.entities:
        m = src._meta[e["entity_number"]]
        fields = {k: v for k, v in e.items() if k not in ("entity_number", "name", "position", "direction")}
        dst.add(e["name"], m["x"] + dx, m["y"] + dy, m["dir"], **fields)


def bbox(bp):
    xs = [x for x, _ in bp._grid]; ys = [y for _, y in bp._grid]
    return min(xs), min(ys), max(xs), max(ys)


def _shelf_stacks(parts, posts, tier, ins):
    """robotized stacks of the parts in order, roboport posts every ~44 tiles"""
    out, used, next_post = [], 6, 20
    height = max(stack_size(s)[1] for p in parts for s in p.stacks)
    for p in parts:
        for s in p.stacks:
            r = robotize(s, p.keep, ins)
            w = stack_size(r)[0]
            if posts and used + w > next_post:
                out.append(post_stack(height, tier)); used += 5; next_post = used + 48
            out.append(r); used += w
    return out


def street_rows(parts):
    """rows a shelf of these parts needs under its stacks: lane groups (8 rows each) + adapter rows"""
    fluids, solid, adapters = set(), 0, 0
    for p in parts:
        solid += len(p.lanes)
        for s in p.stacks:
            fluids |= {i for i in _feeds(s) if i in FLUIDS} | {q[0] for q in s.products if q[1] == "fluid"}
            if any(i not in FLUIDS and i not in p.keep for i in _feeds(s)) or any(
                    k == "item" and it not in p.keep for it, k, _ in s.products):
                adapters = 5
    return 8 * (math.ceil(solid / 6) + math.ceil(len(fluids) / 6)) + adapters + 2


def pack(parts, width):
    """first-fit decreasing height of parts into shelves of at most `width` tiles"""
    size = {id(p): (sum(stack_size(s)[0] for s in p.stacks), max(stack_size(s)[1] for s in p.stacks)) for p in parts}
    shelves = []
    for p in sorted(parts, key=lambda p: -size[id(p)][1]):
        w = size[id(p)][0]
        for sh in shelves:
            if sh[0] + w <= width:
                sh[0] += w; sh[1].append(p); break
        else:
            shelves.append([10 + w, [p]])
    return [sh[1] for sh in shelves], size


def plan(islands, height, aspect=1.4, tier="mid"):
    """Choose the shelf width (and how many parts each island splits into) that wastes least near `aspect`."""
    users = consumers_outside(islands)
    outside_of = {isl.name: {it for it, who in users.items() if who - {isl.name}} for isl in islands}
    cache = {}

    def parts_of(isl, k):
        if (isl.name, k) not in cache:
            cache[(isl.name, k)] = island_parts(isl, k, height, tier, outside_of[isl.name])
        return cache[(isl.name, k)]

    whole = {isl.name: sum(stack_size(s)[0] for p in parts_of(isl, 1) for s in p.stacks) for isl in islands}
    area = sum(stack_size(s)[0] * stack_size(s)[1] for isl in islands for p in parts_of(isl, 1) for s in p.stacks)
    best = None
    w_lo = max(60, int(math.sqrt(area * aspect) * 0.7))
    for width in range(w_lo, int(math.sqrt(area * aspect) * 1.8) + 2, 4):
        parts = []
        for isl in islands:
            k = max(1, math.ceil(whole[isl.name] / (width - 10)))
            ps = parts_of(isl, k)
            if any(sum(stack_size(s)[0] for s in p.stacks) > width - 10 for p in ps):
                ps = parts_of(isl, k + 1)
            parts += ps
        shelves, size = pack(parts, width)
        used = [10 + sum(size[id(p)][0] for p in sh) for sh in shelves]
        hs = [max(size[id(p)][1] for p in sh) + street_rows(sh) for sh in shelves]
        Wd, H = max(used), sum(hs)
        waste = sum((Wd - u) * h for u, h in zip(used, hs)) + sum(
            (h - size[id(p)][1]) * size[id(p)][0] for sh, h in zip(shelves, hs) for p in sh)
        score = waste + abs(math.log(Wd / H / aspect)) * area * 0.5
        if best is None or score < best[0]:
            best = (score, shelves)
    return best[1]


def compose_base(label, shelves, tier="blue", street_gap=1, ins="bulk-inserter", posts=True, plain=False):
    """Shelves (lists of parts) bottom → top into one rectangle. Returns (bp, info)."""
    bp = Blueprint(label, game="2.0")
    y_top = None
    names = []
    for parts in shelves:
        stacks = _shelf_stacks(parts, posts, "mid", ins)
        layout = auto_layout(stacks, tuple(l for p in parts for l in p.lanes), plain)
        gap = max(getattr(s, "_depth", 0) for s in stacks) + 2
        part, rep = compose(label, layout, stacks, tier=tier, gap=gap, fluid_plain=plain)
        if rep["warnings"]:
            raise ValueError("; ".join(rep["warnings"]))
        x0, y0, x1, y1 = bbox(part)
        dy = 0 if y_top is None else (y_top - street_gap - 1 - y1)
        _paste(bp, part, 0, dy)
        y_top = y0 + dy
        names.append([s.name for s in stacks if s.name != "Roboport post"])
    return bp, {"shelves": names}


def _floatable(st):
    """a stack that needs nothing from a street: no fluids, no belt lanes (robots bring and take everything)"""
    return not any(i in FLUIDS for i in _feeds(st)) and not any(k == "fluid" for _, k, _ in st.products)


def place_floaters(bp, stacks, box, margin=1):
    """Put robot-fed, fluid-free stacks into the empty space of the core (above short blocks, ends of shelves):
    bottom-left first fit over a prefix-sum grid of occupied tiles. Returns the stacks that found no room."""
    x0, y0, x1, y1 = box
    W, H = x1 - x0 + 1, y1 - y0 + 1

    def table():
        occ = [[0] * (W + 1) for _ in range(H + 1)]
        for (x, y) in bp._grid:
            if x0 <= x <= x1 and y0 <= y <= y1:
                occ[y - y0 + 1][x - x0 + 1] = 1
        for j in range(1, H + 1):
            row, prev = occ[j], occ[j - 1]
            acc = 0
            for i in range(1, W + 1):
                acc += row[i]
                row[i] = acc + prev[i]
        return occ

    def empty(occ, i, j, w, h):                            # i, j = top-left (0-based) incl. margin
        if i < 0 or j < 0 or i + w > W or j + h > H:
            return False
        return occ[j + h][i + w] - occ[j][i + w] - occ[j + h][i] + occ[j][i] == 0

    left = []
    for st in sorted(stacks, key=lambda s: -stack_size(s)[0] * stack_size(s)[1]):
        part = Blueprint(st.name, game="2.0")
        st.build(part, st.tier)
        gx0, gy0, gx1, gy1 = bbox(part)
        w, h = gx1 - gx0 + 1 + 2 * margin, gy1 - gy0 + 1 + 2 * margin
        occ = table()
        spot = None
        for j in range(H - h, -1, -1):                    # bottom first
            for i in range(0, W - w + 1):
                if empty(occ, i, j, w, h):
                    spot = (i, j); break
            if spot:
                break
        if not spot:
            left.append(st); continue
        _paste(bp, part, x0 + spot[0] + margin - gx0, y0 + spot[1] + margin - gy0)
    return left


def place_gates(bp, gates):
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


def extend_inputs(bp, depth, tier="mid", plain=False):
    """Lead every external input out through the frame (`depth` tiles): west-edge markers (raw lanes of a street)
    run west, south-edge markers (gates) run south. Each line ends in an underground pair (belt) / pipe-to-ground
    pair (fluid) whose outer piece is what the player connects to, with the marker and a display panel beyond it.
    Call before the frame, so the frame leaves gaps where the lines pass."""
    belt, ug = FT[tier]["belt"], FT[tier]["ug"]
    x0, y0, x1, y1 = bbox(bp)
    for e in list(bp.entities):
        if e["name"] != "constant-combinator":
            continue
        m = bp._meta[e["entity_number"]]
        sig = e["control_behavior"]["sections"]["sections"][0]["filters"][0]
        item, count = sig["name"], sig.get("count", 0)
        fluid = item in FLUIDS
        if m["x"] == -1:
            y = m["y"]
            bp.remove([e["entity_number"]])
            end = -1 - depth                                # outer piece
            if fluid and not plain:
                # pipe-to-ground pairs only (lanes on neighbouring rows must not touch): the first piece opens east
                # onto the street's west pipe-to-ground, relays meet open end to open end
                x = -1
                while True:
                    far = max(end, x - 10)
                    bp.add("pipe-to-ground", x, y, E); bp.add("pipe-to-ground", far, y, W)
                    if far == end:
                        break
                    x = far - 1
                bp.add_marker(end - 1, y, {item: count})
                bp.add_panel(end - 2, y, item, "Input")
                continue
            for xx in range(-1, end + 3, -1):
                bp.add("pipe" if fluid else belt, xx, y, **({} if fluid else {"direction": E}))
            if fluid:
                bp.add("pipe-to-ground", end + 3, y, E); bp.add("pipe-to-ground", end, y, W)
            else:
                bp.add(ug, end + 3, y, E, type="output"); bp.add(ug, end, y, E, type="input")
            bp.add_marker(end - 1, y, {item: count})
            bp.add_panel(end - 2, y, item, "Input")
        elif m["y"] >= y1 - 1 and not fluid:                # gate input on the south edge
            x, y = m["x"], m["y"]
            bp.remove([e["entity_number"]])
            end = y + depth
            for yy in range(y, end - 2):
                bp.add(belt, x, yy, N)
            bp.add(ug, x, end - 2, N, type="output"); bp.add(ug, x, end + 1, N, type="input")
            bp.add_marker(x, end + 2, {item: count})
            bp.add_panel(x, end + 3, item, "Input")


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


LOGISTIC = ("requester-chest", "passive-provider-chest", "buffer-chest", "active-provider-chest", "storage-chest",
            "rocket-silo", "cargo-landing-pad")


def roboports(bp, box=None):
    """A roboport wherever a logistic chest is outside every roboport's 50 x 50 area (placed on the nearest free
    4x4 spot, preferring the chest's own neighbourhood)."""
    have = [(bp._meta[e["entity_number"]]["x"] + 2, bp._meta[e["entity_number"]]["y"] + 2)
            for e in bp.entities if e["name"] == "roboport"]
    n = 0
    for e in list(bp.entities):
        if e["name"] not in LOGISTIC:
            continue
        m = bp._meta[e["entity_number"]]
        cx, cy = m["x"] + m["w"] / 2, m["y"] + m["h"] / 2
        if any(abs(hx - cx) <= 25 and abs(hy - cy) <= 25 for hx, hy in have):
            continue
        s = _spot(bp, int(cx) - 2, int(cy) - 2, 4, 4, 18)
        if s:
            bp.add("roboport", *s); have.append((s[0] + 2, s[1] + 2)); n += 1
    return n


def _electric(bp):
    from blueprint import type_of, _ELECTRIC_TYPES, _NOT_ELECTRIC
    return [e for e in bp.entities if type_of(e["name"]) in _ELECTRIC_TYPES and e["name"] not in _NOT_ELECTRIC]


def power_fix(bp, pole="medium-electric-pole"):
    """A pole beside every electric entity that no pole covers."""
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
        bp.add(pole, best[1], best[2])
        poles.append(bp.entities[-1])
        added += 1
    return added


def link_poles(bp, pole="medium-electric-pole"):
    """Join pole groups that are out of reach of each other with a straight chain of poles on free tiles."""
    reach = POLES[pole]["reach"]
    while True:
        ps = [e for e in bp.entities if e["name"] in POLES]
        pos = {e["entity_number"]: (e["position"]["x"], e["position"]["y"], POLES[e["name"]]["reach"]) for e in ps}
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


def density(bp, box):
    """entities per tile inside `box` (the core) — community bases reach 0.3-0.45"""
    x0, y0, x1, y1 = box
    n = sum(1 for e in bp.entities if x0 <= e["position"]["x"] <= x1 + 1 and y0 <= e["position"]["y"] <= y1 + 1)
    return n / ((x1 - x0 + 1) * (y1 - y0 + 1))


def build_base(label, islands, height, frame=None, aspect=1.4, tier="blue", gates=(), finish=None, posts=True,
               controls=None, plain=False, float_dry=True):
    """The whole base: islands → parts → shelves → rectangle → gates → inputs led out through the frame →
    roboport holes filled → frame → controls(bp) (circuits that need the whole picture) → poles → finish.
    Returns (bp, info)."""
    shelves = plan(islands, height, aspect)
    floaters = []
    if float_dry:                                           # fluid-free robot stacks fill the gaps afterwards
        parts = [p for sh in shelves for p in sh]
        for p in parts:
            if not p.keep:
                floaters += [s for s in p.stacks if _floatable(s)]
                p.stacks = [s for s in p.stacks if not _floatable(s)]
        parts = [p for p in parts if p.stacks]
        area = sum(stack_size(s)[0] * stack_size(s)[1] for p in parts for s in p.stacks) * 1.6 + \
            sum(stack_size(s)[0] * stack_size(s)[1] for s in floaters) * 1.15
        width = max([int(math.sqrt(area * aspect))] + [10 + sum(stack_size(s)[0] for s in p.stacks) for p in parts])
        shelves, _ = pack(parts, width) if parts else ([], None)
    bp, info = compose_base(label, shelves, tier, posts=posts, plain=plain) if shelves else (Blueprint(label, game="2.0"), {"shelves": []})
    if floaters:
        robo = [robotize(s, set(), "bulk-inserter") for s in floaters]
        if bp.entities:
            x0, y0, x1, y1 = bbox(bp)
        else:
            x0, y0, x1, y1 = -1, 0, width, 0
        x1 = max(x1, x0 + width - 1)
        spare = sum(stack_size(s)[0] * stack_size(s)[1] for s in robo) * 1.5 / (x1 - x0 + 1)
        top = y0 - int(spare) - max(stack_size(s)[1] for s in robo) - 4
        left = place_floaters(bp, robo, (x0, top, x1, y1))
        if left:
            raise ValueError(f"no room for {[s.name for s in left]}")
        info["floaters"] = len(floaters)
        info["shelves"].append([s.name for s in floaters])
    place_gates(bp, gates)
    core = bbox(bp)
    info["core"] = core
    extend_inputs(bp, (frame.thickness if frame else 0) + 4, plain=plain)
    roboports(bp)
    if frame:
        info["frame"] = frame(bp, core)
    if controls:
        info["controls"] = controls(bp)
    power_fix(bp)
    link_poles(bp)
    if finish:
        info["finish"] = finish(bp)
    bp.connect_poles()
    info["density"] = round(density(bp, core), 2)
    return bp, info


# ------------------------------------------------------------------------------------------ frames
class Frame:
    """A ring around the core: `build(bp, core_box)`; `thickness` tiles outside the core box."""
    def __init__(self, build, thickness):
        self.build, self.thickness = build, thickness

    def __call__(self, bp, core):
        return self.build(bp, core)


def wall_and_turrets(bp, box=None, margin=4, spacing=4, gun_every=3, walls=2, ammo="firearm-magazine", tier="mid",
                     mines=0):
    """Defence ring (Gleba): optional land-mine rows outside, `walls` rows of stone wall, a row of turrets every
    `spacing` tiles inside them — laser turrets, every `gun_every`-th a gun turret fed from a requester chest (its
    inserter stops at 500 magazines in the network) — with medium poles between them. Lines already crossing the
    ring (inputs) leave gaps."""
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
    mn = 0
    for r in range(mines):                                  # mine rows outside the walls, every other tile
        a0, b0, a1, b1 = tx0 - 3 - walls - 2 * r, ty0 - 3 - walls - 2 * r, tx1 + 4 + walls + 2 * r, ty1 + 4 + walls + 2 * r
        ring = [(x, b0) for x in range(a0, a1 + 1, 2)] + [(x, b1) for x in range(a0, a1 + 1, 2)]
        ring += [(a0, y) for y in range(b0 + 2, b1, 2)] + [(a1, y) for y in range(b0 + 2, b1, 2)]
        for x, y in ring:
            if (x, y) not in bp._grid:
                bp.add("land-mine", x, y); mn += 1
    return n, wn, mn


def defence_frame(**kw):
    """wall_and_turrets as a Frame (thickness: margin + turret + gap + walls + mine rows)"""
    margin, walls, mines = kw.get("margin", 4), kw.get("walls", 2), kw.get("mines", 0)
    return Frame(lambda bp, core: wall_and_turrets(bp, core, **kw), margin + 2 + 2 + walls + 2 * mines)


def field_ring(bp, tile, size=12, rings=1, margin=2, box=None):
    """A band of `tile(bp, x, y)` blocks (size x size) all around the rectangle. Returns the tiles placed."""
    x0, y0, x1, y1 = box or bbox(bp)
    n = 0
    for r in range(rings):
        ax0 = x0 - margin - size * (r + 1)
        ay0 = y0 - margin - size * (r + 1)
        nx = math.ceil((x1 + margin + 1 + size * r - ax0) / size)
        ny = math.ceil((y1 + margin + 1 + size * r - ay0) / size)
        for i in range(nx + 1):
            for j in range(ny + 1):
                if i in (0, nx) or j in (0, ny):
                    x, y = ax0 + size * i, ay0 + size * j
                    if _free(bp, x, y, size, size):
                        tile(bp, x, y); n += 1
    return n


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
    building is protected (lightning hits the nearest rod within range)."""
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


# --------------------------------------------------------------------------------------- controls
def power_alarm(bp, accumulator_num, message="Power low", threshold=20):
    """Programmable speaker + map alert while the accumulator charge (signal A) is below `threshold` %, wired to
    the given accumulator (which outputs signal A)."""
    m = bp._meta[accumulator_num]
    acc = bp._ent(accumulator_num)
    acc["control_behavior"] = {"output_signal": {"type": "virtual", "name": "signal-A"}}
    sp = _spot(bp, m["x"] + 2, m["y"], 1, 1, 6)
    num = bp.add("programmable-speaker", *sp, control_behavior={
        "circuit_condition": {"first_signal": {"type": "virtual", "name": "signal-A"}, "constant": threshold,
                              "comparator": "<"},
        "circuit_parameters": {"signal_value_is_pitch": False, "stop_playing_sounds": False, "instrument_id": 0,
                               "note_id": 1}},
        parameters={"playback_volume": 1, "playback_mode": "global", "allow_polyphony": False,
                    "volume_controlled_by_signal": False},
        alert_parameters={"show_alert": True, "show_on_map": True,
                          "icon_signal_id": {"type": "virtual", "name": "signal-A"}, "alert_message": message})
    bp.wire(accumulator_num, num, "red")
    return num
