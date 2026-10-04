# demo-resources 분석

[English](README.en.md)

사용자가 모은 블루프린트 9개를 이번 규칙(같은 구조로 초·중·후반 업그레이드, 6+2 메인버스, waterfill)에
비추어 순서대로 분석했습니다. 원본 문자열은 저장소에 포함하지 않습니다(`demo-resources/`는 git 제외).
이미지는 `tools/render_demo.py`가 Factorio Blueprint Editor로 렌더링한 것입니다.

| # | 자료 | 한 줄 평가 |
|---|---|---|
| 01 | [6×6 로드밸런서 (처리량 무제한)](01-6x6-balancer.md) | 버스 시작점용 6→6 밸런서. 규칙에 그대로 맞음 |
| 02 | [다이소 1 (세로형 몰, 빨강 벨트)](02-daiso-1.md) | 세로형 몰(조립기 80). 지하 간격·롱암 때문에 업그레이드형 아님 → 재설계 대상 |
| 03 | [다이소 2 (세로형 몰, 파랑 벨트)](03-daiso-2.md) | 다이소 1을 다른 티어로 다시 만든 판 — 업그레이드형 골격의 필요성을 보여 줌 |
| 04 | [녹색 회로 (Nilaus #6)](04-green-circuits.md) | 녹색 회로 3:2. 규칙에 가장 잘 맞는 기준 모듈 |
| 05 | [플라스틱 + 황산 (Nilaus #11)](05-plastic-sulfuric.md) | 석유 계열: 기계 티어 없음 → 최종 크기로 짓고 모듈 추가 |
| 06 | [타일형 원자력 발전소](06-nuclear.md) | 타일형 원자력. 확장=이어 붙이기, waterfill과 궁합 좋음 |
| 07 | [Nilaus' Base-In-A-Book (45개)](07-nilaus-base-in-a-book.md) | 단계별 다른 블루프린트. 버스 분기 아이디어를 6줄 키트로 옮김 |
| 08 | [우주선 북 (9척)](08-spaceships.md) | 같은 선체를 행성→Aquilo→Endgame으로 확장 — 규칙의 좋은 예 |
| 09 | [Science Book (XtremeZion, 메가베이스)](09-science-book-xtremezion.md) | 후반 전용 메가베이스 → 업그레이드형 과학 라인으로 재설계 |

## 함께 보기

- [메인버스 6+2 가이드](../guides/main-bus-6x2.md)
- [업그레이드형 설계 원칙](../guides/upgrade-in-place.md)
- [최근 최적화 설계 참고 자료](../references/optimized-builds.md)

## 다시 만들기

```sh
.venv/bin/python tools/render_demo.py          # 이미지 + data/*.md (demo-resources/ 필요)
python3 docs/demo-analysis/_write_pages.py     # 이 문서들
```
