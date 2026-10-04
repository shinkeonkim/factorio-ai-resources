#!/usr/bin/env python3
"""Render blueprints with real game sprites via Factorio Blueprint Editor (headless Chromium).

    python3 tools/render_fbe.py blueprints/<id>/blueprint.txt -o out.png [--focus] [--max-px 1600]

How it works: opens https://fbe.factorygamefan.com (FactoryGameFan's maintained FBE fork, Factorio 2.0 +
Space Age), focuses the canvas, dispatches a synthetic `paste` event carrying the blueprint string (the URL
`?source=` route fails with HTTP 414 above ~8k characters), waits for the loading screen to clear, then triggers
the editor's own image export (Ctrl+S) and catches the download. The PNG (32 px/tile, transparent
background, auto-shrunk by FBE to ≤8192 px) is composited on a dark background and downscaled.

Requires: pip install -r tools/requirements.txt && python3 -m playwright install chromium
"""
from __future__ import annotations

import argparse
import io
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "factorio-blueprint" / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))
from blueprint import decode, encode, _footprints  # noqa: E402

FBE_URL = "https://fbe.factorygamefan.com/"
BACKGROUND = (49, 48, 49, 255)          # close to the game's dark ground in map view


class FBERenderer:
    """Keeps one browser page open; call render(string) repeatedly."""

    def __init__(self, url: str = FBE_URL, timeout_s: int = 120):
        from playwright.sync_api import sync_playwright
        self.timeout = timeout_s * 1000
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch()
        ctx = self._browser.new_context(viewport={"width": 1400, "height": 900}, accept_downloads=True)
        self.page = ctx.new_page()
        self.page.goto(url, wait_until="networkidle", timeout=self.timeout)
        self.page.wait_for_function("() => document.querySelector('canvas') !== null", timeout=self.timeout)
        self.page.wait_for_timeout(1500)

    def render(self, bp_string: str) -> Image.Image:
        pg = self.page
        pg.evaluate("document.querySelector('canvas').focus()")
        pg.evaluate("""s => { const dt = new DataTransfer(); dt.setData('text/plain', s);
            document.dispatchEvent(new ClipboardEvent('paste', {clipboardData: dt, bubbles: true})) }""",
                    bp_string.strip())
        # importReplace() shows #loadingScreen synchronously inside the paste handler and hides it when
        # the blueprint is built; an import failure leaves the toast + no 'active' class change.
        pg.wait_for_function("() => !document.getElementById('loadingScreen').classList.contains('active')",
                             timeout=self.timeout)
        if pg.evaluate("document.getElementById('loadingScreen').classList.contains('error')"):
            raise RuntimeError("FBE failed to load the blueprint")
        pg.wait_for_timeout(500)                   # let the last sprites/wires settle
        pg.evaluate("document.querySelector('canvas').focus()")
        with pg.expect_download(timeout=self.timeout) as dl:
            pg.keyboard.press("Control+KeyS")
        path = dl.value.path()
        return Image.open(io.BytesIO(pathlib.Path(path).read_bytes())).convert("RGBA")

    def close(self):
        self._browser.close()
        self._pw.stop()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def finish(img: Image.Image, max_px: int = 1600, pad: int = 16) -> Image.Image:
    """Composite on a dark background with a small margin and fit the longest side into max_px."""
    scale = min(1.0, (max_px - 2 * pad) / max(img.size))
    if scale < 1:
        img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.LANCZOS)
    out = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), BACKGROUND)
    out.alpha_composite(img, (pad, pad))
    return out.convert("RGB")


def sub_blueprint(obj: dict, box) -> dict:
    """Blueprint with only the entities whose footprint touches box=(x0,y0,x1,y1) tiles (wires kept)."""
    bp = obj["blueprint"]
    keep = {e["entity_number"] for e, d, x0, y0, w, h in _footprints(bp)
            if x0 < box[2] and x0 + w > box[0] and y0 < box[3] and y0 + h > box[1]}
    renum = {old: i + 1 for i, old in enumerate(sorted(keep))}
    ents = []
    for e in bp["entities"]:
        if e["entity_number"] in keep:
            ents.append({**e, "entity_number": renum[e["entity_number"]]})
    wires = [[renum[a], ca, renum[b], cb] for a, ca, b, cb in bp.get("wires", []) if a in keep and b in keep]
    out = {k: v for k, v in bp.items() if k not in ("entities", "wires", "snap-to-grid", "absolute-snapping",
                                                     "position-relative-to-grid")}
    out["entities"] = ents
    if wires:
        out["wires"] = wires
    return {"blueprint": out}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("blueprint")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--max-px", type=int, default=1600)
    ap.add_argument("--focus", action="store_true", help="only the non-rail part (see render_preview.focus_box)")
    a = ap.parse_args()
    text = pathlib.Path(a.blueprint).read_text()
    if a.focus:
        from render_preview import focus_box
        obj = decode(text)
        text = encode(sub_blueprint(obj, focus_box(obj)))
    with FBERenderer() as r:
        img = finish(r.render(text), a.max_px)
    out = pathlib.Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, optimize=True)
    print(f"wrote {out} {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    main()
