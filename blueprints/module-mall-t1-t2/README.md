# 모듈 몰 (1·2단계, 4종)

> 속도·효율·생산성·품질 모듈 1·2단계를 메인버스의 녹/적/청 회로로 만들어 상자에 쌓는 몰.

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base, quality) |
| 크기 | 52×9 타일 |
| 엔티티 | 193 |
| 주요 설비 | `assembling-machine-3` ×12 (speed-module 2, efficiency-module 2, productivity-module 2, quality-module 2, speed-module-2 1, efficiency-module-2 1, productivity-module-2 1, quality-module-2 1)<br>`steel-chest` ×12 |
| 검사 | 통과 |

### 입력

_블루프린트 안의 일정 신호 조합기 표시 (값 = 분당 필요량, 위치 = 블루프린트 왼쪽 위 기준 타일 좌표)_

| 신호 | 분당 | 위치 |
|---|---:|---|
| `electronic-circuit` | 200 | (0, 1) |
| `processing-unit` | 50 | (0, 3) |
| `advanced-circuit` | 250 | (0, 5) |

### 출력

| 아이템 | 분당 | 위치 |
|---|---:|---|
| `*-module / *-module-2` | 2.5 (T2) | 조립기 아래 강철 상자 |

### 파일

| 파일 | 설명 |
|---|---|
| [`blueprint.txt`](blueprint.txt) | 기본 |

문자열을 클립보드에 복사한 뒤 게임에서 블루프린트 라이브러리 → 문자열 가져오기:

```sh
pbcopy < blueprints/module-mall-t1-t2/blueprint.txt   # macOS
xclip -selection clipboard < blueprints/module-mall-t1-t2/blueprint.txt   # Linux
```

### 다시 생성

```sh
python3 blueprints/module-mall-t1-t2/generate.py
python3 tools/build.py module-mall-t1-t2
```

<!-- AUTO:END -->

{'ko': '## 구조\n\n- 모듈 종류마다 [1단계 · 2단계 · 1단계] 조립기 3 세 대. 2단계 1대가 1단계를 분당 10개 쓰고 1단계 1대는 5개를 만들어서, 1단계 2대가 가운데 2단계에 옆으로 바로 넣습니다.\n- 녹색 회로(북쪽 레인)와 청색 회로(남쪽 레인)는 블루프린트 안에서 한 벨트로 합쳐집니다. 버스에서 벨트를 따로 끌어오면 됩니다.\n- 1단계 상자는 1칸(50개), 2단계 상자는 2칸으로 제한해 남는 것만 쌓입니다.\n\n## 참고\n\n- Quality 모드가 필요합니다. 3단계는 Space Age 재료가 필요해 제외했습니다.\n- 더 많이 만들려면 `generate.py`의 `TYPES`에 종류를 반복해 넣으세요.\n', 'en': '## Layout\n\n- One [T1 · T2 · T1] group of assembling machine 3 per module kind. A T2 assembler eats 10 T1/min and a T1 makes 5/min, so two T1 feed the middle T2 sideways.\n- Green circuits (north lane) and processing units (south lane) are merged onto one belt inside the blueprint; bring them from the bus separately.\n- T1 chests are limited to 1 slot (50), T2 chests to 2 slots, so only surplus accumulates.\n\n## Notes\n\n- Requires the Quality mod. Tier 3 was left out because it needs Space Age ingredients.\n- Repeat a kind in `TYPES` in `generate.py` for more output.\n'}