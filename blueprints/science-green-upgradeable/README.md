# 초록 과학 (업그레이드형 타일)

> 과학 조립기 12 + 인서터·벨트·톱니 조립기 4. 같은 배치로 분당 60 → 90 → 150. 버스 분기 3줄(철 2, 녹색 회로).

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base) |
| 크기 | 53×16 타일 |
| 엔티티 | 195 |
| 주요 설비 | `assembling-machine-1` ×16 (logistic-science-pack 12, iron-gear-wheel 2, transport-belt 1, inserter 1) |
| 검사 | 통과 |

### 입력

_블루프린트 안의 일정 신호 조합기 표시 (값 = 분당 필요량, 위치 = 블루프린트 왼쪽 위 기준 타일 좌표)_

| 신호 | 분당 | 위치 |
|---|---:|---|
| `iron-plate` | 450 | (2, 15) |
| `electronic-circuit` | 150 | (0, 15) |
| `iron-plate` | 225 | (5, 15) |

### 출력

| 아이템 | 분당 | 위치 |
|---|---:|---|
| `logistic-science-pack` | 60 / 90 / 150 | 과학 벨트 동쪽 끝 (y=0) |

### 파일

| 파일 | 설명 |
|---|---|
| [`blueprint.txt`](blueprint.txt) | 초반 (노랑·조립기 1·일반) |
| [`variants/mid.txt`](variants/mid.txt) | 중반 (빨강·조립기 2·고속) |
| [`variants/late.txt`](variants/late.txt) | 후반 (파랑·조립기 3·벌크) |

문자열을 클립보드에 복사한 뒤 게임에서 블루프린트 라이브러리 → 문자열 가져오기:

```sh
pbcopy < blueprints/science-green-upgradeable/blueprint.txt   # macOS
xclip -selection clipboard < blueprints/science-green-upgradeable/blueprint.txt   # Linux
```

### 다시 생성

```sh
python3 blueprints/science-green-upgradeable/generate.py
python3 tools/build.py science-green-upgradeable
```

<!-- AUTO:END -->

## 구조

- 위: 과학 벨트(y=0) ← 초록 과학 조립기 12대 ← 공급 벨트(y=6).
- 공급 벨트: **북쪽 레인 = 인서터**, **남쪽 레인 = 벨트**. 서쪽 끝의 두 무리가 서로 반대쪽에서 넣어서 레인이 저절로 나뉩니다.
  - 북쪽 무리(y=2..4): 톱니 B → (옆으로) 벨트 조립기 → 공급 벨트 남쪽 레인. 철은 y=0의 짧은 벨트에서.
  - 남쪽 무리(y=8..10): 톱니 A → (옆으로) 인서터 조립기 → 공급 벨트 북쪽 레인. 철·녹색 회로는 y=12 벨트(두 레인)에서.
- 입력: 아래쪽 끝 분기 줄 3개 — 녹색 회로(x=-15), 철판 A(x=-13), 철판 B(x=-12, 지하 1칸으로 y=12 벨트를 건너 북쪽 무리로).
- 비율: 초록 과학 12 : 인서터 1 : 벨트 1 : 톱니 2 (톱니 A는 인서터용 1:1, 톱니 B는 벨트용).

## 업그레이드

| 단계 | 벨트 | 조립기 | 인서터 | 전봇대 | 타일당 생산 |
|---|---|---|---|---|---|
| 초반 (기본 파일) | 노랑 | 조립기 1 | 일반 | 소형 | 분당 60 |
| 중반 (`variants/mid.txt`) | 빨강 | 조립기 2 | 고속 | 중형 | 분당 90 |
| 후반 (`variants/late.txt`) | 파랑 | 조립기 3 | 벌크 | 중형 | 분당 150 |

- 지하 벨트 간격 1칸, 롱암 없음, 소형 전봇대 기준 배치.
- 표시 조합기 값(철 A 450, 철 B 225, 녹색 회로 150/분)은 **후반 기준**입니다.
- 인서터 조립기 출력은 인서터 1개라 초반(일반 인서터 0.83/s)엔 과학이 약 80%로 돕니다. 중반부터 여유가 있습니다.

## 출처

타일형 과학 아이디어: Christoffer Ramqvist "Tileable Science Production", XtremeZion Science Book, Nilaus Base-In-A-Book 비율 참고. 설계 자체는 이 저장소에서 새로 만든 것입니다.
