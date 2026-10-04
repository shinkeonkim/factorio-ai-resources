# 메인버스 6+2 기본 구간

> 6줄 묶음 3개를 빈칸 2줄로 띄운 가로 버스 구간 (32칸). 줄마다 아이템 표시 조합기 포함.

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base) |
| 크기 | 33×22 타일 |
| 엔티티 | 594 |
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
| `copper-plate` | 900 | (0, 4) |
| `copper-plate` | 900 | (0, 5) |
| `copper-plate` | 900 | (0, 8) |
| `copper-plate` | 900 | (0, 9) |
| `steel-plate` | 900 | (0, 10) |
| `stone-brick` | 900 | (0, 11) |
| `electronic-circuit` | 900 | (0, 12) |
| `electronic-circuit` | 900 | (0, 13) |
| `plastic-bar` | 900 | (0, 16) |
| `advanced-circuit` | 900 | (0, 17) |
| `coal` | 900 | (0, 18) |
| `stone` | 900 | (0, 19) |
| `sulfur` | 900 | (0, 20) |
| `processing-unit` | 900 | (0, 21) |

### 출력

없음

### 파일

| 파일 | 설명 |
|---|---|
| [`blueprint.txt`](blueprint.txt) | 노랑 벨트 (기본) |
| [`variants/red.txt`](variants/red.txt) | 빨강 벨트 |
| [`variants/blue.txt`](variants/blue.txt) | 파랑 벨트 |
| [`variants/turbo.txt`](variants/turbo.txt) | 터보 벨트 |

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

- 버스는 **동쪽으로** 흐르고, 한 묶음 = 6줄, 묶음 사이 = 빈칸 2줄입니다. 3묶음(18줄) 기준 높이 22칸.
- 각 줄 서쪽 끝의 일정 신호 조합기는 **추천 배치** 표시입니다(값 = 그 벨트 한 줄의 분당 용량). 필요에 맞게 신호만 바꾸세요.
  - 1묶음: 철판 ×4, 구리판 ×2
  - 2묶음: 구리판 ×2, 강철, 돌벽돌, 녹색 회로 ×2
  - 3묶음: 플라스틱, 적색 회로, 석탄, 돌, 황, 청색 회로
- 물·원유 같은 유체는 버스에 싣지 않습니다(waterfill로 필요한 곳에 물을 둡니다).

## 업그레이드

업그레이드 플래너로 벨트만 바꾸면 됩니다. 변형 파일(빨강/파랑/터보)은 같은 배치에 벨트만 다른 버전입니다.

자세한 사용법: [메인버스 6+2 가이드](../../docs/guides/main-bus-6x2.md)
