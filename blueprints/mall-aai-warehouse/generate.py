"""AAI warehouse auto-crafter (AAI Containers & Warehouses, Factorio 2.0)

One assembler keeps a stock of the 6x6 warehouse and its five logistic variants in a buffer chest.
Recipes (given by the user):
  aai-warehouse            = 200 steel plate + 100 concrete
  aai-warehouse-<variant>  = 1 aai-warehouse + 20 electronic circuit + 20 advanced circuit

    x: 0 1 2 3 4 5 6
    0  A A A . . D Q      A assembler (set recipe from red)    D decider: variant short -> 1
    1  A A A i R D Q      i fast inserter  R requester (fixed requests, robots fill it)
    2  A A A . m . P      m marker (what the requester asks for)
    3  . o . + . . P      Q latch decider (signal L)   P arithmetic L x10 -> aai-warehouse
    4  . B . K . . .      o fast inserter  B buffer chest (stock)  K constant: wanted variants (negative)

Priority: the plain warehouse is an ingredient of the variants, so it wins (value 10) while the latch is on:
on when the buffer holds < WH_LOW plain warehouses, off again at WH_HIGH. Variants that are short get value 1.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.fbp import *

VARIANTS = ["passive-provider", "active-provider", "storage", "buffer", "requester"]
WANTED = {f"aai-warehouse-{v}": 10 for v in VARIANTS}      # stock kept in the buffer chest
WH_LOW, WH_HIGH = 2, 10                                     # plain warehouse: refill when < LOW, up to HIGH
# fixed requester requests: two crafts of either recipe
REQUESTS = {"steel-plate": 400, "concrete": 200, "electronic-circuit": 40, "advanced-circuit": 40,
            "aai-warehouse": 2}

G_ONLY = {"red": False, "green": True}
R_ONLY = {"red": True, "green": False}
EACH = {"type": "virtual", "name": "signal-each"}
L = {"type": "virtual", "name": "signal-L"}
WH = {"type": "item", "name": "aai-warehouse"}


def filters(items, sign=1):
    return [{"index": i + 1, "type": "item", "name": k, "quality": "normal", "comparator": "=", "count": sign * v}
            for i, (k, v) in enumerate(items.items())]


bp = Blueprint("AAI warehouse auto-crafter", game="2.0", description=(
    "AAI 6x6 창고 + 로지스틱 창고 5종 자동 생산. 요청 상자에 강철판·콘크리트·전자회로·고급회로를 로봇이 공급. "
    "목표 수량: 정수 조합기(로지스틱 창고, 음수), 래치 조합기(일반 창고 2 미만 → 10까지)."))

am = bp.add("assembling-machine-2", 0, 0, control_behavior={
    "input_networks": R_ONLY, "set_recipe": True, "read_ingredients": False})
bp.add("fast-inserter", 3, 1, E)                                        # requester -> assembler
req = bp.add("requester-chest", 4, 1, request_filters={
    "sections": [{"index": 1, "filters": filters(REQUESTS)}], "request_from_buffers": True})
bp.add("fast-inserter", 1, 3, N)                                        # assembler -> buffer
buf = bp.add("buffer-chest", 1, 4, control_behavior={"read_contents": True, "set_requests": False})
bp.add_marker(4, 2, REQUESTS)

dec = bp.add("decider-combinator", 5, 0, N, control_behavior={"decider_conditions": {
    "conditions": [{"first_signal": EACH, "constant": 0, "comparator": "<"}],
    "outputs": [{"signal": EACH, "copy_count_from_input": False}]}})
# SR latch: L = 1 while (wh < LOW) or (wh < HIGH and L > 0)
latch = bp.add("decider-combinator", 6, 0, N, control_behavior={"decider_conditions": {
    "conditions": [
        {"first_signal": WH, "constant": WH_LOW, "comparator": "<", "first_signal_networks": G_ONLY},
        {"first_signal": WH, "constant": WH_HIGH, "comparator": "<", "first_signal_networks": G_ONLY,
         "compare_type": "or"},
        {"first_signal": L, "constant": 0, "comparator": ">", "first_signal_networks": R_ONLY,
         "compare_type": "and"}],
    "outputs": [{"signal": L, "copy_count_from_input": False}]}})
pri = bp.add("arithmetic-combinator", 6, 2, N, control_behavior={"arithmetic_conditions": {
    "first_signal": L, "second_constant": 10, "operation": "*", "output_signal": WH}})
cc = bp.add("constant-combinator", 3, 4, control_behavior={"sections": {"sections": [
    {"index": 1, "filters": filters(WANTED, -1)}]}})
bp.add("medium-electric-pole", 3, 3)

# green stock net: buffer contents + wanted list -> variant decider and latch
bp.wire(buf, cc, "green"); bp.wire(cc, dec, "green", None, "in"); bp.wire(dec, latch, "green", "in", "in")
# red latch loop
bp.wire(latch, latch, "red", "out", "in"); bp.wire(latch, pri, "red", "out", "in")
# red recipe net: variants (1) + plain warehouse (10) -> assembler picks the highest
bp.wire(dec, am, "red", "out", None); bp.wire(pri, dec, "red", "out", "out")

obj = bp.to_dict()
obj["blueprint"]["icons"] = [{"signal": {"name": "aai-warehouse"}, "index": 1},
                             {"signal": {"name": "aai-warehouse-requester"}, "index": 2}]

if __name__ == "__main__":
    print(bp.report())
    save(obj, __file__)
