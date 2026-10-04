# 레일 경사로·지지대 (쌓는 셀)

> 15×8 상자 셀: 지지대·경사로를 양쪽에서 만들어 가운데 상자에. 입력은 정제 콘크리트·강철·레일; 셀을 붙일수록 상자가 늘어납니다.

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base, space-age) |
| 크기 | 19×17 타일 |
| 엔티티 | 127 |
| 주요 설비 | `assembling-machine-1` ×4 (rail-support 2, rail-ramp 2)<br>`iron-chest` ×4 |
| 검사 | 통과 |

### 입력

_블루프린트 안의 일정 신호 조합기 표시 (값 = 분당 필요량, 위치 = 블루프린트 왼쪽 위 기준 타일 좌표)_

| 신호 | 분당 | 위치 |
|---|---:|---|
| `refined-concrete` | 450 | (4, 16) |
| `steel-plate` | 450 | (0, 16) |
| `rail` | 450 | (1, 16) |
| `refined-concrete` | 450 | (14, 16) |
| `steel-plate` | 450 | (18, 16) |
| `rail` | 450 | (17, 16) |

### 출력

| 아이템 | 분당 | 위치 |
|---|---:|---|
| `(chests)` | - | 가운데 상자 (2칸 제한) |

### 셀 종류

모든 셀의 폭은 **15**칸이고 같은 레인을 씁니다. 맨 아래 셀이 공용 레인을 채우는 중간재(예: 톱니)를 만들므로 그 셀을 캡 바로 위에 놓고, 나머지 셀은 필요한 것만 원하는 순서로 북쪽에 붙입니다. 제품은 가운데 상자(2칸 제한)에 쌓입니다.

| 셀 | 크기 | 서쪽 (남→북) | 동쪽 (남→북) |
|---|---|---|---|
| Ramps & supports | 15×8 | `rail-support` → `rail-ramp` | `rail-ramp` → `rail-support` |

레인: `steel-plate` (안쪽), `refined-concrete` (안쪽), `rail` (바깥)

### 로드맵

| 단계 | 시기 / 필요한 연구 | 할 일 |
|---|---|---|
| 0. 연구 (Space Age) | `elevated-rail` (빨강·초록·파랑·보라) | 엘리베이티드 레일 연구가 경사로·지지대를 엽니다(보라 과학). |
| 1. 입력 | - | 정제 콘크리트는 정제 콘크리트 셀의 가운데 벨트에서, 레일은 레일 셀이나 버스에서, 강철은 버스에서 캡 표시 자리로. |
| 2. 재고 | - | 2x2 큰 철도 블럭 하나에 지지대 216개, 경사로 18개. 상자가 모자라면 셀을 북쪽에 하나 더. |
| 3. 업그레이드 | `logistics-2` (빨강·초록), `logistics-3` (빨강·초록·파랑·보라), `construction-robotics` (빨강·초록·파랑) | 빨강/파랑 벨트·조립기 2/3·고속/벌크 인서터, 후반엔 패시브 공급 상자로 봇이 바로 가져가게. |

**다음에 지을 것**

- [정제 콘크리트 (쌓는 셀)](../refined-concrete/README.md) — 정제 콘크리트 공급
- [레일 (쌓는 셀)](../cell-rail/README.md) — 레일 공급
- [철도 큰 블럭 2×2 (가운데 빈 공간)](../rail-city-block-2x2/README.md) — 이걸 쓰는 철도 블럭

### 파일

| 파일 | 설명 |
|---|---|
| [`blueprint.txt`](blueprint.txt) | 캡 + 셀 1개, 초반 (예시·미리보기) |
| [`variants/ramps-supports-early.txt`](variants/ramps-supports-early.txt) | Ramps & supports — 초반 (노랑·조립기 1·일반) |
| [`variants/ramps-supports-mid.txt`](variants/ramps-supports-mid.txt) | Ramps & supports — 중반 (빨강·조립기 2·고속) |
| [`variants/ramps-supports-late.txt`](variants/ramps-supports-late.txt) | Ramps & supports — 후반 (파랑·조립기 3·벌크) |
| [`variants/cap-early.txt`](variants/cap-early.txt) | 캡 — 초반 (노랑·조립기 1·일반) |
| [`variants/cap-mid.txt`](variants/cap-mid.txt) | 캡 — 중반 (빨강·조립기 2·고속) |
| [`variants/cap-late.txt`](variants/cap-late.txt) | 캡 — 후반 (파랑·조립기 3·벌크) |

문자열을 클립보드에 복사한 뒤 게임에서 블루프린트 라이브러리 → 문자열 가져오기:

```sh
pbcopy < blueprints/rail-ramp-support/blueprint.txt   # macOS
xclip -selection clipboard < blueprints/rail-ramp-support/blueprint.txt   # Linux
```

### 다시 생성

```sh
python3 blueprints/rail-ramp-support/generate.py
python3 tools/build.py rail-ramp-support
```

<!-- AUTO:END -->

## 구조

- 몰과 같은 상자 셀입니다: 입력 벨트가 양쪽 가장자리를 따라 셀을 관통하고(안쪽: 강철·정제 콘크리트, 바깥: 레일), 서쪽은 지지대 → 경사로, 동쪽은 경사로 → 지지대 순서로 가운데 상자에 넣습니다.
- 경사로는 정제 콘크리트 100개를 먹어서 인서터가 속도를 제한하지만, 상자가 차면 쉬는 셀이라 문제없습니다.

## 출처

이 저장소의 이전 경사로·지지대 공장을 쌓는 셀로 다시 만들었습니다.
