#!/usr/bin/env python3
"""Which research unlocks a recipe, and what it takes to get there.

    python3 tech.py assembling-machine-3            # unlocking tech, its science packs, prerequisite chain
    python3 tech.py --tech logistics-3              # one technology
    python3 tech.py --plan fast-inserter rail-ramp  # several recipes: all techs needed, in research order

Data: data/tech-unlocks.json (wube/factorio-data: base, space-age, quality, elevated-rails). Packs and
prerequisites are the prototype values; Space Age rewrites rocket-silo (also unlocks the cargo landing
pad and platform foundation) and space-science-pack (triggered by building an asteroid collector).
"""
import argparse
import json
import pathlib

D = json.loads((pathlib.Path(__file__).resolve().parents[1] / "data" / "tech-unlocks.json").read_text())
T, BY = D["technologies"], D["recipe_unlocked_by"]
SHORT = {"automation-science-pack": "red", "logistic-science-pack": "green", "military-science-pack": "military",
         "chemical-science-pack": "blue", "production-science-pack": "purple", "utility-science-pack": "yellow",
         "space-science-pack": "space", "metallurgic-science-pack": "vulcanus", "electromagnetic-science-pack": "fulgora",
         "agricultural-science-pack": "gleba", "cryogenic-science-pack": "aquilo", "promethium-science-pack": "promethium"}


ORDER = list(SHORT)


def packs(t):
    e = T[t]
    p = [SHORT.get(x, x) for x in sorted(e["packs"], key=lambda x: ORDER.index(x) if x in ORDER else 99)]
    trig = e.get("trigger") or e.get("space_age", {}).get("trigger")
    return ", ".join(p) if p else (f"trigger: {trig}" if trig else "-")


def chain(t, seen=None):
    """Prerequisites in research order (depth first, each once)."""
    seen = [] if seen is None else seen
    for p in T.get(t, {}).get("prerequisites", []):
        if p not in seen:
            chain(p, seen)
    if t not in seen:
        seen.append(t)
    return seen


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("recipes", nargs="*")
    ap.add_argument("--tech")
    ap.add_argument("--plan", action="store_true", help="merge the chains of all given recipes")
    a = ap.parse_args()
    if a.tech:
        e = T[a.tech]
        print(f"{a.tech} [{e['mod']}] packs: {packs(a.tech)}\n  prerequisites: {', '.join(e['prerequisites']) or '-'}"
              f"\n  unlocks: {', '.join(e['unlocks'] + e.get('unlocks_space_age', [])) or '-'}")
        return
    order = []
    for r in a.recipes:
        techs = BY.get(r)
        if not techs:
            print(f"{r}: no technology unlocks it (available from the start, or not a recipe)")
            continue
        for t in techs:
            print(f"{r}: {t}  ({packs(t)})")
            if a.plan:
                chain(t, order)
            else:
                print("  chain: " + " → ".join(chain(t)))
    if a.plan and order:
        print("\nresearch order:")
        for t in order:
            print(f"  {t}  ({packs(t)})")


if __name__ == "__main__":
    main()
