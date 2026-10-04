"""Writes the demo-analysis pages (ko + en). Narratives are hand-written here; numbers come from data/*.md.
Run: python3 docs/demo-analysis/_write_pages.py"""
import json
import pathlib

DOC = pathlib.Path(__file__).resolve().parent

P = {}

P["01-6x6-balancer"] = dict(
    title={"ko": "6×6 로드밸런서 (처리량 무제한)", "en": "6×6 load balancer (throughput unlimited)"},
    source={"ko": "출처 미상 (커뮤니티 표준 설계)", "en": "unknown (standard community design)"},
    img="01-6x6-balancer.webp",
    ko="""## 무엇인가

6줄 입력을 6줄 출력으로 고르게 섞는 밸런서입니다. 18×9, 빨강 벨트·지하·스플리터 122개, 기계·전력 없음.
처리량 무제한(throughput unlimited)이라 출력 일부가 막혀도 나머지 줄로 전량이 흐릅니다.

## 규칙 대비

| 항목 | 평가 |
|---|---|
| 업그레이드 | ✅ 벨트 계열만 사용, 지하 벨트 최대 간격 4 → 노랑부터 터보까지 같은 배치 |
| 6+2 버스 | ✅ 6줄 = 버스 한 묶음과 정확히 같은 폭. 제련소 출력 → 버스 시작점에 그대로 사용 |
| 물 | 해당 없음 |

## 활용

- 버스 묶음의 **시작점**(제련 열 여러 개 → 6줄)과, 기차 하역 6줄을 버스로 넣을 때 씁니다.
- 원본 문자열은 저장소에 넣지 않았습니다(demo-resources는 비공개). 버스 키트는 이 밸런서를 앞에 두는 것을 전제로 합니다.
""",
    en="""## What it is

Balances 6 input lanes onto 6 output lanes. 18×9, 122 red belts/undergrounds/splitters, no machines or power.
Throughput unlimited: if some outputs back up, everything still flows through the others.

## Against the rules

| Item | Verdict |
|---|---|
| upgrade | ✅ belts only, longest underground gap 4 → same layout from yellow to turbo |
| 6+2 bus | ✅ exactly one bus group wide; smelter output → bus start |
| water | n/a |

## Use

- At the **start of each bus group** (several smelting columns → 6 lanes) and when unloading 6 train lanes onto the bus.
- The string itself is not in the repo (demo-resources is private); the bus kit assumes this balancer in front.
""")

P["02-daiso-1"] = dict(
    title={"ko": "다이소 1 (세로형 몰, 빨강 벨트)", "en": "Daiso 1 (vertical mall, red belts)"},
    source={"ko": "사용자 제작으로 보임 (모드 아이템 포함)", "en": "apparently user-made (contains mod items)"},
    img="02-daiso-1.webp",
    ko="""## 무엇인가

몰(쇼핑센터)입니다. 37×111, 엔티티 1,049, 조립기 2 80대, 빨강 벨트 590개.
가운데 공유 벨트 줄 양옆으로 조립기가 늘어서고, 완성품은 패시브 공급 상자(44개)와 강철 상자로 들어가 봇이 가져갑니다.
아래쪽에서 톱니바퀴(15)·전선(9)·회로(6)·파이프(7)·철 막대(4)를 직접 만들어 위로 올립니다.

- 만드는 것(약 30종): 벨트·인서터·조립기 2·전봇대·레일·신호·기관차·화물칸·정유소·화학 공장·펌프잭·강철로·연구소·레이더·증기 엔진·수리팩, 그리고 **모드 아이템**(Nanobots 탄약 2종, 갈고리총 탄약)
- 외부 입력: 철판, 구리판, 강철, 돌벽돌, 목재

## 규칙 대비

| 항목 | 평가 |
|---|---|
| 업그레이드 | ⚠ 지하 벨트 최대 간격 5(노랑 불가), 롱암 42개, 전봇대 소형·중형·변전소 혼합 |
| 6+2 버스 | ⚠ 아래에서 입력이 들어오는 세로 구조. 가로 버스에서는 분기 하나로 받는 입구 설계가 필요 |
| 물 | 해당 없음 |

## 재설계 방향

- 입력을 **버스 분기 2~3줄**(철·구리 / 강철·돌벽돌·회로)로 받는 가로형 몰로 바꾸고,
- 지하 벨트 간격 ≤4, 롱암을 고속 인서터 자리로 바꿔 **같은 배치로 노랑→빨강→파랑** 업그레이드되게 합니다.
- 다이소 2와 합쳐 한 설계로 정리했습니다 → ✅ [업그레이드형 몰](../../blueprints/mall-upgradeable/README.md).
""",
    en="""## What it is

A mall. 37×111, 1,049 entities, 80 assembling machine 2, 590 red belts. Assemblers line both sides of a
shared central belt; products go into passive provider chests (44) and steel chests for bots. Gears (15),
cables (9), circuits (6), pipes (7) and sticks (4) are made at the bottom and fed upwards.

- Makes ~30 items: belts, inserters, AM2, poles, rail/signals, locomotive, wagons, refinery, chemical plant,
  pumpjack, steel furnace, lab, radar, steam engine, repair packs and **mod items** (Nanobots ammo ×2, grappling gun ammo)
- External inputs: iron, copper, steel, stone brick, wood

## Against the rules

| Item | Verdict |
|---|---|
| upgrade | ⚠ longest underground gap 5 (not yellow), 42 long-handed inserters, small/medium/substation mix |
| 6+2 bus | ⚠ vertical, fed from the bottom; needs an entrance that takes a few bus branches |
| water | n/a |

## Redesign

- Horizontal mall fed by **2-3 bus branches** (iron+copper / steel+brick+circuits),
- underground gaps ≤4 and fast-inserter slots instead of long-handed, so the **same layout goes yellow→red→blue**.
- Merged with Daiso 2 into one design → ✅ [upgradeable mall](../../blueprints/mall-upgradeable/README.en.md).
""")

P["03-daiso-2"] = dict(
    title={"ko": "다이소 2 (세로형 몰, 파랑 벨트)", "en": "Daiso 2 (vertical mall, blue belts)"},
    source={"ko": "사용자 제작으로 보임 (Space Age·모드 아이템 포함)", "en": "apparently user-made (Space Age and mod items)"},
    img="03-daiso-2.webp",
    ko="""## 무엇인가

다이소 1의 후속판입니다. 39×116, 엔티티 1,074, 파랑 벨트 555, 조립기 2 86대 + 조립기 1 3대.
구조는 다이소 1과 거의 같고, 품목이 바뀌었습니다: 고속 벨트 2배, 수리팩 2배, 포병 화차, 해양 펌프, 펌프 추가.

- 외부 입력: 다이소 1 + **처리 장치, 정제 콘크리트, 텅스텐판**(Space Age 재료)

## 규칙 대비

| 항목 | 평가 |
|---|---|
| 업그레이드 | ⚠ 지하 최대 간격 6, 롱암 52, 조립기 1·2 혼합, 전봇대 혼합 |
| 6+2 버스 | ⚠ 다이소 1과 동일 |

## 다이소 1과의 차이가 말해 주는 것

같은 골격에 벨트 티어와 품목만 바꿔 다시 만든 것이라, **처음부터 업그레이드형 골격**이었다면 다이소 1을
그대로 올려 쓸 수 있었던 경우입니다. 재설계에서는 품목 칸(조립기 + 출력 상자)을 모듈처럼 반복하고,
레시피만 바꾸면 품목을 교체할 수 있게 합니다.
""",
    en="""## What it is

Successor of Daiso 1. 39×116, 1,074 entities, 555 blue belts, 86 AM2 + 3 AM1. Same skeleton; the item list
changed (double fast belts and repair packs, artillery wagon, offshore pump, pump).

- External inputs: Daiso 1 + **processing units, refined concrete, tungsten plate** (Space Age)

## Against the rules

| Item | Verdict |
|---|---|
| upgrade | ⚠ longest underground gap 6, 52 long-handed, AM1/AM2 mix, pole mix |
| 6+2 bus | ⚠ same as Daiso 1 |

## What the difference tells us

The same skeleton was rebuilt with another belt tier and item list — exactly the case where an
**upgrade-in-place skeleton** would have let Daiso 1 simply be upgraded. The redesign repeats an item cell
(assembler + output chest) like a module so items change by recipe only.
""")

P["04-green-circuits"] = dict(
    title={"ko": "녹색 회로 (Nilaus #6)", "en": "Green circuits (Nilaus #6)"},
    source={"ko": "Nilaus Base-In-A-Book의 일부", "en": "part of Nilaus' Base-In-A-Book"},
    img="04-green-circuits.webp",
    ko="""## 무엇인가

26×13, 조립기 2 10대(전선 6 : 회로 4 = 3:2), 고속 인서터 32, 소형 전봇대 10, 노랑 벨트.
조립기 2 기준 분당 360개, 입력은 철판·구리판 벨트.

## 규칙 대비

| 항목 | 평가 |
|---|---|
| 업그레이드 | ✅ 지하 최대 간격 2, 롱암 없음, 소형 전봇대 배치 → 그대로 중형으로. 조립기 3이면 분당 600 |
| 6+2 버스 | ✅ 철·구리 2줄 입력이라 1묶음(철 4·구리 2)에서 분기 2개로 바로 연결 |
| 벨트 여유 | 조립기 3에서 구리 15/s = 노랑 한 줄 가득 → 노랑 입력으로 버티지만 여유 없음. 빨강부터 여유 |

## 평가

이번 규칙에 가장 잘 맞는 표준형입니다. 업그레이드형 라인의 기준 모듈로 삼습니다.
""",
    en="""## What it is

26×13, 10 AM2 (cable 6 : circuit 4 = 3:2), 32 fast inserters, 10 small poles, yellow belts.
360/min with AM2; inputs are iron and copper belts.

## Against the rules

| Item | Verdict |
|---|---|
| upgrade | ✅ longest underground gap 2, no long-handed, small-pole spacing → medium poles fine; 600/min with AM3 |
| 6+2 bus | ✅ iron + copper: two taps from group 1 (iron 4, copper 2) |
| belt headroom | AM3 needs 15 copper/s = one full yellow belt: works, no headroom; fine from red |

## Verdict

The best fit for the rules — used as the reference module for the upgradeable lines.
""")

P["05-plastic-sulfuric"] = dict(
    title={"ko": "플라스틱 + 황산 (Nilaus #11)", "en": "Plastic + sulfuric acid (Nilaus #11)"},
    source={"ko": "Nilaus Base-In-A-Book의 일부", "en": "part of Nilaus' Base-In-A-Book"},
    img="05-plastic-sulfuric-sheet.webp",
    ko="""## 무엇인가

북 2개짜리입니다.
- **플라스틱**: 화학 공장 12대, 22×12, 석탄 + 석유가스 → 플라스틱 (명목 분당 1,440). 롱암 12 + 일반 12, 변전소 1개.
- **황산**: 황 10 + 황산 4, 14×34, 철판·석유가스·물 → 황산.

## 규칙 대비

| 항목 | 평가 |
|---|---|
| 업그레이드 | 화학 공장은 티어가 없음 → 올릴 수 있는 것은 벨트·인서터·모듈. 플라스틱의 롱암 12개는 처리량 상한(1.2/s×12) / 황산 쪽 지하 최대 간격 5 ⚠ |
| 6+2 버스 | 석탄은 3묶음 한 줄, 유체는 파이프. 출력(플라스틱)은 3묶음으로 되돌려 넣음 |
| 물 | ✅ waterfill이면 황산 블럭 옆에 물을 만들어 파이프 길이를 없앨 수 있음 |

## 평가

석유 계열은 기계 티어가 없으니 **처음부터 최종 크기**로 지어 두고 모듈만 추가하는 편이 맞습니다.
""",
    en="""## What it is

A book of two:
- **Plastic**: 12 chemical plants, 22×12, coal + petroleum → plastic (1,440/min nominal); 12 long-handed + 12 basic inserters, 1 substation.
- **Sulfuric acid**: 10 sulfur + 4 acid plants, 14×34; iron + petroleum + water → acid.

## Against the rules

| Item | Verdict |
|---|---|
| upgrade | chemical plants have no tiers → only belts, inserters, modules change. Plastic's 12 long-handed cap throughput (1.2/s each); acid block has a 5-tile underground ⚠ |
| 6+2 bus | coal from group 3, fluids by pipe, plastic goes back onto group 3 |
| water | ✅ with Waterfill, make water beside the acid block |

## Verdict

Oil chains have no machine tiers: build them **at final size from the start** and add modules later.
""")

P["06-nuclear"] = dict(
    title={"ko": "타일형 원자력 발전소", "en": "Tileable nuclear reactor"},
    source={"ko": "출처 미상", "en": "unknown"},
    img="06-nuclear.webp",
    ko="""## 무엇인가

380×15의 가로로 긴 타일형 원자력 발전소. 설명: **N세트 → 480 + 640×(N−1) MW**.
가운데 원자로 2×2(인접 보너스), 양옆으로 열 파이프·열교환기·터빈이 길게 뻗습니다.
연료는 빨강 벨트 + 벌크 인서터 8개, 전력은 중형 전봇대 42 + 변전소 16, 바닥 타일 4,230.

## 규칙 대비

| 항목 | 평가 |
|---|---|
| 업그레이드 | 원자로에는 티어가 없음 → "업그레이드" = 세트를 옆으로 이어 붙이기. 구조 변경 없이 확장 ✅ |
| 물 | ✅ **waterfill에 특히 잘 맞음**: 열교환기 줄 옆에 물을 깔고 해양 펌프를 두면 긴 물 파이프가 필요 없음 |
| 6+2 버스 | 연료(우라늄 연료봉)는 버스가 아니라 별도 벨트/기차 |

## 메모

- 640 MW/세트는 원자로 4기 블럭 기준 인접 보너스 계산과 일치합니다(가운데 세트 이후 증가분).
- 사용후 연료 회수 경로가 블루프린트에 있는지는 게임에서 확인이 필요합니다.
""",
    en="""## What it is

A 380×15 tileable nuclear plant. Description: **N sets → 480 + 640×(N−1) MW**. A 2×2 reactor core in the
middle (neighbour bonus) with heat pipes, heat exchangers and turbines stretching both ways.
Fuel by red belt + 8 bulk inserters; 42 medium poles + 16 substations; 4,230 floor tiles.

## Against the rules

| Item | Verdict |
|---|---|
| upgrade | reactors have no tiers → "upgrading" = tiling more sets sideways, no layout change ✅ |
| water | ✅ **ideal for Waterfill**: water + offshore pumps beside the exchanger rows, no long water pipes |
| 6+2 bus | fuel cells come by their own belt/train, not the bus |

## Notes

- 640 MW per extra set matches the neighbour-bonus math of a 4-reactor block.
- Whether a spent-cell return path exists should be checked in game.
""")

P["07-nilaus-base-in-a-book"] = dict(
    title={"ko": "Nilaus' Base-In-A-Book (45개)", "en": "Nilaus' Base-In-A-Book (45 blueprints)"},
    source={"ko": "Nilaus (커뮤니티 공개 북)", "en": "Nilaus (public community book)"},
    img="07-nilaus-base-in-a-book-sheet.webp",
    ko="""## 무엇인가

시작부터 로켓까지의 기반을 번호 순서로 정리한 유명 북입니다(2.0.77).

| 번호 | 내용 | 벨트 |
|---|---|---|
| 1–3 | 톱니·벨트, 빨강 과학, 용광로, 증기 발전, 채굴, 제련(돌 용광로 24/48) | 노랑 |
| 4 | **버스 조각**: 4×4 밸런서, Full line, Half line(양쪽/한쪽/가운데) — 4줄 묶음 | 노랑 |
| 5–6 | 빨강·초록 과학, 연구소, 녹색 회로 | 노랑 |
| 7–8 | 몰: 물류(초반/후반), 회로망, 하이테크, 원자력, 생산, 기차 상점 | 노랑 |
| 9 | 군사: 관통탄, 수류탄, 포탑, 군사 과학(모듈형 포함) | 노랑/빨강 |
| 10–11 | 석유(기본/고급/비콘), 플라스틱, 황산 | 파이프 |
| 12–16 | 적색 회로(빨강/파랑 벨트 판), 파랑 과학, 엔진, 전기 엔진, 보라 과학, 청색 회로, 노랑 과학 | 빨강/파랑 |
| – | Jump Start Base | 노랑 |

## 규칙 대비

| 항목 | 평가 |
|---|---|
| 업그레이드 | ⚠ 단계별로 **다른 블루프린트**를 씁니다(몰 초반/후반, 적색 회로 빨강/파랑 벨트판). 45개 중 6개는 지하 간격 >4. 파랑 과학 #13은 기계가 빠진 틀(인서터·벨트만, 롱암 56) |
| 6+2 버스 | 4줄 묶음 기준. 분기 조각 아이디어(줄 잠수 + Full/Half)를 6줄용으로 옮겨 [버스 키트](../../blueprints/main-bus-6x2-tap/README.md)를 만들었습니다 |
| 롱암 | 상점·과학 블럭에 롱암이 많음(최대 56) → 후반 처리량 한계 |

## 이 저장소에서 쓰는 방식

- 녹색 회로(#6), 플라스틱/황산(#11)은 개별 분석 참고([04](04-green-circuits.md), [05](05-plastic-sulfuric.md)).
- 업그레이드형 과학 라인은 Nilaus 블럭의 레시피 비율을 출발점으로 하되, 한 블루프린트로 초반→후반을 쓰게 다시 설계합니다.
""",
    en="""## What it is

The well-known book that takes a base from start to rocket, numbered in build order (2.0.77).

| No. | Content | Belts |
|---|---|---|
| 1–3 | gears/belts, red science, furnaces, steam power, mining, smelting (24/48 stone furnaces) | yellow |
| 4 | **bus pieces**: 4×4 balancer, full line, half line (both/one side/middle) — 4-lane groups | yellow |
| 5–6 | red & green science, labs, green circuits | yellow |
| 7–8 | malls: logistics (early/late), circuit network, high tech, nuclear, production, train shops | yellow |
| 9 | military: AP rounds, grenades, turrets, military science (incl. modular) | yellow/red |
| 10–11 | oil (basic/advanced/beaconed), plastic, sulfuric acid | pipes |
| 12–16 | red circuits (red- and blue-belt versions), blue science, engines, electric engines, purple science, blue circuits, yellow science | red/blue |
| – | Jump Start Base | yellow |

## Against the rules

| Item | Verdict |
|---|---|
| upgrade | ⚠ stages use **different blueprints** (early/late mall, red circuits red/blue-belt). 6 of 45 have underground gaps >4. Blue science #13 is a frame without machines (inserters/belts only, 56 long-handed) |
| 6+2 bus | built for 4-lane groups; the tap idea (lanes dive + full/half) was carried over to 6 lanes in the [bus kit](../../blueprints/main-bus-6x2-tap/README.en.md) |
| long-handed | many in shops/science (up to 56) → late-game throughput cap |

## How it is used here

- Green circuits (#6) and plastic/acid (#11) are analysed separately ([04](04-green-circuits.en.md), [05](05-plastic-sulfuric.en.md)).
- Upgradeable science lines start from Nilaus' recipe ratios but are rebuilt so one blueprint serves early → late.
""")

P["08-spaceships"] = dict(
    title={"ko": "우주선 북 (9척)", "en": "Spaceships book (9 ships)"},
    source={"ko": "출처 미상", "en": "unknown"},
    img="08-spaceships-sheet.webp",
    ko="""## 무엇인가

Space Age 우주 플랫폼 9척.

| 이름 | 크기 | 특징 |
|---|---|---|
| Space science platform | 30×27 | 정지형 우주 과학 공장: 조립기 3 6대, 수집기 8, 분쇄기 3, 태양광 26, 저장고 4. 명목 분당 150 |
| Vulcanus / Fulgora / Gleba science+starter | 38×41 | 같은 선체: 추진기 3, 연료·산화제 화학 공장 6, 얼음 녹이기 2, 분쇄기 5, 기관총 포탑 30 |
| Aquilo science+starter, 각 행성 → Aquilo | 38×50 | 위 선체를 늘리고 **로켓 터렛 4**, 열교환기·터빈(가열) 추가 |
| Endgame | 36×50 | 로켓 터렛 5, 레일건 탄 제작, 축전지 25 |

공통: 빨강 벨트, 고속·벌크 인서터, 효율 모듈로 전력 절약, 외부 입력은 철판(+ 폭약·강철 등 탄약 재료).

## 규칙 대비

| 항목 | 평가 |
|---|---|
| 업그레이드 | ✅ **같은 선체를 행성 → Aquilo → Endgame으로 확장**하는 구조. 이번 규칙(같은 구조에서 단계 확장)의 좋은 예 |
| 버스·물 | 해당 없음 (얼음 녹여 물 자급) |

## 메모

- 추진기 3기 + 효율 모듈 조합은 연료 소모를 줄이는 대신 속도가 낮은 설계입니다.
- 프로메튬(최종) 선과 비교하면 회피 능력이 부족하므로, 최종 단계는 [참고 자료](../references/optimized-builds.md)의 역쐐기형 설계를 참고하세요.
""",
    en="""## What it is

Nine Space Age platforms.

| Name | Size | Notes |
|---|---|---|
| Space science platform | 30×27 | stationary space science: 6 AM3, 8 collectors, 3 crushers, 26 solar panels, 4 cargo bays; 150/min nominal |
| Vulcanus / Fulgora / Gleba science+starter | 38×41 | one hull: 3 thrusters, 6 fuel/oxidizer chemical plants, 2 ice melters, 5 crushers, 30 gun turrets |
| Aquilo science+starter, planet → Aquilo | 38×50 | the hull extended with **4 rocket turrets** and heating (exchangers, turbines) |
| Endgame | 36×50 | 5 rocket turrets, railgun ammo production, 25 accumulators |

Common: red belts, fast/bulk inserters, efficiency modules to save power; inputs are iron plates (+ explosives, steel for ammo).

## Against the rules

| Item | Verdict |
|---|---|
| upgrade | ✅ **one hull extended planet → Aquilo → endgame** — a good example of growing within the same structure |
| bus / water | n/a (water from ice) |

## Notes

- 3 thrusters + efficiency modules: frugal but slow.
- For promethium-level trips see the inverted-wedge designs in the [references](../references/optimized-builds.en.md).
""")

P["09-science-book-xtremezion"] = dict(
    title={"ko": "Science Book (XtremeZion, 메가베이스)", "en": "Science Book (XtremeZion, megabase)"},
    source={"ko": "XtremeZion — 각 블루프린트 설명의 'By XtremeZion', 메가베이스 [factorioprints](https://factorioprints.com/view/-NBq4n2SDhvxqWXyadBn)", "en": "XtremeZion — 'By XtremeZion' in every description; megabase on [factorioprints](https://factorioprints.com/view/-NBq4n2SDhvxqWXyadBn)"},
    img="09-science-book-xtremezion-sheet.webp",
    ko="""## 무엇인가

과학팩 메가베이스 북(약 70개). 비콘·모듈을 전제로 한 분당 450~5,400 규모입니다(분석 수치는 모듈·비콘 없는 명목값이라 표기보다 낮게 나옵니다).

| 묶음 | 내용 |
|---|---|
| 0 | 원자재부터 전 과학을 만드는 대형 라인(최대 327×204, 엔티티 35,361), 과학 벨트·파이프 입구, 번개(Fulgora) 조명판 |
| 1 | 연구소: 타일형 과학 연구소(벽돌 타일), 차량으로 과학팩을 나르는 실험적 배치 |
| 2 | 6종 과학 → 스시 벨트, 소형 혼합 생산(각 분당 75) |
| 6–11 | 과학팩별: 빨강 450~5,400 / 초록 270~2,100 / 군사 / 파랑 1,800~2,700 / 보라 / 노랑 (파랑·빨강·터보 벨트판 혼재) |
| 12–16 | 과학 구체(Science Sphere), 우주 과학, 금속(Metallurgic), 극저온(Cryogenic) — Space Age |

## 규칙 대비

| 항목 | 평가 |
|---|---|
| 업그레이드 | ⚠ 처음부터 **후반 전용**(조립기 3, 파랑/터보 벨트, 비콘). 일부는 조립기 1·2·3과 노랑·빨강·파랑이 한 블루프린트에 섞여 있고, 지하 간격 >4가 다수 |
| 6+2 버스 | ✗ 원자재 직입력·전용 벨트 구조라 버스 전제가 아님 |

## 재설계 방향 (사용자 결정: 업그레이드형으로)

XtremeZion의 핵심 아이디어 — **과학팩별 독립 타일, 직접 삽입 위주, 같은 블럭 반복** — 를 가져오되,
6+2 버스 분기로 입력을 받고 노랑→빨강→파랑을 같은 배치로 쓰는 과학 라인으로 다시 설계합니다.
✅ 6종 완료: [빨강](../../blueprints/science-red-upgradeable/README.md), [초록](../../blueprints/science-green-upgradeable/README.md), [군사](../../blueprints/science-military-upgradeable/README.md), [파랑](../../blueprints/science-blue-upgradeable/README.md), [보라](../../blueprints/science-purple-upgradeable/README.md), [노랑](../../blueprints/science-yellow-upgradeable/README.md). 모두 같은 폭·주기 규칙의 **쌓는 셀**입니다. 셀당 출력이 과학마다 달라서(초반 기준 분당 빨강 24, 초록 20, 군사 36, 파랑 15, 보라 25.7, 노랑 25.7) 원하는 분당 생산량 ÷ 셀당 출력만큼 셀을 쌓습니다. 군사·보라·노랑은 중간재를 별도 셀에서 받습니다.
""",
    en="""## What it is

A megabase science book (~70 blueprints) at 450–5,400 SPM with beacons and modules (the analysed numbers
are nominal without modules/beacons, so they read lower than the labels).

| Group | Content |
|---|---|
| 0 | huge raw-to-science lines (up to 327×204, 35,361 entities), science belt/pipe entry, Fulgora lightning panels |
| 1 | labs: tileable science labs (brick tiles), an experimental car-based pack transport |
| 2 | 6 sciences → sushi belt, a small mixed build (75/min each) |
| 6–11 | per science: red 450–5,400 / green 270–2,100 / military / blue 1,800–2,700 / purple / yellow (blue/red/turbo-belt versions) |
| 12–16 | Science Sphere, space science, metallurgic, cryogenic — Space Age |

## Against the rules

| Item | Verdict |
|---|---|
| upgrade | ⚠ **late-game only** from the start (AM3, blue/turbo, beacons); some mix AM1/2/3 and yellow/red/blue in one print; many underground gaps >4 |
| 6+2 bus | ✗ raw-fed dedicated belts, not bus-based |

## Redesign (user decision: make it upgradeable)

Take XtremeZion's core ideas — **one independent tile per science, mostly direct insertion, repeat the same
block** — and rebuild them as science lines fed by 6+2 bus taps that run yellow→red→blue in the same layout.
✅ All six done: [red](../../blueprints/science-red-upgradeable/README.en.md), [green](../../blueprints/science-green-upgradeable/README.en.md), [military](../../blueprints/science-military-upgradeable/README.en.md), [blue](../../blueprints/science-blue-upgradeable/README.en.md), [purple](../../blueprints/science-purple-upgradeable/README.en.md), [yellow](../../blueprints/science-yellow-upgradeable/README.en.md). All are **stackable cells** built on the same width/period rules. Output per cell differs by science (early tier, per minute: red 24, green 20, military 36, blue 15, purple 25.7, yellow 25.7), so stack target ÷ per-cell output cells of each. Military, purple and yellow take their intermediates from separate cells.
""")


def page(slug, lang):
    p = P[slug]
    other = f"{slug}.en.md" if lang == "ko" else f"{slug}.md"
    ol = "English" if lang == "ko" else "한국어"
    src_label = "출처" if lang == "ko" else "Source"
    data_label = "자동 분석 데이터" if lang == "ko" else "Raw analysis"
    return (f"# {p['title'][lang]}\n\n[{ol}]({other})\n\n"
            f"- {src_label}: {p['source'][lang]}\n- {data_label}: [data/{slug}.md](data/{slug}.md)\n\n"
            f"![{p['title'][lang]}](images/{p['img']})\n\n{p[lang]}")


def index(lang):
    if lang == "ko":
        head = ("# demo-resources 분석\n\n[English](README.en.md)\n\n"
                "사용자가 모은 블루프린트 9개를 이번 규칙(같은 구조로 초·중·후반 업그레이드, 6+2 메인버스, waterfill)에\n"
                "비추어 순서대로 분석했습니다. 원본 문자열은 저장소에 포함하지 않습니다(`demo-resources/`는 git 제외).\n"
                "이미지는 `tools/render_demo.py`가 Factorio Blueprint Editor로 렌더링한 것입니다.\n\n"
                "| # | 자료 | 한 줄 평가 |\n|---|---|---|\n")
        rows = {
            "01-6x6-balancer": "버스 시작점용 6→6 밸런서. 규칙에 그대로 맞음",
            "02-daiso-1": "세로형 몰(조립기 80). 지하 간격·롱암 때문에 업그레이드형 아님 → 재설계 대상",
            "03-daiso-2": "다이소 1을 다른 티어로 다시 만든 판 — 업그레이드형 골격의 필요성을 보여 줌",
            "04-green-circuits": "녹색 회로 3:2. 규칙에 가장 잘 맞는 기준 모듈",
            "05-plastic-sulfuric": "석유 계열: 기계 티어 없음 → 최종 크기로 짓고 모듈 추가",
            "06-nuclear": "타일형 원자력. 확장=이어 붙이기, waterfill과 궁합 좋음",
            "07-nilaus-base-in-a-book": "단계별 다른 블루프린트. 버스 분기 아이디어를 6줄 키트로 옮김",
            "08-spaceships": "같은 선체를 행성→Aquilo→Endgame으로 확장 — 규칙의 좋은 예",
            "09-science-book-xtremezion": "후반 전용 메가베이스 → 업그레이드형 과학 라인으로 재설계",
        }
    else:
        head = ("# demo-resources analysis\n\n[한국어](README.md)\n\n"
                "Nine blueprints collected by the user, analysed in order against this repo's rules (upgrade in place\n"
                "early → late, 6+2 main bus, Waterfill). The strings themselves are not in the repo (`demo-resources/`\n"
                "is git-ignored). Images were rendered with Factorio Blueprint Editor by `tools/render_demo.py`.\n\n"
                "| # | Resource | Verdict |\n|---|---|---|\n")
        rows = {
            "01-6x6-balancer": "6→6 balancer for the bus start; fits the rules as is",
            "02-daiso-1": "vertical mall (80 AM). Underground gaps and long-handed inserters → not upgradeable, redesign",
            "03-daiso-2": "Daiso 1 rebuilt for another tier — shows why an upgradeable skeleton matters",
            "04-green-circuits": "green circuits 3:2; the best-fitting reference module",
            "05-plastic-sulfuric": "oil chain: no machine tiers → build at final size, add modules",
            "06-nuclear": "tileable nuclear; growth = tiling, great with Waterfill",
            "07-nilaus-base-in-a-book": "different prints per stage; its tap idea became the 6-lane bus kit",
            "08-spaceships": "one hull grown planet → Aquilo → endgame — a good example of the rule",
            "09-science-book-xtremezion": "late-game-only megabase → rebuilt as upgradeable science lines",
        }
    lines = [head]
    for slug in P:
        n = slug.split("-")[0]
        link = f"{slug}.md" if lang == "ko" else f"{slug}.en.md"
        lines.append(f"| {n} | [{P[slug]['title'][lang]}]({link}) | {rows[slug]} |\n")
    if lang == "ko":
        lines.append("\n## 함께 보기\n\n- [메인버스 6+2 가이드](../guides/main-bus-6x2.md)\n- [업그레이드형 설계 원칙](../guides/upgrade-in-place.md)\n- [최근 최적화 설계 참고 자료](../references/optimized-builds.md)\n\n"
                     "## 다시 만들기\n\n```sh\n.venv/bin/python tools/render_demo.py          # 이미지 + data/*.md (demo-resources/ 필요)\npython3 docs/demo-analysis/_write_pages.py     # 이 문서들\n```\n")
    else:
        lines.append("\n## See also\n\n- [Main bus 6+2 guide](../guides/main-bus-6x2.en.md)\n- [Upgrade-in-place rules](../guides/upgrade-in-place.en.md)\n- [Recent optimized builds](../references/optimized-builds.en.md)\n\n"
                     "## Rebuild\n\n```sh\n.venv/bin/python tools/render_demo.py          # images + data/*.md (needs demo-resources/)\npython3 docs/demo-analysis/_write_pages.py     # these pages\n```\n")
    return "".join(lines)


if __name__ == "__main__":
    for slug in P:
        (DOC / f"{slug}.md").write_text(page(slug, "ko"))
        (DOC / f"{slug}.en.md").write_text(page(slug, "en"))
    (DOC / "README.md").write_text(index("ko"))
    (DOC / "README.en.md").write_text(index("en"))
    print("wrote", len(P) * 2 + 2, "pages")
