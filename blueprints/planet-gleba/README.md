# 글레바 올인원 기지

> 돌벽과 레이저·기관총 포탑으로 둘러싼 직사각형 글레바 기지, 모두 로봇 공급: 과일 가공 → 바이오플럭스·영양분·펜타포드 알 → 농업 과학 분당 약 600, 철 박테리아 → 탄창, 탄소 섬유, 젤리 로켓 연료, 가열탑 전력(부패물 연료), 로켓·착륙장.

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

**구역별 확대 (북서 → 남동, 줄마다 서 → 동)**

![part-1](images/part-1.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base, space-age) |
| 크기 | 145×98 타일 |
| 엔티티 | 3240 |
| 주요 설비 | `requester-chest` ×249<br>`passive-provider-chest` ×120<br>`biochamber` ×108 (pentapod-egg 24, agricultural-science-pack 16, yumako-processing 12, bioflux 12, rocket-fuel-from-jelly 8, burnt-spoilage 8, carbon-fiber 8, iron-bacteria-cultivation 8, jellynut-processing 4, nutrients-from-bioflux 4, iron-bacteria 4)<br>`electric-furnace` ×8<br>`assembling-machine-3` ×4 (firearm-magazine 4)<br>`rocket-silo` ×1 |
| 검사 | 통과 |

### 입력

없음

### 출력

| 아이템 | 분당 | 위치 |
|---|---:|---|
| `agricultural-science-pack` | ~600 | 로켓 화물 요청 (1시간 안에 부패) |

### 단지 구성

| 줄 | 셀 크기 | 셀 수 | 출력 (분당, 후반) | 입력 (분당, 후반) |
|---|---|---:|---|---|
| Yumako processing | 13×12 | 2 | `yumako-seed` 9, `yumako-mash` 855 | `yumako` 285 |
| Jellynut processing | 13×4 | 2 | `jellynut-seed` 1, `jelly` 287 | `jellynut` 48 |
| Bioflux | 13×12 | 2 | `bioflux` 864 | `yumako-mash` 2,160, `jelly` 1,728 |
| Nutrients | 13×4 | 2 | `nutrients` 288 | `bioflux` 24 |
| Pentapod eggs | 17×12 | 4 | `pentapod-egg` 576 | `pentapod-egg` 192, `nutrients` 5,760, `water` (fluid) 11,520 |
| Agricultural science | 13×8 | 4 | `agricultural-science-pack` 720 | `bioflux` 480, `pentapod-egg` 480 |
| Iron bacteria | 13×4 | 2 | `iron-bacteria` 7, `spoilage` 281 | `jelly` 281 |
| Iron bacteria cultivation | 13×8 | 2 | `iron-bacteria` 576 | `iron-bacteria` 96, `bioflux` 96 |
| Iron plates (bacteria ore) | 13×8 | 2 | `iron-plate` 300 | `iron-ore` 300 |
| Firearm magazines | 13×4 | 2 | `firearm-magazine` 288 | `iron-plate` 1,152 |
| Carbon (burnt spoilage) | 13×8 | 2 | `carbon` 120 | `spoilage` 480 |
| Carbon fiber | 13×8 | 2 | `carbon-fiber` 288 | `yumako-mash` 1,920, `carbon` 192 |
| Rocket fuel (jelly) | 17×8 | 2 | `rocket-fuel` 144 | `water` (fluid) 2,880, `jelly` 2,880, `bioflux` 192 |
| Power ×2 | - | - | 가열탑 2기 → 열교환기 8 → 터빈 16씩 (연료: 부패물·젤리넛) | |
| Rocket silo | - | - | 로봇이 재료를 넣는 사일로; 수출은 화물 요청으로 | |
| Landing pad | - | - | 파랑 회로·LDS 수입 | |
| Defence ring | - | - | 돌벽 2겹 + 4칸마다 레이저 포탑, 세 번째마다 기관총 포탑(탄창 요청 상자) | |

선반 (아래 → 위; 섬마다 유체를 스스로 만들고, 유체 없는 블록은 빈자리에 채움):

| 선반 | 블록 |
|---|---|
| 1 | Power: 2 heating towers, 16 turbines, Power: 2 heating towers, 16 turbines, Pentapod eggs x2, Pentapod eggs x2 |
| 2 | Rocket fuel (jelly) x2 |
| 빈자리 채움 | Agricultural science x4, Yumako processing x2, Jellynut processing x2, Bioflux x2, Nutrients x2, Carbon (burnt spoilage) x2, Carbon fiber x2, Iron bacteria x2, Iron bacteria cultivation x2, Iron plates (bacteria ore) x2, Firearm magazines x2, Rocket silo (robot-fed), Landing pad (robot network) |

코어 113×73칸, 전체 145×98칸, 3,240개 엔티티, 밀도 0.23 · 타일 점유율 0.38 (참고 커뮤니티 기지: 0.24–0.44 · 0.55–0.82). 최대 전력 74 MW / 터빈 186 MW (가열탑 연료가 충분할 때).

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

- [풀가오라 올인원 기지](../planet-fulgora/README.md) — 전자기 과학 행성

### 파일

| 파일 | 설명 |
|---|---|
| [`blueprint.txt`](blueprint.txt) | 기지 전체 (코어 + 벽·포탑) |
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
| [`variants/power.txt`](variants/power.txt) | 전력: 가열탑 2 → 열교환기 8 → 터빈 16 (기지에 2세트) |
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

## 기지 모양

커뮤니티의 행성 기지는 행성 전체에 버스를 깔지 않습니다. 빽빽한 직사각형 하나에 생산을 모으고, 전력·방어를 가장자리에 두릅니다(아래 '참고한 커뮤니티 설계'). 이 기지도 그렇게 짓습니다(`lib/base.py`).

- **섬**: 유체와 중간재를 함께 쓰는 줄을 한 섬으로 묶습니다(예: 용융 철 + 그 주조, 용융 구리 + 금속 과학). 섬이 선반보다 넓으면 여러 조각으로 나누는데, 조각마다 자기 유체 생산 셀을 가집니다. 그래서 유체가 기지를 가로지르지 않습니다(`references/base-design.md` §3).
- **선반**: 섬 조각을 키가 비슷한 것끼리 가로 선반에 채우고, 선반을 쌓아 직사각형을 만듭니다. 선반 아래 거리에는 그 선반이 쓰는 유체만 지나갑니다(지하 파이프 6줄 묶음, 마지막 사용처에서 끝남). 유체가 필요 없는 블록(로봇 셀, 사일로, 착륙장 등)은 선반 위 빈자리에 채워 넣습니다.
- **로봇 셀**: 기계마다 요청 상자(재료)와 공급 상자(결과)가 있어 벨트 열이 필요 없습니다. 섬 안에서만 쓰는 중간재(예: 기어·구리선 → 2차 재활용)와 부산물(돌, 넘침)은 짧은 거리 벨트로 갑니다. 로봇 기지는 블록 사이 기둥에 약 48칸마다 있습니다.
- **스스로 조절**: 공급 상자로 나가는 출력 인서터는 네트워크에 약 2분치가 쌓이면 멈춥니다(로지스틱 조건). 가열탑 연료는 축전지가 90% 미만일 때만 버너 인서터로 넣습니다. 전기가 없어도 돌아가므로 기지가 스스로 다시 켜집니다. 축전지가 20% 아래로 떨어지면 스피커와 지도 경고가 울립니다(`references/circuits.md`).
- **입력**: 모두 가장자리에 있습니다. 유체는 선반마다 서쪽, 광석은 남쪽 입구로 들어오고, 바깥 끝은 지하 벨트·지하 파이프입니다. 그 옆에 표시 조합기(분당 수량)와 디스플레이 패널이 있습니다.

## 왜 벨트 대신 로봇인가

글레바에서는 거의 모든 것이 부패합니다(으깬 유마코 3분, 젤리 4분, 영양분 5분, 알 15분). 벨트가 한 번 멈추면 그 위의 물건이 썩어 줄을 막고, **알이 썩으면 적이 부화**합니다. 그래서 이 기지는 모든 셀이 로봇으로 받고 냅니다.

- 기계마다 **요청 상자**(재료 + 생물 반응기 연료인 영양분)와 **공급 상자**(결과, 부패물 포함)가 있습니다. 출력 인서터는 필터가 없어 부패물도 같이 빼 줍니다.
- **부패물은 연료**(250 kJ)라 가열탑이 태웁니다. 기지의 전력원이 곧 부패물 처리장입니다.
- **알 관리**: 알 기계의 입력 인서터는 로봇 네트워크의 알이 40개 미만일 때만 움직입니다(로지스틱 조건). 알이 쌓이지 않아 15분 안에 소비됩니다. 문자열에서 조건이 빠져 보이면 게임에서 입력 인서터에 "로지스틱 네트워크에 연결: 펜타포드 알 < 40"을 걸어 주세요.

## 농장

농업 탑은 특정 토양(유마코 / 젤리넛 습지, 또는 인공 토양) 위에서만 키웁니다. 그래서 `variants/farm-*.txt`를 벽 밖 토양 위에 22칸 간격으로 따로 놓습니다(탑 반경 3칸 = 21×21). 로봇 네트워크가 닿으면 수확물이 알아서 기지로 옵니다. 과학 분당 600에는 유마코 초당 약 20, 젤리넛 초당 약 8이 필요합니다. 농장도 포탑으로 지켜야 합니다.

## 방어

펜타포드는 오염(포자)이 닿은 곳을 공격합니다. 커뮤니티 기지처럼 기지 전체를 벽과 포탑으로 두릅니다.

- 맨 바깥에 지뢰 두 줄, 그 안에 돌벽 두 겹이 있습니다.
- 그 안쪽 줄에 4칸마다 레이저 포탑이 서고, 세 번째 자리마다 기관총 포탑이 섭니다. 기관총 포탑은 탄창을 요청 상자에서 받는데, 탄창은 박테리아 철로 만듭니다.
- 포탑 사이에는 전신주가 있습니다.
- 물 배관이 지나가는 자리만 벽이 비어 있습니다.

로켓 포탑·테슬라 포탑이 생기면 같은 자리를 바꾸세요. 큰 스톰퍼에는 로켓 포탑이 좋습니다.

## 참고한 커뮤니티 설계 (문자열은 저장소에 넣지 않음)

- "Gleba all production, no mods" — 직사각형 + 둘레 레이저 포탑·돌벽, 안쪽 축전지 띠 (https://factorioprints.com/view/-OBSabLpqu-pMQbWkKcy)
- Nir Adar, "Gleba Base (Mall + All)" — 벽·포탑·지뢰로 두른 올인원 (https://factorioprints.com/view/-OFa_ZWh1hQypFqucMTy)
- Nir Adar, "Gleba Book" — 알 유지·영양분 부트스트랩, 로봇 기반 농업 과학 (https://factorioprints.com/view/-OvbAwW4CJ0WvO5NsBBm)
