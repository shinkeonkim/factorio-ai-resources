# 파랑 과학 (업그레이드형 타일)

> 과학 조립기 24 (두 줄). 같은 배치로 분당 60 → 90 → 150. 버스 분기 3줄(엔진, 빨강 회로, 황).

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base) |
| 크기 | 50×18 타일 |
| 엔티티 | 336 |
| 주요 설비 | `assembling-machine-1` ×24 (chemical-science-pack 24) |
| 검사 | 통과 |

### 입력

_블루프린트 안의 일정 신호 조합기 표시 (값 = 분당 필요량, 위치 = 블루프린트 왼쪽 위 기준 타일 좌표)_

| 신호 | 분당 | 위치 |
|---|---:|---|
| `advanced-circuit` | 225 | (2, 17) |
| `engine-unit` | 150 | (0, 17) |
| `sulfur` | 75 | (7, 17) |

### 출력

| 아이템 | 분당 | 위치 |
|---|---:|---|
| `chemical-science-pack` | 60 / 90 / 150 | 과학 벨트 동쪽 끝 (y=0) |

### 파일

| 파일 | 설명 |
|---|---|
| [`blueprint.txt`](blueprint.txt) | 초반 (노랑·조립기 1·일반) |
| [`variants/mid.txt`](variants/mid.txt) | 중반 (빨강·조립기 2·고속) |
| [`variants/late.txt`](variants/late.txt) | 후반 (파랑·조립기 3·벌크) |

문자열을 클립보드에 복사한 뒤 게임에서 블루프린트 라이브러리 → 문자열 가져오기:

```sh
pbcopy < blueprints/science-blue-upgradeable/blueprint.txt   # macOS
xclip -selection clipboard < blueprints/science-blue-upgradeable/blueprint.txt   # Linux
```

### 다시 생성

```sh
python3 blueprints/science-blue-upgradeable/generate.py
python3 tools/build.py science-blue-upgradeable
```

<!-- AUTO:END -->

## 구조

- 조립기 두 줄(12 + 12)이 가운데 벨트 두 개를 같이 씁니다.
  - y=6: 북쪽 레인 엔진, 남쪽 레인 빨강 회로. 윗줄은 고속으로, 아랫줄은 롱암으로 꺼냅니다.
  - y=7: 황. 윗줄은 롱암으로, 아랫줄은 고속으로 꺼냅니다.
- 출력: 윗줄은 y=0, 아랫줄은 y=13. y=13은 동쪽 끝(x=37)에서 위로 올라가 y=0 남쪽 레인에 옆으로 합칩니다.
- 엔진·빨강 회로·황은 모두 버스에서 받습니다. 엔진은 [버스 6+2](../../docs/guides/main-bus-6x2.md)의 5번 묶음에 있습니다.

## 업그레이드

| 단계 | 벨트 | 조립기 | 인서터 | 전봇대 | 타일당 생산 |
|---|---|---|---|---|---|
| 초반 (기본 파일) | 노랑 | 조립기 1 | 일반 | 소형 | 분당 60 |
| 중반 (`variants/mid.txt`) | 빨강 | 조립기 2 | 고속 | 중형 | 분당 90 |
| 후반 (`variants/late.txt`) | 파랑 | 조립기 3 | 벌크 | 중형 | 분당 150 |

- 지하 벨트 간격 3칸 이하, 소형 전봇대 기준 배치.
- 롱암은 기계당 필요량이 초당 1.2개(롱암 기본 속도)보다 충분히 낮은 자리에만 썼습니다. 업그레이드해도 병목이 되지 않습니다.
- 표시 조합기 값은 **후반 기준**입니다: 엔진 150, 빨강 회로 225, 황 75/분.

## 출처

타일형 과학 아이디어: Christoffer Ramqvist "Tileable Science Production", XtremeZion Science Book, Nilaus Base-In-A-Book 비율 참고. 설계 자체는 이 저장소에서 새로 만든 것입니다.
