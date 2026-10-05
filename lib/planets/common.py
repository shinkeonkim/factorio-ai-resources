"""Stacks shared by the planet bases (all follow lib/complex: cap rows 0..7 with markers on row 8 for inputs,
everything else at y < 0, products leave as columns through the cap bottom; lib/base wraps them for robots)."""
from lib.complex import Stack
from lib.fbp import N, E, S, W
from lib.fstack import TIERS as FT

TRASH = "signal-T"          # pseudo item of overflow lanes (mixed leftovers), shown as the virtual signal T


def _filt(*items):
    return {"use_filters": True,
            "filters": [{"index": i + 1, "name": n, "quality": "normal", "comparator": "="} for i, n in enumerate(items)]}


def _requests(items, count):
    return {"sections": [{"index": 1, "filters": [
        {"index": i + 1, "name": it, "quality": "normal", "comparator": "=", "count": count} for i, it in enumerate(items)]}]}


def void_sink(item, recyclers_per_side=7, tier="mid", name=None, demand=30.0):
    """Destroys whatever arrives on `item`'s lane: a belt runs north between two columns of recyclers; each takes
    from it with two inserters and drops its output out of its front (the tile above its left column) onto a short
    belt that side-loads back into the same belt. Raw items recycle into themselves 25 % of the time, everything
    else into its ingredients, so the loop ends in nothing. A recycler (speed 0.5) handles up to 16 raw items/s;
    the inserters set the real rate. Until recycling is researched, leftovers collect in the chest at the top."""
    def build(bp, t):
        f = FT[t]
        c = 4
        for y in range(0, 8):
            bp.add(f["belt"], c, y, N)
        bp.add_marker(c, 8, {item: 0})
        bp.add(f["pole"], c - 1, 0)
        for k in range(recyclers_per_side):
            r = -5 * (k + 1)                                     # return belt row r, recyclers r+1 .. r+4
            for y in range(r, r + 5):
                bp.add(f["belt"], c, y, N)
            bp.add("recycler", c - 3, r + 1, N)
            bp.add("recycler", c + 2, r + 1, N)
            for y in (r + 2, r + 3):
                bp.add(f["ins"], c - 1, y, E)
                bp.add(f["ins"], c + 1, y, W)
            for x in (c - 3, c - 2, c - 1):
                bp.add(f["belt"], x, r, E)
            for x in (c + 2, c + 1):
                bp.add(f["belt"], x, r, W)
            bp.add(f["pole"], c - 1, r + 4); bp.add(f["pole"], c + 1, r + 4)
        top = -5 * recyclers_per_side - 1
        bp.add(f["ins"], c, top, S)
        bp.add("steel-chest", c, top - 1)
        bp.add(f["pole"], c + 1, top)

    return Stack(name or f"Void sink ({item})", build, tier, [], {item: demand})


def recycle_sort_stack(name, inputs, products, recyclers, tier="mid", rate_per_s=None):
    """Recyclers on `inputs` and a sorter for their mixed output.

    Rows (x east, y north = negative):
      y = -2        input belt (east), fed by the input columns from the cap; the first input curves into its
                    start (both lanes), the others side-load it
      y = -3        two inserters per recycler (input belt -> recycler)
      y = -7 .. -4  recyclers, 3 columns apart; each drops its output out of its front onto ...
      y = -8        the mixed belt (east) along the recyclers and through the sort section
      y = -7        sort section: per product up to three filter inserters (mixed belt -> its column)
      y = -6 .. 7   product columns (south) to the bus; the mixed belt ends in the overflow column (TRASH)
    `products`: [(item, inserters)] in sorting order. Returns the Stack; demand/supply in items/s."""
    wr = 3 * recyclers
    xs_in = [0] + [4 * k + 1 for k in range(1, len(inputs))]
    xs_prod = [wr + 3 + 4 * j for j in range(len(products))]
    x_over = (xs_prod[-1] + 4) if xs_prod else wr + 3
    ym = -8

    def build(bp, t):
        f = FT[t]
        # inputs
        for k, (x, item) in enumerate(zip(xs_in, inputs)):
            for y in range(-1, 8):
                bp.add(f["belt"], x, y, N)
            bp.add_marker(x, 8, {item: 0})
        bp.add(f["belt"], 0, -2, E)                                  # first input curves into the input belt
        for x in range(1, wr):
            bp.add(f["belt"], x, -2, E)
        # recyclers
        for k in range(recyclers):
            x = 3 * k
            bp.add("recycler", x, -7, N)
            bp.add(f["ins"], x, -3, S); bp.add(f["ins"], x + 1, -3, S)
            if k % 2 == 0:
                bp.add(f["pole"], x + 2, -3); bp.add(f["pole"], x + 2, -7)
        # mixed belt and sorter
        for x in range(0, x_over):
            bp.add(f["belt"], x, ym, E)
        for (item, n_ins), x in zip(products, xs_prod):
            for k, dx in enumerate((0, -1, 1)[:max(1, n_ins)]):
                bp.add(f["ins"], x + dx, ym + 1, N, **_filt(item))      # picks from the mixed belt (north)
            if n_ins >= 2:
                bp.add(f["belt"], x - 1, ym + 2, E)
            if n_ins >= 3:
                bp.add(f["belt"], x + 1, ym + 2, W)
            for y in range(ym + 2, 8):
                bp.add(f["belt"], x, y, S)
            bp.add(f["pole"], x + 2, ym + 1)
        for y in range(ym, 8):                                       # overflow column
            bp.add(f["belt"], x_over, y, S)
        for x in range(0, x_over + 1, 6):                            # cap-row poles for the spine
            if x not in xs_in and x not in xs_prod and x != x_over:
                bp.add(f["pole"], x, 0)

    prods = [(item, "item", x) for (item, _), x in zip(products, xs_prod)] + [(TRASH, "item", x_over)]
    rate = rate_per_s or {}
    return Stack(name, build, tier, prods, {i: rate.get(i, 0) for i in inputs},
                 {i: rate.get(i, 0) for i, _ in products} | {TRASH: rate.get(TRASH, 0)}, gap=4)


def write_planet(mod, script_file, label, description, specials):
    """blueprint.txt = the whole base (mod.base); variants/<line>.txt = each line alone (cap + 1 cell);
    variants/<file>.txt for every (file, stack) in `specials`."""
    from lib.fbp import Blueprint, save
    from lib.fstack import as_stack as _fluid_stack
    as_stack = getattr(mod, "CELL_STACK", _fluid_stack)
    bp, info = mod.base(label)
    bp.description = description
    save(bp, script_file)
    done = set()
    for key, _ in mod.LINES:
        if key in done:
            continue
        done.add(key)
        one = Blueprint(f"{label}: {mod.C[key].name}", game="2.0")
        as_stack(mod.C[key], 1, "mid").build(one, "mid")
        one.connect_poles()
        save(one, script_file, f"variants/{key}.txt")
    for fname, st in specials:
        one = Blueprint(f"{label}: {st.name}", game="2.0")
        st.build(one, "mid")
        one.connect_poles()
        save(one, script_file, f"variants/{fname}.txt")


# ------------------------------------------------------------------------------ robot-network blocks (lib/base)
def ingress_stack(rates, tier="mid", lane=45.0, name="Raw intake (belts → provider chests)"):
    """Raw items from outside: each belt column (one per `lane` items/s) comes up from the street and ends beside
    k inserters that unload it into passive provider chests, where the robots pick it up."""
    from lib.fstack import INSERTER
    import math
    ins = FT[tier]["ins"]
    cols = []
    for item, r in rates.items():
        n = max(1, math.ceil(r / lane - 1e-9))
        cols += [(item, r / n)] * n
    xs = [1 + 4 * k for k in range(len(cols))]
    deepest = max(math.ceil(r / INSERTER[ins]) for _, r in cols)

    def build(bp, t):
        for x, (item, r) in zip(xs, cols):
            k = max(1, math.ceil(r / INSERTER[ins] - 1e-9))
            for y in range(-k + 1, 8):
                bp.add(FT[t]["belt"], x, y, N)
            for j in range(k):
                bp.add(ins, x + 1, -j, W)                      # picks from the belt, drops into the chest
                bp.add("passive-provider-chest", x + 2, -j)
            bp.add_marker(x, 8, {item: round(r * 60)})
        for x in xs:
            for y in range(0, -max(deepest, 1) - 1, -6):              # beside the chests, every 6 rows
                bp.add(FT[t]["pole"], x + 3, y)

    st = Stack(name, build, tier, [], {}, gap=3)
    st.demand = {}
    for item, r in cols:
        st.demand[item] = r
    return st


def robot_pad(imports, tier="mid", count=200, name="Landing pad (imports into the robot network)"):
    """Cargo landing pad inside the robot network: it requests the imports from orbit and robots take them from it."""
    def build(bp, t):
        bp.add("cargo-landing-pad", 0, -10, request_filters=_requests(imports, count))
        bp.add("roboport", 9, -8)
        bp.add(FT[t]["pole"], 8, -3)
    return Stack(name, build, tier, [], {}, gap=4)


def robot_silo(tier="mid", ingredients=("processing-unit", "low-density-structure", "rocket-fuel"),
               name="Rocket silo (robot-fed)"):
    """Rocket silo fed by robots (a requester chest per ingredient); its cargo requests take the exports straight
    from the network."""
    def build(bp, t):
        f = FT[t]
        bp.add("rocket-silo", 0, -12)
        for k, item in enumerate(ingredients):
            x = 1 + 3 * k
            bp.add(f["ins"], x, -3, S)
            bp.add("requester-chest", x, -2, request_filters=_requests([item], 20))
        bp.add(f["pole"], 2, -2); bp.add(f["pole"], 10, -4)
        bp.add("roboport", 11, -10)
    return Stack(name, build, tier, [], {}, gap=4)


def line_stacks(mod, height, tier="mid", make=None):
    """every line of a planet module as stacks no taller than `height`"""
    from lib.base import split_line
    from lib.fstack import as_stack
    make = make or getattr(mod, "CELL_STACK", as_stack)
    out = []
    for key, n in mod.LINES:
        out += split_line(mod.C[key], n, height, lambda c, m, tr: make(c, m, tr), tier)
    return out


def raw_demand(mod, items, extra=None):
    """items/s of the given raw items the lines draw (late tier)"""
    from lib.fstack import analyse
    need = dict(extra or {})
    for key, n in mod.LINES:
        a = analyse(mod.C[key], "late")
        for k, v in a["in_per_side"].items():
            if k in items:
                need[k] = need.get(k, 0) + 2 * v * n
    return need
