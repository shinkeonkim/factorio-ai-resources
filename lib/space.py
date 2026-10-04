"""Space platform building blocks (Space Age).

Facts used here (wube/factorio-data, checked 2026-10):
* crushing: 1 chunk -> 20 iron ore / 10 carbon / 5 ice in 2 s, the chunk comes back with p = 0.3
* crusher 2x3, 540 kW; asteroid collector 3x3, faces outwards (arms reach ~7.5 tiles ahead)
* thruster 4x5 facing north, fluid ports are pass-through: fuel W(-1.5,-2) & E(1.5,0), oxidizer E(1.5,-2)
  & W(-1.5,0) -> fuel enters at the top-left side, oxidizer at the top-right side. Never put two thrusters
  side by side (A's east fuel port would meet B's west oxidizer port).
* chemical plant fluid boxes: inputs north x=-1 (first fluid), x=+1; outputs south x=-1 (first), x=+1
* solar in space: Nauvis 300 %, Vulcanus 600 %, Gleba 200 %, Fulgora 120 %, Aquilo 60 % of 60 kW
* platform blueprints include the hub (pasting over the existing hub aligns the blueprint) and the
  `space-platform-foundation` tiles; an inserter dropping onto a tile with no foundation throws the
  item overboard, which is how chunk lines are kept moving.
"""
from lib.fbp import N, E, S, W

FOUNDATION = "space-platform-foundation"
CHUNKS = ("metallic-asteroid-chunk", "carbonic-asteroid-chunk", "oxide-asteroid-chunk")
CRUSH = {"iron-ore": ("metallic-asteroid-crushing", "metallic-asteroid-chunk"),
         "carbon": ("carbonic-asteroid-crushing", "carbonic-asteroid-chunk"),
         "ice": ("oxide-asteroid-crushing", "oxide-asteroid-chunk")}


def filt(*items):
    return {"use_filters": True,
            "filters": [{"index": i + 1, "name": n, "quality": "normal", "comparator": "="} for i, n in enumerate(items)]}


def belt(bp, name, x0, y0, x1, y1, d):
    """Straight belt from (x0,y0) to (x1,y1) inclusive, flowing d."""
    xs = range(min(x0, x1), max(x0, x1) + 1)
    ys = range(min(y0, y1), max(y0, y1) + 1)
    for x in xs:
        for y in ys:
            bp.add(name, x, y, d)


def foundation(bp, void=()):
    """Foundation under the bounding box of all entities, except tiles for which void(x, y) is true."""
    from blueprint import _footprints
    fps = list(_footprints(bp.to_dict()["blueprint"]))
    x0 = min(f[2] for f in fps); y0 = min(f[3] for f in fps)
    x1 = max(f[2] + f[4] for f in fps); y1 = max(f[3] + f[5] for f in fps)
    n = 0
    for x in range(int(x0), int(x1)):
        for y in range(int(y0), int(y1)):
            if not any(v(x, y) for v in void):
                bp.add_tile(FOUNDATION, x, y)
                n += 1
    return n


def science_platform(bp, am="assembling-machine-3"):
    """Stationary space-science platform for Nauvis orbit. Hub at (-4,-4)..(3,3).

    South of the hub: 6 science assemblers put packs on y=5, which runs toward x=0 from both sides;
    two filtered inserters put them into the hub. Inputs under the assemblers:
      y=11 [ice N | carbon S]  (ice side-loads from the north at x=-12, carbon from the south)
      y=12 [iron plates]       (two electric furnaces fed straight from the metallic crusher)
    Chunk line: collectors on the south edge and the west side put chunks on y=19 (flowing west), which
    turns north at x=-17 past the carbon and ice crushers; whatever is left at the top is thrown
    overboard at (-17,4), so the line never stops and no chunk type can starve the others.
    """
    BULK, FAST, LH = "bulk-inserter", "fast-inserter", "long-handed-inserter"
    BELT = "fast-transport-belt"
    bp.add("space-platform-hub", -4, -4)
    for x in (-1, 0):                                     # science -> hub
        bp.add(BULK, x, 4, S, **filt("space-science-pack"))
    belt(bp, BELT, -8, 5, -1, 5, E)
    belt(bp, BELT, 0, 5, 7, 5, W)
    for x in (-9, -6, -3, 0, 3, 6):
        bp.add(am, x, 7, recipe="space-science-pack")
        bp.add(FAST, x + 1, 6, S)                         # pack -> y=5
        bp.add(FAST, x + 1, 10, S)                        # ice + carbon <- y=11
        bp.add(LH, x + 2, 10, S)                          # iron plates <- y=12
    belt(bp, BELT, -13, 11, 8, 11, E)
    belt(bp, BELT, -11, 12, 8, 12, E)
    # ice crusher (north-west) -> column down -> side-loads y=11 from the north (north lane)
    bp.add("crusher", -15, 6, recipe="oxide-asteroid-crushing")
    bp.add(BULK, -16, 6, W)                               # chunks in  (from the column at x=-17)
    bp.add(BULK, -16, 7, E, **filt("oxide-asteroid-chunk"))   # returned chunks back to the column
    bp.add(FAST, -13, 7, W, **filt("ice"))
    belt(bp, BELT, -12, 7, -12, 10, S)
    # carbon crusher (west) -> column up -> side-loads y=11 from the south (south lane)
    bp.add("crusher", -15, 13, recipe="carbonic-asteroid-crushing")
    bp.add(BULK, -16, 13, W)
    bp.add(BULK, -16, 14, E, **filt("carbonic-asteroid-chunk"))
    bp.add(FAST, -13, 14, W, **filt("carbon"))
    belt(bp, BELT, -12, 12, -12, 14, N)
    # metallic crusher between two furnaces; plates go up to y=13 (west) and side-load y=12
    bp.add("electric-furnace", -11, 15)
    bp.add("crusher", -7, 15, recipe="metallic-asteroid-crushing")
    bp.add("electric-furnace", -4, 15)
    bp.add(FAST, -8, 16, E, **filt("iron-ore"))          # crusher -> west furnace
    bp.add(FAST, -5, 16, W, **filt("iron-ore"))          # crusher -> east furnace
    bp.add(BULK, -7, 18, S)                               # chunks in  (from y=19)
    bp.add(BULK, -6, 18, N, **filt("metallic-asteroid-chunk"))
    bp.add(FAST, -10, 14, S)                              # plates -> (-10,13)
    bp.add(FAST, -3, 14, S)                               # plates -> (-3,13)
    belt(bp, BELT, -9, 13, -3, 13, W)
    bp.add(BELT, -10, 13, N)                              # side-loads P (y=12)
    # chunk line: y=19 westwards, column x=-17 northwards, overboard at the top
    belt(bp, BELT, -16, 19, 10, 19, W)
    belt(bp, BELT, -17, 5, -17, 19, N)
    bp.add(BULK, -17, 4, S, **filt(*CHUNKS))              # drops onto (-17,3): no foundation = overboard
    for x in (-16, -12, -8, -4, 0, 4, 8):                 # south edge collectors
        bp.add("asteroid-collector", x, 21, S)
        bp.add(BULK, x + 1, 20, S, **filt(*CHUNKS))
    for y in (9, 14):                                     # west side collectors
        bp.add("asteroid-collector", -21, y, W)
        bp.add(BULK, -18, y + 1, W, **filt(*CHUNKS))
    # power: 18 solar panels (Nauvis orbit: 180 kW each) east of the assemblers, substations + one pole
    for x in (11, 14, 17):
        for y in range(4, 22, 3):
            bp.add("solar-panel", x, y)
    for x, y in ((9, 13), (-14, 9), (0, 14), (-14, 17)):
        bp.add("substation", x, y)
    bp.add("medium-electric-pole", 2, 6)
    bp.connect_poles()
    # foundation everywhere except beside the hub's north half (keeps (-17,3) empty for the overboard drop)
    return foundation(bp, void=(lambda x, y: y < 4 and (x < -4 or x > 3),))
