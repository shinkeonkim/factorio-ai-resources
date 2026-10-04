#!/usr/bin/env python3
"""Render every blueprint in a book (or a single blueprint) with FBE and tile the thumbnails into one sheet.

    .venv/bin/python tools/contact_sheet.py book.txt -o sheet.webp [--cols 4] [--cell 420] [--only 0,3]
    .venv/bin/python tools/contact_sheet.py book.txt --each out_dir/      # one WebP per blueprint too

Each cell shows the render fitted into a square plus "[path] label (WxH)" underneath.
"""
from __future__ import annotations

import argparse
import math
import pathlib
import re
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "factorio-blueprint" / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))
from blueprint import decode, encode  # noqa: E402
from render_fbe import FBERenderer, finish  # noqa: E402
from analyze_blueprint import blueprints, analyze  # noqa: E402

BG = (49, 48, 49)


def clean_label(s):
    s = re.sub(r"\[(item|virtual-signal|entity|fluid|recipe|planet)=([^\]]+)\]", r"\2", s or "")
    s = re.sub(r"\[/?(font|color)[^\]]*\]", "", s)
    return "".join(ch if ord(ch) < 0x2000 else "?" for ch in s).strip() or "(no label)"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("-o", "--out")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--cell", type=int, default=420)
    ap.add_argument("--only", help="comma list of top-level indices to include")
    ap.add_argument("--each", help="directory to also save one WebP per blueprint")
    a = ap.parse_args()
    obj = decode(pathlib.Path(a.file).read_text())
    items = list(blueprints(obj))
    if a.only:
        keep = {int(x) for x in a.only.split(",")}
        items = [(p, b) for p, b in items if p and p[0] in keep]
    font = ImageFont.load_default()
    cells = []
    with FBERenderer() as r:
        for path, bp in items:
            if not bp.get("entities") and not bp.get("tiles"):
                continue
            st = analyze(bp)
            img = finish(r.render(encode({"blueprint": bp})), max_px=max(a.cell, 1200 if a.each else a.cell))
            if a.each:
                d = pathlib.Path(a.each); d.mkdir(parents=True, exist_ok=True)
                name = "-".join(str(x) for x in path) or "bp"
                img.save(d / f"{name}.webp", quality=85, method=6)
            thumb = img.copy(); thumb.thumbnail((a.cell, a.cell), Image.LANCZOS)
            cells.append((path, clean_label(bp.get("label")), st["size"], thumb))
            print(f"{list(path)} {clean_label(bp.get('label'))[:50]} {st['size']}", flush=True)
    if not a.out or not cells:
        return
    cols = min(a.cols, len(cells)); rows = math.ceil(len(cells) / cols)
    ch = a.cell + 34
    sheet = Image.new("RGB", (cols * (a.cell + 12) + 12, rows * ch + 12), BG)
    dr = ImageDraw.Draw(sheet)
    for i, (path, label, size, thumb) in enumerate(cells):
        x = 12 + (i % cols) * (a.cell + 12); y = 12 + (i // cols) * ch
        sheet.paste(thumb, (x + (a.cell - thumb.width) // 2, y + (a.cell - thumb.height) // 2))
        dr.text((x, y + a.cell + 4), f"{list(path)} {label[:52]}", fill=(230, 230, 230), font=font)
        dr.text((x, y + a.cell + 18), f"{size[0]}x{size[1]} tiles", fill=(160, 160, 160), font=font)
    out = pathlib.Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=85, method=6)
    print(f"wrote {out} {sheet.size}")


if __name__ == "__main__":
    main()
