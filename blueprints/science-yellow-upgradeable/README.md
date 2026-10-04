# 노랑 과학 (업그레이드형 타일)

> 과학 조립기 14 + 로봇 프레임 14 (1:1 직접 투입). 같은 배치로 분당 60 → 90 → 150. 버스 분기 6줄.

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base) |
| 크기 | 69×18 타일 |
| 엔티티 | 404 |
| 주요 설비 | `assembling-machine-1` ×28 (utility-science-pack 14, flying-robot-frame 14) |
| 검사 | 통과 |

### 입력

_블루프린트 안의 일정 신호 조합기 표시 (값 = 분당 필요량, 위치 = 블루프린트 왼쪽 위 기준 타일 좌표)_

| 신호 | 분당 | 위치 |
|---|---:|---|
| `processing-unit` | 100 | (2, 17) |
| `low-density-structure` | 150 | (0, 17) |
| `electronic-circuit` | 150 | (10, 17) |
| `steel-plate` | 50 | (8, 17) |
| `battery` | 100 | (18, 17) |
| `electric-engine-unit` | 50 | (16, 17) |

### 출력

| 아이템 | 분당 | 위치 |
|---|---:|---|
| `utility-science-pack` | 60 / 90 / 150 | 과학 벨트 동쪽 끝 (y=0) |

### 로드맵

| 단계 | 시기 / 필요한 연구 | 할 일 |
|---|---|---|
| 0. 준비 | `utility-science-pack` (빨강·초록·파랑), `robotics` (빨강·초록·파랑), `low-density-structure` (빨강·초록·파랑), `processing-unit` (빨강·초록·파랑) | 6+2 버스에 필요한 묶음을 깔고, 타일 아래쪽 표시 조합기 위치에 맞춰 버스 분기(Full/Half)를 엽니다. 저밀도 구조물·파랑 회로·전기 엔진·배터리·강철·초록 회로가 필요합니다. |
| 1. 초반 (기본 파일) | `automation` (빨강), `logistics` (빨강), `electronics` (아이템을 처음 만들면) | 노랑 벨트·조립기 1·일반 인서터·소형 전봇대로 짓습니다. 타일당 분당 60. 더 필요하면 같은 타일을 하나 더 놓습니다. |
| 2. 중반 | `logistics-2` (빨강·초록), `automation-2` (빨강·초록), `fast-inserter` (빨강), `electric-energy-distribution-1` (빨강·초록) | 업그레이드 플래너로 빨강 벨트·조립기 2·고속 인서터·중형 전봇대로 바꿉니다. 배치는 그대로, 분당 90. 버스 분기도 빨강으로 함께 올립니다. |
| 3. 후반 | `logistics-3` (빨강·초록·파랑·보라), `automation-3` (빨강·초록·파랑·보라), `bulk-inserter` (빨강·초록) | 파랑 벨트·조립기 3·벌크 인서터로 바꿉니다. 분당 150. 이 단계부터 모듈·비콘을 꽂을 수 있지만, 그러면 입력이 표시 값보다 늘어나니 버스 분기를 Full로 바꾸세요. |

**다음에 지을 것**

- [보라 과학 (업그레이드형 타일)](../science-purple-upgradeable/README.md) — 같이 필요한 과학

### 파일

| 파일 | 설명 |
|---|---|
| [`blueprint.txt`](blueprint.txt) | 초반 (노랑·조립기 1·일반) |
| [`variants/mid.txt`](variants/mid.txt) | 중반 (빨강·조립기 2·고속) |
| [`variants/late.txt`](variants/late.txt) | 후반 (파랑·조립기 3·벌크) |

문자열을 클립보드에 복사한 뒤 게임에서 블루프린트 라이브러리 → 문자열 가져오기:

```sh
pbcopy < blueprints/science-yellow-upgradeable/blueprint.txt   # macOS
xclip -selection clipboard < blueprints/science-yellow-upgradeable/blueprint.txt   # Linux
```

### 다시 생성

```sh
python3 blueprints/science-yellow-upgradeable/generate.py
python3 tools/build.py science-yellow-upgradeable
```

<!-- AUTO:END -->

## 구조

- 과학 조립기 14대(y=2..4). 바로 밑에 로봇 프레임 조립기 14대(y=6..8)가 있고, 프레임을 인서터 하나로 바로 위에 넣습니다.
  - 프레임 20초 : 과학 21초라서 1:1이면 됩니다.
- 과학: 저밀도 구조물·파랑 회로를 y=-1에서 롱암으로 받고, y=0으로 냅니다.
- 프레임: 전기 엔진·배터리는 y=10(고속), 강철·초록 회로는 y=11(롱암)에서 받습니다.
- 입력은 모두 버스 4·5번 묶음과 3번 묶음(회로)에서 받습니다.

## 업그레이드

| 단계 | 벨트 | 조립기 | 인서터 | 전봇대 | 타일당 생산 |
|---|---|---|---|---|---|
| 초반 (기본 파일) | 노랑 | 조립기 1 | 일반 | 소형 | 분당 60 |
| 중반 (`variants/mid.txt`) | 빨강 | 조립기 2 | 고속 | 중형 | 분당 90 |
| 후반 (`variants/late.txt`) | 파랑 | 조립기 3 | 벌크 | 중형 | 분당 150 |

- 지하 벨트 간격 3칸 이하, 소형 전봇대 기준 배치.
- 롱암은 기계당 필요량이 초당 1.2개(롱암 기본 속도)보다 충분히 낮은 자리에만 썼습니다. 업그레이드해도 병목이 되지 않습니다.
- 표시 조합기 값은 **후반 기준**입니다: 저밀도 구조물 150, 파랑 회로 100, 전기 엔진 50, 배터리 100, 강철 50, 초록 회로 150/분.

## 출처

타일형 과학 아이디어: Christoffer Ramqvist "Tileable Science Production", XtremeZion Science Book, Nilaus Base-In-A-Book 비율 참고. 설계 자체는 이 저장소에서 새로 만든 것입니다.
