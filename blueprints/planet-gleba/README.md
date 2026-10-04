# 글레바 올인원 단지

> 로봇이 나르는 쌓는 셀: 과일 가공 → 바이오플럭스·영양분·펜타포드 알 → 농업 과학 분당 약 300, 철 박테리아 → 탄창, 탄소 섬유, 젤리 로켓 연료, 가열탑 전력(부패물 연료), 로켓·착륙장, 포탑 방어선까지.

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

**구간별 확대 (서쪽 → 동쪽)**

![part-1](images/part-1.webp)
![part-2](images/part-2.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base, space-age) |
| 크기 | 305×55 타일 |
| 엔티티 | 1293 |
| 주요 설비 | `requester-chest` ×147<br>`passive-provider-chest` ×60<br>`biochamber` ×54 (pentapod-egg 12, agricultural-science-pack 8, yumako-processing 6, bioflux 6, iron-bacteria-cultivation 4, burnt-spoilage 4, carbon-fiber 4, rocket-fuel-from-jelly 4, jellynut-processing 2, nutrients-from-bioflux 2, iron-bacteria 2)<br>`electric-furnace` ×4<br>`assembling-machine-3` ×2 (firearm-magazine 2)<br>`rocket-silo` ×1 |
| 검사 | 통과 |

### 입력

없음

### 출력

| 아이템 | 분당 | 위치 |
|---|---:|---|
| `agricultural-science-pack` | ~300 | 로켓 화물 요청 (1시간 안에 부패) |

### 단지 구성

| 줄 | 셀 크기 | 셀 수 | 출력 (분당, 후반) | 입력 (분당, 후반) |
|---|---|---:|---|---|
| Yumako processing | 13×12 | 1 | `yumako-seed` 4, `yumako-mash` 428 | `yumako` 143 |
| Jellynut processing | 13×4 | 1 | `jellynut-seed` 1, `jelly` 143 | `jellynut` 24 |
| Bioflux | 13×12 | 1 | `bioflux` 432 | `yumako-mash` 1,080, `jelly` 864 |
| Nutrients | 13×4 | 1 | `nutrients` 144 | `bioflux` 12 |
| Pentapod eggs | 17×12 | 2 | `pentapod-egg` 288 | `pentapod-egg` 96, `nutrients` 2,880, `water` (fluid) 5,760 |
| Agricultural science | 13×8 | 2 | `agricultural-science-pack` 360 | `bioflux` 240, `pentapod-egg` 240 |
| Iron bacteria | 13×4 | 1 | `iron-bacteria` 4, `spoilage` 140 | `jelly` 140 |
| Iron bacteria cultivation | 13×8 | 1 | `iron-bacteria` 288 | `iron-bacteria` 48, `bioflux` 48 |
| Iron plates (bacteria ore) | 13×8 | 1 | `iron-plate` 150 | `iron-ore` 150 |
| Firearm magazines | 13×4 | 1 | `firearm-magazine` 144 | `iron-plate` 576 |
| Carbon (burnt spoilage) | 13×8 | 1 | `carbon` 60 | `spoilage` 240 |
| Carbon fiber | 13×8 | 1 | `carbon-fiber` 144 | `yumako-mash` 960, `carbon` 96 |
| Rocket fuel (jelly) | 17×8 | 1 | `rocket-fuel` 72 | `water` (fluid) 1,440, `jelly` 1,440, `bioflux` 96 |
| Power | - | - | 가열탑 2기 → 열교환기 8 → 터빈 16 (연료: 부패물·젤리넛) | |
| Rocket silo | - | - | 로봇이 재료를 넣는 사일로; 수출은 화물 요청으로 | |
| Landing pad | - | - | 파랑 회로·LDS 수입 | |
| Defence ring | - | - | 포탑 + 탄창 요청 상자를 단지 둘레에 18칸마다 | |

버스 (위 → 아래, 6줄 + 빈 2줄 묶음; 유체는 맨 아래):

| 묶음 | 줄 |
|---|---|
| 1 (fluid) | `water` (fluid), `water` (fluid), -, -, -, - |

전체 1,293개 엔티티, 폭 289칸. 최대 전력 40 MW / 터빈 93 MW (가열탑 연료가 충분할 때). 버스 줄마다 수요가 한 줄 용량(파랑 벨트 45/s, 파이프 1,200/s)을 넘지 않는지 생성할 때 검사합니다.

### 로드맵

| 단계 | 시기 / 필요한 연구 | 할 일 |
|---|---|---|
| 0. 도착 | `yumako` (처음 캐면), `jellynut` (처음 캐면), `bioflux` (아이템을 처음 만들면) | 유마코·젤리넛을 손으로 캐면 가공·바이오플럭스 연구가 열립니다. 물가 근처, 유마코·젤리넛 토양 옆에 자리를 잡습니다. |
| 1. 농장·전력 | `agriculture` (처음 캐면), `heating-tower` (처음 캐면) | 농장 타일(농업 탑 + 씨앗 요청 + 수확물 제공 상자)을 각 토양 위에 22칸 간격으로, 가열탑 전력 줄을 놓습니다. 부패물과 젤리넛을 태우므로 쌓이는 부패물이 곧 연료입니다. |
| 2. 영양분 부트스트랩 | `bioflux` (아이템을 처음 만들면), `biochamber` (아이템을 처음 만들면) | 생물 반응기는 영양분을 태워야 돌아갑니다. 처음엔 손으로 영양분 몇 묶음을 공급 상자에 넣어 시작하세요. |
| 3. 알·과학 | `biochamber` (아이템을 처음 만들면), `agricultural-science-pack` (아이템을 처음 만들면) | 펜타포드 알은 처음 하나가 필요합니다(둥지에서 얻음). 알 기계는 네트워크에 알이 40개 미만일 때만 재료를 받아서 알이 쌓여 부패(→ 적 부화)하지 않습니다. 농업 과학은 1시간 안에 부패하니 바로 로켓으로. |
| 4. 철·방어 | `jellynut` (처음 캐면), `bacteria-cultivation` (아이템을 처음 만들면) | 철 박테리아(젤리) → 배양 → 1분 뒤 철광석 → 전기로 → 탄창. 단지 둘레 포탑이 탄창을 로봇으로 받습니다. 로켓·테슬라 포탑이 생기면 바꿉니다. |
| 5. 수출 | `carbon-fiber` (빨강·초록·파랑·우주·글레바), `bioflux-processing` (아이템을 처음 만들면), `rocket-silo` (빨강·초록·파랑·보라·노랑) | 탄소 섬유(아킬로 기초판 재료), 젤리 로켓 연료, 파랑 회로·LDS 수입으로 로켓 부품. |

**다음에 지을 것**

- [풀가오라 올인원 단지](../planet-fulgora/README.md) — 전자기 과학 행성

### 파일

| 파일 | 설명 |
|---|---|
| [`blueprint.txt`](blueprint.txt) | 단지 전체 (물 버스 + 모든 줄 + 방어선) |
| [`variants/yumako-processing.txt`](variants/yumako-processing.txt) | 유마코 가공 — 캡 + 셀 1개 |
| [`variants/jellynut-processing.txt`](variants/jellynut-processing.txt) | 젤리넛 가공 — 캡 + 셀 1개 |
| [`variants/bioflux.txt`](variants/bioflux.txt) | 바이오플럭스 — 캡 + 셀 1개 |
| [`variants/nutrients.txt`](variants/nutrients.txt) | 영양분 — 캡 + 셀 1개 |
| [`variants/eggs.txt`](variants/eggs.txt) | 펜타포드 알 — 캡 + 셀 1개 |
| [`variants/science.txt`](variants/science.txt) | 농업 과학 — 캡 + 셀 1개 |
| [`variants/iron-bacteria.txt`](variants/iron-bacteria.txt) | 철 박테리아 — 캡 + 셀 1개 |
| [`variants/iron-cultivation.txt`](variants/iron-cultivation.txt) | 철 박테리아 배양 — 캡 + 셀 1개 |
| [`variants/iron-plate.txt`](variants/iron-plate.txt) | 철판 (박테리아 광석) — 캡 + 셀 1개 |
| [`variants/magazine.txt`](variants/magazine.txt) | 탄창 — 캡 + 셀 1개 |
| [`variants/carbon.txt`](variants/carbon.txt) | 탄소 (태운 부패물) — 캡 + 셀 1개 |
| [`variants/carbon-fiber.txt`](variants/carbon-fiber.txt) | 탄소 섬유 — 캡 + 셀 1개 |
| [`variants/rocket-fuel.txt`](variants/rocket-fuel.txt) | 로켓 연료 (젤리) — 캡 + 셀 1개 |
| [`variants/power.txt`](variants/power.txt) | 전력: 가열탑 2 → 열교환기 8 → 터빈 16 |
| [`variants/rocket-silo.txt`](variants/rocket-silo.txt) | 로켓 사일로 (로봇 공급) |
| [`variants/landing-pad.txt`](variants/landing-pad.txt) | 착륙장 |
| [`variants/farm-yumako.txt`](variants/farm-yumako.txt) | 농장 타일: 유마코 (토양 위에) |
| [`variants/farm-jellynut.txt`](variants/farm-jellynut.txt) | 농장 타일: 젤리넛 (토양 위에) |

문자열을 클립보드에 복사한 뒤 게임에서 블루프린트 라이브러리 → 문자열 가져오기:

```sh
pbcopy < blueprints/planet-gleba/blueprint.txt   # macOS
xclip -selection clipboard < blueprints/planet-gleba/blueprint.txt   # Linux
```

### 다시 생성

```sh
python3 blueprints/planet-gleba/generate.py
python3 tools/build.py planet-gleba
```

<!-- AUTO:END -->

## 왜 벨트 대신 로봇인가

글레바에서는 거의 모든 것이 부패합니다(으깬 유마코 3분, 젤리 4분, 영양분 5분, 알 15분). 벨트가 한 번 멈추면 그 위의 물건이 썩어 줄을 막고, **알이 썩으면 적이 부화**합니다. 그래서 이 단지는 아이템 버스 없이 로봇으로 나릅니다.

- 기계마다 **요청 상자**(재료 + 생물 반응기 연료인 영양분)와 **공급 상자**(결과, 부패물 포함)가 있습니다. 출력 인서터는 필터가 없어 부패물도 같이 빼 줍니다.
- **부패물은 연료**(250 kJ)라 가열탑이 태웁니다. 단지의 전력원이 곧 부패물 처리장입니다.
- **알 관리**: 알 기계의 입력 인서터는 로봇 네트워크의 알이 40개 미만일 때만 움직입니다(로지스틱 조건). 알이 쌓이지 않아 15분 안에 소비됩니다. 문자열에서 조건이 빠져 보이면 게임에서 입력 인서터에 "로지스틱 네트워크에 연결: 펜타포드 알 < 40"을 걸어 주세요.
- 셀은 여전히 쌓는 형태(고정 폭·주기)이고, 물만 아래 버스의 파이프로 들어옵니다. 각 줄의 캡과 맨 위에 로봇 기지가 있어 네트워크가 이어집니다.

## 농장

농업 탑은 특정 토양(유마코 / 젤리넛 습지, 또는 인공 토양) 위에서만 키우므로 단지와 따로 `variants/farm-*.txt`를 토양 위에 22칸 간격으로 놓습니다(탑 반경 3칸 = 21×21). 로봇 네트워크 안에만 있으면 수확물이 알아서 단지로 옵니다. 과학 분당 300에는 유마코 초당 약 10, 젤리넛 초당 약 4가 필요합니다.

## 방어

펜타포드는 오염(포자)이 있는 곳을 공격합니다. 단지 둘레 18칸마다 포탑 + 탄창 요청 상자를 두고, 탄창은 박테리아 철로 만듭니다. 로켓 포탑·테슬라 포탑이 생기면 같은 자리를 바꾸세요.

## 참고한 커뮤니티 설계 (문자열은 저장소에 넣지 않음)

- Nir Adar, "Gleba Book" (https://factorioprints.com/view/-OvbAwW4CJ0WvO5NsBBm)
