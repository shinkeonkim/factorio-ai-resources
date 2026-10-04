"""Tile a grid-snapped blueprint (e.g. a rail city block) into an NxN blueprint.

Usage: tile.py <string|file> N [out.txt]
Copies are offset by snap-to-grid; entities identical after the shift (shared border streets)
are merged, wires are remapped and de-duplicated, snap-to-grid becomes N x cell.
Same-spot entities with different settings are kept (rail crossings/switches legitimately stack)
and counted as 'same-spot' for review."""
import json, sys, copy, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blueprint import decode, encode, _read_arg

SRC = CELL = None

def key(e):
    rest = {k: v for k, v in e.items() if k not in ("entity_number", "position")}
    return (e["name"], e["position"]["x"], e["position"]["y"], json.dumps(rest, sort_keys=True))

def tile(n):
    out, index, conflicts, by_pos = [], {}, 0, {}
    wires = set()
    for i in range(n):
        for j in range(n):
            remap = {}
            for e in SRC["entities"]:
                f = copy.deepcopy(e)
                f["position"] = {"x": e["position"]["x"] + CELL * i, "y": e["position"]["y"] + CELL * j}
                k = key(f)
                if k in index:                         # identical entity already placed by a neighbour
                    remap[e["entity_number"]] = index[k]; continue
                pk = (f["name"], f["position"]["x"], f["position"]["y"])
                if pk in by_pos:                       # same spot, different settings -> report
                    conflicts += 1
                f["entity_number"] = len(out) + 1
                out.append(f); index[k] = f["entity_number"]; by_pos[pk] = f["entity_number"]
                remap[e["entity_number"]] = f["entity_number"]
            for a, ca, b, cb in SRC.get("wires", []):
                w = (remap[a], ca, remap[b], cb)
                if w not in wires and (w[2], w[3], w[0], w[1]) not in wires:
                    wires.add(w)
    bp = {k: v for k, v in SRC.items() if k not in ("entities", "wires")}
    bp["label"] = f"{SRC.get('label', 'Block')} {n}x{n}"
    bp["snap-to-grid"] = {"x": CELL * n, "y": CELL * n}
    bp["entities"] = out
    bp["wires"] = [list(w) for w in sorted(wires)]
    return {"blueprint": bp}, conflicts

if __name__ == "__main__":
    SRC = decode(_read_arg(sys.argv[1]))["blueprint"]
    if "snap-to-grid" not in SRC:
        sys.exit("blueprint has no snap-to-grid; nothing to tile against")
    CELL = SRC["snap-to-grid"]["x"]
    n = int(sys.argv[2])
    obj, conflicts = tile(n)
    s = encode(obj)
    assert decode(s) == obj
    if len(sys.argv) > 3:
        open(sys.argv[3], "w").write(s + "\n")
    else:
        print(s)
    print(f"{n}x{n}: {len(obj['blueprint']['entities'])} entities (naive {len(SRC['entities']) * n * n}), "
          f"wires {len(obj['blueprint']['wires'])}, same-spot entries {conflicts}, {len(s)} chars", file=sys.stderr)
