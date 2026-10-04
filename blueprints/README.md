# blueprints/

블루프린트마다 폴더 하나 / one folder per blueprint:

```
blueprints/<id>/
├── meta.json        # 직접 작성: 제목·요약(ko/en), 게임/모드, 태그, 출력, 변형, 필요한 원본, 출처, 이미지
├── generate.py      # 선택: blueprint.txt (+ variants/*.txt)를 만드는 스크립트
├── blueprint.txt    # 블루프린트 문자열 (게임에서 '문자열 가져오기')
├── variants/        # 선택: 다른 아이템용 변형
├── README.md        # 한국어 문서
├── README.en.md     # English doc
└── images/
    ├── preview.png  # 자동 생성 (tools/build.py)
    ├── detail.png   # 자동 생성: 큰 철도 블럭에서 설비 부분만 확대
    └── *.png        # tools/attach_image.py 로 첨부한 스크린샷
```

## meta.json

| key | 필수 | 설명 / description |
|---|---|---|
| `id` | ✓ | folder name |
| `title`, `summary` | ✓ | `{"ko": ..., "en": ...}` |
| `game`, `mods` | ✓ | `"2.0"`, `["base", "quality", "space-age"]` |
| `tags`, `order` | | catalog tags / sort order |
| `outputs`, `inputs` | | `[{"item", "per_minute", "where": {"ko","en"}}]` — `inputs` only when the blueprint has no constant-combinator markers (e.g. train-fed stations) |
| `variants`, `default_label` | | extra blueprint files and their labels |
| `requires` | | files in `third_party/` the generator needs |
| `credits` | | `{"ko","en"}` text for third-party material |
| `images` | | managed by `tools/attach_image.py` |
| `allow_problems` | | `true` to publish despite validation warnings (explain why in the README) |

## README

`<!-- AUTO:START ... -->` ~ `<!-- AUTO:END -->` 구간은 `tools/build.py`가 다시 씁니다 (미리보기, 크기·설비 표,
입력/출력 표, 파일 목록, 재생성 방법, 갤러리). 설명은 그 바깥에 쓰세요. The AUTO block is regenerated; write prose outside it.
