# 군사 과학 (업그레이드형 타일)

> 과학 조립기 10 + 벽 3·관통탄 3·탄창 2·수류탄 8. 같은 배치로 분당 60 → 90 → 150. 버스 분기 6줄(벽돌, 철 2, 구리, 강철, 석탄).

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base) |
| 크기 | 68×26 타일 |
| 엔티티 | 500 |
| 주요 설비 | `assembling-machine-1` ×26 (military-science-pack 10, grenade 8, stone-wall 3, piercing-rounds-magazine 3, firearm-magazine 2) |
| 검사 | 통과 |

### 입력

_블루프린트 안의 일정 신호 조합기 표시 (값 = 분당 필요량, 위치 = 블루프린트 왼쪽 위 기준 타일 좌표)_

| 신호 | 분당 | 위치 |
|---|---:|---|
| `stone-brick` | 750 | (1, 25) |
| `iron-plate` | 600 | (7, 25) |
| `copper-plate` | 150 | (12, 25) |
| `steel-plate` | 38 | (10, 25) |
| `coal` | 750 | (27, 25) |
| `iron-plate` | 375 | (31, 25) |

### 출력

| 아이템 | 분당 | 위치 |
|---|---:|---|
| `military-science-pack` | 60 / 90 / 150 | 과학 벨트 동쪽 끝 (y=0) |

### 파일

| 파일 | 설명 |
|---|---|
| [`blueprint.txt`](blueprint.txt) | 초반 (노랑·조립기 1·일반) |
| [`variants/mid.txt`](variants/mid.txt) | 중반 (빨강·조립기 2·고속) |
| [`variants/late.txt`](variants/late.txt) | 후반 (파랑·조립기 3·벌크) |

문자열을 클립보드에 복사한 뒤 게임에서 블루프린트 라이브러리 → 문자열 가져오기:

```sh
pbcopy < blueprints/science-military-upgradeable/blueprint.txt   # macOS
xclip -selection clipboard < blueprints/science-military-upgradeable/blueprint.txt   # Linux
```

### 다시 생성

```sh
python3 blueprints/science-military-upgradeable/generate.py
python3 tools/build.py science-military-upgradeable
```

<!-- AUTO:END -->

## 구조

- 과학 조립기 10대(y=2..4) → 과학 벨트(y=0).
  - 북쪽: 벽을 y=-1 벨트에서 롱암으로. 벽 조립기 3대(북서쪽)가 y=-7 벽돌 벨트에서 벽돌을 받아 y=-1에 놓습니다.
  - 남쪽: 관통탄(y=6 북쪽 레인, 고속) + 수류탄(y=7, 롱암).
- 관통탄 무리(남서쪽): `관통 탄창 관통 탄창 관통` 순서, 간격 4. 탄창 조립기가 양옆 관통탄 조립기에 직접 넣습니다.
  - 탄창은 철 4개가 들어가서 탄창 조립기 하나에 인서터 3개로 철을 넣습니다(초반 초당 2개).
  - 철은 y=6 남쪽 레인, 관통탄의 강철·구리는 y=12에서.
- 수류탄 8대(y=9..11): 석탄은 y=13(고속), 철은 y=14(롱암). 출력은 y=7.
- 비율: 군사 10 : 수류탄 8 : 관통 3 : 탄창 2 : 벽 3.

## 업그레이드

| 단계 | 벨트 | 조립기 | 인서터 | 전봇대 | 타일당 생산 |
|---|---|---|---|---|---|
| 초반 (기본 파일) | 노랑 | 조립기 1 | 일반 | 소형 | 분당 60 |
| 중반 (`variants/mid.txt`) | 빨강 | 조립기 2 | 고속 | 중형 | 분당 90 |
| 후반 (`variants/late.txt`) | 파랑 | 조립기 3 | 벌크 | 중형 | 분당 150 |

- 지하 벨트 간격 3칸 이하, 소형 전봇대 기준 배치.
- 롱암은 기계당 필요량이 초당 1.2개(롱암 기본 속도)보다 충분히 낮은 자리에만 썼습니다. 업그레이드해도 병목이 되지 않습니다.
- 표시 조합기 값은 **후반 기준**입니다: 벽돌 750, 철(탄창) 600, 구리 150, 강철 38, 석탄 750, 철(수류탄) 375/분.

## 출처

타일형 과학 아이디어: Christoffer Ramqvist "Tileable Science Production", XtremeZion Science Book, Nilaus Base-In-A-Book 비율 참고. 설계 자체는 이 저장소에서 새로 만든 것입니다.
