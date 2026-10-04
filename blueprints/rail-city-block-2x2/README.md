# 철도 시티블럭 2×2

> 182칸 빈 철도 블럭을 2×2로 확장 (364칸 그리드, 경계 거리 병합).

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base, space-age) |
| 크기 | 466×465 타일 |
| 엔티티 | 4515 |
| 주요 설비 | - |
| 검사 | 통과 |

### 입력

없음

### 출력

없음

### 파일

| 파일 | 설명 |
|---|---|
| [`blueprint.txt`](blueprint.txt) | 기본 |

문자열을 클립보드에 복사한 뒤 게임에서 블루프린트 라이브러리 → 문자열 가져오기:

```sh
pbcopy < blueprints/rail-city-block-2x2/blueprint.txt   # macOS
xclip -selection clipboard < blueprints/rail-city-block-2x2/blueprint.txt   # Linux
```

### 다시 생성

```sh
python3 blueprints/rail-city-block-2x2/generate.py
python3 tools/build.py rail-city-block-2x2
```

필요한 원본 (저장소에 포함되지 않음): `third_party/empty-block.txt`

<!-- AUTO:END -->

{'ko': '## 구조\n\n- 원본 Empty Block(절대 스냅 182×182, 기준점 (-8,-22))을 182칸씩 복제하고, 맞닿는 블럭이 공유하는 경계 거리 엔티티는 하나로 합쳤습니다.\n- 스냅 그리드만 364로 바뀌고 기준점은 같아서, 기존 1×1 블럭과 같은 격자에 찍힙니다.\n- 같은 칸에 방향이 다른 레일이 겹치는 곳은 원본 교차로의 교차·분기 레일입니다.\n', 'en': '## Layout\n\n- The original Empty Block (absolute snapping 182×182, offset (-8,-22)) is copied every 182 tiles; entities on shared border streets are merged.\n- Only the snap grid changes (364); the offset is unchanged, so it lands on the same grid as 1×1 blocks.\n- Rails stacked on one tile with different directions are the original junction crossings/switches.\n'}
## 출처

레일·정거장·신호 배치는 사용자가 제공한 철도 블루프린트 북('Rails' 북의 **Mixed Elev. Cityblock**, 원작자 미상)을 그대로 사용합니다. 이 저장소에는 원본 북이 들어 있지 않으며, 생성기를 돌리려면 `third_party/`에 원본을 두어야 합니다.
