# factorio-ai-resources

Factorio 블루프린트를 AI(Claude Code)와 함께 설계·관리하기 위한 저장소입니다. 레시피 비율 계산부터 블루프린트 문자열 생성, 검증, 미리보기 이미지, 한/영 문서까지 한 흐름으로 다룹니다.

[English](README.en.md)

## 구성

| 경로 | 내용 |
|---|---|
| [`skills/factorio-blueprint/`](skills/factorio-blueprint/SKILL.md) | Claude Code 스킬: 비율 계산기(`calc.py`), 블루프린트 빌더·인코더·검사기(`blueprint.py`), 레이아웃 패턴 문서, 게임 데이터 |
| [`blueprints/`](blueprints/README.md) | 블루프린트마다 폴더 하나: 문자열, 생성 스크립트, 한/영 문서, 미리보기 이미지 |
| [`docs/`](docs/) | [메인버스 6+2 가이드](docs/guides/main-bus-6x2.md), [업그레이드형 설계 원칙](docs/guides/upgrade-in-place.md), [demo-resources 분석](docs/demo-analysis/README.md), [최근 최적화 설계 참고](docs/references/optimized-builds.md) |
| `lib/` | 여러 블루프린트가 공유하는 생성 코드 (정제 콘크리트 모듈, 철도 시티블럭 역 도구) |
| `tools/` | `build.py`(검증·미리보기·문서·카탈로그), `render_fbe.py`(게임 그래픽 미리보기), `render_preview.py`(도식 미리보기, 예비용), `new_blueprint.py`, `attach_image.py` |
| `third_party/` | 저장소에 포함하지 않는 원본 입력 (철도 북 등) — [안내](third_party/README.md) |
| `scripts/install-skills.sh` | 스킬을 `~/.claude/skills`에 설치 |

## 빠른 시작

```sh
git clone https://github.com/shinkeonkim/factorio-ai-resources.git
cd factorio-ai-resources
scripts/install-skills.sh          # 스킬을 심볼릭 링크로 설치 (--copy 로 복사 설치)
python3 -m venv .venv && .venv/bin/pip install -r tools/requirements.txt
.venv/bin/python -m playwright install chromium   # 게임 그래픽 미리보기용 (헤드리스 브라우저)

.venv/bin/python tools/build.py    # 전체 검증 + 미리보기 + 문서 갱신
pbcopy < blueprints/refined-concrete-60/blueprint.txt   # 게임에서 '문자열 가져오기'
```

새 블루프린트 추가:

```sh
python3 tools/new_blueprint.py my-factory --title-ko "내 공장" --title-en "My factory" --tags production
# blueprints/my-factory/generate.py 편집 후
python3 blueprints/my-factory/generate.py
python3 tools/build.py my-factory
```

게임 스크린샷 첨부 (갤러리에 추가됨):

```sh
python3 tools/attach_image.py my-factory ~/Desktop/shot.png --caption-ko "게임 안 모습" --caption-en "In game"
```

## 블루프린트 카탈로그

<!-- CATALOG:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

| 미리보기 | 블루프린트 | 설명 | 크기 | 입력 |
|---|---|---|---|---|
| <img src="blueprints/main-bus-6x2-segment/images/preview.webp" width="160"> | [메인버스 6+2 기본 구간](blueprints/main-bus-6x2-segment/README.md)<br>`main-bus` `kit` `upgradeable` | 이 저장소의 버스 구간(33칸): 철 6 | 구리 6 | 회로 2·2·2 | 강철 2·플라스틱 2·돌·벽돌 | 석탄·황·건전지·엔진·전기 엔진·LDS | 유체 6줄. 묶음 사이 빈칸 2줄. | 35×46 | iron-plate 900/min, iron-plate 900/min, iron-plate 900/min, iron-plate 900/min, iron-plate 900/min, iron-plate 900/min, copper-plate 900/min, copper-plate 900/min, copper-plate 900/min, copper-plate 900/min, copper-plate 900/min, copper-plate 900/min, electronic-circuit 900/min, electronic-circuit 900/min, advanced-circuit 900/min, advanced-circuit 900/min, processing-unit 900/min, processing-unit 900/min, steel-plate 900/min, steel-plate 900/min, plastic-bar 900/min, plastic-bar 900/min, stone 900/min, stone-brick 900/min, coal 900/min, sulfur 900/min, battery 900/min, engine-unit 900/min, electric-engine-unit 900/min, low-density-structure 900/min, petroleum-gas 60,000/min, light-oil 60,000/min, heavy-oil 60,000/min, lubricant 60,000/min, sulfuric-acid 60,000/min, water 60,000/min |
| <img src="blueprints/main-bus-6x2-tap/images/preview.webp" width="160"> | [메인버스 6+2 분기 조각](blueprints/main-bus-6x2-tap/README.md)<br>`main-bus` `kit` `upgradeable` | 6줄 묶음의 한 줄을 북쪽으로 빼는 조각: 벨트 줄 0~5 × 전부/반 12종 + 유체 줄 0~5 6종. | 7×8 | - |
| <img src="blueprints/main-bus-6x2-crossing/images/preview.webp" width="160"> | [메인버스 6+2 통과 조각](blueprints/main-bus-6x2-crossing/README.md)<br>`main-bus` `kit` `upgradeable` | 아래 묶음에서 올라오는 분기 벨트가 6줄 묶음을 세로로 가로지르게 하는 조각 (6줄 모두 1칸 잠수). | 7×9 | - |
| <img src="blueprints/refined-concrete/images/preview.webp" width="160"> | [정제 콘크리트 (쌓는 셀)](blueprints/refined-concrete/README.md)<br>`concrete` `stackable` `upgradeable` | 21×12 셀을 북쪽으로 쌓아 늘립니다. 입력 벽돌, 철광석, 강철, 철판; 같은 배치로 노랑→빨강→파랑. | 21×45 | water 1,125/min, water 1,125/min, iron-ore 8/min, stone-brick 38/min, steel-plate 4/min, iron-plate 15/min, iron-ore 8/min, stone-brick 38/min, steel-plate 4/min, iron-plate 15/min |
| <img src="blueprints/cell-concrete/images/preview.webp" width="160"> | [콘크리트 (쌓는 셀)](blueprints/cell-concrete/README.md)<br>`concrete` `stackable` `upgradeable` | 21×8 셀을 북쪽으로 쌓아 늘립니다. 입력 벽돌, 철광석; 같은 배치로 노랑→빨강→파랑. | 21×33 | water 1,500/min, water 1,500/min, iron-ore 15/min, stone-brick 75/min, iron-ore 15/min, stone-brick 75/min |
| <img src="blueprints/rail-ramp-support/images/preview.webp" width="160"> | [레일 경사로·지지대 (쌓는 셀)](blueprints/rail-ramp-support/README.md)<br>`rail` `space-age` `stackable` `upgradeable` | 15×8 상자 셀: 지지대·경사로를 양쪽에서 만들어 가운데 상자에. 입력은 정제 콘크리트·강철·레일; 셀을 붙일수록 상자가 늘어납니다. | 19×17 | refined-concrete 450/min, steel-plate 450/min, rail 450/min, refined-concrete 450/min, steel-plate 450/min, rail 450/min |
| <img src="blueprints/science-red-upgradeable/images/preview.webp" width="160"> | [빨강 과학 (쌓는 셀)](blueprints/science-red-upgradeable/README.md)<br>`science` `stackable` `upgradeable` | 13×12 셀을 북쪽으로 쌓아 늘립니다. 입력 철판, 구리판; 같은 배치로 노랑→빨강→파랑. | 15×45 | copper-plate 30/min, iron-plate 60/min, copper-plate 30/min, iron-plate 60/min |
| <img src="blueprints/science-green-upgradeable/images/preview.webp" width="160"> | [초록 과학 (쌓는 셀)](blueprints/science-green-upgradeable/README.md)<br>`science` `stackable` `upgradeable` | 15×20 셀을 북쪽으로 쌓아 늘립니다. 입력 철판, 초록 회로; 같은 배치로 노랑→빨강→파랑. | 15×69 | iron-plate 113/min, electronic-circuit 25/min, iron-plate 113/min, electronic-circuit 25/min |
| <img src="blueprints/science-military-upgradeable/images/preview.webp" width="160"> | [군사 과학 (쌓는 셀)](blueprints/science-military-upgradeable/README.md)<br>`science` `stackable` `upgradeable` | 15×12 셀을 북쪽으로 쌓아 늘립니다. 입력 관통탄, 수류탄, 벽; 같은 배치로 노랑→빨강→파랑. | 19×45 | grenade 22/min, piercing-rounds-magazine 22/min, stone-wall 45/min, grenade 22/min, piercing-rounds-magazine 22/min, stone-wall 45/min |
| <img src="blueprints/science-blue-upgradeable/images/preview.webp" width="160"> | [파랑 과학 (쌓는 셀)](blueprints/science-blue-upgradeable/README.md)<br>`science` `stackable` `upgradeable` | 15×12 셀을 북쪽으로 쌓아 늘립니다. 입력 엔진, 빨강 회로, 황; 같은 배치로 노랑→빨강→파랑. | 19×45 | advanced-circuit 28/min, engine-unit 19/min, sulfur 9/min, advanced-circuit 28/min, engine-unit 19/min, sulfur 9/min |
| <img src="blueprints/science-purple-upgradeable/images/preview.webp" width="160"> | [보라 과학 (쌓는 셀)](blueprints/science-purple-upgradeable/README.md)<br>`science` `stackable` `upgradeable` | 15×12 셀을 북쪽으로 쌓아 늘립니다. 입력 레일, 전기로, 생산 모듈; 같은 배치로 노랑→빨강→파랑. | 19×45 | electric-furnace 11/min, rail 321/min, productivity-module 11/min, electric-furnace 11/min, rail 321/min, productivity-module 11/min |
| <img src="blueprints/science-yellow-upgradeable/images/preview.webp" width="160"> | [노랑 과학 (쌓는 셀)](blueprints/science-yellow-upgradeable/README.md)<br>`science` `stackable` `upgradeable` | 15×12 셀을 북쪽으로 쌓아 늘립니다. 입력 저밀도 구조물, 파랑 회로, 로봇 프레임; 같은 배치로 노랑→빨강→파랑. | 19×45 | processing-unit 21/min, low-density-structure 32/min, flying-robot-frame 11/min, processing-unit 21/min, low-density-structure 32/min, flying-robot-frame 11/min |
| <img src="blueprints/cell-piercing-rounds/images/preview.webp" width="160"> | [관통탄 (쌓는 셀)](blueprints/cell-piercing-rounds/README.md)<br>`intermediate` `stackable` `upgradeable` | 15×12 셀을 북쪽으로 쌓아 늘립니다. 입력 철판, 구리판, 강철; 같은 배치로 노랑→빨강→파랑. | 19×45 | copper-plate 50/min, iron-plate 200/min, steel-plate 25/min, copper-plate 50/min, iron-plate 200/min, steel-plate 25/min |
| <img src="blueprints/cell-grenade/images/preview.webp" width="160"> | [수류탄 (쌓는 셀)](blueprints/cell-grenade/README.md)<br>`intermediate` `stackable` `upgradeable` | 13×12 셀을 북쪽으로 쌓아 늘립니다. 입력 석탄, 철판; 같은 배치로 노랑→빨강→파랑. | 15×45 | iron-plate 141/min, coal 281/min, iron-plate 141/min, coal 281/min |
| <img src="blueprints/cell-stone-wall/images/preview.webp" width="160"> | [벽 (쌓는 셀)](blueprints/cell-stone-wall/README.md)<br>`intermediate` `stackable` `upgradeable` | 13×4 셀을 북쪽으로 쌓아 늘립니다. 입력 벽돌; 같은 배치로 노랑→빨강→파랑. | 15×21 | stone-brick 416/min, stone-brick 416/min |
| <img src="blueprints/cell-rail/images/preview.webp" width="160"> | [레일 (쌓는 셀)](blueprints/cell-rail/README.md)<br>`intermediate` `stackable` `upgradeable` | 15×12 셀을 북쪽으로 쌓아 늘립니다. 입력 돌, 강철, 철판; 같은 배치로 노랑→빨강→파랑. | 19×45 | steel-plate 300/min, stone 300/min, iron-plate 150/min, steel-plate 300/min, stone 300/min, iron-plate 150/min |
| <img src="blueprints/cell-electric-furnace/images/preview.webp" width="160"> | [전기로 (쌓는 셀)](blueprints/cell-electric-furnace/README.md)<br>`intermediate` `stackable` `upgradeable` | 15×12 셀을 북쪽으로 쌓아 늘립니다. 입력 강철, 벽돌, 빨강 회로; 같은 배치로 노랑→빨강→파랑. | 19×45 | stone-brick 416/min, steel-plate 416/min, advanced-circuit 208/min, stone-brick 416/min, steel-plate 416/min, advanced-circuit 208/min |
| <img src="blueprints/rail-city-block-2x2/images/preview.webp" width="160"> | [철도 큰 블럭 2×2 (가운데 빈 공간)](blueprints/rail-city-block-2x2/README.md)<br>`rail` `city-block` | 1×1 블럭 2×2개 크기의 한 블럭. 교차로는 네 모서리에만 있고 가장자리는 긴 직선이라 가운데 350칸 안팎의 큰 공간이 생깁니다. | 466×465 | - |
| <img src="blueprints/cell-productivity-module/images/preview.webp" width="160"> | [생산 모듈 (쌓는 셀)](blueprints/cell-productivity-module/README.md)<br>`intermediate` `stackable` `upgradeable` | 13×12 셀을 북쪽으로 쌓아 늘립니다. 입력 빨강 회로, 초록 회로; 같은 배치로 노랑→빨강→파랑. | 15×45 | electronic-circuit 75/min, advanced-circuit 75/min, electronic-circuit 75/min, advanced-circuit 75/min |
| <img src="blueprints/rail-city-block-3x3/images/preview.webp" width="160"> | [철도 큰 블럭 3×3 (가운데 빈 공간)](blueprints/rail-city-block-3x3/README.md)<br>`rail` `city-block` | 1×1 블럭 3×3개 크기의 한 블럭. 교차로는 네 모서리에만 있고 가장자리는 긴 직선이라 가운데 532칸 안팎의 큰 공간이 생깁니다. | 648×647 | - |
| <img src="blueprints/cell-robot-frame/images/preview.webp" width="160"> | [로봇 프레임 (쌓는 셀)](blueprints/cell-robot-frame/README.md)<br>`intermediate` `stackable` `upgradeable` | 15×12 셀을 북쪽으로 쌓아 늘립니다. 입력 배터리, 초록 회로, 전기 엔진, 강철; 같은 배치로 노랑→빨강→파랑. | 19×45 | electronic-circuit 34/min, battery 22/min, electric-engine-unit 11/min, steel-plate 11/min, electronic-circuit 34/min, battery 22/min, electric-engine-unit 11/min, steel-plate 11/min |
| <img src="blueprints/mall-upgradeable/images/preview.webp" width="160"> | [업그레이드형 몰 (쌓는 셀)](blueprints/mall-upgradeable/README.md)<br>`mall` `stackable` `upgradeable` | 15칸 폭 셀 4종(벨트·인서터/조립기·파이프/물류·기차/유체, 24품목)을 북쪽으로 쌓습니다. 입력은 철·강철·초록 회로, 톱니는 맨 아래 셀이 만듭니다. | 17×57 | iron-plate 450/min, steel-plate 450/min, electronic-circuit 450/min, iron-plate 450/min, steel-plate 450/min, electronic-circuit 450/min |
| <img src="blueprints/rail-buffer-station/images/preview.webp" width="160"> | [철도 버퍼 역 블럭](blueprints/rail-buffer-station/README.md)<br>`rail` `city-block` `station` `buffer` | 한 아이템을 위 역에서 하역해 상자 24개에 쌓고 아래 역에서 적재. 열차 제한은 재고로 자동 설정. | 284×283 | iron-plate ≤900/min |
| <img src="blueprints/module-mall-t1-t2/images/preview.webp" width="160"> | [모듈 몰 1·2단계 (쌓는 셀)](blueprints/module-mall-t1-t2/README.md)<br>`mall` `stackable` `upgradeable` | 15칸 폭 셀 2종(속도·효율 / 생산·품질)을 북쪽으로 쌓습니다. 1단계 모듈이 바로 위 2단계 기계로 넘어갑니다. 입력은 초록·빨강·파랑 회로. | 19×25 | electronic-circuit 450/min, advanced-circuit 450/min, processing-unit 450/min, electronic-circuit 450/min, advanced-circuit 450/min, processing-unit 450/min |
| <img src="blueprints/rail-mining-station/images/preview.webp" width="160"> | [철도 채굴 공급 역 블럭](blueprints/rail-mining-station/README.md)<br>`rail` `city-block` `station` `mining` | 블럭 안을 채굴기 64대로 채우고 수집 벨트로 적재 역에 실어 보내는 공급 블럭. | 284×283 | - |
| <img src="blueprints/rail-smelter-station/images/preview.webp" width="160"> | [철도 제련 공급 역 블럭](blueprints/rail-smelter-station/README.md)<br>`rail` `city-block` `station` `smelting` | 위 역에서 광석을 하역해 전기 용광로 42대로 제련하고 아래 역에서 판을 적재. | 284×283 | iron-ore ~900/min |
| <img src="blueprints/planet-vulcanus/images/preview.webp" width="160"> | [불카누스 올인원 단지](blueprints/planet-vulcanus/README.md)<br>`planet` `vulcanus` `space-age` `all-in-one` `stackable` | 용암 → 용융 금속 → 주조·텅스텐·금속 과학 분당 360, 윤활유, 몰(주조기·대형 채굴기·터보 벨트), 전력 372 MW, 착륙장 수입·로켓 수출, 돌 처리까지 버스 하나에 쌓는 셀로. | 643×107 | - |
| <img src="blueprints/planet-fulgora/images/preview.webp" width="160"> | [풀가오라 올인원 단지](blueprints/planet-fulgora/README.md)<br>`planet` `fulgora` `space-age` `all-in-one` `stackable` | 고철 초당 160 → 재활용·분류 → 홀뮴·전해액·초전도체·슈퍼커패시터 → 전자기 과학 분당 약 100, 2차 재활용(철·구리·초록 회로·플라스틱), 로켓·수출, 전자기 공장 몰, 번개 발전·보호, 넘침 처리까지 버스 하나에. | 975×112 | - |
| <img src="blueprints/planet-gleba/images/preview.webp" width="160"> | [글레바 올인원 단지](blueprints/planet-gleba/README.md)<br>`planet` `gleba` `space-age` `all-in-one` `stackable` `robots` | 로봇이 나르는 쌓는 셀: 과일 가공 → 바이오플럭스·영양분·펜타포드 알 → 농업 과학 분당 약 300, 철 박테리아 → 탄창, 탄소 섬유, 젤리 로켓 연료, 가열탑 전력(부패물 연료), 로켓·착륙장, 포탑 방어선까지. | 305×55 | - |

<!-- CATALOG:END -->

## 미리보기 이미지

`tools/build.py`는 [Factorio Blueprint Editor](https://fbe.factorygamefan.com)(FactoryGameFan 포크, 2.0·Space Age 지원)를
헤드리스 Chromium으로 열어 실제 게임 스프라이트로 렌더링합니다. 큰 철도 블럭은 설비 부분만 잘라낸 `detail.webp`도 만듭니다.
Playwright가 없거나 접속이 안 되면 도식 렌더러로 대체합니다(`--renderer schematic`로 직접 고를 수도 있습니다).

## 규칙

- 공장은 **가로 메인버스(6줄 묶음 + 빈칸 2줄)**에서 분기로 입력을 받고, **같은 배치로 초반 → 중반 → 후반 업그레이드**되게 만듭니다([원칙](docs/guides/upgrade-in-place.md)). 물은 waterfill로 현장에서 만듭니다.
- 모든 외부 입력에는 **일정 신호 조합기** 표시를 둡니다 (신호 = 넣을 아이템/유체, 값 = 분당 필요량). 문서의 입력 표는 이 표시에서 자동으로 만들어집니다.
- `README.md` / `README.en.md`의 `AUTO` 구역과 이 카탈로그는 `tools/build.py`가 다시 씁니다. 직접 쓴 설명은 그 바깥에 둡니다.
- CI(GitHub Actions)가 모든 블루프린트를 다시 생성·검증하고, 문서가 최신인지 확인합니다.

## 라이선스

MIT — 제3자 자료는 [NOTICE.md](NOTICE.md)를 보세요. Factorio는 Wube Software의 상표이며 이 프로젝트는 Wube와 관련이 없습니다.
