# 빨강 과학 (업그레이드형 타일)

> 과학 조립기 10 + 톱니 1. 같은 배치로 분당 60 → 90 → 150. 6+2 버스에서 철·구리 분기 2줄로 입력.

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base) |
| 크기 | 41×16 타일 |
| 엔티티 | 136 |
| 주요 설비 | `assembling-machine-1` ×11 (automation-science-pack 10, iron-gear-wheel 1) |
| 검사 | 통과 |

### 입력

_블루프린트 안의 일정 신호 조합기 표시 (값 = 분당 필요량, 위치 = 블루프린트 왼쪽 위 기준 타일 좌표)_

| 신호 | 분당 | 위치 |
|---|---:|---|
| `iron-plate` | 300 | (0, 15) |
| `copper-plate` | 150 | (9, 15) |

### 출력

| 아이템 | 분당 | 위치 |
|---|---:|---|
| `automation-science-pack` | 60 / 90 / 150 | 과학 벨트 동쪽 끝 (y=0) |

### 파일

| 파일 | 설명 |
|---|---|
| [`blueprint.txt`](blueprint.txt) | 초반 (노랑·조립기 1·일반) |
| [`variants/mid.txt`](variants/mid.txt) | 중반 (빨강·조립기 2·고속) |
| [`variants/late.txt`](variants/late.txt) | 후반 (파랑·조립기 3·벌크) |

문자열을 클립보드에 복사한 뒤 게임에서 블루프린트 라이브러리 → 문자열 가져오기:

```sh
pbcopy < blueprints/science-red-upgradeable/blueprint.txt   # macOS
xclip -selection clipboard < blueprints/science-red-upgradeable/blueprint.txt   # Linux
```

### 다시 생성

```sh
python3 blueprints/science-red-upgradeable/generate.py
python3 tools/build.py science-red-upgradeable
```

<!-- AUTO:END -->

## 구조

- 위: 과학 벨트(y=0, 동쪽으로 나감) ← 출력 인서터 ← 빨강 과학 조립기 10대 ← 입력 인서터 ← 공급 벨트(y=6).
- 공급 벨트: **북쪽 레인 = 톱니바퀴**(서쪽 끝 톱니 조립기가 아래에서 넣음), **남쪽 레인 = 구리판**(구리 분기가 아래에서 옆으로 합류).
- 입력: 아래쪽 끝의 분기 줄 2개(철판 x=-9, 구리판 x=-2). 버스 [분기 조각](../main-bus-6x2-tap/README.md)에서 올라온 벨트를 그대로 잇습니다.
- 비율: 톱니 조립기 1대 = 과학 조립기 10대 분량(티어가 같으면 항상 성립).

## 업그레이드

| 단계 | 벨트 | 조립기 | 인서터 | 전봇대 | 타일당 생산 |
|---|---|---|---|---|---|
| 초반 (기본 파일) | 노랑 | 조립기 1 | 일반 | 소형 | 분당 60 |
| 중반 (`variants/mid.txt`) | 빨강 | 조립기 2 | 고속 | 중형 | 분당 90 |
| 후반 (`variants/late.txt`) | 파랑 | 조립기 3 | 벌크 | 중형 | 분당 150 |

- 지하 벨트 없음, 롱암 없음, 전봇대는 소형 기준 배치라 업그레이드 플래너로 그대로 올라갑니다.
- 표시 조합기 값(철 300, 구리 150/분)은 **후반 기준**입니다. 초반은 약 40%만 필요합니다.
- 톱니 조립기 출력·입력 인서터는 2개씩이라 초반(일반 인서터)에도 병목이 없습니다.

## 출처

타일형 과학 아이디어: Christoffer Ramqvist "Tileable Science Production", XtremeZion Science Book, Nilaus Base-In-A-Book 비율 참고. 설계 자체는 이 저장소에서 새로 만든 것입니다.
