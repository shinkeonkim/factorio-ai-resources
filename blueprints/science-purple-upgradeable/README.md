# 보라 과학 (업그레이드형 타일)

> 과학 14 + 레일 6·막대 3·전기로 4·생산 모듈 10. 같은 배치로 분당 60 → 90 → 150. 버스 분기 9줄.

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base) |
| 크기 | 115×30 타일 |
| 엔티티 | 735 |
| 주요 설비 | `assembling-machine-1` ×37 (production-science-pack 14, productivity-module 10, rail 6, electric-furnace 4, iron-stick 3) |
| 검사 | 통과 |

### 입력

_블루프린트 안의 일정 신호 조합기 표시 (값 = 분당 필요량, 위치 = 블루프린트 왼쪽 위 기준 타일 좌표)_

| 신호 | 분당 | 위치 |
|---|---:|---|
| `steel-plate` | 500 | (49, 29) |
| `stone-brick` | 500 | (47, 29) |
| `advanced-circuit` | 250 | (53, 29) |
| `electronic-circuit` | 250 | (71, 29) |
| `advanced-circuit` | 250 | (69, 29) |
| `steel-plate` | 750 | (2, 29) |
| `stone` | 750 | (0, 29) |
| `iron-plate` | 375 | (5, 29) |

### 출력

| 아이템 | 분당 | 위치 |
|---|---:|---|
| `production-science-pack` | 60 / 90 / 150 | 과학 벨트 동쪽 끝 (y=0) |

### 파일

| 파일 | 설명 |
|---|---|
| [`blueprint.txt`](blueprint.txt) | 초반 (노랑·조립기 1·일반) |
| [`variants/mid.txt`](variants/mid.txt) | 중반 (빨강·조립기 2·고속) |
| [`variants/late.txt`](variants/late.txt) | 후반 (파랑·조립기 3·벌크) |

문자열을 클립보드에 복사한 뒤 게임에서 블루프린트 라이브러리 → 문자열 가져오기:

```sh
pbcopy < blueprints/science-purple-upgradeable/blueprint.txt   # macOS
xclip -selection clipboard < blueprints/science-purple-upgradeable/blueprint.txt   # Linux
```

### 다시 생성

```sh
python3 blueprints/science-purple-upgradeable/generate.py
python3 tools/build.py science-purple-upgradeable
```

<!-- AUTO:END -->

## 구조

- 과학 조립기 14대(y=2..4) → y=0. 레일은 y=6에서 고속으로, 전기로·모듈은 y=7에서 롱암으로 꺼냅니다.
- y=7은 레인을 나눕니다.
  - 북쪽 레인: 생산 모듈. 조립기 10대(y=9..11, x=3..32)가 아래에서 넣습니다.
  - 남쪽 레인: 전기로. 조립기 4대(서쪽)가 따로 쓰는 y=7 구간에 놓고, 이 구간이 y=8로 내려가 레일 기둥 밑을 지하로 지난 뒤 x=1에서 옆으로 합칩니다.
  - 두 물건이 한 레인에 섞이면 막히기 때문에 이렇게 나눴습니다.
- 레일 줄(y=21..23, 서쪽): `레일 막대 레일 레일 막대 레일 레일 막대 레일`. 막대 조립기가 양옆 레일 조립기에 막대를 직접 넣습니다.
  - 레일은 y=19로 나가고 두 구간으로 나뉩니다. 서쪽 구간은 위로 올라가 y=6 시작점으로 들어가고(북쪽 레인), 동쪽 구간은 y=6에 옆으로 합칩니다(남쪽 레인).
  - 그래서 레일이 두 레인을 다 씁니다. 후반에는 초당 25개가 필요해서 한 레인으로는 모자랍니다.
- 입력: 레일 줄은 y=25(강철, 돌)와 y=26(철). 전기로는 y=13(강철, 벽돌)과 y=14(빨강 회로). 모듈은 y=13(초록, 빨강 회로).

## 업그레이드

| 단계 | 벨트 | 조립기 | 인서터 | 전봇대 | 타일당 생산 |
|---|---|---|---|---|---|
| 초반 (기본 파일) | 노랑 | 조립기 1 | 일반 | 소형 | 분당 60 |
| 중반 (`variants/mid.txt`) | 빨강 | 조립기 2 | 고속 | 중형 | 분당 90 |
| 후반 (`variants/late.txt`) | 파랑 | 조립기 3 | 벌크 | 중형 | 분당 150 |

- 지하 벨트 간격 3칸 이하, 소형 전봇대 기준 배치.
- 롱암은 기계당 필요량이 초당 1.2개(롱암 기본 속도)보다 충분히 낮은 자리에만 썼습니다. 업그레이드해도 병목이 되지 않습니다.
- 표시 조합기 값은 **후반 기준**입니다: 강철 750 + 500, 돌 750, 철 375, 벽돌 500, 빨강 회로 250 + 250, 초록 회로 250/분.
- 전기로 조립기의 빨강 회로 롱암은 후반에 초당 약 1.04개로 롱암 기본 속도(1.2)에 가깝습니다. 인서터 용량 연구가 있으면 여유가 생깁니다.

## 출처

타일형 과학 아이디어: Christoffer Ramqvist "Tileable Science Production", XtremeZion Science Book, Nilaus Base-In-A-Book 비율 참고. 설계 자체는 이 저장소에서 새로 만든 것입니다.
