#!/usr/bin/env bash
# Install the skills in ./skills into Claude Code's skills directory.
#
#   scripts/install-skills.sh            # symlink (edits in this repo apply immediately)
#   scripts/install-skills.sh --copy     # copy instead of symlink
#   scripts/install-skills.sh --target ./.claude/skills   # project-level install
#
# An existing skill with the same name is moved to <target>/../skills-backup/<name>-<timestamp> first
# (outside the skills dir so it is not loaded twice; never deleted).
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${HOME}/.claude/skills"
MODE="link"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --copy) MODE="copy"; shift ;;
    --target) TARGET="$2"; shift 2 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 1 ;;
  esac
done

mkdir -p "$TARGET"
for src in "$REPO"/skills/*/; do
  name="$(basename "$src")"
  dest="$TARGET/$name"
  if [[ -L "$dest" && "$(readlink "$dest")" == "${src%/}" ]]; then
    echo "✓ $name already linked"; continue
  fi
  if [[ -e "$dest" || -L "$dest" ]]; then
    backup_dir="$(dirname "$TARGET")/skills-backup"
    mkdir -p "$backup_dir"
    backup="$backup_dir/$name-$(date +%Y%m%d%H%M%S)"
    mv "$dest" "$backup"
    echo "  moved existing $name -> $backup"
  fi
  if [[ "$MODE" == "link" ]]; then
    ln -s "${src%/}" "$dest"; echo "✓ linked $name -> ${src%/}"
  else
    cp -R "${src%/}" "$dest"; echo "✓ copied $name"
  fi
done
