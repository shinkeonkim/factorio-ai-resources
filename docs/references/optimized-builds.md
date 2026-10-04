# 최근 최적화 설계 참고 자료 (2.0 / Space Age)

[English](optimized-builds.en.md)

demo-resources에 없는 영역을 보강하기 위해 조사한 커뮤니티 설계와 핵심 아이디어입니다(2026년 10월 기준).
링크는 원작자 페이지이며, 이 저장소의 업그레이드형 설계에 반영한 아이디어는 ✅로 표시했습니다.

## 초·중반 기반 (Nauvis)

| 자료 | 핵심 아이디어 | 반영 |
|---|---|---|
| [Tileable Science Production 1.0–2.0 (Christoffer Ramqvist)](https://factorioprints.com/view/-KnQ865j-qQ21WoUPbd3) | 과학팩마다 타일 하나, 노랑→빨강→파랑으로 **같은 배치를 업그레이드**. 권장 타일 비율 빨강 1 : 초록 1 : 파랑 2 : 군사 2 : 보라 2 : 노랑 2 | ✅ 업그레이드형 과학 라인 원칙 |
| Nilaus Base-In-A-Book (데모 07) | 4줄 버스 + Full/Half line 분기 조각, 몰(쇼핑센터) 분리 | ✅ 분기 조각 방식 |
| [Main bus 가이드 (factoriocalculator.blog)](https://factoriocalculator.blog/factorio-main-bus/) | 묶음 사이 2칸, 분기 사이 4~6칸, 전체 줄을 통째로 빼지 말 것 | ✅ 6+2 가이드 |

## Space Age 행성별

| 행성 | 자료 | 핵심 아이디어 |
|---|---|---|
| Vulcanus | [Smelting by Foundries](https://factorioprints.com/view/-OBi8Zr6ZQ7mOehtFN0Z), [Compact Molten Iron/Copper](https://factorioprints.com/view/-OAiUZYupH8fEb0985qF), [Foundry 위키](https://wiki.factorio.com/Foundry) | 용암 + 방해석 → 용융 금속 → 파운드리 주조(속도 4, +50% 생산성). **부산물 돌의 배출구**가 없으면 전체가 멈춤 |
| Fulgora | [Scrap Products Recycling](https://www.factorio.school/view/-OMrlOg3wjmlptdGZa7S), [Fulgora 재활용 가이드](https://factorioguides.com/space-age/fulgora/fulgora-recycling-guide/) | 고철 12종을 모두 분리, 희귀품(홀뮴·얼음)은 소비처로, 남는 것은 버퍼/재활용기로 **넘침 배출** |
| Gleba | [Gleba Modules: Science 360/min](https://www.factorio.school/view/-OXYYEf0Deceo7XUfVjR), [Agricultural Science](https://factorioprints.com/view/-OAjxHVkwRp6DeQBzEeX) | 버퍼를 두지 않는 흐름, **부패물 전용 회수 벨트**, 바이오플럭스 중심 |
| Aquilo / 우주 | [Promethium Platform (Normal quality)](https://www.factoriocodex.com/blueprints/283), [Moonscar 연구선](https://www.factoriocodex.com/blueprints/63), [포럼: 비-품질 프로메튬 선 설계 원칙](https://forums.factorio.com/viewtopic.php?t=132851) | 앞이 넓은 역쐐기형 선체, 허브는 최대한 뒤쪽, 소행성 처리 10 / 로켓 12 연구 이후 |
| 전자 | [ALL THE CIRCUITS](https://www.factorio.school/view/-OMwsTvG3zRe6tQO1qbU), [EM plant 녹색 회로 60/s](https://factoriobin.com/post/uxmzyt) | EM 플랜트(속도 2, +50% 생산성, 모듈 5칸)로 전선→회로 직접 삽입 |

## 품질

| 자료 | 핵심 아이디어 |
|---|---|
| [Recycle to Legendary](https://factorioprints.com/view/-OAUx9oAYc-E3JyivkvG), [Quality Casino Cycler (파라미터)](https://www.factorio.school/view/-OAOJZRaFp0U8hy2mnNs), [Steam: Guide to Legendary Quality](https://steamcommunity.com/sharedfiles/filedetails/?id=3394020732) | 만들기 ↔ 재활용 루프. 품질 모듈 3 기준 1단계 상승 약 10%씩. EM 플랜트로 최종 제품도 생산성 적용 |

## 이 저장소에 반영할 순서 (계획)

1. 업그레이드형 과학 라인 — ✅ [빨강](../../blueprints/science-red-upgradeable/README.md)·[초록](../../blueprints/science-green-upgradeable/README.md) 완료, 군사·파랑·보라·노랑 진행 예정 — 데모 09(XtremeZion)·07(Nilaus) 아이디어를 6+2 버스 기준으로 재설계
2. 업그레이드형 몰(다이소) — 데모 02·03 분석 기반
3. Space Age 행성 블럭은 위 링크의 원칙을 따라 별도 진행
