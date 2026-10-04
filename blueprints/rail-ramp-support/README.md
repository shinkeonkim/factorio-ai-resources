# 철도 경사로·지지대 공장

> 철광석·돌·정제 콘크리트로 철도 경사로와 지지대를 만드는 소형 공장 (강철 병목).

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base, space-age) |
| 크기 | 46×15 타일 |
| 엔티티 | 211 |
| 주요 설비 | `electric-furnace` ×12<br>`assembling-machine-2` ×4 (iron-stick 1, rail 1, rail-ramp 1, rail-support 1)<br>`steel-chest` ×2 |
| 검사 | 통과 |

### 입력

_블루프린트 안의 일정 신호 조합기 표시 (값 = 분당 필요량, 위치 = 블루프린트 왼쪽 위 기준 타일 좌표)_

| 신호 | 분당 | 위치 |
|---|---:|---|
| `iron-ore` | 225 | (2, 1) |
| `stone` | 4 | (0, 6) |
| `refined-concrete` | 160 | (2, 14) |

### 출력

| 아이템 | 분당 | 위치 |
|---|---:|---|
| `rail-ramp` | ~1 | 상자 (2칸 제한) |
| `rail-support` | ~3 | 상자 (2칸 제한) |

### 파일

| 파일 | 설명 |
|---|---|
| [`blueprint.txt`](blueprint.txt) | 기본 |

문자열을 클립보드에 복사한 뒤 게임에서 블루프린트 라이브러리 → 문자열 가져오기:

```sh
pbcopy < blueprints/rail-ramp-support/blueprint.txt   # macOS
xclip -selection clipboard < blueprints/rail-ramp-support/blueprint.txt   # Linux
```

### 다시 생성

```sh
python3 blueprints/rail-ramp-support/generate.py
python3 tools/build.py rail-ramp-support
```

<!-- AUTO:END -->

{'ko': '## 구조\n\n- 철 용광로 6 → 철판 벨트(남쪽 레인, 돌은 북쪽 레인) → 강철 용광로 6 → 강철 벨트.\n- 철 막대 → 레일 → 경사로 조립기는 옆으로 바로 넣고, 지지대 조립기는 따로 있습니다.\n- 경사로 쪽이 강철을 먼저 가져가므로 두 상자를 2칸으로 제한해 강철이 지지대 쪽으로도 넘어가게 했습니다.\n\n## 참고\n\n- Space Age(고가 철도)가 필요합니다. 생산량을 늘리려면 `generate.py`의 `range(6)` 두 곳을 같이 늘리세요.\n', 'en': '## Layout\n\n- 6 iron furnaces → plate belt (south lane; stone on the north lane) → 6 steel furnaces → steel belt.\n- Stick → rail → ramp assemblers insert directly into each other; the support assembler is separate.\n- The ramp assembler takes steel first, so both chests are limited to 2 slots to let steel reach the supports.\n\n## Notes\n\n- Requires Space Age (elevated rails). Scale up by raising both `range(6)` in `generate.py`.\n'}