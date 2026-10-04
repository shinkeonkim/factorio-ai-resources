"""Shared helpers for blueprint generators in this repo.

Every blueprints/<id>/generate.py starts with:

    import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
    from lib.fbp import *

and ends with save(bp, __file__)  (or save(obj, __file__, "variants/x.txt")).
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL_SCRIPTS = ROOT / "skills" / "factorio-blueprint" / "scripts"
THIRD_PARTY = ROOT / "third_party"
sys.path.insert(0, str(SKILL_SCRIPTS))

from blueprint import (Blueprint, N, E, S, W, encode, decode, validate, render_ascii,  # noqa: E402,F401
                       OverlapError, POLES, make_book)

SKIP_EXIT = 3   # exit code meaning "inputs not available, generation skipped" (build.py treats as OK)


def third_party(name: str) -> pathlib.Path:
    """Path of a gitignored third-party input; exits with SKIP_EXIT when it is missing."""
    p = THIRD_PARTY / name
    if not p.exists():
        print(f"skip: third_party/{name} not found (see third_party/README.md)", file=sys.stderr)
        sys.exit(SKIP_EXIT)
    return p


def save(bp, script_file: str, name: str = "blueprint.txt", check: bool = True) -> pathlib.Path:
    """Validate and write a Blueprint (or blueprint dict) next to the generator script."""
    obj = bp.to_dict() if isinstance(bp, Blueprint) else bp
    if check:
        problems = validate(obj) if "blueprint" in obj else []
        if problems:
            print("validation problems:", *problems, sep="\n  - ", file=sys.stderr)
            sys.exit(1)
    s = encode(obj)
    assert decode(s) == obj
    out = pathlib.Path(script_file).resolve().parent / name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(s + "\n")
    print(f"wrote {out.relative_to(ROOT)} ({len(s)} chars)")
    return out
