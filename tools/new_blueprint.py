#!/usr/bin/env python3
"""Create a new blueprint folder with meta.json, generate.py, README.md (ko) and README.en.md (en).

    python3 tools/new_blueprint.py green-circuits-3to2 \\
        --title-ko "전자회로 3:2" --title-en "Green circuits 3:2" \\
        --summary-ko "..." --summary-en "..." --tags production,circuits

Then edit generate.py, run it, and run `python3 tools/build.py <id>`.
Use --from-string FILE to start from an existing blueprint string instead of a generator.
"""
import argparse
import json
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]

GEN = '''"""{title_en}

Describe the layout here: inputs (edge/row), outputs, machine counts, assumptions."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.fbp import *

bp = Blueprint("{title_en}", game="2.0")

# --- build the layout (x, y = top-left tile; see skills/factorio-blueprint/SKILL.md) ---
bp.belt_line("transport-belt", 0, 0, E, 9)
for i in range(3):
    x = 3 * i
    bp.add("inserter", x + 1, 1, N)
    bp.add("assembling-machine-2", x, 2, recipe="iron-gear-wheel")
    bp.add("inserter", x + 1, 5, N)
bp.belt_line("transport-belt", 8, 6, W, 9)
bp.add("medium-electric-pole", 2, 1); bp.add("medium-electric-pole", 2, 5)
bp.add("medium-electric-pole", 8, 1); bp.add("medium-electric-pole", 8, 5)

# --- input markers: one constant combinator per external input, count = per minute ---
bp.add_marker(-1, 0, {{"iron-plate": 150}})

bp.connect_poles()
save(bp, __file__)
'''

README = {
    "ko": '''# {title}

> {summary}

[English](README.en.md)

<!-- AUTO:START -->
<!-- AUTO:END -->

## 구조

- (레이아웃 설명: 입력이 어디로 들어와 어떤 기계를 거쳐 어디로 나가는지)

## 참고

- (전제 조건, 연구, 알려진 한계)
''',
    "en": '''# {title}

> {summary}

[한국어](README.md)

<!-- AUTO:START -->
<!-- AUTO:END -->

## Layout

- (describe the flow: where inputs enter, which machines they pass, where outputs leave)

## Notes

- (assumptions, research, known limits)
''',
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("id")
    ap.add_argument("--title-ko", required=True)
    ap.add_argument("--title-en", required=True)
    ap.add_argument("--summary-ko", default="(한 줄 요약)")
    ap.add_argument("--summary-en", default="(one-line summary)")
    ap.add_argument("--tags", default="")
    ap.add_argument("--mods", default="base")
    ap.add_argument("--from-string", help="file containing an existing blueprint string (no generator)")
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", a.id):
        raise SystemExit("id must be lowercase letters, digits and '-'")
    d = ROOT / "blueprints" / a.id
    if d.exists():
        raise SystemExit(f"{d} already exists")
    (d / "images").mkdir(parents=True)
    meta = {"id": a.id, "order": 100, "game": "2.0", "mods": a.mods.split(","),
            "tags": [t for t in a.tags.split(",") if t],
            "title": {"ko": a.title_ko, "en": a.title_en},
            "summary": {"ko": a.summary_ko, "en": a.summary_en},
            "outputs": [], "images": []}
    (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    for lang, name in (("ko", "README.md"), ("en", "README.en.md")):
        (d / name).write_text(README[lang].format(title=meta["title"][lang], summary=meta["summary"][lang]))
    if a.from_string:
        shutil.copy(a.from_string, d / "blueprint.txt")
    else:
        (d / "generate.py").write_text(GEN.format(title_en=a.title_en))
    print(f"created {d.relative_to(ROOT)}")
    print("next: " + ("" if a.from_string else f"edit + run blueprints/{a.id}/generate.py, then ")
          + f"python3 tools/build.py {a.id}")


if __name__ == "__main__":
    main()
