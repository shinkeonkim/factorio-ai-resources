"""Stacks shared by the planet complexes (all follow lib/complex: cap rows 0..7 with markers on row 8 for inputs,
everything else at y < 0, products leave as columns through the cap bottom)."""
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


def landing_pad_stack(imports, tier="mid", count=200, name="Landing pad (imports)"):
    """Imports: the cargo landing pad requests `imports` from orbit; logistic bots carry each item to its own
    requester chest, which an inserter empties onto a column running down to the bus, where that column
    starts the item's lane. Columns are 4 apart so the bus taps never collide."""
    xs = [1 + 4 * k for k in range(len(imports))]

    def build(bp, t):
        f = FT[t]
        for x, item in zip(xs, imports):
            bp.add("requester-chest", x, -3, request_filters=_requests([item], count))
            bp.add(f["ins"], x, -2, N)                         # picks from the chest above
            for y in range(-1, 8):
                bp.add(f["belt"], x, y, S)
        for x in xs[::2]:
            bp.add(f["pole"], x + 1, -2)
        mid = xs[len(xs) // 2]
        bp.add("cargo-landing-pad", mid - 4, -14, request_filters=_requests(imports, count * 2))
        bp.add("roboport", mid + 6, -10)
        bp.add(f["pole"], mid + 5, -5); bp.add(f["pole"], mid + 5, -11)

    return Stack(name, build, tier, [(it, "item", x) for it, x in zip(imports, xs)], {}, {it: 15.0 for it in imports}, gap=4)


def rocket_stack(exports, ingredients=("processing-unit", "low-density-structure", "rocket-fuel"), tier="mid",
                 name="Rocket silo + exports"):
    """Rocket silo fed from the bus through its bottom edge (one rocket part = one of each ingredient, 3 s).
    Exports from the bus go into passive provider chests beside it; the silo's cargo requests pull them in
    with logistic bots (roboport included)."""
    def build(bp, t):
        f = FT[t]
        bp.add("rocket-silo", 0, -12)
        for k, item in enumerate(ingredients):
            x = 1 + 4 * k
            for y in range(-2, 8):
                bp.add(f["belt"], x, y, N)
            bp.add(f["ins"], x, -3, S)                        # belt end -> silo
            bp.add_marker(x, 8, {item: 20})
        x0 = 1 + 4 * len(ingredients)
        for k, item in enumerate(exports):
            x = x0 + 4 * k
            for y in range(-2, 8):
                bp.add(f["belt"], x, y, N)
            bp.add(f["ins"], x, -3, S)
            bp.add("passive-provider-chest", x, -4)
            bp.add_marker(x, 8, {item: 60})
        for x in range(3, x0 + 4 * len(exports), 4):
            bp.add(f["pole"], x, -2)
        bp.add("roboport", x0 + 1, -12)
        bp.add(f["pole"], x0 - 2, -6)

    return Stack(name, build, tier, [], {i: 0.4 for i in ingredients} | {e: 1.0 for e in exports}, gap=4)


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
    """blueprint.txt = the whole complex; variants/<line>.txt = each fluid-cell line alone (cap + 1 cell);
    variants/<file>.txt for every (file, stack) in `specials`."""
    from lib.complex import compose
    from lib.fbp import Blueprint, save
    from lib.fstack import as_stack
    bp, rep = compose(label, mod.LAYOUT, mod.stacks(), tier=mod.BUS_TIER, cover=getattr(mod, "COVER", None))
    if rep["warnings"]:
        raise SystemExit("\n".join(rep["warnings"]))
    bp.description = description
    bp.connect_poles()
    save(bp, script_file)
    done = set()
    for key, _ in getattr(mod, "LINES", mod.PLAN):
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
