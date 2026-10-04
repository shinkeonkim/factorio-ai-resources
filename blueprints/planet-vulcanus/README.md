# 불카누스 올인원 단지

> 용암 → 용융 금속 → 주조·텅스텐·금속 과학 분당 360, 윤활유, 몰(주조기·대형 채굴기·터보 벨트), 전력 372 MW, 착륙장 수입·로켓 수출, 돌 처리까지 버스 하나에 쌓는 셀로.

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base, space-age) |
| 크기 | 621×107 타일 |
| 엔티티 | 18997 |
| 주요 설비 | `foundry` ×64 (tungsten-plate 16, molten-copper-from-lava 12, metallurgic-science-pack 10, molten-iron-from-lava 6, casting-iron 4, casting-steel 4, casting-low-density-structure 2, foundry 2, big-mining-drill 2, turbo-transport-belt 2, turbo-underground-belt 2, turbo-splitter 2)<br>`recycler` ×42<br>`chemical-plant` ×22 (carbon 18, acid-neutralisation 2, lubricant 2)<br>`passive-provider-chest` ×14<br>`assembling-machine-3` ×12 (tungsten-carbide 12)<br>`requester-chest` ×11<br>`steel-chest` ×3<br>`oil-refinery` ×2 (simple-coal-liquefaction 2)<br>`rocket-silo` ×1 |
| 검사 | 통과 |

### 입력

없음

### 출력

| 아이템 | 분당 | 위치 |
|---|---:|---|
| `metallurgic-science-pack` | 360 | 로켓 수출 상자 (버스 동쪽 끝) |

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
| Tungsten plate | 21×12 | 4 | `tungsten-plate` 576 | `tungsten-ore` 1,536, `molten-iron` (fluid) 3,840 |
| Iron plates | 21×6 | 2 | `iron-plate` 900 | `molten-iron` (fluid) 6,000 |
| Steel | 21×6 | 2 | `steel-plate` 450 | `molten-iron` (fluid) 9,000 |
| Metallurgic science | 21×6 | 5 | `metallurgic-science-pack` 360 | `tungsten-carbide` 720, `tungsten-plate` 480, `molten-copper` (fluid) 48,000 |
| Low density structure | 25×6 | 1 | `low-density-structure` 48 | `molten-iron` (fluid) 2,560, `molten-copper` (fluid) 8,000, `plastic-bar` 160 |
| Mall: foundry | 23×6 | 1 | 상자 (몰) | `tungsten-carbide` 288, `steel-plate` 288, `electronic-circuit` 173, `refined-concrete` 115, `lubricant` (fluid) 115 |
| Mall: big mining drill | 23×6 | 1 | 상자 (몰) | `electric-mining-drill` 14, `molten-iron` (fluid) 2,880, `tungsten-carbide` 288, `electric-engine-unit` 144, `advanced-circuit` 144 |
| Mall: turbo belt | 21×6 | 1 | 상자 (몰) | `tungsten-plate` 480, `express-transport-belt` 96, `lubricant` (fluid) 1,920 |
| Mall: turbo underground | 21×6 | 1 | 상자 (몰) | `tungsten-plate` 1,829, `express-underground-belt` 91, `lubricant` (fluid) 1,829 |
| Mall: turbo splitter | 23×6 | 1 | 상자 (몰) | `express-splitter` 60, `tungsten-plate` 900, `processing-unit` 120, `lubricant` (fluid) 4,800 |

버스 (위 → 아래, 6줄 + 빈 2줄 묶음; 유체는 맨 아래):

| 묶음 | 줄 |
|---|---|
| 1 (solid) | `calcite`, `coal`, `tungsten-ore`, `tungsten-ore`, `carbon`, `tungsten-carbide` |
| 2 (solid) | `tungsten-plate`, `metallurgic-science-pack`, `iron-plate`, `steel-plate`, `low-density-structure`, - |
| 3 (solid) | `stone`, `stone`, `stone`, -, -, - |
| 4 (solid) | `electronic-circuit`, `advanced-circuit`, `processing-unit`, `electric-engine-unit`, `electric-mining-drill`, `refined-concrete` |
| 5 (solid) | `express-transport-belt`, `express-underground-belt`, `express-splitter`, `plastic-bar`, `rocket-fuel`, - |
| 6 (fluid) | `lava` (fluid), `lava` (fluid), `sulfuric-acid` (fluid), `molten-iron` (fluid), `molten-copper` (fluid), `molten-copper` (fluid) |
| 7 (fluid) | `heavy-oil` (fluid), `lubricant` (fluid), -, -, -, - |

전체 18,997개 엔티티, 폭 620칸. 최대 전력 194 MW / 발전 372 MW. 버스 줄마다 수요가 한 줄 용량(파랑 벨트 45/s, 파이프 1,200/s)을 넘지 않는지 생성할 때 검사합니다.

### 로드맵

| 단계 | 시기 / 필요한 연구 | 할 일 |
|---|---|---|
| 0. 도착 | `foundry` (아이템을 처음 만들면), `rocket-silo` (빨강·초록·파랑·보라·노랑) | 주조기 연구 전: 우주 플랫폼에서 착륙장·로봇·기본 건물을 내립니다. 용암 호수 옆, 방해석·석탄·텅스텐 광맥 근처의 디몰리셔 영역 밖에 자리를 잡습니다. |
| 1. 전력 | `calcite-processing` (처음 캐면), `nuclear-power` (빨강·초록·파랑) | 전력 줄(산 중화 + 터빈)을 먼저: 방해석과 황산(산 간헐천 펌프잭)만 있으면 372 MW. 처음엔 터빈 몇 대로 시작해도 됩니다. |
| 2. 용융 금속·주조 | `foundry` (아이템을 처음 만들면) | 용융 철·구리 줄과 철판·강철 주조. 용암은 버스 서쪽 끝 표시 자리에 해양 펌프로. 돌이 나오므로 돌 처리 줄도 같이 놓습니다(재활용 연구 전엔 상자에 쌓임). |
| 3. 텅스텐·과학 | `tungsten-carbide` (처음 캐면), `tungsten-steel` (아이템을 처음 만들면), `metallurgic-science-pack` (아이템을 처음 만들면) | 탄소 → 탄화 텅스텐, 텅스텐 판, 금속 과학(분당 360). 셀을 더 쌓으면 비례해서 늘어납니다. |
| 4. 몰·윤활유 | `calcite-processing` (처음 캐면), `big-mining-drill` (아이템을 처음 만들면), `turbo-transport-belt` (빨강·초록·파랑·보라·우주·불카누스) | 간이 석탄 액화 → 윤활유, 몰 줄(주조기·대형 채굴기·터보 벨트류). 회로·엔진·급행 벨트는 착륙장 수입. |
| 5. 로켓·수출 | `foundry` (아이템을 처음 만들면), `rocket-silo` (빨강·초록·파랑·보라·노랑) | 저밀도 구조물 주조(플라스틱 수입)와 로켓 사일로. 금속 과학·탄화 텅스텐·텅스텐 판·철판을 수출 상자에서 로켓 화물로. |

**다음에 지을 것**

- [정제 콘크리트 (쌓는 셀)](../refined-concrete/README.md) — 주조기 재료(정제 콘크리트) — 수입 대신 직접

### 파일

| 파일 | 설명 |
|---|---|
| [`blueprint.txt`](blueprint.txt) | 단지 전체 (버스 + 모든 줄) |
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
| [`variants/landing-pad.txt`](variants/landing-pad.txt) | 착륙장 (수입) |
| [`variants/rocket-silo-and-exports.txt`](variants/rocket-silo-and-exports.txt) | 로켓 사일로 + 수출 상자 |
| [`variants/stone-sink.txt`](variants/stone-sink.txt) | 돌 처리 (재활용기) |

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

## 구조

- **버스 하나 + 쌓는 셀 줄들.** 6줄 + 빈 2줄 묶음의 가로 버스(유체 묶음은 맨 아래) 북쪽에 생산 줄이 서쪽 → 동쪽으로 섭니다. 각 줄은 이 저장소의 쌓는 셀(`lib/fstack.py`)이라 셀을 더 붙이면 그대로 늘어납니다.
- **입력**: 서쪽 끝 표시 조합기 자리 = 원자재. 용암(용암 위 해양 펌프), 방해석·석탄·텅스텐 광석(채굴), 황산(산 간헐천 펌프잭). 수입품(회로, 엔진, 급행 벨트류, 정제 콘크리트, 플라스틱, 로켓 연료)은 착륙장 → 로봇 → 요청 상자 → 버스 줄로 들어옵니다.
- **제품은 버스로 돌아갑니다.** 각 줄의 가운데 출력이 남쪽으로 내려와 자기 버스 줄을 시작하고, 동쪽의 다음 줄이 그 줄에서 분기합니다(탄소 → 탄화 텅스텐 → 금속 과학 순서).
- **유체 셀**: 주조기는 유체 입력이 벨트 쪽, 출력이 가운데를 보도록 돌려 놓습니다. 입력 유체마다 한 기계 행을 따로 쓰고(지하 파이프 쌍이 서로 엉키지 않게), 바깥 본관에서 지하 파이프로 들어옵니다. 용융 금속은 가운데 파이프 두 줄로, 부산물 돌은 그 사이 벨트로 나갑니다.
- **돌**: 용암 주조는 돌을 많이 냅니다(주조기 한 대가 초당 2.5–3.75개). 쌓이면 용융 금속 생산이 멈추므로 돌 줄마다 재활용기 처리 줄을 하나씩 둡니다(돌은 25% 확률로 자기 자신이 되므로 75%가 사라짐). 재활용 연구(풀가오라) 전에는 위쪽 상자에 쌓입니다.
- **생성할 때 검사**: 모든 타일 충돌, 버스 줄 용량(파랑 벨트 45/s, 파이프 1,200/s), 전력망 연결을 생성 단계에서 검사합니다. 하나라도 어긋나면 문자열을 만들지 않습니다.

## 전력·방어

- 전력: 산 중화(방해석 + 황산 → 500°C 증기) 화학 공장 2대가 증기 터빈 64대를 돌립니다(372 MW). 단지 최대 소비는 아래 표의 값입니다.
- 방어: 불카누스의 적은 디몰리셔입니다. 포탑으로 막는 대상이 아니므로 **영역 밖에 짓는 것**이 원칙입니다. 영역을 넓혀야 하면 레일건·테슬라 연구 후 처리하세요.

## 늘리는 법

- 과학을 늘리려면: 금속 과학 줄에 셀을 붙이고, 아래 '단지 구성' 표에서 모자라는 입력 줄(탄화 텅스텐, 텅스텐 판, 용융 구리)에도 같은 비율로 셀을 붙입니다.
- 줄 하나만 따로 쓰려면 `variants/<줄>.txt`(캡 + 셀 1개, 입력에 표시 조합기)를 쓰세요.

## 참고한 커뮤니티 설계 (문자열은 저장소에 넣지 않음)

- Space Ghost, "Vulcanus MALL 108 items+ from ores" — 몰 품목 구성, 로켓 공장 규모 (https://factorioprints.com/view/-OL_rvijZDQI7WVI8mxG)
- Nir Adar, "Vulcanus Starter Base" — 도착 직후 순서, 산 중화 전력으로 자립 (https://factorioprints.com/view/-OU4xpv_3uAJk-nIYB2y)
- Zabr, "Complete Space Age v1.0" — 로켓 부품 재료는 플랫폼으로 들여오는 전략 (https://factorioprints.com/view/-OJe1VpH5-TunS6dqcbi)
