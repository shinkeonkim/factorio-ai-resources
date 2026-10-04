"""Aquilo heating: buildings freeze unless a heat source above 30 C is within one tile (orthogonally or
diagonally) — wiki.factorio.com/Aquilo. Heat pipes count as heat sources; they connect to orthogonal neighbours.

`fill(bp, sources)` puts a heat pipe on every empty tile next to a freezable entity, then joins every heat-pipe
group that does not reach a heat source to one that does (shortest path over empty tiles). `check(bp)` verifies
both rules and returns the problems, so a complex that passes is a complex that stays warm."""
from __future__ import annotations

from collections import deque

# heating_energy from space-age/base-data-updates.lua (kW); immune: chests, poles, turrets, robots, rails …
FREEZE = {"electric-furnace": 100, "inserter": 30, "fast-inserter": 30, "long-handed-inserter": 50, "bulk-inserter": 50,
          "stack-inserter": 50, "assembling-machine-1": 100, "assembling-machine-2": 100, "assembling-machine-3": 100,
          "oil-refinery": 200, "chemical-plant": 100, "cryogenic-plant": 100, "lab": 100, "rocket-silo": 300,
          "roboport": 300, "storage-tank": 100, "pipe": 1, "pipe-to-ground": 150, "pump": 30, "beacon": 400,
          "radar": 300, "steam-turbine": 50, "transport-belt": 10, "fast-transport-belt": 10,
          "express-transport-belt": 10, "turbo-transport-belt": 10, "underground-belt": 50,
          "fast-underground-belt": 100, "express-underground-belt": 150, "splitter": 40, "electric-mining-drill": 100,
          "pumpjack": 50, "recycler": 100, "electromagnetic-plant": 100, "foundry": 100, "biochamber": 100,
          "heat-exchanger": 0, "offshore-pump": 0}
SOURCES = ("heating-tower", "nuclear-reactor", "heat-exchanger")


def _cells(bp):
    """tile -> entity number, and entity number -> list of tiles"""
    tiles = {}
    for (x, y), n in bp._grid.items():
        tiles.setdefault(n, []).append((x, y))
    return tiles


def _near(t):
    x, y = t
    return [(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]


def _orth(t):
    x, y = t
    return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]


def fill(bp, box=None):
    """Heat pipes on every empty tile beside a freezable entity, then connect every group to a heat source."""
    ents = {e["entity_number"]: e for e in bp.entities}
    tiles = _cells(bp)
    want = set()
    for n, ts in tiles.items():
        if FREEZE.get(ents[n]["name"], 0) > 0:
            for t in ts:
                for q in _near(t):
                    if q not in bp._grid and (box is None or (box[0] <= q[0] <= box[2] and box[1] <= q[1] <= box[3])):
                        want.add(q)
    for q in sorted(want):
        bp.add("heat-pipe", *q)
    _connect(bp, box)
    return len(want)


def _groups(bp):
    ents = {e["entity_number"]: e for e in bp.entities}
    hp = {t for t, n in bp._grid.items() if ents[n]["name"] == "heat-pipe"}
    src = {t for t, n in bp._grid.items() if ents[n]["name"] in SOURCES}
    seen, groups = set(), []
    for t in hp:
        if t in seen:
            continue
        g, q = set(), deque([t])
        seen.add(t)
        while q:
            c = q.popleft()
            g.add(c)
            for o in _orth(c):
                if o in hp and o not in seen:
                    seen.add(o); q.append(o)
        warm = any(o in src for c in g for o in _orth(c))
        groups.append((g, warm))
    return groups, hp, src


def _connect(bp, box):
    """Join cold heat-pipe groups to warm ones through empty tiles (breadth-first, shortest path). Groups that
    cannot be reached are skipped; repeats until nothing more can be joined."""
    failed = set()
    while True:
        groups, hp, src = _groups(bp)
        warm = set().union(*[g for g, w in groups if w]) if any(w for _, w in groups) else set()
        cold = [g for g, w in groups if not w and min(g) not in failed]
        if not cold or not (warm or src):
            return
        g = min(cold, key=len) if False else cold[0]
        prev = {t: None for t in g}
        q = deque(g)
        hit = None
        while q and hit is None:
            c = q.popleft()
            for o in _orth(c):
                if o in prev:
                    continue
                if o in warm or o in src:
                    hit = c; break
                if o in bp._grid:
                    continue
                if box and not (box[0] - 4 <= o[0] <= box[2] + 4 and box[1] - 4 <= o[1] <= box[3] + 4):
                    continue
                prev[o] = c
                q.append(o)
            if len(prev) > 60000:
                break
        if hit is None:
            failed.add(min(g))
            continue
        while hit is not None and hit not in g:
            bp.add("heat-pipe", *hit)
            hit = prev[hit]


def check(bp):
    """Problems: freezable entities with no heat pipe / source within one tile, and heat-pipe groups that reach no
    heat source."""
    ents = {e["entity_number"]: e for e in bp.entities}
    tiles = _cells(bp)
    groups, hp, src = _groups(bp)
    warm_tiles = set().union(*[g for g, w in groups if w]) if groups else set()
    heat = warm_tiles | src
    cold = []
    for n, ts in tiles.items():
        name = ents[n]["name"]
        if FREEZE.get(name, 0) > 0 and not any(q in heat for t in ts for q in _near(t)):
            cold.append(f"{name}@{ts[0]}")
    unheated = sum(1 for g, w in groups if not w)
    out = []
    if cold:
        out.append(f"{len(cold)} freezable entities without heat: {cold[:6]}")
    if unheated:
        out.append(f"{unheated} heat-pipe groups not connected to a heat source")
    return out


def load_kw(bp):
    """heat needed to keep everything warm (kW)"""
    return sum(FREEZE.get(e["name"], 0) for e in bp.entities)


def prune(bp):
    """Remove heat-pipe groups that reach no heat source (they heat nothing). Returns how many pipes went."""
    groups, hp, src = _groups(bp)
    dead = [bp._grid[t] for g, w in groups if not w for t in g]
    if dead:
        bp.remove(dead)
    return len(dead)
