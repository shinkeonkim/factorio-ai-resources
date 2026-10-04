"""Build stations into the 182x182 'Mixed Elev. Cityblock' station blocks (book 17).

Geometry (verified against the book's Fuel Supply / Refuelling blueprints): for a train stop whose
centre is at x=S facing east (train heading east), the locomotive occupies tile columns S-6..S-1 and
cargo wagon k occupies S-7k-6 .. S-7k-1.  Station track rail centre y=R -> wagon rows R-1 and R.
"""
import json, math, sys, copy
from lib.fbp import Blueprint, N, E, S, W, encode, decode, validate, render_ascii, POLES, third_party

_BOOK = None


def book():
    """The third-party rail blueprint book (third_party/rail-book.txt), decoded once."""
    global _BOOK
    if _BOOK is None:
        _BOOK = decode(third_party("rail-book.txt").read_text())
    return _BOOK
FI, MP, CHEST, BELT, UG = "fast-inserter", "medium-electric-pole", "steel-chest", "fast-transport-belt", "fast-underground-belt"
STACK = {"iron-plate": 100, "copper-plate": 100, "steel-plate": 100, "iron-ore": 50, "copper-ore": 50, "stone": 50,
         "coal": 50, "stone-brick": 100, "plastic-bar": 100, "electronic-circuit": 200, "advanced-circuit": 200,
         "processing-unit": 100, "iron-gear-wheel": 100, "sulfur": 50, "concrete": 100, "refined-concrete": 100}


def book_bp(path):
    o = book()
    for p in path:
        o = [e for e in o["blueprint_book"]["blueprints"] if e["index"] == p][0]
    return copy.deepcopy(o["blueprint"])


def wagon_cols(stop_x, k):
    """tile columns of cargo wagon k (1-based) for an east-facing stop at x=stop_x"""
    start = stop_x - 7 * k - 6
    return list(range(start, start + 6))


class Overlay(Blueprint):
    """Builder that knows the occupied tiles of the base block so new entities can't collide."""
    def __init__(self, base, label):
        super().__init__(label, game="2.0")
        from blueprint import _footprints, type_of, _NO_GRID
        self.base = base
        for e, d, x0, y0, w, h in _footprints(base):
            if type_of(e["name"]) in _NO_GRID:
                continue
            for i in range(w):
                for j in range(h):
                    self._grid[(x0 + i, y0 + j)] = -e["entity_number"]

    def _ent(self, num):
        return self.base["entities"][-num - 1] if num < 0 else self.entities[num - 1]


def merge(base, ov, link_reach=9):
    """Append overlay entities/wires to the base blueprint; link overlay poles to the base grid."""
    off = len(base["entities"])
    for e in ov.entities:
        f = dict(e); f["entity_number"] += off
        base["entities"].append(f)
    base.setdefault("wires", [])
    for a, ca, b, cb in ov.wires:
        base["wires"].append([a + off if a > 0 else -a, ca, b + off if b > 0 else -b, cb])
    # copper link: each overlay pole group must reach a base pole
    base_poles = [e for e in base["entities"][:off] if e["name"] in POLES]
    ov_poles = [e for e in base["entities"][off:] if e["name"] in POLES]
    linked = 0
    for p in ov_poles:
        px, py = p["position"]["x"], p["position"]["y"]
        best = min(base_poles, key=lambda q: math.dist((px, py), (q["position"]["x"], q["position"]["y"])))
        dd = math.dist((px, py), (best["position"]["x"], best["position"]["y"]))
        if dd <= min(link_reach, POLES[best["name"]]["reach"], POLES[p["name"]]["reach"]):
            base["wires"].append([p["entity_number"], 5, best["entity_number"], 5]); linked += 1
    return linked


def stitch_power(bp):
    """Union-find over copper wires; join every separate pole group to the nearest pole of another
    group within wire reach (fixes overlay + any loose poles of the base). Returns wires added."""
    poles = [e for e in bp["entities"] if e["name"] in POLES]
    par = {e["entity_number"]: e["entity_number"] for e in poles}
    def f(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for a, ca, b, cb in bp.get("wires", []):
        if ca == 5 and cb == 5 and a in par and b in par:
            par[f(a)] = f(b)
    pos = {e["entity_number"]: (e["position"]["x"], e["position"]["y"]) for e in poles}
    reach = {e["entity_number"]: POLES[e["name"]]["reach"] for e in poles}
    added = 0
    while True:
        groups = {}
        for n in par: groups.setdefault(f(n), []).append(n)
        if len(groups) == 1: break
        best = None
        for a in par:
            for b in par:
                if f(b) == f(a): continue
                d = math.dist(pos[a], pos[b])
                if d <= min(reach[a], reach[b]) and (best is None or d < best[0]): best = (d, a, b)
        if best is None: break
        _, a, b = best
        bp["wires"].append([a, 5, b, 5]); par[f(a)] = f(b); added += 1
    return added


def set_stop(base, pos, name, limit_signal=True):
    for e in base["entities"]:
        if e["name"] == "train-stop" and e["position"] == pos:
            e["station"] = name
            e.pop("manual_trains_limit", None)
            if limit_signal:
                e["control_behavior"] = {"set_trains_limit": True,
                                         "trains_limit_signal": {"type": "virtual", "name": "signal-L"}}
            return e["entity_number"]
    raise KeyError(f"no train stop at {pos}")


def wagon_side(ov, stop_x, rail_y, wagons, side, mode, belt_row_dir):
    """Chest+inserter wall for `wagons` cargo wagons on one side of the station track.
    side: 'N' (rows above the track) or 'S'.  mode: 'unload' (wagon->chest->belt) or 'load'.
    Returns (chest entity numbers in order, poles in chest row, belt row y)."""
    sgn = -1 if side == "N" else 1
    edge = rail_y - 2 if side == "N" else rail_y + 1      # row next to the wagon
    chest_row, ins2_row, belt_row = edge + sgn, edge + 2 * sgn, edge + 3 * sgn
    toward_wagon = S if side == "N" else N                  # pickup side when picking FROM the wagon
    away = N if side == "N" else S
    chests, poles = [], []
    cols_all = []
    for k in range(1, wagons + 1):
        cols = wagon_cols(stop_x, k); cols_all += cols
        for x in cols:
            if mode == "unload":
                ov.add(FI, x, edge, toward_wagon)           # wagon -> chest
                ov.add(FI, x, ins2_row, toward_wagon)       # chest -> belt
            else:
                ov.add(FI, x, edge, away)                   # chest -> wagon
                ov.add(FI, x, ins2_row, away)               # belt -> chest
            chests.append((x, ov.add(CHEST, x, chest_row)))
    # poles in the chest row at each gap column (between wagons, and both ends)
    gaps = sorted({min(cols_all) - 1} | {wagon_cols(stop_x, k)[-1] + 1 for k in range(1, wagons + 1)})
    for gx in gaps:
        poles.append((gx, ov.add(MP, gx, chest_row)))
    return chests, poles, belt_row, cols_all


def red_chain(ov, items):
    """items: list of (x, entity_number) sorted along a row -> red wire chain"""
    items = sorted(items)
    for (xa, a), (xb, b) in zip(items, items[1:]):
        ov.wire(a, b, "red")
    return items


def provider_limit(ov, base, item, wagons, chests_poles, comb_xy, stop_pos, name):
    """Red-chain the load chests and set the stop's train limit to stored trainloads."""
    from blueprint import Blueprint
    load = wagons * 40 * STACK.get(item, 50)
    A = ov.add("arithmetic-combinator", comb_xy[0], comb_xy[1], control_behavior={"arithmetic_conditions": {
        "first_signal": {"type": "item", "name": item}, "second_constant": load, "operation": "/",
        "output_signal": {"type": "virtual", "name": "signal-L"}}},
        player_description="train limit L = stored items / trainload")
    P = ov.add(MP, comb_xy[0] + 1, comb_xy[1])
    ov.wire(max(chests_poles[1])[1], P, "red")
    ov.wire(P, A, "red", None, "in")
    stop = set_stop(base, stop_pos, name)
    return A, stop, load


def drill_band(ov, x0, y0, pairs, direction, belt=BELT, drill="electric-mining-drill"):
    """Two drill rows facing a shared belt at y0+3; pairs of drills around a pole column (pitch 7).
    direction: belt flow E or W; the belt ends one tile past the field so it can side-load a collector."""
    for p in range(pairs):
        x = x0 + 7 * p
        for dx in (0, 4):
            ov.add(drill, x + dx, y0, S); ov.add(drill, x + dx, y0 + 4, N)
        ov.add(MP, x + 3, y0 + 1); ov.add(MP, x + 3, y0 + 5)
    w = 7 * pairs
    if direction == E:
        ov.belt_line(belt, x0, y0 + 3, E, w)        # last tile points at x0+w (collector)
    else:
        ov.belt_line(belt, x0 + w - 1, y0 + 3, W, w)  # last tile points at x0-1
    return 4 * pairs


# ---------------------------------------------------------------------------------------------------
# Big blocks: one N x N block whose interior is empty (perimeter streets only)
# ---------------------------------------------------------------------------------------------------
CELL = 182
CORNERS = {"nw": (1, 1), "ne": (183, 1), "sw": (1, 183), "se": (183, 183)}   # street crossings of the 1x1
ZONE = 64             # half-size of the corner area copied verbatim (intersection + ramps + merges)
MARGIN = 6            # keep generated signals/supports this far from a corner area


def _key(e):
    rest = {k: v for k, v in e.items() if k not in ("entity_number", "position")}
    return (e["name"], e["position"]["x"], e["position"]["y"], json.dumps(rest, sort_keys=True))


def big_block(src: dict, n: int) -> dict:
    """Perimeter-only N x N block from the 1x1 'Empty Block' `src` (blueprint dict, not wrapped).

    Corners: the 1x1 corner areas (|dx|,|dy| <= ZONE around each street crossing) are copied to the
    four corners of the big block. Edges: the straight street between corners is regenerated with the
    same pattern the 1x1 uses on its straight sections:
      horizontal  rails y=-3 (elevated) / y=5 (ground), signals every 14 (elev y=-4.5 dir E, ground
                  y=6.5 dir W), supports every 14 on the elevated line, big poles every 28 at y=1
      vertical    rails x=-3 / x=5, elevated signals every 12 (x=-4.5 dir N), ground every 14
                  (x=6.5 dir S), supports every 6, medium poles every 9 at x=-0.5
    No interior streets or intersections; power is re-stitched with copper wire afterwards."""
    span = CELL * (n - 1)
    shift = {"nw": (0, 0), "ne": (span, 0), "sw": (0, span), "se": (span, span)}
    ents, index, wires = [], {}, set()

    def add(e):
        k = _key(e)
        if k in index:
            return index[k]
        f = dict(e); f["entity_number"] = len(ents) + 1
        ents.append(f); index[k] = f["entity_number"]
        return f["entity_number"]

    for name, (cx, cy) in CORNERS.items():
        dx, dy = shift[name]
        remap = {}
        for e in src["entities"]:
            x, y = e["position"]["x"], e["position"]["y"]
            if abs(x - cx) <= ZONE and abs(y - cy) <= ZONE:
                remap[e["entity_number"]] = add({**e, "position": {"x": x + dx, "y": y + dy}})
        for a, ca, b, cb in src.get("wires", []):
            if a in remap and b in remap:
                w = (remap[a], ca, remap[b], cb)
                if (w[2], w[3], w[0], w[1]) not in wires:
                    wires.add(w)

    def gap(lo_corner, hi_corner_shifted):
        """inclusive coordinate range along an edge between two corner areas"""
        return lo_corner + ZONE + 1, hi_corner_shifted - ZONE - 1

    def phase(lo, period, rem):
        """first value >= lo with value % period == rem (keeps the 1x1's rail-grid alignment)"""
        return lo + (rem - lo) % period

    def even(a, b, maxgap):
        """points strictly between anchors a and b, evenly spaced, gaps <= maxgap"""
        k = max(0, math.ceil((b - a) / maxgap) - 1)
        return [a + (b - a) * (i + 1) / (k + 1) for i in range(k)]

    def anchors(name, axis, line, lo, hi, tol=4):
        """pole coordinates (along `axis`) of corner-area poles near a street line: last <= lo, first >= hi"""
        other = "y" if axis == "x" else "x"
        vals = [e["position"][axis] for e in ents if e["name"] == name and abs(e["position"][other] - line) <= tol]
        return max(v for v in vals if v <= lo), min(v for v in vals if v >= hi)

    def hline(y0, xa, xb):          # horizontal street: elevated rail y0-3, ground rail y0+5
        for x in range(xa | 1, xb + 1, 2):
            add({"name": "straight-rail", "position": {"x": x, "y": y0 + 5}, "direction": 4})
            add({"name": "elevated-straight-rail", "position": {"x": x, "y": y0 - 3}, "direction": 4})
        for x in range(phase(xa + MARGIN, 14, 49 % 14), xb - MARGIN + 1, 14):
            add({"name": "rail-signal", "position": {"x": x + 0.5, "y": y0 - 4.5}, "direction": 4})
            add({"name": "rail-signal", "position": {"x": x + 1.5, "y": y0 + 6.5}, "direction": 12})
        for x in range(phase(xa + MARGIN, 14, 50 % 14), xb - MARGIN + 1, 14):
            add({"name": "rail-support", "position": {"x": x, "y": y0 - 3}, "direction": 4})
        a, b = anchors("big-electric-pole", "x", y0 + 2, xa, xb)
        for x in even(a, b, 28):
            add({"name": "big-electric-pole", "position": {"x": round(x), "y": y0 + 1}})

    def vline(x0, ya, yb):          # vertical street: elevated rail x0-3, ground rail x0+5
        for y in range(ya | 1, yb + 1, 2):
            add({"name": "straight-rail", "position": {"x": x0 + 5, "y": y}})
            add({"name": "elevated-straight-rail", "position": {"x": x0 - 3, "y": y}})
        for y in range(phase(ya + MARGIN, 12, 72 % 12), yb - MARGIN + 1, 12):
            add({"name": "rail-signal", "position": {"x": x0 - 4.5, "y": y + 0.5}})
        for y in range(phase(ya + MARGIN, 14, 77 % 14), yb - MARGIN + 1, 14):
            add({"name": "rail-signal", "position": {"x": x0 + 6.5, "y": y + 0.5}, "direction": 8})
        for y in range(phase(ya, 6, 0), yb + 1, 6):
            add({"name": "rail-support", "position": {"x": x0 - 3, "y": y}})
        a, b = anchors("medium-electric-pole", "y", x0 - 0.5, ya, yb, tol=0.1)
        for y in even(a, b, 9):
            add({"name": "medium-electric-pole", "position": {"x": x0 - 0.5, "y": math.floor(y) + 0.5}})

    if n > 1:
        xa, xb = gap(CORNERS["nw"][0], CORNERS["ne"][0] + span)
        hline(0, xa, xb); hline(CELL * n, xa, xb)
        ya, yb = gap(CORNERS["nw"][1], CORNERS["sw"][1] + span)
        vline(0, ya, yb); vline(CELL * n, ya, yb)

    bp = {k: v for k, v in src.items() if k not in ("entities", "wires")}
    bp["label"] = f"Big Block {n}x{n} (empty interior)"
    bp["snap-to-grid"] = {"x": CELL * n, "y": CELL * n}
    bp["entities"] = ents
    bp["wires"] = [list(w) for w in sorted(wires)]
    stitch_power(bp)
    return bp
