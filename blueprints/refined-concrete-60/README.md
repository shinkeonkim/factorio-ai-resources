# 정제 콘크리트 60/분

> 돌·철광석·물로 정제 콘크리트를 분당 60개 만드는 소형 공장. 입출력은 모두 서쪽 끝.

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base) |
| 크기 | 38×20 타일 |
| 엔티티 | 278 |
| 주요 설비 | `assembling-machine-2` ×6 (concrete 3, refined-concrete 2, iron-stick 1)<br>`electric-furnace` ×5 |
| 검사 | 통과 |

### 입력

_블루프린트 안의 일정 신호 조합기 표시 (값 = 분당 필요량, 위치 = 블루프린트 왼쪽 위 기준 타일 좌표)_

| 신호 | 분당 | 위치 |
|---|---:|---|
| `water` (fluid) | 1,800 | (0, 0) |
| `iron-ore` | 66 | (0, 2) |
| `stone` | 120 | (0, 5) |

### 출력

| 아이템 | 분당 | 위치 |
|---|---:|---|
| `refined-concrete` | 60 | 서쪽 끝 아래쪽 벨트 (서쪽으로 나감) |

### 파일

| 파일 | 설명 |
|---|---|
| [`blueprint.txt`](blueprint.txt) | 기본 |

문자열을 클립보드에 복사한 뒤 게임에서 블루프린트 라이브러리 → 문자열 가져오기:

```sh
pbcopy < blueprints/refined-concrete-60/blueprint.txt   # macOS
xclip -selection clipboard < blueprints/refined-concrete-60/blueprint.txt   # Linux
```

### 다시 생성

```sh
python3 blueprints/refined-concrete-60/generate.py
python3 tools/build.py refined-concrete-60
```

<!-- AUTO:END -->

{'ko': '## 구조\n\n- 위 줄: 철 용광로 2 · [콘크리트 조립기 · 벽돌 용광로] 교대 배치. 벽돌 용광로가 양옆 조립기에 벽돌을 바로 넣습니다.\n- 가운데 벨트 2줄: 콘크리트(남쪽 레인) + 철 막대(북쪽 레인), 철판(남쪽 레인) + 강철(북쪽 레인).\n- 아래 줄: 강철 용광로 · 철 막대 조립기 · 정제 콘크리트 조립기 2.\n- 물은 위쪽 파이프로 들어와 오른쪽 끝에서 아래 물 라인으로 내려갑니다. 조립기에는 지하 파이프로 연결됩니다.\n\n## 참고\n\n- 고속 벨트(빨강), 전기 용광로, 조립기 2, 고속 로봇팔. 2칸 떨어진 벨트를 집는 곳만 롱암입니다.\n- 외부 전력은 아무 전봇대에나 연결하세요.\n', 'en': '## Layout\n\n- Top row: 2 iron furnaces, then alternating [concrete assembler · brick furnace]; each brick furnace inserts directly into both neighbours.\n- Two middle belts: concrete (south lane) + iron sticks (north lane), iron plates (south lane) + steel (north lane).\n- Bottom row: steel furnace, stick assembler, 2 refined-concrete assemblers.\n- Water enters on the top pipe and returns along the east edge to the bottom main; machines connect via pipe-to-ground.\n\n## Notes\n\n- Fast belts, electric furnaces, assembling machine 2, fast inserters; long-handed only where a 2-tile reach is needed.\n- Connect external power to any pole.\n'}