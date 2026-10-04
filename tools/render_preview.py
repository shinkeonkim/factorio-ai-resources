#!/usr/bin/env python3
"""Render a top-down PNG preview of a blueprint string.

    python3 tools/render_preview.py blueprints/<id>/blueprint.txt -o blueprints/<id>/images/preview.png

Entities are drawn as their footprint, coloured by category; belts and inserters get a direction mark
when the scale allows; elevated rails are drawn translucent on top of ground rails. The output is
deterministic for a given input and Pillow version.
"""
from __future__ import annotations

import argparse
import math
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "factorio-blueprint" / "scripts"))
from blueprint import decode, _footprints, type_of, _VEC  # noqa: E402

BG = (30, 32, 36)
GRID = (40, 43, 48)

# (category, colour) – first match wins
CATEGORIES = [
    ("elevated rail", lambda n, t: n.startswith("elevated-"), (150, 110, 200, 120)),
    ("rail", lambda n, t: t in ("straight-rail", "curved-rail-a", "curved-rail-b", "half-diagonal-rail",
                                "legacy-straight-rail", "legacy-curved-rail"), (92, 92, 100, 255)),
    ("rail ramp / support", lambda n, t: n in ("rail-ramp", "rail-support"), (130, 100, 160, 255)),
    ("rail signal", lambda n, t: t in ("rail-signal", "rail-chain-signal"), (230, 90, 90, 255)),
    ("train stop", lambda n, t: t == "train-stop", (255, 110, 190, 255)),
    ("transport belt", lambda n, t: t in ("transport-belt", "underground-belt", "splitter", "loader",
                                          "loader-1x1", "lane-splitter"), None),   # colour by tier
    ("inserter", lambda n, t: t == "inserter", (200, 200, 205, 255)),
    ("assembler", lambda n, t: t == "assembling-machine", (90, 130, 170, 255)),
    ("furnace", lambda n, t: t == "furnace", (190, 120, 70, 255)),
    ("mining drill", lambda n, t: t == "mining-drill", (140, 110, 80, 255)),
    ("chest", lambda n, t: t in ("container", "logistic-container"), (200, 170, 110, 255)),
    ("pipe / fluid", lambda n, t: t in ("pipe", "pipe-to-ground", "pump", "storage-tank", "offshore-pump"),
     (80, 170, 200, 255)),
    ("electric pole", lambda n, t: t == "electric-pole", (245, 215, 80, 255)),
    ("combinator", lambda n, t: t.endswith("combinator") or t in ("lamp", "display-panel", "programmable-speaker"),
     (90, 200, 120, 255)),
    ("beacon / lab", lambda n, t: t in ("beacon", "lab"), (160, 90, 200, 255)),
    ("other", lambda n, t: True, (150, 150, 150, 255)),
]
BELT_TIER = {"": (220, 190, 60, 255), "fast-": (220, 80, 60, 255),
             "express-": (70, 140, 230, 255), "turbo-": (120, 200, 90, 255)}


def category(name: str):
    t = type_of(name)
    for label, pred, colour in CATEGORIES:
        if pred(name, t):
            if colour is None:
                tier = next((k for k in ("turbo-", "express-", "fast-") if name.startswith(k)), "")
                colour = BELT_TIER[tier]
            return label, colour
    return "other", (150, 150, 150, 255)


def _blueprints(obj):
    if "blueprint" in obj:
        yield obj["blueprint"].get("label", ""), obj
    elif "blueprint_book" in obj:
        for e in obj["blueprint_book"].get("blueprints", []):
            yield from _blueprints({k: v for k, v in e.items() if k != "index"})


RAILISH = ("rail", "elevated rail", "rail ramp / support", "rail signal", "electric pole")


def focus_box(obj: dict, margin: int = 8):
    """Tile bbox of the non-rail entities (stations, factories inside a rail block), or None."""
    _, obj = next(_blueprints(obj))
    pts = [(x0, y0, x0 + w, y0 + h) for e, d, x0, y0, w, h in _footprints(obj["blueprint"])
           if category(e["name"])[0] not in RAILISH]
    if not pts:
        return None
    return (min(p[0] for p in pts) - margin, min(p[1] for p in pts) - margin,
            max(p[2] for p in pts) + margin, max(p[3] for p in pts) + margin)


def render(obj: dict, max_px: int = 1600, title: str | None = None, box=None) -> Image.Image:
    """box=(x0, y0, x1, y1) in tiles limits the drawing to that window."""
    bp_label, obj = next(_blueprints(obj))
    fps = list(_footprints(obj["blueprint"]))
    if box:
        fps = [f for f in fps if f[2] < box[2] and f[2] + f[4] > box[0] and f[3] < box[3] and f[3] + f[5] > box[1]]
    if not fps:
        raise ValueError("blueprint has no entities")
    minx = min(f[2] for f in fps); miny = min(f[3] for f in fps)
    maxx = max(f[2] + f[4] for f in fps); maxy = max(f[3] + f[5] for f in fps)
    if box:
        minx, miny, maxx, maxy = max(minx, box[0]), max(miny, box[1]), min(maxx, box[2]), min(maxy, box[3])
    w_t, h_t = maxx - minx, maxy - miny
    s = max(2, min(24, max_px // max(w_t, h_t)))             # pixels per tile
    pad, legend_h = 2 * s, 0
    used = {}
    # draw order: ground rails, everything else, elevated on top
    order = sorted(fps, key=lambda f: (0 if category(f[0]["name"])[0] in ("rail", "rail ramp / support")
                                       else 2 if category(f[0]["name"])[0] == "elevated rail" else 1))
    for f in fps:
        used.setdefault(*category(f[0]["name"]))
    font = ImageFont.load_default()
    line_h = 14
    cols = 3
    legend_rows = math.ceil(len(used) / cols)
    legend_h = 28 + legend_rows * line_h + 10
    W = w_t * s + 2 * pad
    H = h_t * s + 2 * pad
    canvas_w = max(W, 520)
    img = Image.new("RGB", (canvas_w, H + legend_h), BG)
    layer = Image.new("RGBA", (canvas_w, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ox = pad + (canvas_w - W) // 2
    if s >= 6:                                              # faint tile grid every 10 tiles
        for gx in range(0, w_t + 1, 10):
            d.line([(ox + gx * s, pad), (ox + gx * s, pad + h_t * s)], fill=GRID + (255,))
        for gy in range(0, h_t + 1, 10):
            d.line([(ox, pad + gy * s), (ox + w_t * s, pad + gy * s)], fill=GRID + (255,))
    for e, direc, x0, y0, w, h in order:
        label, colour = category(e["name"])
        if box:                                         # clip to the window
            cx0, cy0 = max(x0, minx), max(y0, miny)
            w, h = min(x0 + w, maxx) - cx0, min(y0 + h, maxy) - cy0
            x0, y0 = cx0, cy0
        px0, py0 = ox + (x0 - minx) * s, pad + (y0 - miny) * s
        box = [px0 + (1 if s >= 6 else 0), py0 + (1 if s >= 6 else 0), px0 + w * s - 1, py0 + h * s - 1]
        d.rectangle(box, fill=colour)
        if s >= 6 and direc in _VEC and label in ("transport belt", "inserter"):
            dx, dy = _VEC[direc]
            if label == "inserter":                          # arrow shows item flow (opposite pickup)
                dx, dy = -dx, -dy
            cx, cy = px0 + w * s / 2, py0 + h * s / 2
            r = s * 0.32
            tip = (cx + dx * r, cy + dy * r)
            left = (cx - dx * r + dy * r, cy - dy * r - dx * r)
            right = (cx - dx * r - dy * r, cy - dy * r + dx * r)
            d.polygon([tip, left, right], fill=(25, 25, 25, 255))
    img.paste(layer, (0, 0), layer)
    dr = ImageDraw.Draw(img)
    y = H + 6
    head = (title or bp_label or "blueprint").replace("×", "x")
    head = "".join(ch if ord(ch) < 0x2000 else "?" for ch in head)   # default font is Latin-only
    dr.text((pad, y), f"{head[:90]}   {w_t}x{h_t} tiles, {len(fps)} entities", fill=(230, 230, 230), font=font)
    y += 20
    for i, (label, colour) in enumerate(used.items()):
        cx = pad + (i % cols) * ((canvas_w - 2 * pad) // cols)
        cy = y + (i // cols) * line_h
        dr.rectangle([cx, cy + 2, cx + 10, cy + 12], fill=colour[:3])
        dr.text((cx + 16, cy), label, fill=(210, 210, 210), font=font)
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("blueprint", help="file with a blueprint string (or '-' for stdin)")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--max-px", type=int, default=1600)
    ap.add_argument("--title")
    ap.add_argument("--focus", action="store_true", help="crop to the non-rail entities")
    a = ap.parse_args()
    text = sys.stdin.read() if a.blueprint == "-" else pathlib.Path(a.blueprint).read_text()
    obj = decode(text)
    img = render(obj, a.max_px, a.title, focus_box(obj) if a.focus else None)
    out = pathlib.Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, optimize=True)
    print(f"wrote {out} {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    main()
