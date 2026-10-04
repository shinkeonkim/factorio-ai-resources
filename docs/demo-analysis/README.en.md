# demo-resources analysis

[한국어](README.md)

Nine blueprints collected by the user, analysed in order against this repo's rules (upgrade in place
early → late, 6+2 main bus, Waterfill). The strings themselves are not in the repo (`demo-resources/`
is git-ignored). Images were rendered with Factorio Blueprint Editor by `tools/render_demo.py`.

| # | Resource | Verdict |
|---|---|---|
| 01 | [6×6 load balancer (throughput unlimited)](01-6x6-balancer.en.md) | 6→6 balancer for the bus start; fits the rules as is |
| 02 | [Daiso 1 (vertical mall, red belts)](02-daiso-1.en.md) | vertical mall (80 AM). Underground gaps and long-handed inserters → not upgradeable, redesign |
| 03 | [Daiso 2 (vertical mall, blue belts)](03-daiso-2.en.md) | Daiso 1 rebuilt for another tier — shows why an upgradeable skeleton matters |
| 04 | [Green circuits (Nilaus #6)](04-green-circuits.en.md) | green circuits 3:2; the best-fitting reference module |
| 05 | [Plastic + sulfuric acid (Nilaus #11)](05-plastic-sulfuric.en.md) | oil chain: no machine tiers → build at final size, add modules |
| 06 | [Tileable nuclear reactor](06-nuclear.en.md) | tileable nuclear; growth = tiling, great with Waterfill |
| 07 | [Nilaus' Base-In-A-Book (45 blueprints)](07-nilaus-base-in-a-book.en.md) | different prints per stage; its tap idea became the 6-lane bus kit |
| 08 | [Spaceships book (9 ships)](08-spaceships.en.md) | one hull grown planet → Aquilo → endgame — a good example of the rule |
| 09 | [Science Book (XtremeZion, megabase)](09-science-book-xtremezion.en.md) | late-game-only megabase → rebuilt as upgradeable science lines |

## See also

- [Main bus 6+2 guide](../guides/main-bus-6x2.en.md)
- [Upgrade-in-place rules](../guides/upgrade-in-place.en.md)
- [Recent optimized builds](../references/optimized-builds.en.md)

## Rebuild

```sh
.venv/bin/python tools/render_demo.py          # images + data/*.md (needs demo-resources/)
python3 docs/demo-analysis/_write_pages.py     # these pages
```
