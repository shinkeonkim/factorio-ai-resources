#!/usr/bin/env python3
"""Structured analysis of a blueprint string (or every blueprint inside a book).

    python3 tools/analyze_blueprint.py demo-resources/다이소1.txt            # markdown report
    python3 tools/analyze_blueprint.py book.txt --json                        # machine-readable
    python3 tools/analyze_blueprint.py book.txt --list                        # book tree only

Reports per blueprint: size, version, required mods (base / quality / space-age), tier mix of belts,
inserters, assemblers and poles (is it upgrade-in-place friendly?), machines per recipe with their
nominal crafting rate (no modules/beacons), modules & beacons, and the recipe graph's external
inputs (consumed but not made here) and final outputs (made but not consumed here).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "factorio-blueprint" / "scripts"))
from blueprint import decode, int_to_version, _footprints, type_of  # noqa: E402

DATA = ROOT / "skills" / "factorio-blueprint" / "data"
RECIPES = json.loads((DATA / "recipes-space-age.json").read_text())["recipes"]
MACHINES = json.loads((DATA / "machines.json").read_text())

TIERS = {
    "belt": [("transport-belt", "underground-belt", "splitter", "loader"),
             ("fast-transport-belt", "fast-underground-belt", "fast-splitter", "fast-loader"),
             ("express-transport-belt", "express-underground-belt", "express-splitter", "express-loader"),
             ("turbo-transport-belt", "turbo-underground-belt", "turbo-splitter", "turbo-loader")],
    "assembler": [("assembling-machine-1",), ("assembling-machine-2",), ("assembling-machine-3",)],
    "furnace": [("stone-furnace",), ("steel-furnace",), ("electric-furnace",)],
    "inserter": [("burner-inserter",), ("inserter", "long-handed-inserter"), ("fast-inserter",),
                 ("bulk-inserter", "stack-inserter")],
    "pole": [("small-electric-pole",), ("medium-electric-pole",), ("substation",)],
}
TIER_NAMES = {"belt": ["yellow", "red", "blue", "turbo"], "assembler": ["AM1", "AM2", "AM3"],
              "furnace": ["stone", "steel", "electric"], "inserter": ["burner", "basic/long", "fast", "bulk/stack"],
              "pole": ["small", "medium", "substation"]}
SPACE_AGE = ("foundry", "electromagnetic-plant", "biochamber", "cryogenic-plant", "recycler", "crusher",
             "big-mining-drill", "turbo-", "elevated-", "rail-ramp", "rail-support", "asteroid-collector",
             "thruster", "space-platform-hub", "cargo-bay", "agricultural-tower", "heating-tower", "lightning",
             "captive-biter-spawner", "fusion-", "stack-inserter", "biolab")
MACHINE_TYPES = ("assembling-machine", "furnace", "rocket-silo")


def crafting_speed(name):
    c = MACHINES["crafters"].get(name)
    return c["speed"] if c else 1.0


def blueprints(obj, path=()):
    if "blueprint_book" in obj:
        for e in obj["blueprint_book"].get("blueprints", []):
            yield from blueprints({k: v for k, v in e.items() if k != "index"}, path + (e.get("index"),))
    elif "blueprint" in obj:
        yield path, obj["blueprint"]


def tree(obj, depth=0, path=()):
    if "blueprint_book" in obj:
        b = obj["blueprint_book"]
        print("  " * depth + f"📚 {list(path)} {b.get('label') or '(no label)'} — {len(b.get('blueprints', []))} entries")
        for e in b.get("blueprints", []):
            tree({k: v for k, v in e.items() if k != "index"}, depth + 1, path + (e.get("index"),))
    elif "blueprint" in obj:
        b = obj["blueprint"]
        print("  " * depth + f"📄 {list(path)} {b.get('label') or '(no label)'} — {len(b.get('entities', []))} entities")


def analyze(bp: dict) -> dict:
    ents = bp.get("entities", [])
    fps = list(_footprints(bp)) if ents else []
    w = (max(f[2] + f[4] for f in fps) - min(f[2] for f in fps)) if fps else 0
    h = (max(f[3] + f[5] for f in fps) - min(f[3] for f in fps)) if fps else 0
    names = Counter(e["name"] for e in ents)
    tiers = {}
    for cat, levels in TIERS.items():
        cnt = Counter()
        for i, group in enumerate(levels):
            cnt[TIER_NAMES[cat][i]] = sum(v for n, v in names.items() if n in group)
        tiers[cat] = {k: v for k, v in cnt.items() if v}
    mods = sorted({"space-age" for n in names if any(n.startswith(p) or n == p for p in SPACE_AGE)}
                  | {"quality" for e in ents if e.get("quality") not in (None, "normal")}
                  | {"quality" for e in ents if any("quality-module" in str(i) for i in (e.get("items") or []))})
    machines = defaultdict(Counter)
    rates = Counter()                 # item -> nominal items/s produced
    consumes = Counter()              # item -> nominal items/s consumed
    for e in ents:
        if type_of(e["name"]) not in MACHINE_TYPES:
            continue
        r = e.get("recipe")
        machines[r or "(auto)"][e["name"]] += 1
        rec = RECIPES.get(r) if r else None
        if rec:
            crafts = crafting_speed(e["name"]) / rec["energy_required"]
            for x in rec["results"]:
                rates[x["name"]] += crafts * x.get("amount", (x.get("amount_min", 0) + x.get("amount_max", 0)) / 2) * x.get("probability", 1)
            for x in rec["ingredients"]:
                consumes[x["name"]] += crafts * x["amount"]
    modules = Counter()
    for e in ents:
        for it in e.get("items") or []:
            if isinstance(it, dict):
                n = it["id"]["name"]
                modules[n] += len(it.get("items", {}).get("in_inventory", [])) or 1
            elif isinstance(e.get("items"), dict):
                pass
        if isinstance(e.get("items"), dict):            # 1.1 format
            for n, c in e["items"].items():
                modules[n] += c
    # longest underground-belt span (tiles between entrance and exit): >4 breaks with yellow undergrounds
    from blueprint import _VEC, dir_from_value
    game = "2.0" if (bp.get("version", 0) >> 48) >= 2 else "1.1"
    ugs = {(e["position"]["x"], e["position"]["y"]): e for e in ents if type_of(e["name"]) == "underground-belt"}
    max_gap = 0
    for (x, y), e in ugs.items():
        if e.get("type") != "input":
            continue
        d = dir_from_value(e.get("direction", 0), game)
        if d not in _VEC:
            continue
        dx, dy = _VEC[d]
        for k in range(1, 12):
            f = ugs.get((x + dx * k, y + dy * k))
            if f and f["name"] == e["name"] and f.get("type") == "output":
                max_gap = max(max_gap, k - 1)
                break
    produced, consumed = set(rates), set(consumes)
    return {
        "label": bp.get("label"), "version": int_to_version(bp.get("version", 0)),
        "size": [w, h], "entities": len(ents), "tiles": len(bp.get("tiles", [])), "mods": mods,
        "tiers": tiers, "machines": {r: dict(c) for r, c in machines.items()},
        "nominal_rate_per_min": {k: round(v * 60, 1) for k, v in rates.most_common()},
        "external_inputs": sorted(consumed - produced), "final_outputs": sorted(produced - consumed),
        "intermediates": sorted(produced & consumed),
        "beacons": names.get("beacon", 0), "max_underground_gap": max_gap,
        "long_handed": names.get("long-handed-inserter", 0), "modules": dict(modules.most_common()),
        "poles": {n: c for n, c in names.items() if type_of(n) == "electric-pole"},
        "description": bp.get("description"),
        "top_entities": dict(names.most_common(12)),
    }


def tier_text(t):
    if not t:
        return "-"
    mark = " ⚠ mixed" if len(t) > 1 else ""
    return ", ".join(f"{k} {v}" for k, v in t.items()) + mark


def markdown(path, a):
    out = [f"### {list(path) if path else ''} {a['label'] or '(no label)'}", "",
           f"- size **{a['size'][0]}×{a['size'][1]}**, {a['entities']} entities, {a['tiles']} tiles, v{a['version']}, mods: {', '.join(a['mods']) or 'base'}",
           f"- belts: {tier_text(a['tiers']['belt'])} · assemblers: {tier_text(a['tiers']['assembler'])} · furnaces: {tier_text(a['tiers']['furnace'])}",
           f"- inserters: {tier_text(a['tiers']['inserter'])} · poles: {tier_text(a['tiers']['pole'])}",
           f"- upgrade check: longest underground gap {a['max_underground_gap']}" + (" ⚠ >4 (yellow can't)" if a['max_underground_gap'] > 4 else " ✓") + f", long-handed inserters {a['long_handed']}"]
    if a["machines"]:
        out.append("- machines: " + "; ".join(f"{r} ×{sum(c.values())}" for r, c in sorted(a["machines"].items(), key=lambda kv: -sum(kv[1].values()))))
    if a["final_outputs"]:
        out.append("- final outputs (nominal/min, no modules): " + ", ".join(f"{i} {a['nominal_rate_per_min'].get(i, 0)}" for i in a["final_outputs"]))
    if a["external_inputs"]:
        out.append("- external inputs: " + ", ".join(a["external_inputs"]))
    if a["beacons"] or a["modules"]:
        out.append(f"- beacons {a['beacons']}, modules/items: {a['modules']}")
    if a["description"]:
        out.append("- description: " + a["description"].replace("\n", " ")[:300])
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    obj = decode(pathlib.Path(a.file).read_text())
    if a.list:
        tree(obj)
        return
    res = [(p, analyze(bp)) for p, bp in blueprints(obj)]
    if a.json:
        print(json.dumps([{"path": list(p), **r} for p, r in res], ensure_ascii=False, indent=1))
    else:
        print("\n\n".join(markdown(p, r) for p, r in res))


if __name__ == "__main__":
    main()
