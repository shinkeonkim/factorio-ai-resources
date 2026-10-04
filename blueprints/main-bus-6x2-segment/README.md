# 메인버스 6+2 기본 구간

> 이 저장소의 버스 구간(33칸): 철 6 | 구리 6 | 회로 2·2·2 | 강철 2·플라스틱 2·돌·벽돌 | 석탄·황·건전지·엔진·전기 엔진·LDS | 유체 6줄. 묶음 사이 빈칸 2줄.

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base) |
| 크기 | 35×46 타일 |
| 엔티티 | 1062 |
| 주요 설비 | - |
| 검사 | 통과 |

### 입력

_블루프린트 안의 일정 신호 조합기 표시 (값 = 분당 필요량, 위치 = 블루프린트 왼쪽 위 기준 타일 좌표)_

| 신호 | 분당 | 위치 |
|---|---:|---|
| `iron-plate` | 900 | (0, 0) |
| `iron-plate` | 900 | (0, 1) |
| `iron-plate` | 900 | (0, 2) |
| `iron-plate` | 900 | (0, 3) |
| `iron-plate` | 900 | (0, 4) |
| `iron-plate` | 900 | (0, 5) |
| `copper-plate` | 900 | (0, 8) |
| `copper-plate` | 900 | (0, 9) |
| `copper-plate` | 900 | (0, 10) |
| `copper-plate` | 900 | (0, 11) |
| `copper-plate` | 900 | (0, 12) |
| `copper-plate` | 900 | (0, 13) |
| `electronic-circuit` | 900 | (0, 16) |
| `electronic-circuit` | 900 | (0, 17) |
| `advanced-circuit` | 900 | (0, 18) |
| `advanced-circuit` | 900 | (0, 19) |
| `processing-unit` | 900 | (0, 20) |
| `processing-unit` | 900 | (0, 21) |
| `steel-plate` | 900 | (0, 24) |
| `steel-plate` | 900 | (0, 25) |
| `plastic-bar` | 900 | (0, 26) |
| `plastic-bar` | 900 | (0, 27) |
| `stone` | 900 | (0, 28) |
| `stone-brick` | 900 | (0, 29) |
| `coal` | 900 | (0, 32) |
| `sulfur` | 900 | (0, 33) |
| `battery` | 900 | (0, 34) |
| `engine-unit` | 900 | (0, 35) |
| `electric-engine-unit` | 900 | (0, 36) |
| `low-density-structure` | 900 | (0, 37) |
| `petroleum-gas` (fluid) | 60,000 | (0, 40) |
| `light-oil` (fluid) | 60,000 | (0, 41) |
| `heavy-oil` (fluid) | 60,000 | (0, 42) |
| `lubricant` (fluid) | 60,000 | (0, 43) |
| `sulfuric-acid` (fluid) | 60,000 | (0, 44) |
| `water` (fluid) | 60,000 | (0, 45) |

### 출력

없음

### 로드맵

| 단계 | 시기 / 필요한 연구 | 할 일 |
|---|---|---|
| 1. 첫 버스 | `logistics` (빨강) | 철 6줄·구리 6줄 묶음만 먼저 깔고, 아래 묶음 자리(8칸 간격)는 비워 둡니다. 제련소가 늘 때마다 동쪽으로 33칸 조각을 이어 붙입니다. |
| 2. 회로·강철 | `steel-processing` (빨강) | 3번 묶음(초록·빨강·파랑 회로)에 초록 2줄, 4번 묶음에 강철·돌·벽돌을 채웁니다. 빈 줄은 그대로 두면 나중에 같은 자리에 들어갑니다. |
| 3. 빨강 벨트 | `logistics-2` (빨강·초록) | 업그레이드 플래너로 `variants/red.txt`와 같은 상태로 바꿉니다. 지하 간격이 4칸 이하라 그대로 됩니다. |
| 4. 석유 이후 | `plastics` (빨강·초록), `sulfur-processing` (빨강·초록), `advanced-circuit` (빨강·초록), `battery` (빨강·초록), `engine` (빨강·초록) | 플라스틱, 황, 빨강 회로, 배터리, 엔진을 4·5번 묶음과 3번 묶음에 넣고, 6번 묶음에 유체 줄(지하 파이프, 11칸 주기)을 깝니다. 물은 Waterfill로 필요한 곳에서 바로 뽑습니다. |
| 5. 파랑 / 터보 | `logistics-3` (빨강·초록·파랑·보라), `turbo-transport-belt` (빨강·초록·파랑·보라·우주·불카누스) | `variants/blue.txt`, Space Age면 `variants/turbo.txt`. 버스가 꽉 차면 `variants/extension.txt`로 새 묶음을 아래에 붙입니다. |

**다음에 지을 것**

- [메인버스 6+2 분기 조각](../main-bus-6x2-tap/README.md) — 버스에서 한 줄을 빼는 분기
- [메인버스 6+2 통과 조각](../main-bus-6x2-crossing/README.md) — 아래 묶음 분기가 위 묶음을 건너는 조각
- [빨강 과학 (업그레이드형 타일)](../science-red-upgradeable/README.md) — 첫 번째로 붙일 공장

### 파일

| 파일 | 설명 |
|---|---|
| [`blueprint.txt`](blueprint.txt) | 노랑 벨트 (기본) |
| [`variants/red.txt`](variants/red.txt) | 빨강 벨트 |
| [`variants/blue.txt`](variants/blue.txt) | 파랑 벨트 |
| [`variants/turbo.txt`](variants/turbo.txt) | 터보 벨트 |
| [`variants/extension.txt`](variants/extension.txt) | 연장용 (표시 없음, 동쪽에 이어 붙이기) |

문자열을 클립보드에 복사한 뒤 게임에서 블루프린트 라이브러리 → 문자열 가져오기:

```sh
pbcopy < blueprints/main-bus-6x2-segment/blueprint.txt   # macOS
xclip -selection clipboard < blueprints/main-bus-6x2-segment/blueprint.txt   # Linux
```

### 다시 생성

```sh
python3 blueprints/main-bus-6x2-segment/generate.py
python3 tools/build.py main-bus-6x2-segment
```

<!-- AUTO:END -->

## 구조

- 버스는 **동쪽으로** 흐르고, 한 묶음 = 6줄, 묶음 사이 = 빈칸 2줄입니다. 6묶음 46줄.
- 각 줄 서쪽 끝의 일정 신호 조합기가 그 줄의 아이템입니다(값 = 그 벨트 한 줄의 분당 용량, 유체는 표시용).
- 맨 아래 유체 묶음은 지하 파이프 사슬이라 줄끼리 섞이지 않습니다. 유체 입구는 각 줄 첫 지하 파이프의 서쪽 칸이며, **지하 파이프로 연결**하세요(일반 파이프를 세로로 붙이면 줄끼리 섞입니다).
- 버스를 늘릴 때는 `variants/extension.txt`(표시 없음)를 33칸 단위로 동쪽에 이어 붙입니다. 벨트와 지하 파이프 사슬이 그대로 이어집니다.

## 업그레이드

업그레이드 플래너로 벨트만 바꾸면 됩니다. 변형 파일(빨강/파랑/터보)은 같은 배치에 벨트만 다른 버전입니다.

자세한 사용법: [메인버스 6+2 가이드](../../docs/guides/main-bus-6x2.md)
