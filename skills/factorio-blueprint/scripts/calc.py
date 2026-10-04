#!/usr/bin/env python3
"""Factorio production-ratio calculator (recipe tree -> machine counts, belts, raw inputs).

Examples:
  calc.py electronic-circuit 10                     # 10/s with default machines (vanilla 2.0)
  calc.py electronic-circuit 600 --per-min
  calc.py processing-unit 1 --space-age --machine crafting=assembling-machine-3
  calc.py rocket-fuel 1 --raw petroleum-gas,light-oil  # treat these as supplied inputs
  calc.py plastic-bar 5 --prod 0.4                  # +40% productivity from modules (where allowed)
  calc.py --recipes-for heavy-oil                   # list recipes that make an item
  calc.py --show advanced-circuit                   # print a recipe
  calc.py electronic-circuit 10 --json

Defaults: crafting→assembling-machine-2, smelting→steel-furnace, chemistry→chemical-plant, …
Override with --machine CATEGORY=MACHINE (e.g. smelting=electric-furnace).
Use --tier 1|2|3 to pick assembling-machine-N for crafting categories in one go.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

DEFAULT_RAW = {"iron-ore", "copper-ore", "coal", "stone", "uranium-ore", "crude-oil", "water",
               "wood", "raw-fish", "steam",
               # Space Age planet resources
               "tungsten-ore", "calcite", "lava", "scrap", "holmium-ore", "lithium-brine",
               "fluorine", "ammoniacal-solution", "yumako", "jellynut", "pentapod-egg",
               "metallic-asteroid-chunk", "carbonic-asteroid-chunk", "oxide-asteroid-chunk",
               "spoilage", "biter-egg"}
# Products of multi-output processes: solved as raw by default, with a note.
DEFAULT_RAW_MULTI = {"petroleum-gas", "light-oil", "heavy-oil", "uranium-235", "uranium-238"}

DEFAULT_MACHINE = {
    "crafting": "assembling-machine-2", "advanced-crafting": "assembling-machine-2",
    "crafting-with-fluid": "assembling-machine-2", "smelting": "steel-furnace",
    "oil-processing": "oil-refinery", "chemistry": "chemical-plant", "centrifuging": "centrifuge",
    "rocket-building": "rocket-silo", "metallurgy": "foundry", "electromagnetics": "electromagnetic-plant",
    "cryogenics": "cryogenic-plant", "organic": "biochamber", "crushing": "crusher",
    "recycling": "recycler",
}
# Sensible default when an item has several recipes and none shares its name.
PREFERRED = {"solid-fuel": "solid-fuel-from-light-oil", "molten-iron": "iron-ore-melting",
             "molten-copper": "copper-ore-melting", "ice": "oxide-asteroid-crushing"}
# Recipes the solver never picks automatically (they loop or are niche).
SKIP_PREFIXES = ("empty-", "parameter-")
SKIP_SUFFIXES = ("-barrel", "-recycling")
MINING_TIME = {"uranium-ore": 2}
DRILLABLE = {"iron-ore", "copper-ore", "coal", "stone", "uranium-ore", "tungsten-ore", "calcite",
             "holmium-ore", "scrap"}


def load(space_age: bool):
    with open(os.path.join(DATA, "recipes-space-age.json" if space_age else "recipes-base.json")) as f:
        recipes = json.load(f)["recipes"]
    with open(os.path.join(DATA, "machines.json")) as f:
        machines = json.load(f)
    return recipes, machines


def producers(recipes, item):
    out = []
    for r in recipes.values():
        if r["name"].startswith(SKIP_PREFIXES) or r["name"].endswith(SKIP_SUFFIXES):
            continue
        if any(x["name"] == item for x in r["results"]):
            out.append(r["name"])
    return out


def result_amount(res):
    if "amount" in res:
        a = res["amount"]
    else:
        a = (res.get("amount_min", 0) + res.get("amount_max", 0)) / 2
    return a * res.get("probability", 1)


class Solver:
    def __init__(self, recipes, machines, machine_for, recipe_for, raw, prod, speed, space_age):
        self.recipes, self.m = recipes, machines
        self.machine_for, self.recipe_for, self.raw = machine_for, recipe_for, raw
        self.prod, self.speed, self.space_age = prod, speed, space_age
        self.demand = defaultdict(float)       # item -> rate/s
        self.order: list[str] = []
        self.notes: list[str] = []

    def pick_recipe(self, item):
        if item in self.recipe_for:
            return self.recipe_for[item]
        if item in self.raw:
            return None
        cands = producers(self.recipes, item)
        if not cands:
            return None
        if item in cands:
            return item
        if PREFERRED.get(item) in cands:
            self.notes.append(f"'{item}': using '{PREFERRED[item]}' (alternatives: "
                              f"{[c for c in cands if c != PREFERRED[item]]})")
            return PREFERRED[item]
        if len(cands) > 1:
            self.notes.append(f"'{item}' has several recipes {cands}; using '{cands[0]}' "
                              f"(override with --recipe {item}=NAME)")
        return cands[0]

    def pick_machine(self, recipe):
        cats = recipe["categories"]
        for c in cats:
            if c in self.machine_for:
                return self.machine_for[c]
        for c in cats:
            mname = DEFAULT_MACHINE.get(c)
            if mname and (self.space_age or not self.m["crafters"].get(mname, {}).get("space_age")):
                return mname
        return None

    def solve(self, item, rate):
        # topological accumulation: process items after all their consumers
        graph, visiting = {}, set()

        def visit(it):
            if it in graph:
                return
            if it in visiting:
                self.notes.append(f"cycle through '{it}' – treated as raw at that point")
                return
            visiting.add(it)
            rname = self.pick_recipe(it)
            graph[it] = rname
            if rname:
                for ing in self.recipes[rname]["ingredients"]:
                    visit(ing["name"])
            visiting.discard(it)
            self.order.append(it)

        visit(item)
        self.order.reverse()   # consumers first
        self.demand[item] = rate
        rows = []
        for it in self.order:
            need = self.demand[it]
            rname = graph[it]
            if not rname or need <= 0:
                rows.append({"item": it, "rate": need, "raw": True})
                continue
            r = self.recipes[rname]
            mname = self.pick_machine(r)
            cr = self.m["crafters"].get(mname, {})
            base_prod = cr.get("base_productivity", 0)
            prod = (self.prod + base_prod) if r.get("allow_productivity") else 0
            out = next(result_amount(x) for x in r["results"] if x["name"] == it)
            crafts_per_s = need / (out * (1 + prod))
            mspeed = cr.get("speed", 1) * (1 + self.speed)
            count = crafts_per_s * r["energy_required"] / mspeed if mname else float("nan")
            for ing in r["ingredients"]:
                self.demand[ing["name"]] += crafts_per_s * ing["amount"]
            byproducts = {x["name"]: crafts_per_s * result_amount(x) * (1 + prod)
                          for x in r["results"] if x["name"] != it}
            rows.append({"item": it, "rate": need, "recipe": rname, "machine": mname,
                         "machines": count, "machines_ceil": math.ceil(count - 1e-9) if count == count else None,
                         "craft_time": r["energy_required"], "productivity": prod,
                         "inputs": {i["name"]: crafts_per_s * i["amount"] for i in r["ingredients"]},
                         "byproducts": byproducts})
        return rows


def belts_needed(rate, machines):
    return {b: rate / v["items_per_s"] for b, v in machines["belts"].items()}


def fmt(x):
    return f"{x:.3g}" if x < 10 else f"{x:.1f}"


def fluid_names(recipes):
    return {x["name"] for r in recipes.values() for x in r["ingredients"] + r["results"] if x["type"] == "fluid"}


def print_table(rows, machines, space_age, per_min, target, fluids=frozenset()):
    unit = "/min" if per_min else "/s"
    k = 60 if per_min else 1
    belt_names = [b for b, v in machines["belts"].items() if space_age or not v.get("space_age")]
    short = {"transport-belt": "yellow", "fast-transport-belt": "red", "express-transport-belt": "blue",
             "turbo-transport-belt": "turbo"}
    print(f"Target: {fmt(rows[0]['rate'] * k)}{unit} {target}\n")
    print(f"{'item':28} {'rate' + unit:>10}  {'recipe / machine':44} {'count':>7} {'built':>5}")
    print("-" * 100)
    raws = []
    for r in rows:
        r["fluid"] = r["item"] in fluids
        if r.get("raw"):
            raws.append(r)
            continue
        label = f"{r['recipe']} @ {r['machine']}"
        prod = f" (+{r['productivity']:.0%} prod)" if r["productivity"] else ""
        print(f"{r['item']:28} {fmt(r['rate'] * k):>10}  {label + prod:44} {fmt(r['machines']):>7} {r['machines_ceil']:>5}")
        for b, v in r["byproducts"].items():
            print(f"{'':28} {'':>10}    byproduct: {b} {fmt(v * k)}{unit}")
    print("\nRaw / external inputs:")
    for r in raws:
        line = f"  {r['item']:26} {fmt(r['rate'] * k):>10}{unit}" + (" (fluid)" if r["fluid"] else "")
        if r["item"] in DRILLABLE:
            per = machines["drills"]["electric-mining-drill"]["speed"] / MINING_TIME.get(r["item"], 1)
            line += f"   ≈ {math.ceil(r['rate'] / per - 1e-9)} electric mining drills"
        print(line)
    print("\nBelt lanes (full belt = both lanes) for solid flows:")
    print(f"  {'item':26} " + " ".join(f"{short.get(b, b):>7}" for b in belt_names))
    for r in rows:
        if r["item"] in fluids:
            continue
        bn = belts_needed(r["rate"], machines)
        print(f"  {r['item']:26} " + " ".join(f"{bn[b]:7.2f}" for b in belt_names))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("item", nargs="?")
    ap.add_argument("rate", nargs="?", type=float, help="items per second (or per minute with --per-min)")
    ap.add_argument("--per-min", action="store_true")
    ap.add_argument("--space-age", action="store_true", help="use Space Age recipe set (default: vanilla 2.0)")
    ap.add_argument("--machine", action="append", default=[], help="CATEGORY=MACHINE override")
    ap.add_argument("--tier", type=int, choices=[1, 2, 3], help="assembling-machine tier for crafting categories")
    ap.add_argument("--recipe", action="append", default=[], help="ITEM=RECIPE override")
    ap.add_argument("--raw", default="", help="comma list of extra items to treat as inputs")
    ap.add_argument("--not-raw", default="", help="comma list of default-raw items to solve anyway")
    ap.add_argument("--prod", type=float, default=0.0, help="extra productivity bonus from modules, e.g. 0.4")
    ap.add_argument("--speed", type=float, default=0.0, help="net speed bonus from modules/beacons, e.g. 0.5")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--recipes-for", metavar="ITEM")
    ap.add_argument("--show", metavar="RECIPE")
    a = ap.parse_args()

    recipes, machines = load(a.space_age)
    if a.recipes_for:
        for n in producers(recipes, a.recipes_for):
            print(json.dumps(recipes[n], ensure_ascii=False))
        return
    if a.show:
        print(json.dumps(recipes.get(a.show) or f"no recipe '{a.show}'", indent=2, ensure_ascii=False))
        return
    if not a.item or a.rate is None:
        ap.error("item and rate are required")
    if not producers(recipes, a.item) and a.item not in recipes:
        close = [n for n in recipes if a.item.split("-")[0] in n][:15]
        sys.exit(f"no recipe produces '{a.item}'. Similar names: {close}")

    machine_for = {}
    if a.tier:
        for c in ("crafting", "advanced-crafting", "crafting-with-fluid"):
            machine_for[c] = f"assembling-machine-{a.tier}"
        if a.tier == 1:
            machine_for["crafting-with-fluid"] = "assembling-machine-2"
    for kv in a.machine:
        c, m = kv.split("=")
        machine_for[c] = m
    recipe_for = dict(kv.split("=") for kv in a.recipe)
    raw = (DEFAULT_RAW | DEFAULT_RAW_MULTI | set(filter(None, a.raw.split(",")))) - set(filter(None, a.not_raw.split(",")))
    rate = a.rate / 60 if a.per_min else a.rate

    s = Solver(recipes, machines, machine_for, recipe_for, raw, a.prod, a.speed, a.space_age)
    rows = s.solve(a.item, rate)
    if a.json:
        print(json.dumps({"target": a.item, "rate_per_s": rate, "rows": rows, "notes": s.notes}, indent=2))
        return
    print_table(rows, machines, a.space_age, a.per_min, a.item, fluid_names(recipes))
    multi = [r["item"] for r in rows if r.get("raw") and r["item"] in DEFAULT_RAW_MULTI]
    notes = s.notes + ([f"{multi} come from multi-output recipes (oil processing / uranium processing) and "
                        f"are treated as supplied inputs; size refineries/centrifuges separately "
                        f"(e.g. `calc.py --show advanced-oil-processing`)."] if multi else [])
    if notes:
        print("\nNotes:")
        for n in dict.fromkeys(notes):
            print(f"  - {n}")


if __name__ == "__main__":
    main()
