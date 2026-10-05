#!/usr/bin/env python3
"""Study a blueprint (or every blueprint in a book) the way a designer would: shape, density, how items move,
which circuit tricks it uses, where its inputs are, how it is powered and defended.

    python3 study.py <string|file> [--top 6] [--match TEXT] [--map [SCALE]]

Per blueprint it prints
  size, entities, density (entities per tile of the bounding box — dense community bases are 0.3-0.5)
  machines by recipe, beacons and modules (+ quality)
  inserter flows: what each inserter picks from → drops into (belt→machine, machine→machine = direct
      insertion, requester→machine, machine→buffer, …) — the clearest fingerprint of a design style
  circuit features used (entity kind + control_behavior key, e.g. assembler set_recipe, inserter
      logistic_condition) and how many wires
  inputs the designer labelled (display panels, constant combinators) and items requested from robots
  power (turbines, solar, accumulators, heating towers, lightning) and defence (walls, turrets, mines)
--map draws a coarse map (SCALE tiles per character; letters: W wall, T turret/mine, R silo/pad,
P power, H heat pipe, S recycler, M machine, c chest/roboport, = belt, ~ pipe).
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from blueprint import decode, size_of, dir_from_value, type_of  # noqa: E402

TURRETS = {"gun-turret", "laser-turret", "rocket-turret", "tesla-turret", "flamethrower-turret", "railgun-turret",
           "artillery-turret", "land-mine"}
POWER = {"steam-turbine", "steam-engine", "heat-exchanger", "heating-tower", "nuclear-reactor", "boiler",
         "solar-panel", "accumulator", "lightning-rod", "lightning-collector", "fusion-reactor", "fusion-generator"}
CRAFTERS = ("assembling-machine", "furnace", "rocket-silo", "lab")
VEC = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}


def walk(o, path=""):
    if "blueprint" in o:
        yield path + (o["blueprint"].get("label") or ""), o["blueprint"]
    if "blueprint_book" in o:
        bb = o["blueprint_book"]
        for b in bb.get("blueprints", []):
            yield from walk(b, path + (bb.get("label") or "") + " / ")


def footprint(e, game="2.0"):
    d = dir_from_value(e.get("direction", 0), game)
    try:
        w, h = size_of(e["name"], d)
    except KeyError:
        w = h = 1
    return d, math.floor(e["position"]["x"] - w / 2 + 1e-6), math.floor(e["position"]["y"] - h / 2 + 1e-6), w, h


def kind(e):
    if e is None:
        return "nothing"
    n, t = e["name"], type_of(e["name"])
    if "belt" in n or "splitter" in n or "loader" in n:
        return "belt"
    if "chest" in n:
        for k in ("requester", "buffer", "passive-provider", "active-provider", "storage"):
            if k in n:
                return k
        return "chest"
    if t in CRAFTERS:
        return "machine"
    return t


def category(n):
    if n in ("stone-wall", "gate"):
        return "W"
    if n in TURRETS:
        return "T"
    if n in ("rocket-silo", "cargo-landing-pad", "cargo-bay"):
        return "R"
    if n in POWER:
        return "P"
    if n == "heat-pipe":
        return "H"
    if n == "recycler":
        return "S"
    t = type_of(n)
    if t in CRAFTERS or t in ("mining-drill", "reactor"):
        return "M"
    if "chest" in n or n == "roboport":
        return "c"
    if "belt" in n or "splitter" in n:
        return "="
    if "pipe" in n or "pump" in n or "tank" in n:
        return "~"
    return None


def study(label, bp, show_map=0):
    es = bp.get("entities", [])
    if not es:
        return
    game = "2.0" if bp.get("version", 0) >= (2 << 48) else "1.1"
    grid, fp = {}, {}
    for e in es:
        d, x0, y0, w, h = footprint(e, game)
        fp[e["entity_number"]] = (d, x0, y0, w, h)
        for i in range(w):
            for j in range(h):
                grid[(x0 + i, y0 + j)] = e
    xs = [x for x, _ in grid]; ys = [y for _, y in grid]
    W, H = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
    c = collections.Counter(e["name"] for e in es)
    machines = [e for e in es if type_of(e["name"]) in CRAFTERS]
    recipes = collections.Counter(e.get("recipe") or e["name"] for e in machines)
    mods = collections.Counter()
    for e in es:
        for it in e.get("items") or []:
            if isinstance(it, dict):
                mods[it.get("id", {}).get("name")] += len(it.get("items", {}).get("in_inventory", []))
    quality = collections.Counter(e.get("quality") for e in es if e.get("quality"))
    flows = collections.Counter()
    for e in es:
        if type_of(e["name"]) != "inserter":
            continue
        d, x0, y0, _, _ = fp[e["entity_number"]]
        if d not in VEC:
            continue
        r = 2 if "long" in e["name"] else 1
        dx, dy = VEC[d]
        flows[(kind(grid.get((x0 + dx * r, y0 + dy * r))), kind(grid.get((x0 - dx * r, y0 - dy * r))))] += 1
    circuits = collections.Counter()
    for e in es:
        for k, v in (e.get("control_behavior") or {}).items():
            if v not in (False, None) and k not in ("circuit_condition_enabled",):
                circuits[f"{e['name']}.{k}"] += 1
    inputs = []
    for e in es:
        if e["name"] == "display-panel":
            p = (e.get("control_behavior") or {}).get("parameters") or []
            txt = e.get("text") or (p[0].get("text") if p else "") or ""
            icon = (e.get("icon") or (p[0].get("icon") if p else {}) or {}).get("name", "")
            inputs.append(f"panel '{txt.strip()}' {icon}".strip())
    requested = collections.Counter()
    for e in es:
        for sec in (e.get("request_filters") or {}).get("sections", []):
            for f in sec.get("filters", []):
                requested[f.get("name")] += 1
    filt = sum(1 for e in es if e.get("use_filters") and type_of(e["name"]) == "inserter")
    print(f"\n### {label or '(unnamed)'}")
    print(f"  {W}x{H} tiles, {len(es)} entities, density {len(es) / (W * H):.2f}, machines {len(machines)}, "
          f"beacons {c['beacon']}, wires {len(bp.get('wires', []))}, filter inserters {filt}")
    print("  recipes:", ", ".join(f"{k} {v}" for k, v in recipes.most_common(16)))
    if mods:
        print("  modules:", ", ".join(f"{k} {v}" for k, v in mods.most_common(6)), f"| quality: {dict(quality)}" if quality else "")
    tot = sum(flows.values()) or 1
    print("  inserter flows:", ", ".join(f"{a}→{b} {v} ({100 * v // tot}%)" for (a, b), v in flows.most_common(10)))
    if circuits:
        print("  circuits:", ", ".join(f"{k} {v}" for k, v in circuits.most_common(14)))
    if inputs:
        print("  labelled:", "; ".join(inputs[:16]))
    if requested:
        print(f"  robot requests ({len(requested)} items):", ", ".join(k for k, _ in requested.most_common(24)))
    power = {k: v for k, v in c.items() if k in POWER}
    defence = {k: v for k, v in c.items() if k in TURRETS or k in ("stone-wall", "gate")}
    if power:
        print("  power:", power)
    if defence:
        print("  defence:", defence)
    if bp.get("description"):
        print("  description:", bp["description"][:400].replace("\n", " "))
    if show_map:
        k = show_map
        cells = collections.defaultdict(collections.Counter)
        x0, y0 = min(xs), min(ys)
        for e in es:
            cat = category(e["name"])
            if cat:
                cells[((e["position"]["x"] - x0) // k, (e["position"]["y"] - y0) // k)][cat] += 1
        pri = "RTWPSMHc=~"
        for y in range(int(H // k) + 1):
            print("  " + "".join(min(cells[(x, y)], key=pri.index) if cells.get((x, y)) else "."
                                 for x in range(int(W // k) + 1)))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="blueprint string or a file holding one")
    ap.add_argument("--top", type=int, default=6, help="largest N blueprints of a book")
    ap.add_argument("--match", default="", help="only blueprints whose label contains this")
    ap.add_argument("--map", type=int, nargs="?", const=3, default=0, help="coarse map, SCALE tiles per char")
    a = ap.parse_args(argv)
    src = a.source.strip()
    if not src.startswith("0") or len(src) < 200:              # a path, not a blueprint string
        src = pathlib.Path(a.source).read_text().strip()
    obj = decode(src)
    top = obj.get("blueprint_book") or obj.get("blueprint") or {}
    bps = [(l, b) for l, b in walk(obj) if a.match in l]
    print(f"{top.get('label', '')}: {len(bps)} blueprint(s)")
    for label, bp in sorted(bps, key=lambda t: -len(t[1].get("entities", [])))[:a.top]:
        study(label, bp, a.map)


if __name__ == "__main__":
    main()
