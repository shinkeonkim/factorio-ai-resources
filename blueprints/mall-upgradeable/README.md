# 업그레이드형 몰 (쌓는 셀)

> 15칸 폭 셀 4종(벨트·인서터/조립기·파이프/물류·기차/유체, 24품목)을 북쪽으로 쌓습니다. 입력은 철·강철·초록 회로, 톱니는 맨 아래 셀이 만듭니다.

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base) |
| 크기 | 17×57 타일 |
| 엔티티 | 429 |
| 주요 설비 | `assembling-machine-1` ×24 (pipe 3, iron-gear-wheel 2, transport-belt 2, underground-belt 1, splitter 1, long-handed-inserter 1, inserter 1, fast-inserter 1, assembling-machine-2 1, assembling-machine-1 1, electric-mining-drill 1, pipe-to-ground 1, radar 1, steel-chest 1, repair-pack 1, rail-signal 1, engine-unit 1, locomotive 1, storage-tank 1, fluid-wagon 1)<br>`iron-chest` ×22 |
| 검사 | 통과 |

### 입력

_블루프린트 안의 일정 신호 조합기 표시 (값 = 분당 필요량, 위치 = 블루프린트 왼쪽 위 기준 타일 좌표)_

| 신호 | 분당 | 위치 |
|---|---:|---|
| `iron-plate` | 450 | (3, 56) |
| `steel-plate` | 450 | (0, 56) |
| `electronic-circuit` | 450 | (2, 56) |
| `iron-plate` | 450 | (13, 56) |
| `steel-plate` | 450 | (16, 56) |
| `electronic-circuit` | 450 | (14, 56) |

### 출력

| 아이템 | 분당 | 위치 |
|---|---:|---|
| `(chests)` | - | 각 셀 가운데 상자 (2칸 제한) |

### 셀 종류

모든 셀의 폭은 **15**칸이고 같은 레인을 씁니다. 맨 아래 셀이 공용 레인을 채우는 중간재(예: 톱니)를 만들므로 그 셀을 캡 바로 위에 놓고, 나머지 셀은 필요한 것만 원하는 순서로 북쪽에 붙입니다. 제품은 가운데 상자(2칸 제한)에 쌓입니다.

| 셀 | 크기 | 서쪽 (남→북) | 동쪽 (남→북) |
|---|---|---|---|
| gears & belts | 15×12 | `iron-gear-wheel` → `transport-belt` → `underground-belt` | `iron-gear-wheel` → `transport-belt` → `splitter` |
| inserters & assemblers | 15×12 | `long-handed-inserter` → `inserter` → `fast-inserter` | `assembling-machine-2` → `assembling-machine-1` → `electric-mining-drill` |
| pipes & logistics | 15×12 | `pipe` → `pipe-to-ground` → `radar` | `steel-chest` → `repair-pack` → `rail-signal` |
| trains & fluids | 15×12 | `pipe` → `engine-unit` → `locomotive` | `storage-tank` → `fluid-wagon` → `pipe` |

레인: `iron-gear-wheel` (안쪽, 셀 안에서 만듦), `iron-plate` (안쪽), `steel-plate` (바깥), `electronic-circuit` (바깥)

### 로드맵

| 단계 | 시기 / 필요한 연구 | 할 일 |
|---|---|---|
| 1. 첫 셀 | `logistics` (빨강), `steel-processing` (빨강) | 버스에서 철·강철·초록 회로를 분기해 캡 + '톱니·벨트' 셀을 놓습니다. 벨트·지하 벨트·분배기가 상자에 쌓입니다. 이 셀이 톱니 레인을 채우니 항상 맨 아래에 둡니다. |
| 2. 셀 추가 | `electric-mining-drill` (빨강), `fast-inserter` (빨강), `automation-2` (빨강·초록), `radar` (빨강), `automated-rail-transportation` (빨강·초록), `engine` (빨강·초록), `railway` (빨강·초록), `fluid-wagon` (빨강·초록) | 필요한 셀만 북쪽에 붙입니다: 인서터·조립기, 파이프·물류, 기차·유체. 연구 안 된 품목 칸은 멈춰 있다가 연구되면 저절로 돕니다. |
| 3. 중반 | `logistics-2` (빨강·초록), `electric-energy-distribution-1` (빨강·초록) | 업그레이드 플래너: 빨강 벨트·조립기 2·고속 인서터·중형 전봇대. |
| 4. 후반 / 봇 | `logistics-3` (빨강·초록·파랑·보라), `automation-3` (빨강·초록·파랑·보라), `bulk-inserter` (빨강·초록), `construction-robotics` (빨강·초록·파랑) | 파랑 벨트·조립기 3·벌크 인서터, 상자를 패시브 공급 상자로 바꾸면 건설 로봇이 몰에서 바로 가져갑니다. |

**다음에 지을 것**

- [모듈 몰 1·2단계 (쌓는 셀)](../module-mall-t1-t2/README.md) — 모듈 몰
- [빨강 과학 (쌓는 셀)](../science-red-upgradeable/README.md) — 첫 과학 셀

### 파일

| 파일 | 설명 |
|---|---|
| [`blueprint.txt`](blueprint.txt) | 캡 + 셀 종류별 1개, 초반 (예시·미리보기) |
| [`variants/gears-belts-early.txt`](variants/gears-belts-early.txt) | Mall: gears & belts — 초반 (노랑·조립기 1·일반) |
| [`variants/gears-belts-mid.txt`](variants/gears-belts-mid.txt) | Mall: gears & belts — 중반 (빨강·조립기 2·고속) |
| [`variants/gears-belts-late.txt`](variants/gears-belts-late.txt) | Mall: gears & belts — 후반 (파랑·조립기 3·벌크) |
| [`variants/inserters-assemblers-early.txt`](variants/inserters-assemblers-early.txt) | Mall: inserters & assemblers — 초반 (노랑·조립기 1·일반) |
| [`variants/inserters-assemblers-mid.txt`](variants/inserters-assemblers-mid.txt) | Mall: inserters & assemblers — 중반 (빨강·조립기 2·고속) |
| [`variants/inserters-assemblers-late.txt`](variants/inserters-assemblers-late.txt) | Mall: inserters & assemblers — 후반 (파랑·조립기 3·벌크) |
| [`variants/pipes-logistics-early.txt`](variants/pipes-logistics-early.txt) | Mall: pipes & logistics — 초반 (노랑·조립기 1·일반) |
| [`variants/pipes-logistics-mid.txt`](variants/pipes-logistics-mid.txt) | Mall: pipes & logistics — 중반 (빨강·조립기 2·고속) |
| [`variants/pipes-logistics-late.txt`](variants/pipes-logistics-late.txt) | Mall: pipes & logistics — 후반 (파랑·조립기 3·벌크) |
| [`variants/trains-fluids-early.txt`](variants/trains-fluids-early.txt) | Mall: trains & fluids — 초반 (노랑·조립기 1·일반) |
| [`variants/trains-fluids-mid.txt`](variants/trains-fluids-mid.txt) | Mall: trains & fluids — 중반 (빨강·조립기 2·고속) |
| [`variants/trains-fluids-late.txt`](variants/trains-fluids-late.txt) | Mall: trains & fluids — 후반 (파랑·조립기 3·벌크) |
| [`variants/cap-early.txt`](variants/cap-early.txt) | 캡 — 초반 (노랑·조립기 1·일반) |
| [`variants/cap-mid.txt`](variants/cap-mid.txt) | 캡 — 중반 (빨강·조립기 2·고속) |
| [`variants/cap-late.txt`](variants/cap-late.txt) | 캡 — 후반 (파랑·조립기 3·벌크) |

문자열을 클립보드에 복사한 뒤 게임에서 블루프린트 라이브러리 → 문자열 가져오기:

```sh
pbcopy < blueprints/mall-upgradeable/blueprint.txt   # macOS
xclip -selection clipboard < blueprints/mall-upgradeable/blueprint.txt   # Linux
```

### 다시 생성

```sh
python3 blueprints/mall-upgradeable/generate.py
python3 tools/build.py mall-upgradeable
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

사용자의 다이소1·다이소2 몰(데모 02·03)을 Nilaus 초록칩 모듈 같은 쌓는 셀로 다시 설계했습니다.
