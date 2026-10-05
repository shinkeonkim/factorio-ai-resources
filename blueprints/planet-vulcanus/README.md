# 불카누스 올인원 기지

> 직사각형 하나로 지은 불카누스 기지: 용암 선반(용융 금속 + 돌 처리) → 주조·텅스텐·금속 과학 분당 360, 윤활유, 몰(주조기·대형 채굴기·터보 벨트), 전력 372 MW, 남쪽 광석 입구, 로켓·착륙장. 블록 사이는 로봇, 유체는 서쪽 줄기 배관.

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

**구역별 확대 (북서 → 남동, 줄마다 서 → 동)**

![part-1](images/part-1.webp)
![part-2](images/part-2.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base, space-age) |
| 크기 | 264×201 타일 |
| 엔티티 | 9376 |
| 주요 설비 | `requester-chest` ×83<br>`passive-provider-chest` ×80<br>`foundry` ×68 (tungsten-plate 20, molten-copper-from-lava 12, metallurgic-science-pack 10, molten-iron-from-lava 6, casting-iron 4, casting-steel 4, casting-low-density-structure 2, foundry 2, big-mining-drill 2, turbo-transport-belt 2, turbo-underground-belt 2, turbo-splitter 2)<br>`recycler` ×42<br>`chemical-plant` ×22 (carbon 18, acid-neutralisation 2, lubricant 2)<br>`assembling-machine-3` ×12 (tungsten-carbide 12)<br>`steel-chest` ×3<br>`oil-refinery` ×2 (simple-coal-liquefaction 2)<br>`rocket-silo` ×1 |
| 검사 | 통과 |

### 입력

_블루프린트 안의 일정 신호 조합기 표시 (값 = 분당 필요량, 위치 = 블루프린트 왼쪽 위 기준 타일 좌표)_

| 신호 | 분당 | 위치 |
|---|---:|---|
| `calcite` | 412 | (22, 200) |
| `coal` | 2,400 | (26, 200) |
| `tungsten-ore` | 1,860 | (30, 200) |
| `tungsten-ore` | 1,860 | (34, 200) |

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

선반 (아래 → 위; 줄이 길면 같은 높이의 스택 여러 개로 나뉨):

| 선반 | 블록 |
|---|---|
| 1 | Molten iron x3, Molten copper x3, Molten copper x3, Stone void 1, Stone void 2, Stone void 3, Power: acid neutralisation + 64 turbines, Carbon x3, Tungsten plate x3, Metallurgic science x5 |
| 2 | Tungsten carbide x3, Tungsten plate x2, Iron plates x2, Steel x2, Heavy oil (simple coal liquefaction) x1, Low density structure x1, Mall: foundry x1, Lubricant x1 |
| 3 | Mall: big mining drill x1, Mall: turbo belt x1, Mall: turbo underground x1, Mall: turbo splitter x1, Rocket silo (robot-fed), Landing pad (imports into the robot network) |

코어 253×196칸, 전체 264×201칸, 9,376개 엔티티. 최대 전력 215 MW / 발전 372 MW. 블록 사이 아이템은 로봇(요청 상자 → 블록 → 공급 상자), 유체는 서쪽 줄기 배관으로 모든 선반에 이어집니다.

### 로드맵

| 단계 | 시기 / 필요한 연구 | 할 일 |
|---|---|---|
| 0. 도착 | `foundry` (아이템을 처음 만들면), `rocket-silo` (빨강·초록·파랑·보라·노랑) | 주조기 연구 전: 우주 플랫폼에서 착륙장·로봇·기본 건물을 내립니다. 용암 호수 옆, 방해석·석탄·텅스텐 광맥 근처의 디몰리셔 영역 밖에 자리를 잡습니다. |
| 1. 전력 | `calcite-processing` (처음 캐면), `nuclear-power` (빨강·초록·파랑) | 전력 줄(산 중화 + 터빈)을 먼저: 방해석과 황산(산 간헐천 펌프잭)만 있으면 372 MW. 처음엔 터빈 몇 대로 시작해도 됩니다. |
| 2. 용융 금속·주조 | `foundry` (아이템을 처음 만들면) | 용융 철·구리 줄과 철판·강철 주조. 용암은 북서쪽 줄기 배관 끝 표시에 해양 펌프로. 돌이 나오므로 같은 선반의 돌 처리 블록도 같이 놓습니다(재활용 연구 전엔 상자에 쌓임). |
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

- **선반**: 생산 줄을 같은 높이의 블록(쌓는 셀 스택)으로 나눠 가로 선반에 빽빽하게 채웁니다. 선반을 위로 쌓으면 직사각형이 됩니다. 폭은 빈 칸이 가장 적게 남는 값을 찾아 정합니다.
- **블록 사이는 로봇**: 블록 입력마다 요청 상자 → 인서터 → 벨트, 출력마다 벨트 끝 → 인서터 → 공급 상자를 둡니다. 벨트는 블록 안에만 있고, 로봇 기지는 40칸 격자로 코어 전체를 덮습니다.
- **유체는 서쪽 줄기**: 선반마다 자기가 쓰는 유체만 선반 아래 짧은 거리에 깝니다. 서쪽 가장자리의 세로 줄기 배관이 같은 유체를 모든 선반에 잇습니다. 바깥에서 들어오는 유체는 줄기의 북쪽 끝 표시(상수 조합기)로 들어옵니다.
- **용암 선반**(맨 아래): 용융 철·구리 주조기와 돌 처리 재활용기가 돌 벨트를 함께 씁니다. 돌은 초당 약 80개라 로봇 대신 벨트로 처리합니다. 돌이 쌓이면 용융 금속 생산이 멈추므로 처리 블록이 같은 선반에 있어야 합니다(돌은 25% 확률로 자기 자신이 되므로 75%가 사라짐). 재활용 연구(풀가오라) 전에는 처리 블록 위쪽 상자에 쌓입니다.
- **남쪽 광석 입구**: 방해석·석탄·텅스텐 광석 벨트가 남쪽에서 들어와 공급 상자로 내려집니다.
- **유체 셀**: 주조기는 유체 입력이 벨트 쪽, 출력이 가운데를 보도록 돌려 놓습니다. 입력 유체마다 기계 행을 따로 씁니다.
- **생성할 때 검사**: 모든 타일 충돌, 선반 거리의 줄 용량(파이프 1,200/s), 전력망 연결을 생성 단계에서 검사합니다. 하나라도 어긋나면 문자열을 만들지 않습니다.

## 전력·방어

- 전력: 산 중화(방해석 + 황산 → 500°C 증기) 화학 공장 2대가 증기 터빈 64대를 돌립니다(372 MW). 이 블록도 선반 안에 들어갑니다.
- 방어: 불카누스의 적은 디몰리셔입니다. 포탑으로 막는 대상이 아니므로 둘레 방어 대신 **영역 밖에 짓는 것**이 원칙입니다. 그래서 이 기지에는 외곽 띠가 없습니다.

## 늘리는 법

- 블록 하나를 더 키우려면 그 블록 위에 셀을 더 붙입니다(쌓는 셀). 줄 전체를 늘리려면 `lib/planets/vulcanus.py`의 `PLAN` 숫자를 바꾸고 다시 생성하세요. 같은 높이로 다시 나눠 다시 채웁니다.
- 줄 하나만 따로 쓰려면 `variants/<줄>.txt`(캡 + 셀 1개, 입력에 표시 조합기)를 쓰세요.

## 참고한 커뮤니티 설계 (문자열은 저장소에 넣지 않음)

- "Vulcanus all production, no mods" — 직사각형 하나, 터빈 블록을 한쪽 가장자리에 (https://factorioprints.com/view/-OBM-LoRxzZKXi8dvphv)
- "Vulcanus Production" — 블록별 고밀도 생산 (https://factorioprints.com/view/-OAjOz4bGjyJdIo5eMRl)
- Space Ghost, "Vulcanus MALL 108 items+ from ores" — 몰 품목 구성 (https://factorioprints.com/view/-OL_rvijZDQI7WVI8mxG)
- Nir Adar, "Vulcanus Starter Base" — 도착 직후 순서, 산 중화 전력으로 자립 (https://factorioprints.com/view/-OU4xpv_3uAJk-nIYB2y)
