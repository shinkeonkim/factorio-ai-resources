"""Vulcanus all-in-one complex (lib/planets/vulcanus.py): one bus, every production line as a stack of cells.
blueprint.txt = the whole complex; variants/<line>.txt = each line alone (cap + 1 cell, markers on its inputs)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.fbp import *
from lib.complex import compose
from lib.planets import vulcanus as V

if __name__ == "__main__":
    bp, rep = compose("Vulcanus all-in-one", V.LAYOUT, V.stacks(), tier=V.BUS_TIER)
    if rep["warnings"]:
        raise SystemExit("\n".join(rep["warnings"]))
    bp.description = ("Markers on the west end = raw inputs (lava: offshore pumps on lava; calcite, coal, tungsten ore: "
                      "mining; sulfuric acid: pumpjacks on acid geysers). Imports arrive at the landing pad.")
    bp.connect_poles()
    save(bp, __file__)
    for key, _ in V.PLAN:
        st = V.as_stack(V.C[key], 1, "mid")
        one = Blueprint(f"Vulcanus: {V.C[key].name}", game="2.0")
        st.build(one, "mid")
        one.connect_poles()
        save(one, __file__, f"variants/{key}.txt")
    for st in (V.power_stack(), V.rocket_stack(), V.landing_pad_stack(V.IMPORTS), V.stone_sink()):
        one = Blueprint(f"Vulcanus: {st.name}", game="2.0")
        st.build(one, "mid")
        one.connect_poles()
        save(one, __file__, f"variants/{st.name.split(':')[0].split(' (')[0].lower().replace(' ', '-').replace('+', 'and')}.txt")
