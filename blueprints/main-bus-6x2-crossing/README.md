# 메인버스 6+2 통과 조각

> 아래 묶음에서 올라오는 분기 벨트가 6줄 묶음을 세로로 가로지르게 하는 조각 (6줄 모두 1칸 잠수).

[English](README.en.md)

<!-- AUTO:START (tools/build.py가 생성하는 구역입니다. 직접 수정하지 마세요) -->

![미리보기](images/preview.webp)

<sub>이미지: [Factorio Blueprint Editor](https://fbe.factorygamefan.com)로 렌더링 (게임 그래픽 © Wube Software)</sub>

| 항목 | 값 |
|---|---|
| 게임 | Factorio 2.0 (base) |
| 크기 | 7×9 타일 |
| 엔티티 | 45 |
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
pbcopy < blueprints/main-bus-6x2-crossing/blueprint.txt   # macOS
xclip -selection clipboard < blueprints/main-bus-6x2-crossing/blueprint.txt   # Linux
```

### 다시 생성

```sh
python3 blueprints/main-bus-6x2-crossing/generate.py
python3 tools/build.py main-bus-6x2-crossing
```

<!-- AUTO:END -->

## 구조

- 6줄이 모두 지하 벨트로 한 열 아래를 지나가고, 그 열에 북쪽으로 가는 분기 벨트가 지나갑니다.
- 아래 빈칸 2줄에서 들어와 위쪽으로 나갑니다. 분기를 뺀 묶음과 공장 사이의 모든 묶음에 같은 열로 하나씩 놓습니다.
- 지하 벨트 간격 1칸이라 모든 티어에서 동작합니다.

자세한 사용법: [메인버스 6+2 가이드](../../docs/guides/main-bus-6x2.md)
