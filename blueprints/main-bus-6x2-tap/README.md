# 메인버스 6+2 분기 조각

> 6줄 묶음의 한 줄을 북쪽으로 빼는 조각: 벨트 줄 0~5 × 전부/반 12종 + 유체 줄 0~5 6종.

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base) |
| 크기 | 7×8 타일 |
| 엔티티 | 41 |
| 주요 설비 | - |
| 검사 | 통과 |

### 입력

없음

### 출력

없음

### 로드맵

| 단계 | 시기 / 필요한 연구 | 할 일 |
|---|---|---|
| 1. 분기 자리 정하기 | `logistics` (빨강) | 공장 타일 아래쪽 표시 조합기의 x 위치에 맞춰 분기 조각을 버스 위에 겹쳐 놓습니다. 위 묶음 줄들이 1-2칸 잠수해서 빈 2줄로 분기가 올라옵니다. |
| 2. Full / Half | - | 공장이 그 줄을 다 먹으면 Full, 다른 공장과 나눠 쓰면 Half(분배기로 절반). 초반엔 Half로 시작해서 공장이 커지면 Full 조각으로 갈아끼웁니다. |
| 3. 유체 분기 | `steam-power` (아이템을 처음 만들면) | 6번 묶음 유체 줄은 `fluid-line*.txt`. 지하 파이프가 구간 안에서 올라와 빈 줄까지 올라옵니다. 같은 x에 고체 분기와 겹치지 않게 1칸 비켜 놓으세요. |
| 4. 업그레이드 | `logistics-2` (빨강·초록), `logistics-3` (빨강·초록·파랑·보라) | 버스와 함께 업그레이드 플래너로 바꿉니다. 잠수 간격이 1-2칸이라 노랑부터 터보까지 같은 조각입니다. |

**다음에 지을 것**

- [메인버스 6+2 통과 조각](../main-bus-6x2-crossing/README.md) — 분기가 다른 묶음을 지나가야 할 때
- [빨강 과학 (쌓는 셀)](../science-red-upgradeable/README.md) — 분기 2개로 시작하는 공장

### 파일

| 파일 | 설명 |
|---|---|
| [`blueprint.txt`](blueprint.txt) | 전부 · 줄 0 (기본) |
| [`variants/full-lane1.txt`](variants/full-lane1.txt) | 전부 · 줄 1 |
| [`variants/full-lane2.txt`](variants/full-lane2.txt) | 전부 · 줄 2 |
| [`variants/full-lane3.txt`](variants/full-lane3.txt) | 전부 · 줄 3 |
| [`variants/full-lane4.txt`](variants/full-lane4.txt) | 전부 · 줄 4 |
| [`variants/full-lane5.txt`](variants/full-lane5.txt) | 전부 · 줄 5 |
| [`variants/half-lane0.txt`](variants/half-lane0.txt) | 반 · 줄 0 |
| [`variants/half-lane1.txt`](variants/half-lane1.txt) | 반 · 줄 1 |
| [`variants/half-lane2.txt`](variants/half-lane2.txt) | 반 · 줄 2 |
| [`variants/half-lane3.txt`](variants/half-lane3.txt) | 반 · 줄 3 |
| [`variants/half-lane4.txt`](variants/half-lane4.txt) | 반 · 줄 4 |
| [`variants/half-lane5.txt`](variants/half-lane5.txt) | 반 · 줄 5 |
| [`variants/fluid-line0.txt`](variants/fluid-line0.txt) | 유체 · 줄 0 |
| [`variants/fluid-line1.txt`](variants/fluid-line1.txt) | 유체 · 줄 1 |
| [`variants/fluid-line2.txt`](variants/fluid-line2.txt) | 유체 · 줄 2 |
| [`variants/fluid-line3.txt`](variants/fluid-line3.txt) | 유체 · 줄 3 |
| [`variants/fluid-line4.txt`](variants/fluid-line4.txt) | 유체 · 줄 4 |
| [`variants/fluid-line5.txt`](variants/fluid-line5.txt) | 유체 · 줄 5 |

문자열을 클립보드에 복사한 뒤 게임에서 블루프린트 라이브러리 → 문자열 가져오기:

```sh
pbcopy < blueprints/main-bus-6x2-tap/blueprint.txt   # macOS
xclip -selection clipboard < blueprints/main-bus-6x2-tap/blueprint.txt   # Linux
```

### 다시 생성

```sh
python3 blueprints/main-bus-6x2-tap/generate.py
python3 tools/build.py main-bus-6x2-tap
```

<!-- AUTO:END -->

## 구조

- 줄 번호는 묶음 안에서 위에서부터 0~5입니다. 분기는 묶음 위(북쪽)로 나갑니다.
- **전부(full)**: 그 줄이 북쪽으로 꺾이고 거기서 끝납니다. 그 위 줄들은 지하 벨트로 1칸 아래를 지나갑니다.
- **반(half)**: 스플리터가 절반을 북쪽으로 보내고 나머지는 계속 동쪽으로 갑니다. 위 줄들은 2칸 아래를 지나갑니다.
- 지하 벨트 간격이 최대 2칸이라 **노랑 지하 벨트(최대 4칸)로도 동작**하고, 업그레이드해도 배치가 그대로입니다.
- 기존 버스 구간 위에 '강제 건설(Shift+클릭)'로 덮어 놓으면 직선 벨트가 교체됩니다.
- 아래쪽 묶음에서 뺀 분기는 위쪽 묶음마다 [통과 조각](../main-bus-6x2-crossing/README.md)을 같은 열에 놓아 올립니다.

## 유체 분기

- `variants/fluid-line*.txt`: 유체 묶음의 한 줄을 사슬 중간에서 지상으로 올리고(지하 파이프 쌍 사이 **2~8칸 지점**에 강제 건설), 지하 파이프로 묶음 위 빈칸까지 올립니다.
- 그 위 묶음들은 [통과 조각](../main-bus-6x2-crossing/README.md)의 `fluid` 변형을 같은 열에 쌓아 올립니다.

자세한 사용법: [메인버스 6+2 가이드](../../docs/guides/main-bus-6x2.md)
