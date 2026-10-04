# CLAUDE.md — working in factorio-ai-resources

- Design work uses the `factorio-blueprint` skill in `skills/factorio-blueprint/` (installed into
  `~/.claude/skills` by `scripts/install-skills.sh` as a symlink, so edits here are live).
- New blueprint → `python3 tools/new_blueprint.py <id> --title-ko … --title-en …`, write `generate.py`
  using `from lib.fbp import *` and `save(bp, __file__)`, then `python3 tools/build.py <id>`.
- Every external input gets a constant-combinator marker (`bp.add_marker`), count = per minute.
- Write both `README.md` (Korean) and `README.en.md` (English); keep prose outside the AUTO block.
- Shared generator code goes to `lib/`; never commit anything under `third_party/` except its README.
- Rail city-block stations: take rail geometry from the user's book (`third_party/rail-book.txt` via
  `lib/rail_city_block.py`); do not invent rail positions.
- Before committing: `.venv/bin/python tools/build.py --regen` (renders game-sprite previews via FBE; needs
  `pip install -r tools/requirements.txt` + `playwright install chromium`) and make sure validation passes.
