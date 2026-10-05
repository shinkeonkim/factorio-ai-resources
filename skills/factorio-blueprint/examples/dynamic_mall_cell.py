"""Dynamic mall cell (Factorio 2.0): one assembler makes whatever building item is short.

Pattern decoded from community bases (Fulgora Starter, Fulgora Mall, Gleba Base — see references/base-design.md §6):
  buffer chests (read contents, green) + constant combinator (wanted items as NEGATIVE counts, green)
  → decider "each < 0 → each = 1"  (only items below target survive)
  → assembler: set_recipe from the red input, read_ingredients to the green output
  → arithmetic "each × 4"  → requester chest set_requests (asks robots for 4 crafts' worth of ingredients)
  assembler → inserter → buffer chests (output, read by the same green network)

    python3 dynamic_mall_cell.py      # prints the report and the string
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from blueprint import Blueprint, N, E, S, W

WANTED = {"transport-belt": 200, "underground-belt": 50, "splitter": 50, "inserter": 100, "fast-inserter": 100,
          "medium-electric-pole": 100, "pipe": 100, "pipe-to-ground": 50, "assembling-machine-2": 20}

bp = Blueprint("Dynamic mall cell", game="2.0",
               description="Keeps the WANTED stock of building items in the buffer chests. Needs a robot network "
                           "with plates / circuits / gears; edit the constant combinator to change the list.")

#   x: 0 1 2 3 4 5
#   0  A A A . . D      A assembler (3x3)   D decider (1x2, input south / output north when facing N)
#   1  A A A i R D      i inserter (requester -> assembler)   R requester chest
#   2  A A A . . M      M arithmetic (1x2)
#   3  . o . + . M      o inserter (assembler -> buffer)   + medium pole
#   4  . B . K . .      B buffer chest   K constant combinator (the wanted list)
am = bp.add("assembling-machine-3", 0, 0, control_behavior={
    "input_networks": {"red": True, "green": False}, "output_networks": {"red": False, "green": True},
    "set_recipe": True, "read_ingredients": True})
bp.add("fast-inserter", 3, 1, E)                      # picks from the requester east of it
req = bp.add("requester-chest", 4, 1, control_behavior={"set_requests": True, "read_contents": False})
bp.add("fast-inserter", 1, 3, N)                      # picks from the assembler north of it
buf = bp.add("buffer-chest", 1, 4)
dec = bp.add("decider-combinator", 5, 0, N, control_behavior={"decider_conditions": {
    "conditions": [{"first_signal": {"type": "virtual", "name": "signal-each"}, "constant": 0, "comparator": "<"}],
    "outputs": [{"signal": {"type": "virtual", "name": "signal-each"}, "copy_count_from_input": False}]}})
mul = bp.add("arithmetic-combinator", 5, 2, N, control_behavior={"arithmetic_conditions": {
    "first_signal": {"type": "virtual", "name": "signal-each"}, "second_constant": 4, "operation": "*",
    "output_signal": {"type": "virtual", "name": "signal-each"}}})
cc = bp.add("constant-combinator", 3, 4, control_behavior={"sections": {"sections": [{"index": 1, "filters": [
    {"index": i + 1, "name": k, "quality": "normal", "comparator": "=", "count": -v}
    for i, (k, v) in enumerate(WANTED.items())]}]}})
bp.add("medium-electric-pole", 3, 3)

# green: buffer chest contents + wanted list (negative) -> decider input
bp.wire(buf, cc, "green"); bp.wire(cc, dec, "green", None, "in")
# red: decider output (each short item = 1) -> assembler picks its recipe
bp.wire(dec, am, "red", "out", None)
# green: assembler ingredients -> x4 -> requester requests
bp.wire(am, mul, "green", None, "in"); bp.wire(mul, req, "green", "out", None)

if __name__ == "__main__":
    print(bp.report())
    print(bp.to_string())
