# AAI 창고 자동 조합기

> 조합기 1대가 회로로 레시피를 바꿔 가며 6x6 창고와 로지스틱 창고 5종을 정해진 수량만큼 유지합니다.

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base, aai-containers) |
| 크기 | 7×5 타일 |
| 엔티티 | 11 |
| 주요 설비 | `assembling-machine-2` ×1<br>`requester-chest` ×1<br>`buffer-chest` ×1 |
| 검사 | 통과 |

### 입력

없음

### 출력

| 아이템 | 분당 | 위치 |
|---|---:|---|
| `aai-warehouse` | - | 버퍼 상자 (2개 미만이면 10개까지 채움) |
| `aai-warehouse-passive-provider` | - | 버퍼 상자 (목표 10개) |
| `aai-warehouse-active-provider` | - | 버퍼 상자 (목표 10개) |
| `aai-warehouse-storage` | - | 버퍼 상자 (목표 10개) |
| `aai-warehouse-buffer` | - | 버퍼 상자 (목표 10개) |
| `aai-warehouse-requester` | - | 버퍼 상자 (목표 10개) |

### 로드맵

| 단계 | 시기 / 필요한 연구 | 할 일 |
|---|---|---|
| 0. 연구 | `logistic-system` (빨강·초록·파랑·노랑), `circuit-network` (빨강·초록), `automation-2` (빨강·초록) | 로봇 네트워크(요청·버퍼 상자)와 회로 조합기, AAI 창고 연구. |
| 1. 설치 | - | 로봇 네트워크 안에 붙여 넣고 전기만 연결. 강철판·콘크리트·전자회로·고급회로가 네트워크에 있으면 바로 일반 창고부터 만듭니다. |

**다음에 지을 것**

- [업그레이드형 몰 (쌓는 셀)](../mall-upgradeable/README.md) — 건물 자재를 만드는 다른 몰

### 파일

| 파일 | 설명 |
|---|---|
| [`blueprint.txt`](blueprint.txt) | 기본 |

문자열을 클립보드에 복사한 뒤 게임에서 블루프린트 라이브러리 → 문자열 가져오기:

```sh
pbcopy < blueprints/mall-aai-warehouse/blueprint.txt   # macOS
xclip -selection clipboard < blueprints/mall-aai-warehouse/blueprint.txt   # Linux
```

### 다시 생성

```sh
python3 blueprints/mall-aai-warehouse/generate.py
python3 tools/build.py mall-aai-warehouse
```

<!-- AUTO:END -->

## 구조

```
x: 0 1 2 3 4 5 6
0  A A A . . D Q    A 조합기 2 (빨강선 신호로 레시피 설정)
1  A A A i R D Q    i 고속 투입기   R 요청 상자 (고정 요청, 로봇이 채움)
2  A A A . m . P    m 표시용 정수 조합기 (요청 품목)
3  . o . + . . P    Q 래치 판별 조합기 (신호 L)   P 연산 조합기 L×10 → aai-warehouse
4  . B . K . . .    o 고속 투입기   B 버퍼 상자 (재고)   K 정수 조합기 (로지스틱 창고 목표, 음수)
```

- **요청 상자** 고정 요청 (레시피 2회분): 강철판 400, 콘크리트 200, 전자회로 40, 고급회로 40, aai-warehouse 2.
  "버퍼 상자에서 요청"이 켜져 있어 이 셀이 만든 일반 창고를 그대로 재료로 씁니다.
- **레시피 선택**: 버퍼 상자 재고 + 목표(음수)를 판별 조합기가 읽어 모자란 로지스틱 창고마다 1을 냅니다.
  일반 창고는 래치가 켜져 있으면 10을 냅니다. 조합기는 가장 큰 신호의 레시피를 고르므로 일반 창고가 먼저입니다.
- **래치**: 버퍼의 일반 창고가 2개 미만이면 켜지고 10개가 되면 꺼집니다. 로지스틱 창고를 만들다 일반 창고가
  떨어질 때만 한 번 레시피가 바뀝니다.

## 수량 바꾸기

| 대상 | 위치 | 기본값 |
|---|---|---|
| 로지스틱 창고 5종 | 정수 조합기 K (음수) | 각 -10 |
| 일반 창고 하한 / 상한 | 래치 조합기 Q의 `aai-warehouse < 2` / `< 10` | 2 / 10 |
| 재료 요청량 | 요청 상자 R | 레시피 2회분 |

## 참고

- 모드: AAI Containers & Warehouses. 레시피 — 일반 창고: 강철판 200 + 콘크리트 100,
  로지스틱 창고: 일반 창고 1 + 전자회로 20 + 고급회로 20.
- 로봇 네트워크 안에 설치하고 전기만 연결하면 됩니다. 만든 창고는 버퍼 상자에 있으므로 로봇 건설에 바로 쓰입니다.
- 표시용 정수 조합기(m)의 수량은 분당 소모량이 아니라 요청 상자의 요청량입니다.
- 래치 조건은 `(창고 < 2 [초록]) OR (창고 < 10 [초록] AND L > 0 [빨강])` 입니다. 가져온 뒤 묶음이 다르면 게임에서 이 모양으로 고쳐 주세요.
