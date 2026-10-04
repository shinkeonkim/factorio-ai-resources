# 모듈 몰 1·2단계 (쌓는 셀)

> 15칸 폭 셀 2종(속도·효율 / 생산·품질)을 북쪽으로 쌓습니다. 1단계 모듈이 바로 위 2단계 기계로 넘어갑니다. 입력은 초록·빨강·파랑 회로.

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base, quality) |
| 크기 | 19×25 타일 |
| 엔티티 | 181 |
| 주요 설비 | `assembling-machine-1` ×8 (speed-module 1, speed-module-2 1, efficiency-module 1, efficiency-module-2 1, productivity-module 1, productivity-module-2 1, quality-module 1, quality-module-2 1)<br>`iron-chest` ×8 |
| 검사 | 통과 |

### 입력

_블루프린트 안의 일정 신호 조합기 표시 (값 = 분당 필요량, 위치 = 블루프린트 왼쪽 위 기준 타일 좌표)_

| 신호 | 분당 | 위치 |
|---|---:|---|
| `electronic-circuit` | 450 | (4, 24) |
| `advanced-circuit` | 450 | (0, 24) |
| `processing-unit` | 450 | (1, 24) |
| `electronic-circuit` | 450 | (14, 24) |
| `advanced-circuit` | 450 | (18, 24) |
| `processing-unit` | 450 | (17, 24) |

### 출력

| 아이템 | 분당 | 위치 |
|---|---:|---|
| `(chests)` | - | 각 셀 가운데 상자 (2칸 제한) |

### 셀 종류

모든 셀의 폭은 **15**칸이고 같은 레인을 씁니다. 맨 아래 셀이 공용 레인을 채우는 중간재(예: 톱니)를 만들므로 그 셀을 캡 바로 위에 놓고, 나머지 셀은 필요한 것만 원하는 순서로 북쪽에 붙입니다. 제품은 가운데 상자(2칸 제한)에 쌓입니다.

| 셀 | 크기 | 서쪽 (남→북) | 동쪽 (남→북) |
|---|---|---|---|
| speed & efficiency | 15×8 | `speed-module` → `speed-module-2` | `efficiency-module` → `efficiency-module-2` |
| productivity & quality | 15×8 | `productivity-module` → `productivity-module-2` | `quality-module` → `quality-module-2` |

레인: `advanced-circuit` (안쪽), `electronic-circuit` (안쪽), `processing-unit` (바깥)

### 로드맵

| 단계 | 시기 / 필요한 연구 | 할 일 |
|---|---|---|
| 1. 1단계 | `speed-module` (빨강·초록), `efficiency-module` (빨강·초록), `productivity-module` (빨강·초록), `advanced-circuit` (빨강·초록) | 버스 3번 묶음에서 회로를 분기해 캡 + 셀을 놓습니다. 2단계 칸은 연구 전까지 멈춰 있습니다. |
| 2. 2단계 | `speed-module-2` (빨강·초록·파랑), `efficiency-module-2` (빨강·초록·파랑), `productivity-module-2` (빨강·초록·파랑), `processing-unit` (빨강·초록·파랑) | 2단계 모듈은 1단계 4개 + 빨강·파랑 회로 5개씩입니다(2.1 데이터). 1단계 기계가 바로 위 2단계 기계에 넣고 남는 것은 상자로. |
| 3. 품질 (Space Age) | `quality-module` (빨강·초록), `quality-module-2` (빨강·초록·파랑) | 품질 셀은 Quality 모드가 있을 때만 씁니다. 없으면 그 셀은 빼고 쌓으세요. |

**다음에 지을 것**

- [보라 과학 (쌓는 셀)](../science-purple-upgradeable/README.md) — 생산 모듈을 쓰는 과학
- [업그레이드형 몰 (쌓는 셀)](../mall-upgradeable/README.md) — 건물 몰

### 파일

| 파일 | 설명 |
|---|---|
| [`blueprint.txt`](blueprint.txt) | 캡 + 셀 종류별 1개, 초반 (예시·미리보기) |
| [`variants/speed-efficiency-early.txt`](variants/speed-efficiency-early.txt) | Modules: speed & efficiency — 초반 (노랑·조립기 1·일반) |
| [`variants/speed-efficiency-mid.txt`](variants/speed-efficiency-mid.txt) | Modules: speed & efficiency — 중반 (빨강·조립기 2·고속) |
| [`variants/speed-efficiency-late.txt`](variants/speed-efficiency-late.txt) | Modules: speed & efficiency — 후반 (파랑·조립기 3·벌크) |
| [`variants/productivity-quality-early.txt`](variants/productivity-quality-early.txt) | Modules: productivity & quality — 초반 (노랑·조립기 1·일반) |
| [`variants/productivity-quality-mid.txt`](variants/productivity-quality-mid.txt) | Modules: productivity & quality — 중반 (빨강·조립기 2·고속) |
| [`variants/productivity-quality-late.txt`](variants/productivity-quality-late.txt) | Modules: productivity & quality — 후반 (파랑·조립기 3·벌크) |
| [`variants/cap-early.txt`](variants/cap-early.txt) | 캡 — 초반 (노랑·조립기 1·일반) |
| [`variants/cap-mid.txt`](variants/cap-mid.txt) | 캡 — 중반 (빨강·조립기 2·고속) |
| [`variants/cap-late.txt`](variants/cap-late.txt) | 캡 — 후반 (파랑·조립기 3·벌크) |

문자열을 클립보드에 복사한 뒤 게임에서 블루프린트 라이브러리 → 문자열 가져오기:

```sh
pbcopy < blueprints/module-mall-t1-t2/blueprint.txt   # macOS
xclip -selection clipboard < blueprints/module-mall-t1-t2/blueprint.txt   # Linux
```

### 다시 생성

```sh
python3 blueprints/module-mall-t1-t2/generate.py
python3 tools/build.py module-mall-t1-t2
```

<!-- AUTO:END -->

## 구조

- 과학 셀과 같은 틀입니다: 입력 벨트가 양쪽 가장자리를 따라 북쪽으로 셀을 관통하고, 기계는 3칸마다 한 대씩(4칸 주기) 한 열로 섭니다.
- 가운데 열은 벨트 대신 **상자**입니다. 각 기계가 자기 상자에 넣고, 바로 위나 아래 기계가 그 제품을 쓰면 빈 줄의 인서터가 바로 넘겨 줍니다(예: 벨트 → 지하 벨트·분배기, 인서터 → 롱암·고속 인서터, 조립기 1 → 조립기 2, 1단계 → 2단계 모듈).
- 버스에 없는 중간재(톱니)는 맨 아래 셀이 만들어 바깥쪽 레인에 올리고, 위쪽 셀이 모두 그 레인을 씁니다.
- 표시 조합기 값은 입력마다 분당 450(노랑 레인 하나)입니다. 몰은 상자가 차면 쉬므로 실제로는 훨씬 적게 씁니다.

## 업그레이드

업그레이드 플래너로 벨트·조립기·인서터·전봇대를 바꾸고, 후반에는 철 상자를 패시브 공급 상자로 바꿉니다(같은 크기).

## 출처

이 저장소의 이전 모듈 몰을 쌓는 셀 형태로 다시 만들었습니다.
