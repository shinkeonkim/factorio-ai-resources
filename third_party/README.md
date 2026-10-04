# third_party

Inputs that are **not redistributed** in this repository (git-ignored). Generators that need them exit
with code 3 ("skipped") when they are missing; the committed `blueprint.txt` files still work.

이 저장소에 포함하지 않는 원본 입력입니다(git 제외). 파일이 없으면 해당 생성기는 건너뜁니다(종료 코드 3).
커밋된 `blueprint.txt`는 그대로 사용할 수 있습니다.

| File / 파일 | Used by / 사용처 | How to get it / 얻는 방법 |
|---|---|---|
| `rail-book.txt` | `rail-buffer-station`, `rail-mining-station`, `rail-smelter-station` | Export the "Rails" blueprint book (contains *Mixed Elev. Cityblock*) from the game and save the string. 게임에서 'Rails' 북을 문자열로 내보내 저장. |
| `empty-block.txt` | `rail-city-block-2x2`, `rail-city-block-3x3` | Export the 182×182 "Empty Block" blueprint string. 182×182 "Empty Block" 블루프린트 문자열. |

```sh
pbpaste > third_party/rail-book.txt      # macOS, right after copying the string in game
python3 skills/factorio-blueprint/scripts/blueprint.py info third_party/rail-book.txt | head
# a mangled character from copy/paste can be fixed with:
python3 skills/factorio-blueprint/scripts/blueprint.py repair third_party/rail-book.txt > fixed.txt
```
