"""House main bus segment (33 tiles, flows east): 5 solid groups of 6 lanes + 1 fluid group of 6
pipe-to-ground chains, 2 empty rows between groups. Every lane starts with a label combinator."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.fbp import *
from lib.main_bus import segment

def build(tier, markers=True):
    bp = Blueprint(f"Main bus 6+2 ({tier}{'' if markers else ', extension'})", game="2.0",
                   description="iron 6 | copper 6 | circuits 2+2+2 | steel 2, plastic 2, stone, brick | coal, sulfur, battery, engine, e-engine, LDS | fluids (petroleum, light, heavy, lubricant, acid, water)")
    segment(bp, length=33, tier=tier, markers=markers)
    return bp

if __name__ == "__main__":
    save(build("yellow"), __file__)
    for t in ("red", "blue", "turbo"):
        save(build(t), __file__, f"variants/{t}.txt")
    save(build("yellow", markers=False), __file__, "variants/extension.txt")
