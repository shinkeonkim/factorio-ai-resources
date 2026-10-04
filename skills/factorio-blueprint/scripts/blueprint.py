#!/usr/bin/env python3
"""Factorio blueprint string toolkit: encode/decode, a layout builder, validation and ASCII preview.

Library use (preferred for building blueprints):

    import sys; sys.path.insert(0, "<skill>/scripts")
    from blueprint import Blueprint, N, E, S, W

    bp = Blueprint("Green circuits", game="2.0")
    bp.add("assembling-machine-2", 0, 0, recipe="copper-cable")     # x, y = TOP-LEFT tile
    bp.add("inserter", 3, 1, direction=W)   # direction = side the inserter PICKS UP from
    bp.connect_poles()                      # copper wires between poles (auto)
    print(bp.report())                      # overlaps, unpowered machines, ASCII map
    print(bp.to_string())

CLI:
    blueprint.py decode <string|file|->  [--json]   # pretty JSON
    blueprint.py info   <string|file|->             # summary + ASCII map + validation
    blueprint.py encode <json-file|->               # JSON -> blueprint string
    blueprint.py repair <string|file|->             # fix one mistyped char (checksum error)
    blueprint.py version <int | x.y.z[.b]>          # convert version formats
"""
from __future__ import annotations

import base64
import json
import math
import os
import sys
import zlib
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

# ---------------------------------------------------------------------------
# String format
# ---------------------------------------------------------------------------

def encode(obj: dict) -> str:
    """dict -> '0' + base64(zlib(json, level 9))."""
    raw = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "0" + base64.b64encode(zlib.compress(raw, 9)).decode("ascii")


def decode(s: str) -> dict:
    """Blueprint string (or raw JSON, which 2.0 also accepts) -> dict."""
    s = s.strip()
    if s.startswith("{"):
        return json.loads(s)
    if s[0] != "0":
        raise ValueError(f"unknown blueprint string version byte {s[0]!r} (expected '0')")
    return json.loads(zlib.decompress(base64.b64decode(_b64_body(s))).decode("utf-8"))


def _b64_body(s: str) -> str:
    """Base64 part of a blueprint string, tolerant of copy/paste damage: whitespace inside, missing
    '=' padding, or one stray trailing character (length = 1 mod 4 is never valid base64)."""
    body = "".join(s[1:].split())
    if len(body) % 4 == 1:
        body = body[:-1]
    return body + "=" * (-len(body) % 4)


def repair(s: str, window: int = 400) -> tuple[str, int] | None:
    """Fix a single mistyped base64 character (common when a long string is re-typed/copied).
    Locates where inflation diverges, then tries every substitution near it until the zlib
    checksum passes. Returns (fixed_string, position) or None."""
    import string
    s = s.strip()
    raw = base64.b64decode(_b64_body(s))
    try:
        zlib.decompress(raw)
        return s, -1
    except zlib.error:
        pass
    d, out, guess = zlib.decompressobj(-15), b"", len(s) // 2
    try:
        text = d.decompress(raw[2:-4]).decode("utf-8", "replace")
        json.loads(text)
    except json.JSONDecodeError as e:          # first broken char in the JSON -> input offset
        d2, acc = zlib.decompressobj(-15), b""
        for i in range(2, len(raw) - 4, 16):
            acc += d2.decompress(raw[i:i + 16])
            if len(acc) > e.pos - 200:
                guess = 1 + (i * 4) // 3
                break
    except zlib.error:
        pass
    alphabet = string.ascii_letters + string.digits + "+/"
    order = sorted(range(1, len(s)), key=lambda p: abs(p - guess))
    for p in order[: window] + order[window:]:
        for c in alphabet:
            if c == s[p]:
                continue
            t = s[:p] + c + s[p + 1:]
            try:
                zlib.decompress(base64.b64decode(t[1:]))
                return t, p
            except Exception:
                continue
    return None


def version_to_int(v: str) -> int:
    parts = [int(p) for p in v.split(".")] + [0, 0, 0, 0]
    major, minor, patch, build = parts[:4]
    return (major << 48) | (minor << 32) | (patch << 16) | build


def int_to_version(n: int) -> str:
    return f"{(n >> 48) & 0xFFFF}.{(n >> 32) & 0xFFFF}.{(n >> 16) & 0xFFFF}.{n & 0xFFFF}"


# Known-good versions. Importing a blueprint stamped with an OLDER version is always fine
# (the game migrates it); a NEWER version than the player's game can be rejected.
DEFAULT_VERSION = {"2.0": version_to_int("2.0.10.1"), "1.1": version_to_int("1.1.110.0")}

# ---------------------------------------------------------------------------
# Directions
# ---------------------------------------------------------------------------
# Builder API always takes these 4-way constants; they are converted to the right
# numbering for the target game version (2.0 uses 16-way: N=0 E=4 S=8 W=12,
# 1.1 uses 8-way: N=0 E=2 S=4 W=6).
N, E, S, W = "N", "E", "S", "W"
_DIR_INDEX = {N: 0, E: 1, S: 2, W: 3}
_DIR_VALUE = {"2.0": {N: 0, E: 4, S: 8, W: 12}, "1.1": {N: 0, E: 2, S: 4, W: 6}}
_VEC = {N: (0, -1), E: (1, 0), S: (0, 1), W: (-1, 0)}
_OPPOSITE = {N: S, S: N, E: W, W: E}


def dir_from_value(value: int, game: str) -> str:
    step = 4 if game == "2.0" else 2
    return [N, E, S, W][(value // step) % 4] if value % step == 0 else f"diag({value})"


# ---------------------------------------------------------------------------
# Static data
# ---------------------------------------------------------------------------

def _load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


SIZES = _load("entity_sizes.json")
# Factorio 1.1 names that were renamed in 2.0 (so 1.1 blueprints still size/validate correctly).
LEGACY_1_1 = {"filter-inserter": "inserter", "stack-filter-inserter": "inserter",
              "logistic-chest-requester": "requester-chest", "logistic-chest-passive-provider": "passive-provider-chest",
              "logistic-chest-active-provider": "active-provider-chest", "logistic-chest-storage": "storage-chest",
              "logistic-chest-buffer": "buffer-chest", "curved-rail": "curved-rail-a"}
for _old, _new in LEGACY_1_1.items():
    SIZES.setdefault(_old, dict(SIZES[_new], legacy=True))
# Rails and rolling stock sit on a 2-tile rail grid / free positions; skip grid checks for them.
_NO_GRID = {"straight-rail", "curved-rail-a", "curved-rail-b", "half-diagonal-rail", "legacy-straight-rail",
            "legacy-curved-rail", "elevated-straight-rail", "elevated-curved-rail-a", "elevated-curved-rail-b",
            "elevated-half-diagonal-rail", "rail-ramp", "rail-support", "rail-signal", "rail-chain-signal",
            "locomotive", "cargo-wagon", "fluid-wagon", "artillery-wagon", "car", "spider-vehicle"}
MACHINES = _load("machines.json")
POLES = MACHINES["poles"]

# Entity types that draw electricity (used by the power-coverage check).
_ELECTRIC_TYPES = {
    "assembling-machine", "furnace", "mining-drill", "inserter", "lab", "beacon", "radar",
    "lamp", "pump", "roboport", "electric-turret", "rocket-silo", "offshore-pump",
    "agricultural-tower", "asteroid-collector", "arithmetic-combinator", "decider-combinator",
    "selector-combinator", "programmable-speaker", "display-panel", "assembling-machine",
}
_NOT_ELECTRIC = {"stone-furnace", "steel-furnace", "burner-mining-drill", "burner-inserter",
                 "offshore-pump", "captive-biter-spawner", "pumpjack-burner"}

# Module inventory index (defines.inventory) per entity type, Factorio 2.0.
_MODULE_INVENTORY = {"assembling-machine": 4, "furnace": 4, "rocket-silo": 4,
                     "mining-drill": 2, "lab": 3, "beacon": 1}

# Wire connector ids (defines.wire_connector_id), Factorio 2.0.
_WIRE = {("red", None): 1, ("green", None): 2, ("red", "in"): 1, ("green", "in"): 2,
         ("red", "out"): 3, ("green", "out"): 4, ("copper", None): 5}


_FLUIDS = None


def _signal_type(name: str) -> str:
    """'fluid' for fluids in the recipe data, 'virtual' for signal-*, else 'item'."""
    global _FLUIDS
    if name.startswith("signal-"):
        return "virtual"
    if _FLUIDS is None:
        recipes = _load("recipes-space-age.json")["recipes"]
        _FLUIDS = {x["name"] for r in recipes.values() for x in r["ingredients"] + r["results"]
                   if x["type"] == "fluid"}
    return "fluid" if name in _FLUIDS else "item"


def size_of(name: str, direction: str = N) -> tuple[int, int]:
    info = SIZES.get(name)
    if info is None:
        raise KeyError(f"unknown entity '{name}' – check data/entity_sizes.json for the exact "
                       f"prototype name (2.0 names: e.g. 'bulk-inserter', 'requester-chest')")
    w, h = info["w"], info["h"]
    return (h, w) if direction in (E, W) else (w, h)


def type_of(name: str) -> str:
    return SIZES.get(name, {}).get("type", "?")


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

class OverlapError(ValueError):
    pass


class Blueprint:
    """Grid-based blueprint builder. Coordinates are integer tiles; (x, y) is the
    top-left tile of the entity footprint, +x = east, +y = south."""

    def __init__(self, label: str = "Blueprint", game: str = "2.0", description: str | None = None,
                 icons: list[str] | None = None, version: int | None = None):
        if game not in _DIR_VALUE:
            raise ValueError("game must be '2.0' or '1.1'")
        self.game = game
        self.label = label
        self.description = description
        self.extra = {}            # extra top-level blueprint fields, e.g. {"snap-to-grid": {"x": 13, "y": 12}}
        self.icons = icons
        self.version = version or DEFAULT_VERSION[game]
        self.entities: list[dict] = []        # raw blueprint entity dicts
        self._meta: dict[int, dict] = {}      # entity_number -> {x,y,w,h,dir}
        self._grid: dict[tuple[int, int], int] = {}
        self.wires: list[list[int]] = []
        self.tiles: list[dict] = []

    # -- placement ---------------------------------------------------------
    def add(self, name: str, x: int, y: int, direction: str = N, *, modules: dict | None = None,
            allow_overlap: bool = False, size: tuple[int, int] | None = None, **fields) -> int:
        """Place an entity with its top-left tile at (x, y). Returns entity_number.

        direction: N/E/S/W. Meaning per entity:
          belts/splitters/undergrounds: direction items travel
          inserters: side it PICKS UP from (drops on the opposite side)
          machines with fluid boxes: rotates the pipe connections (see references)
        fields: passed straight into the entity JSON (recipe=, type='input'|'output', quality=,
          filters=, bar=, control_behavior=, ...).
        modules: {"productivity-module-3": 4} – encoded per game version.
        size: (w, h) footprint when facing north, for modded entities not in data/entity_sizes.json.
        """
        if direction not in _DIR_INDEX:
            raise ValueError(f"direction must be one of N/E/S/W, got {direction!r}")
        if size:
            w, h = (size[1], size[0]) if direction in (E, W) else size
        else:
            w, h = size_of(name, direction)
        cells = [(x + i, y + j) for i in range(w) for j in range(h)]
        clash = {self._grid[c] for c in cells if c in self._grid}
        if clash and not allow_overlap:
            others = ", ".join(f"#{n} {self._ent(n)['name']}" for n in sorted(clash))
            raise OverlapError(f"{name} at ({x},{y}) size {w}x{h} overlaps {others}")
        num = len(self.entities) + 1
        ent = {"entity_number": num, "name": name,
               "position": {"x": x + w / 2, "y": y + h / 2}}
        dv = _DIR_VALUE[self.game][direction]
        if dv:
            ent["direction"] = dv
        if modules:
            ent["items"] = self._module_items(name, modules)
        ent.update(fields)
        self.entities.append(ent)
        self._meta[num] = {"x": x, "y": y, "w": w, "h": h, "dir": direction}
        for c in cells:
            self._grid[c] = num
        return num

    def belt_line(self, name: str, x: int, y: int, direction: str, length: int) -> list[int]:
        """Straight run of belt starting at (x, y) going `direction`."""
        dx, dy = _VEC[direction]
        return [self.add(name, x + dx * i, y + dy * i, direction) for i in range(length)]

    def underground(self, name: str, x: int, y: int, direction: str, gap: int) -> tuple[int, int]:
        """Underground pair: entrance at (x, y), exit `gap` tiles further along `direction`."""
        dx, dy = _VEC[direction]
        a = self.add(name, x, y, direction, type="input")
        b = self.add(name, x + dx * (gap + 1), y + dy * (gap + 1), direction, type="output")
        return a, b

    def add_marker(self, x: int, y: int, signals: dict, direction: str = N) -> int:
        """Constant combinator used as an I/O label: signals = {"stone": 1440, "water": 43500}.
        Convention: one marker next to every external input, signal = the item/fluid that must be
        supplied there, count = required rate PER MINUTE (rounded up). Fluids/virtual signals are
        detected automatically; pass ("virtual", "signal-A") as a key to force a type."""
        filters = []
        for i, (key, count) in enumerate(signals.items(), 1):
            sig_type, name = key if isinstance(key, tuple) else (_signal_type(key), key)
            count = int(math.ceil(count))
            if self.game == "2.0":
                filters.append({"index": i, "type": sig_type, "name": name, "quality": "normal",
                                "comparator": "=", "count": count})
            else:
                filters.append({"index": i, "signal": {"type": sig_type, "name": name}, "count": count})
        if self.game == "2.0":
            cb = {"sections": {"sections": [{"index": 1, "filters": filters}]}}
        else:
            cb = {"filters": filters}
        return self.add("constant-combinator", x, y, direction, control_behavior=cb)

    def add_tile(self, name: str, x: int, y: int):
        self.tiles.append({"name": name, "position": {"x": x, "y": y}})

    def _module_items(self, name, modules):
        if self.game == "1.1":
            return dict(modules)
        inv = _MODULE_INVENTORY.get(type_of(name), 4)
        out, slot = [], 0
        for mod, count in modules.items():
            mid = {"name": mod}
            if isinstance(count, tuple):        # ("rare", 4) -> quality module
                mid["quality"], count = count
            out.append({"id": mid, "items": {"in_inventory": [
                {"inventory": inv, "stack": slot + i} for i in range(count)]}})
            slot += count
        return out

    # -- wires -------------------------------------------------------------
    def wire(self, a: int, b: int, color: str = "copper", a_side: str | None = None,
             b_side: str | None = None):
        """color: 'red' | 'green' | 'copper'. side: None, or 'in'/'out' for combinators."""
        if self.game == "2.0":
            self.wires.append([a, _WIRE[(color, a_side)], b, _WIRE[(color, b_side)]])
            return
        # 1.1 format
        if color == "copper":
            for p, q in ((a, b), (b, a)):
                nb = self._ent(p).setdefault("neighbours", [])
                if q not in nb:
                    nb.append(q)
            return
        pa = "2" if a_side == "out" else "1"
        pb = "2" if b_side == "out" else "1"
        for p, sp, q, sq in ((a, pa, b, pb), (b, pb, a, pa)):
            conn = self._ent(p).setdefault("connections", {}).setdefault(sp, {})
            entry = {"entity_id": q}
            if sq == "2":
                entry["circuit_id"] = 2
            conn.setdefault(color, []).append(entry)

    def connect_poles(self) -> int:
        """Connect all electric poles with copper wire (minimum spanning tree within reach).
        Returns the number of wires added. Unreachable poles are reported by validate()."""
        poles = [e for e in self.entities if e["name"] in POLES]
        if len(poles) < 2:
            return 0
        pos = {e["entity_number"]: (e["position"]["x"], e["position"]["y"]) for e in poles}
        reach = {e["entity_number"]: POLES[e["name"]]["reach"] for e in poles}
        nums = list(pos)
        in_tree, added = {nums[0]}, 0
        while len(in_tree) < len(nums):
            best = None
            for a in in_tree:
                for b in nums:
                    if b in in_tree:
                        continue
                    d = math.dist(pos[a], pos[b])
                    if d <= min(reach[a], reach[b]) and (best is None or d < best[0]):
                        best = (d, a, b)
            if best is None:          # remaining poles are out of reach: start a new tree
                nxt = next(n for n in nums if n not in in_tree)
                in_tree.add(nxt)
                continue
            _, a, b = best
            self.wire(a, b, "copper")
            in_tree.add(b)
            added += 1
        return added

    # -- output ------------------------------------------------------------
    def _ent(self, num: int) -> dict:
        return self.entities[num - 1]

    def _auto_icons(self):
        if self.icons:
            names = self.icons
        else:
            c = Counter(e["name"] for e in self.entities
                        if type_of(e["name"]) not in ("transport-belt", "electric-pole", "inserter"))
            names = [n for n, _ in c.most_common(2)] or ["blueprint"]
            recipes = Counter(e.get("recipe") for e in self.entities if e.get("recipe"))
            if recipes:
                names = [recipes.most_common(1)[0][0]] + names[:1]
        icons = []
        for i, n in enumerate(names[:4], 1):
            sig = {"name": n} if self.game == "2.0" else {"type": "item", "name": n}
            icons.append({"signal": sig, "index": i})
        return icons

    def to_dict(self) -> dict:
        bp = {"item": "blueprint", "label": self.label, "icons": self._auto_icons(),
              "entities": self.entities, "version": self.version}
        if self.description:
            bp["description"] = self.description
        if self.wires:
            bp["wires"] = self.wires
        if self.tiles:
            bp["tiles"] = self.tiles
        bp.update(self.extra)
        return {"blueprint": bp}

    def to_string(self) -> str:
        return encode(self.to_dict())

    def validate(self) -> list[str]:
        return validate(self.to_dict())

    def ascii(self) -> str:
        return render_ascii(self.to_dict())

    def report(self) -> str:
        problems = self.validate()
        lines = [self.ascii(), ""]
        lines.append("Validation: OK" if not problems else "Validation problems:")
        lines += [f"  - {p}" for p in problems]
        return "\n".join(lines)


def make_book(label: str, blueprints: list[dict], version: int | None = None) -> dict:
    """Wrap blueprint dicts (as returned by Blueprint.to_dict()) into a blueprint book."""
    return {"blueprint_book": {
        "item": "blueprint-book", "label": label, "active_index": 0,
        "version": version or DEFAULT_VERSION["2.0"],
        "blueprints": [{"index": i, **bp} for i, bp in enumerate(blueprints)]}}


# ---------------------------------------------------------------------------
# Analysis of arbitrary blueprint dicts (also used for decoded strings)
# ---------------------------------------------------------------------------

def _game_of(bp: dict) -> str:
    return "2.0" if (bp.get("version", 0) >> 48) >= 2 else "1.1"


def _footprints(bp: dict):
    game = _game_of(bp)
    for e in bp.get("entities", []):
        d = dir_from_value(e.get("direction", 0), game)
        try:
            w, h = size_of(e["name"], d if d in _DIR_INDEX else N)
        except KeyError:
            w = h = 1
        cx, cy = e["position"]["x"], e["position"]["y"]
        x0, y0 = math.floor(cx - w / 2 + 1e-6), math.floor(cy - h / 2 + 1e-6)
        yield e, d, x0, y0, w, h


def validate(obj: dict) -> list[str]:
    """Sanity checks: overlap, unknown names, power coverage, pole reach, undergrounds."""
    bp = obj.get("blueprint", obj)
    game = _game_of(bp)
    problems, grid, rects, unknown = [], {}, {}, Counter()
    for e, d, x0, y0, w, h in _footprints(bp):
        n = e["entity_number"]
        rects[n] = (x0, y0, w, h, d, e)
        if e["name"] not in SIZES:
            unknown[e["name"]] += 1
            continue
        if SIZES[e["name"]].get("legacy") and game == "2.0":
            problems.append(f"#{n} '{e['name']}' is a 1.1 name; 2.0 uses '{LEGACY_1_1[e['name']]}'")
        if type_of(e["name"]) in _NO_GRID:
            continue
        cx, cy = e["position"]["x"], e["position"]["y"]
        if abs((cx - w / 2) - round(cx - w / 2)) > 1e-6 or abs((cy - h / 2) - round(cy - h / 2)) > 1e-6:
            problems.append(f"#{n} {e['name']} position {cx},{cy} is off-grid for a {w}x{h} entity")
        for i in range(w):
            for j in range(h):
                c = (x0 + i, y0 + j)
                if c in grid:
                    problems.append(f"#{n} {e['name']} overlaps #{grid[c]} at tile {c}")
                    break
                grid[c] = n
            else:
                continue
            break

    if unknown:
        problems.append("unknown entity names (typo, mod, or renamed prototype?): "
                        + ", ".join(f"{k}×{v}" for k, v in unknown.items()))

    # power coverage
    poles = [(r, POLES[r[5]["name"]]) for r in rects.values() if r[5]["name"] in POLES]
    has_any_pole = bool(poles)
    unpowered = []
    for n, (x0, y0, w, h, d, e) in rects.items():
        name = e["name"]
        if type_of(name) not in _ELECTRIC_TYPES or name in _NOT_ELECTRIC:
            continue
        powered = False
        for (px, py, pw, ph, _, pe), info in poles:
            cx, cy = px + pw / 2, py + ph / 2
            s = info["supply"]
            if x0 < cx + s and x0 + w > cx - s and y0 < cy + s and y0 + h > cy - s:
                powered = True
                break
        if not powered:
            unpowered.append(f"#{n} {name}@({x0},{y0})")
    if unpowered and has_any_pole:
        problems.append("not covered by any pole: " + ", ".join(unpowered[:12])
                        + (" ..." if len(unpowered) > 12 else ""))
    elif unpowered:
        problems.append(f"{len(unpowered)} electric entities but no electric poles (fine only if "
                        f"the user will power it themselves)")

    # pole connectivity
    if len(poles) > 1:
        nums = [p[0][5]["entity_number"] for p in poles]
        reach = {p[0][5]["entity_number"]: p[1]["reach"] for p in poles}
        pos = {p[0][5]["entity_number"]: (p[0][5]["position"]["x"], p[0][5]["position"]["y"]) for p in poles}
        adj = {n: set() for n in nums}
        if game == "2.0":
            for a, ca, b, cb in bp.get("wires", []):
                if ca == 5 and cb == 5 and a in adj and b in adj:
                    adj[a].add(b); adj[b].add(a)
        else:
            for n in nums:
                for m in rects[n][5].get("neighbours", []):
                    if m in adj:
                        adj[n].add(m); adj[m].add(n)
        for a in nums:
            for b in adj[a]:
                if math.dist(pos[a], pos[b]) > min(reach[a], reach[b]) + 1e-6:
                    problems.append(f"copper wire #{a}-#{b} longer than reach")
        seen, stack = {nums[0]}, [nums[0]]
        while stack:
            for m in adj[stack.pop()]:
                if m not in seen:
                    seen.add(m); stack.append(m)
        if len(seen) < len(nums):
            problems.append(f"{len(nums) - len(seen)} pole(s) not wired into the main network "
                            f"(call connect_poles(), or poles are farther apart than their reach)")

    # underground pairing
    ugs = [r for r in rects.values() if type_of(r[5]["name"]) == "underground-belt"]
    for x0, y0, w, h, d, e in ugs:
        if e.get("type") != "input" or d not in _VEC:
            continue
        dx, dy = _VEC[d]
        tier = e["name"].replace("underground-belt", "transport-belt") if e["name"] != "underground-belt" else "transport-belt"
        max_gap = MACHINES["belts"].get(tier, {}).get("underground_max_gap", 4)
        found = False
        for k in range(1, max_gap + 2):
            n2 = grid.get((x0 + dx * k, y0 + dy * k))
            if n2 and rects[n2][5]["name"] == e["name"] and rects[n2][5].get("type") == "output" and rects[n2][4] == d:
                found = True
                break
        if not found:
            problems.append(f"#{e['entity_number']} {e['name']} entrance at ({x0},{y0}) has no matching exit "
                            f"within {max_gap} tiles going {d}")
    return problems


_ARROWS = {N: "^", E: ">", S: "v", W: "<"}
_INS = {N: "↓", E: "←", S: "↑", W: "→"}   # arrow shows item MOVEMENT (opposite of pickup side)
_CHAR = {"assembling-machine": "A", "furnace": "F", "mining-drill": "D", "lab": "L", "beacon": "B",
         "container": "C", "logistic-container": "C", "pipe": "=", "pipe-to-ground": "P",
         "electric-pole": "+", "storage-tank": "T", "pump": "p", "offshore-pump": "O",
         "boiler": "b", "generator": "G", "solar-panel": "s", "accumulator": "a", "radar": "R",
         "roboport": "R", "rocket-silo": "X", "arithmetic-combinator": "k", "decider-combinator": "k",
         "selector-combinator": "k", "constant-combinator": "c", "lamp": "o", "wall": "#", "gate": "#"}


def render_ascii(obj: dict, max_width: int = 140) -> str:
    """Top-down ASCII map. Belts ^>v<, undergrounds as U/u (entry/exit) with arrow when 1 tile,
    inserters as ↑→↓← showing item movement, machines filled with a letter and their first
    tile marked with a legend number."""
    bp = obj.get("blueprint", obj)
    fp = list(_footprints(bp))
    if not fp:
        return "(no entities)"
    minx = min(f[2] for f in fp); miny = min(f[3] for f in fp)
    maxx = max(f[2] + f[4] for f in fp); maxy = max(f[3] + f[5] for f in fp)
    W_, H_ = maxx - minx, maxy - miny
    if W_ > max_width:
        return f"(blueprint is {W_}x{H_} tiles – too wide for ASCII preview)"
    grid = [["." for _ in range(W_)] for _ in range(H_)]
    legend, legend_ids = [], {}
    for e, d, x0, y0, w, h in fp:
        t = type_of(e["name"])
        gx, gy = x0 - minx, y0 - miny
        if t in ("transport-belt",):
            ch = _ARROWS.get(d, "?")
        elif t == "underground-belt":
            ch = "U" if e.get("type") == "input" else "u"
        elif t in ("splitter", "lane-splitter"):
            ch = "S"
        elif t == "inserter":
            ch = _INS.get(d, "?")
            if "long" in e["name"]:
                ch = {"↓": "⇓", "←": "⇐", "↑": "⇑", "→": "⇒"}.get(ch, ch)
        else:
            ch = _CHAR.get(t, "#")
        for i in range(w):
            for j in range(h):
                grid[gy + j][gx + i] = ch
        if w * h >= 4 and t not in ("splitter",):
            key = (e["name"], e.get("recipe"))
            if key not in legend_ids:
                legend_ids[key] = len(legend_ids) + 1
                legend.append(f"  {ch}{legend_ids[key]}: {e['name']}" + (f" [{e['recipe']}]" if e.get("recipe") else ""))
            for k, c in enumerate(str(legend_ids[key])):   # "A1A" – id written after the letter
                if 1 + k < w:
                    grid[gy][gx + 1 + k] = c
    out = [f"{W_}x{H_} tiles, origin=({minx},{miny})  (x→ east, y↓ south)"]
    out += ["".join(r) for r in grid]
    if legend:
        out.append("legend:")
        out += legend
    out.append("  belts ^>v<  undergrounds U(in)/u(out)  splitter S  inserters ↑→↓← (⇑⇒⇓⇐ long) = item flow  "
               "+ pole  = pipe  P pipe-to-ground")
    return "\n".join(out)


def summarize(obj: dict) -> str:
    if "blueprint_book" in obj:
        book = obj["blueprint_book"]
        lines = [f"Blueprint book '{book.get('label', '')}' – {len(book.get('blueprints', []))} entries"]
        for entry in book.get("blueprints", []):
            inner = {k: v for k, v in entry.items() if k != "index"}
            lines.append(f"\n--- [{entry.get('index')}] ---")
            lines.append(summarize(inner))
        return "\n".join(lines)
    key = next((k for k in ("blueprint", "deconstruction_planner", "upgrade_planner") if k in obj), None)
    if key != "blueprint":
        return f"{key or 'unknown object'}: " + json.dumps(obj)[:500]
    bp = obj["blueprint"]
    v = bp.get("version", 0)
    lines = [f"Blueprint '{bp.get('label', '')}'  version {int_to_version(v)} ({_game_of(bp)} format)"]
    if bp.get("description"):
        lines.append(f"description: {bp['description']}")
    ents = bp.get("entities", [])
    lines.append(f"entities: {len(ents)}  tiles: {len(bp.get('tiles', []))}  wires: {len(bp.get('wires', []))}")
    for name, cnt in Counter(e["name"] for e in ents).most_common():
        lines.append(f"  {cnt:4d} × {name}")
    markers = []
    for e in ents:
        if e["name"] != "constant-combinator":
            continue
        cb = e.get("control_behavior", {})
        fl = [f for sec in cb.get("sections", {}).get("sections", []) for f in sec.get("filters", [])]
        fl += cb.get("filters", [])          # 1.1 format
        sigs = ", ".join(f"{f.get('name') or f.get('signal', {}).get('name')}={f.get('count')}" for f in fl)
        if sigs:
            markers.append(f"  ({e['position']['x']}, {e['position']['y']}): {sigs}")
    if markers:
        lines.append("constant-combinator markers (input labels, count = per minute by convention):")
        lines += markers
    recipes = Counter(e["recipe"] for e in ents if e.get("recipe"))
    if recipes:
        lines.append("recipes: " + ", ".join(f"{r}×{c}" for r, c in recipes.most_common()))
    lines.append("")
    lines.append(render_ascii(obj))
    probs = validate(obj)
    lines.append("")
    lines.append("Validation: OK" if not probs else "Validation problems:\n" + "\n".join(f"  - {p}" for p in probs))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _read_arg(a: str) -> str:
    if a == "-":
        return sys.stdin.read()
    if os.path.exists(a):
        with open(a) as f:
            return f.read()
    return a


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd = argv[1]
    if cmd == "decode":
        print(json.dumps(decode(_read_arg(argv[2])), indent=2, ensure_ascii=False))
    elif cmd == "info":
        print(summarize(decode(_read_arg(argv[2]))))
    elif cmd == "encode":
        print(encode(json.loads(_read_arg(argv[2]))))
    elif cmd == "repair":
        res = repair(_read_arg(argv[2]))
        if res is None:
            print("could not repair with a single-character fix", file=sys.stderr); return 1
        fixed, pos = res
        print(("string was already valid" if pos < 0 else f"fixed char at index {pos}"), file=sys.stderr)
        print(fixed)
    elif cmd == "version":
        a = argv[2]
        print(int_to_version(int(a)) if a.isdigit() and "." not in a else version_to_int(a))
    else:
        print(f"unknown command {cmd}\n{__doc__}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
