# 불카누스 올인원 기지

> 직사각형 하나로 지은 불카누스 기지: 용융 금속을 스스로 만드는 섬(주조·금속 과학·몰) → 금속 과학 분당 360, 텅스텐, 몰(주조기·대형 채굴기·터보 벨트), 스스로 다시 켜지는 전력 372 MW, 남쪽 광석 입구, 로켓·착륙장. 로봇 셀, 출력마다 재고 한도.

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

**구역별 확대 (북서 → 남동, 줄마다 서 → 동)**

![part-1](images/part-1.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base, space-age) |
| 크기 | 205×156 타일 |
| 엔티티 | 3453 |
| 주요 설비 | `passive-provider-chest` ×90<br>`foundry` ×70 (tungsten-plate 20, molten-copper-from-lava 12, metallurgic-science-pack 10, molten-iron-from-lava 8, casting-iron 4, casting-steel 4, casting-low-density-structure 2, foundry 2, turbo-transport-belt 2, turbo-underground-belt 2, turbo-splitter 2, big-mining-drill 2)<br>`requester-chest` ×66<br>`recycler` ×26<br>`chemical-plant` ×22 (carbon 18, acid-neutralisation 2, lubricant 2)<br>`assembling-machine-3` ×12 (tungsten-carbide 12)<br>`steel-chest` ×5<br>`oil-refinery` ×2 (simple-coal-liquefaction 2)<br>`rocket-silo` ×1 |
| 검사 | 통과 |

### 입력

_블루프린트 안의 일정 신호 조합기 표시 (값 = 분당 필요량, 위치 = 블루프린트 왼쪽 위 기준 타일 좌표)_

| 신호 | 분당 | 위치 |
|---|---:|---|
| `calcite` | 412 | (15, 154) |
| `coal` | 2,400 | (19, 154) |
| `tungsten-ore` | 1,860 | (23, 154) |
| `tungsten-ore` | 1,860 | (27, 154) |

### 출력

| 아이템 | 분당 | 위치 |
|---|---:|---|
| `metallurgic-science-pack` | 360 | 로봇 네트워크 → 로켓 화물 요청 |

### 단지 구성

| 줄 | 셀 크기 | 셀 수 | 출력 (분당, 후반) | 입력 (분당, 후반) |
|---|---|---:|---|---|
| Molten iron | 23×6 | 3 | `molten-iron` (fluid) 33,750, `stone` 1,350 | `lava` (fluid) 45,000, `calcite` 90 |
| Molten copper | 23×6 | 3 | `molten-copper` (fluid) 28,800, `stone` 1,728 | `lava` (fluid) 38,400, `calcite` 77 |
| Molten copper | 23×6 | 3 | `molten-copper` (fluid) 28,800, `stone` 1,728 | `lava` (fluid) 38,400, `calcite` 77 |
| Heavy oil (simple coal liquefaction) | 21×6 | 1 | `heavy-oil` (fluid) 1,200 | `coal` 240, `calcite` 48, `sulfuric-acid` (fluid) 600 |
| Lubricant | 17×4 | 1 | `lubricant` (fluid) 1,200 | `heavy-oil` (fluid) 1,200 |
| Carbon | 17×12 | 3 | `carbon` 1,080 | `coal` 2,160, `sulfuric-acid` (fluid) 21,600 |
| Tungsten carbide | 17×8 | 3 | `tungsten-carbide` 900 | `tungsten-ore` 1,800, `sulfuric-acid` (fluid) 9,000, `carbon` 900 |
| Tungsten plate | 21×12 | 5 | `tungsten-plate` 720 | `tungsten-ore` 1,920, `molten-iron` (fluid) 4,800 |
| Iron plates | 21×6 | 2 | `iron-plate` 900 | `molten-iron` (fluid) 6,000 |
| Steel | 21×6 | 2 | `steel-plate` 450 | `molten-iron` (fluid) 9,000 |
| Metallurgic science | 21×6 | 5 | `metallurgic-science-pack` 360 | `tungsten-carbide` 720, `tungsten-plate` 480, `molten-copper` (fluid) 48,000 |
| Low density structure | 25×6 | 1 | `low-density-structure` 48 | `molten-iron` (fluid) 2,560, `molten-copper` (fluid) 8,000, `plastic-bar` 160 |
| Mall: foundry | 23×6 | 1 | 상자 (몰) | `tungsten-carbide` 288, `steel-plate` 288, `electronic-circuit` 173, `refined-concrete` 115, `lubricant` (fluid) 115 |
| Mall: big mining drill | 23×6 | 1 | 상자 (몰) | `electric-mining-drill` 14, `molten-iron` (fluid) 2,880, `tungsten-carbide` 288, `electric-engine-unit` 144, `advanced-circuit` 144 |
| Mall: turbo belt | 21×6 | 1 | 상자 (몰) | `tungsten-plate` 480, `express-transport-belt` 96, `lubricant` (fluid) 1,920 |
| Mall: turbo underground | 21×6 | 1 | 상자 (몰) | `tungsten-plate` 1,829, `express-underground-belt` 91, `lubricant` (fluid) 1,829 |
| Mall: turbo splitter | 23×6 | 1 | 상자 (몰) | `express-splitter` 60, `tungsten-plate` 900, `processing-unit` 120, `lubricant` (fluid) 4,800 |
| Raw intake (south gate) | - | - | 방해석·석탄·텅스텐 광석 벨트 → 공급 상자 | |
| Power | - | - | 산 중화 화학 공장 2대 + 증기 터빈 64대 (372 MW) | |
| Stone voids ×3 | - | - | 용암 선반의 돌 벨트 끝, 재활용기 14대씩 | |
| Landing pad | - | - | 수입품 11종 → 로봇 네트워크 | |
| Rocket silo | - | - | 로봇이 재료를 넣는 사일로; 수출은 화물 요청으로 | |

선반 (아래 → 위; 섬마다 유체를 스스로 만들고, 유체 없는 블록은 빈자리에 채움):

| 선반 | 블록 |
|---|---|
| 1 | Power: acid neutralisation + 64 turbines, Molten iron x2, Iron plates x4 + Steel x4 + Tungsten plate x2 (dense), Tungsten plate x10 (dense), Tungsten plate x8 (dense), Stone void (15/s) |
| 2 | Molten copper x3, Molten copper x3, Molten iron x1, Low density structure x1, Carbon x16 (dense), Carbon x2 + Tungsten carbide x12 (dense), Metallurgic science x10 (dense), Stone void (22/s), Stone void (22/s), Stone void (22/s) |
| 3 | Molten iron x1, Heavy oil (simple coal liquefaction) x1, Lubricant x1, Mall: foundry x2 + Mall: turbo belt x2 + Mall: turbo underground x2 + Mall: turbo splitter x2 (dense), Mall: big mining drill x2 (dense), Stone void (8/s) |
| 빈자리 채움 | Solar restart kit, Rocket silo (robot-fed), Landing pad (imports into the robot network) |

코어 199×149칸, 전체 205×156칸, 3,453개 엔티티, 밀도 0.11 · 타일 점유율 0.22 (참고 커뮤니티 기지: 0.24–0.44 · 0.55–0.82). 최대 전력 206 MW / 발전 372 MW.

### 로드맵

| 단계 | 시기 / 필요한 연구 | 할 일 |
|---|---|---|
| 0. 도착 | `foundry` (아이템을 처음 만들면), `rocket-silo` (빨강·초록·파랑·보라·노랑) | 주조기 연구 전: 우주 플랫폼에서 착륙장·로봇·기본 건물을 내립니다. 용암 호수 옆, 방해석·석탄·텅스텐 광맥 근처의 디몰리셔 영역 밖에 자리를 잡습니다. |
| 1. 전력 | `calcite-processing` (처음 캐면), `nuclear-power` (빨강·초록·파랑) | 전력 줄(산 중화 + 터빈)을 먼저: 방해석과 황산(산 간헐천 펌프잭)만 있으면 372 MW. 처음엔 터빈 몇 대로 시작해도 됩니다. |
| 2. 용융 금속·주조 | `foundry` (아이템을 처음 만들면) | 용융 철·구리 섬과 철판·강철 주조. 용암은 그 선반 서쪽 끝 지하 파이프에 해양 펌프로 연결합니다. 돌이 나오므로 같은 섬의 돌 처리 블록도 함께 놓습니다(재활용 연구 전엔 상자에 쌓임). |
| 3. 텅스텐·과학 | `tungsten-carbide` (처음 캐면), `tungsten-steel` (아이템을 처음 만들면), `metallurgic-science-pack` (아이템을 처음 만들면) | 탄소 → 탄화 텅스텐, 텅스텐 판, 금속 과학(분당 360). 셀을 더 쌓으면 비례해서 늘어납니다. |
| 4. 몰·윤활유 | `calcite-processing` (처음 캐면), `big-mining-drill` (아이템을 처음 만들면), `turbo-transport-belt` (빨강·초록·파랑·보라·우주·불카누스) | 간이 석탄 액화 → 윤활유, 몰 줄(주조기·대형 채굴기·터보 벨트류). 회로·엔진·급행 벨트는 착륙장 수입. |
| 5. 로켓·수출 | `foundry` (아이템을 처음 만들면), `rocket-silo` (빨강·초록·파랑·보라·노랑) | 저밀도 구조물 주조(플라스틱 수입)와 로켓 사일로. 금속 과학·탄화 텅스텐·텅스텐 판·철판을 수출 상자에서 로켓 화물로. |

**다음에 지을 것**

- [정제 콘크리트 (쌓는 셀)](../refined-concrete/README.md) — 주조기 재료(정제 콘크리트) — 수입 대신 직접

### 파일

| 파일 | 설명 |
|---|---|
| [`blueprint.txt`](blueprint.txt) | 기지 전체 (직사각형 코어 + 남쪽 광석 입구) |
| [`variants/molten-iron.txt`](variants/molten-iron.txt) | 용융 철 — 캡 + 셀 1개 |
| [`variants/molten-copper.txt`](variants/molten-copper.txt) | 용융 구리 — 캡 + 셀 1개 |
| [`variants/heavy-oil.txt`](variants/heavy-oil.txt) | 중유 (간이 석탄 액화) — 캡 + 셀 1개 |
| [`variants/lubricant.txt`](variants/lubricant.txt) | 윤활유 — 캡 + 셀 1개 |
| [`variants/carbon.txt`](variants/carbon.txt) | 탄소 — 캡 + 셀 1개 |
| [`variants/tungsten-carbide.txt`](variants/tungsten-carbide.txt) | 탄화 텅스텐 — 캡 + 셀 1개 |
| [`variants/tungsten-plate.txt`](variants/tungsten-plate.txt) | 텅스텐 판 — 캡 + 셀 1개 |
| [`variants/iron-plate.txt`](variants/iron-plate.txt) | 철판 주조 — 캡 + 셀 1개 |
| [`variants/steel-plate.txt`](variants/steel-plate.txt) | 강철 주조 — 캡 + 셀 1개 |
| [`variants/science.txt`](variants/science.txt) | 금속 과학 — 캡 + 셀 1개 |
| [`variants/low-density-structure.txt`](variants/low-density-structure.txt) | 저밀도 구조물 주조 — 캡 + 셀 1개 |
| [`variants/mall-foundry.txt`](variants/mall-foundry.txt) | 몰: 주조기 — 캡 + 셀 1개 |
| [`variants/mall-big-drill.txt`](variants/mall-big-drill.txt) | 몰: 대형 채굴기 — 캡 + 셀 1개 |
| [`variants/mall-turbo-belt.txt`](variants/mall-turbo-belt.txt) | 몰: 터보 벨트 — 캡 + 셀 1개 |
| [`variants/mall-turbo-underground.txt`](variants/mall-turbo-underground.txt) | 몰: 터보 지하 벨트 — 캡 + 셀 1개 |
| [`variants/mall-turbo-splitter.txt`](variants/mall-turbo-splitter.txt) | 몰: 터보 분배기 — 캡 + 셀 1개 |
| [`variants/power.txt`](variants/power.txt) | 전력: 산 중화 + 터빈 64기 (372 MW) |
| [`variants/rocket-silo.txt`](variants/rocket-silo.txt) | 로켓 사일로 (로봇 공급) |
| [`variants/stone-void.txt`](variants/stone-void.txt) | 돌 처리 (재활용기) |
| [`variants/landing-pad.txt`](variants/landing-pad.txt) | 착륙장 (로봇 네트워크로 수입) |
| [`variants/raw-intake.txt`](variants/raw-intake.txt) | 남쪽 광석 입구 (벨트 → 공급 상자) |

문자열을 클립보드에 복사한 뒤 게임에서 블루프린트 라이브러리 → 문자열 가져오기:

```sh
pbcopy < blueprints/planet-vulcanus/blueprint.txt   # macOS
xclip -selection clipboard < blueprints/planet-vulcanus/blueprint.txt   # Linux
```

### 다시 생성

```sh
python3 blueprints/planet-vulcanus/generate.py
python3 tools/build.py planet-vulcanus
```

<!-- AUTO:END -->

## 기지 모양

커뮤니티의 행성 기지는 행성 전체에 버스를 깔지 않습니다. 빽빽한 직사각형 하나에 생산을 모으고, 전력·방어를 가장자리에 두릅니다(아래 '참고한 커뮤니티 설계'). 이 기지도 그렇게 짓습니다(`lib/base.py`).

- **섬**: 유체와 중간재를 함께 쓰는 줄을 한 섬으로 묶습니다(예: 용융 철 + 그 주조, 용융 구리 + 금속 과학). 섬이 선반보다 넓으면 여러 조각으로 나누는데, 조각마다 자기 유체 생산 셀을 가집니다. 그래서 유체가 기지를 가로지르지 않습니다(`references/base-design.md` §3).
- **선반**: 섬 조각을 키가 비슷한 것끼리 가로 선반에 채우고, 선반을 쌓아 직사각형을 만듭니다. 선반 아래 거리에는 그 선반이 쓰는 유체만 지나갑니다(지하 파이프 6줄 묶음, 마지막 사용처에서 끝남). 유체가 필요 없는 블록(로봇 셀, 사일로, 착륙장 등)은 선반 위 빈자리에 채워 넣습니다.
- **로봇 셀**: 기계마다 요청 상자(재료)와 공급 상자(결과)가 있어 벨트 열이 필요 없습니다. 섬 안에서만 쓰는 중간재(예: 기어·구리선 → 2차 재활용)와 부산물(돌, 넘침)은 짧은 거리 벨트로 갑니다. 로봇 기지는 블록 사이 기둥에 약 48칸마다 있습니다.
- **스스로 조절**: 공급 상자로 나가는 출력 인서터는 네트워크에 약 2분치가 쌓이면 멈춥니다(로지스틱 조건). 가열탑 연료는 축전지가 90% 미만일 때만 버너 인서터로 넣습니다. 전기가 없어도 돌아가므로 기지가 스스로 다시 켜집니다. 축전지가 20% 아래로 떨어지면 스피커와 지도 경고가 울립니다(`references/circuits.md`).
- **입력**: 모두 가장자리에 있습니다. 유체는 선반마다 서쪽, 광석은 남쪽 입구로 들어오고, 바깥 끝은 지하 벨트·지하 파이프입니다. 그 옆에 표시 조합기(분당 수량)와 디스플레이 패널이 있습니다.
- **용암 섬**: 용융 철·구리 주조기와 돌 처리 재활용기가 같은 섬에서 돌 벨트를 함께 씁니다(주조기 스택마다 벨트 하나). 돌은 초당 약 80개라 로봇 대신 벨트로 처리합니다. 돌이 쌓이면 용융 금속 생산이 멈추므로 처리 블록이 같은 선반에 있어야 합니다(돌은 25% 확률로 자기 자신이 되므로 75%가 사라짐). 재활용 연구(풀가오라) 전에는 처리 블록 위쪽 상자에 쌓입니다.
- **남쪽 광석 입구**: 방해석·석탄·텅스텐 광석 벨트가 남쪽에서 들어와 공급 상자로 내려집니다.
- **유체 셀**: 주조기는 유체 입력이 벨트 쪽, 출력이 가운데를 보도록 돌려 놓습니다. 입력 유체마다 기계 행을 따로 씁니다.
- **생성할 때 검사**: 모든 타일 충돌, 선반 거리의 줄 용량(파이프 1,200/s), 전력망 연결을 생성 단계에서 검사합니다. 하나라도 어긋나면 문자열을 만들지 않습니다.

## 전력·방어

- 전력: 산 중화(방해석 + 황산 → 500°C 증기) 화학 공장 2대가 증기 터빈 64대를 돌립니다(372 MW). 태양광 8장 + 축전지 4개의 재시동 키트가 터빈이 식었을 때 화학 공장을 돌립니다(불카누스 태양광 400%).
- 방어: 불카누스의 적은 디몰리셔입니다. 포탑으로 막는 대상이 아니므로 둘레 방어 대신 **영역 밖에 짓는 것**이 원칙입니다. 그래서 이 기지에는 외곽 띠가 없습니다.

## 늘리는 법

- 블록 하나를 더 키우려면 그 블록 위에 셀을 더 붙입니다(쌓는 셀). 줄 전체를 늘리려면 `lib/planets/vulcanus.py`의 `PLAN` 숫자를 바꾸고 다시 생성하세요. 같은 높이로 다시 나눠 다시 채웁니다.
- 줄 하나만 따로 쓰려면 `variants/<줄>.txt`(캡 + 셀 1개, 입력에 표시 조합기)를 쓰세요.

## 참고한 커뮤니티 설계 (문자열은 저장소에 넣지 않음)

- "Vulcanus all production, no mods" — 직사각형 하나, 터빈 블록을 한쪽 가장자리에 (https://factorioprints.com/view/-OBM-LoRxzZKXi8dvphv)
- "Vulcanus Production" — 블록별 고밀도 생산 (https://factorioprints.com/view/-OAjOz4bGjyJdIo5eMRl)
- Space Ghost, "Vulcanus MALL 108 items+ from ores" — 몰 품목 구성 (https://factorioprints.com/view/-OL_rvijZDQI7WVI8mxG)
- Nir Adar, "Vulcanus Starter Base" — 도착 직후 순서, 산 중화 전력으로 자립 (https://factorioprints.com/view/-OU4xpv_3uAJk-nIYB2y)
