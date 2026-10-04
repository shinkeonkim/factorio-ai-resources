#!/usr/bin/env python3
"""Attach an image (e.g. an in-game screenshot) to a blueprint's gallery.

    python3 tools/attach_image.py rail-buffer-station ~/Desktop/shot.png \\
        --caption-ko "게임 안에서 첫 열차 하역 중" --caption-en "First train unloading in game"

Copies the file to blueprints/<id>/images/<name> (default: original file name, lowercased),
registers it in meta.json "images", then refreshes the READMEs (gallery section).
Large PNGs are downscaled to --max-width (default 1600 px) to keep the repo small.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("id")
    ap.add_argument("image")
    ap.add_argument("--caption-ko", required=True)
    ap.add_argument("--caption-en", required=True)
    ap.add_argument("--name", help="file name inside images/")
    ap.add_argument("--max-width", type=int, default=1600)
    a = ap.parse_args()
    d = ROOT / "blueprints" / a.id
    if not (d / "meta.json").exists():
        raise SystemExit(f"unknown blueprint {a.id}")
    src = pathlib.Path(a.image).expanduser()
    name = a.name or re.sub(r"[^a-z0-9._-]+", "-", src.name.lower())
    if name in ("preview.webp", "detail.webp"):
        raise SystemExit("preview.webp / detail.webp are reserved for generated images")
    dst = d / "images" / name
    dst.parent.mkdir(exist_ok=True)
    img = Image.open(src)
    if img.width > a.max_width:
        img = img.resize((a.max_width, round(img.height * a.max_width / img.width)), Image.LANCZOS)
    img.save(dst, optimize=True)
    meta = json.loads((d / "meta.json").read_text())
    images = [i for i in meta.get("images", []) if i["file"] != f"images/{name}"]
    images.append({"file": f"images/{name}", "caption": {"ko": a.caption_ko, "en": a.caption_en}})
    meta["images"] = images
    (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    print(f"attached {dst.relative_to(ROOT)} ({img.width}x{img.height})")
    subprocess.run([sys.executable, str(ROOT / "tools" / "build.py"), a.id, "--no-images"], check=True)


if __name__ == "__main__":
    main()
