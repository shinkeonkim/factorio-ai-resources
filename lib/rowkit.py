"""Small layout kit for row-based factories that are fed from the 6+2 main bus below them.

Coordinates: x east, y south. Feed columns come up from the bottom edge (`bottom`) where bus taps connect.

* `Kit.belt(y, xa, xb)`   – horizontal belt flowing east from xa to xb (inclusive)
* `Kit.column(x, y_top)`  – belt flowing north from the bottom edge up to y_top (inclusive)
* `Kit.feed(y, xs, xe, south_item, north_item)` – a two-lane belt starting with a dead tile at xs:
      south_item side-loads from the south  -> south lane
      north_item comes up west of xs, turns east one row above and side-loads from the north -> north lane
  Pass None for a lane you do not need.
* `Kit.render()` – places everything. Wherever a column crosses a horizontal belt, that belt dives
  under the column with a 1-tile underground (entrance x-1, exit x+1), so every tier still works.

All belts use the kit's tier; undergrounds never span more than 1 tile (+ merging of adjacent crossings
up to 3 tiles), inside the yellow limit of 4.
"""
from lib.fbp import N, E, S, W


class Kit:
    def __init__(self, bp, belt, ug, bottom):
        self.bp, self.belt_name, self.ug_name, self.bottom = bp, belt, ug, bottom
        self.hbelts = []          # [y, xa, xb]
        self.vcols = []           # [x, y_top, y_bottom]
        self.tiles = []           # explicit single belts (x, y, dir)
        self.markers = []         # (x, y, {item: count})

    # ---- registration --------------------------------------------------------------------
    def belt(self, y, xa, xb):
        self.hbelts.append([y, xa, xb])

    def column(self, x, y_top, y_bottom=None):
        self.vcols.append([x, y_top, self.bottom if y_bottom is None else y_bottom])

    def tile(self, x, y, d):
        self.tiles.append((x, y, d))

    def marker(self, x, y, signals):
        self.markers.append((x, y, signals))

    def feed(self, y, xs, xe, south_item=None, north_item=None, rate=None):
        """Two-lane belt on row y from xs (dead start) to xe. Inputs come up from the bottom edge."""
        self.belt(y, xs, xe)
        if south_item:
            self.column(xs + 1, y + 1)                                  # side-loads (xs+1, y) from the south
            self.marker(xs + 1, self.bottom + 1, {south_item[0]: south_item[1]})
        if north_item:
            self.column(xs - 1, y)                                      # passes row y west of the belt start
            self.tile(xs - 1, y - 1, E)                                 # curve east one row above
            self.tile(xs, y - 1, E); self.tile(xs + 1, y - 1, E)
            self.tile(xs + 2, y - 1, S)                                 # side-loads (xs+2, y) from the north
            self.marker(xs - 1, self.bottom + 1, {north_item[0]: north_item[1]})

    # ---- rendering --------------------------------------------------------------------------
    def render(self):
        occupied = {(x, y) for x, y, d in self.tiles}
        col_tiles = {}
        for x, yt, yb in self.vcols:
            for y in range(yt, yb + 1):
                col_tiles[(x, y)] = True
        for y, xa, xb in self.hbelts:
            dives = sorted({x for (x, yy) in col_tiles if yy == y and xa < x < xb})
            for x in (xa, xb):
                if (x, y) in col_tiles:
                    raise ValueError(f"column crosses the end of the belt at ({x},{y}); move it")
            # merge crossings into spans (entrance before first, exit after last), max 3 tiles apart
            spans, cur = [], None
            for x in dives:
                if cur and x - cur[1] <= 2:
                    cur[1] = x
                else:
                    if cur:
                        spans.append(cur)
                    cur = [x, x]
            if cur:
                spans.append(cur)
            skip = set()
            for a, b in spans:
                if b - a > 3:
                    raise ValueError(f"crossings at row {y} too wide for one underground: {a}..{b}")
                skip.update(range(a - 1, b + 2))
                self.bp.add(self.ug_name, a - 1, y, E, type="input")
                self.bp.add(self.ug_name, b + 1, y, E, type="output")
            for x in range(xa, xb + 1):
                if x not in skip and (x, y) not in occupied:
                    self.bp.add(self.belt_name, x, y, E)
        for (x, y) in col_tiles:
            if (x, y) not in occupied:
                self.bp.add(self.belt_name, x, y, N)
        for x, y, d in self.tiles:
            self.bp.add(self.belt_name, x, y, d)
        for x, y, sig in self.markers:
            self.bp.add_marker(x, y, sig)
