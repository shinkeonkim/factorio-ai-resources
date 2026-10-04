"""Write the standard file set for a stackable cell (used by every blueprints/<id>/generate.py).

    blueprint.txt               cap + 3 cells, early tier (the example and preview)
    variants/cell-<tier>.txt    one cell, snaps to a width x period grid: drag to stack
    variants/cap-<tier>.txt     the base piece that turns bus taps into lanes
"""
from lib.fbp import Blueprint, save
from lib.stack import TIERS, analyse, build_cap, build_cell, stack

EXAMPLE_CELLS = 3


def _late_rates(cell):
    a = analyse(cell, "late")
    return {k: v * 60 for k, v in a["lane_per_side"].items()}


def example(cell, tier="early", n=EXAMPLE_CELLS):
    bp = Blueprint(f"{cell.name}: cap + {n} cells ({tier})", game="2.0",
                   description=f"Paste the cell {cell.period} rows further north to grow. Markers = per-cell demand "
                               "per side at the late tier (per minute).")
    stack(bp, cell, tier, n, rates=_late_rates(cell))
    bp.connect_poles()
    return bp


def cell_bp(cell, tier):
    bp = Blueprint(f"{cell.name} cell ({tier})", game="2.0",
                   description=f"{cell.width}x{cell.period}. Drag-place northwards: the grid makes each copy "
                               "continue the belts of the one below.")
    build_cell(bp, cell, tier, 0)
    bp.connect_poles()
    bp.extra["snap-to-grid"] = {"x": cell.width, "y": cell.period}
    return bp


def cap_bp(cell, tier):
    bp = Blueprint(f"{cell.name} cap ({tier})", game="2.0",
                   description="Base piece under the lowest cell: bus taps enter at the bottom (markers), the "
                               "product leaves south through the centre.")
    build_cap(bp, cell, tier, _late_rates(cell))
    # the cap's poles reach into the lowest cell; validation of an empty-ish cap is fine without wiring
    bp.connect_poles()
    return bp


def write_all(cell, script_file):
    """A lone cell's bottom row is powered from the gap row below it (the cap's row 0 or the next cell's), so
    the real check is cap + stacked cells at every tier; the cell file itself is saved unchecked."""
    for tier in TIERS:
        problems = example(cell, tier).validate()
        if problems:
            raise SystemExit(f"{cell.name} {tier}: " + "; ".join(problems))
    save(example(cell), script_file)
    for tier in TIERS:
        save(cell_bp(cell, tier), script_file, f"variants/cell-{tier}.txt", check=False)
        save(cap_bp(cell, tier), script_file, f"variants/cap-{tier}.txt")


def variants_meta():
    out = []
    for kind, ko, en in (("cell", "셀", "cell"), ("cap", "캡(시작 조각)", "cap (base piece)")):
        for tier, t in TIERS.items():
            out.append({"file": f"variants/{kind}-{tier}.txt",
                        "label": {"ko": f"{ko} — {t['label']['ko']}", "en": f"{en} — {t['label']['en']}"}})
    return out
