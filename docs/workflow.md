# Workflow — build & release

© Mayanktaker Computers & Web Development | https://mayanktaker.com

## Milestone flow
1. `python3 tools/dev/check_contrast.py` — must pass before committing any palette changes.
2. Build the layer being changed (`tools/shell/build.py`, `tools/gtk/build.py`, `tools/icons/generate_icons.py`, `tools/wallpaper/generate.py`).
3. Verify installation with tweaks: `./install.sh --panel round-island --controls macos`.
4. Verify on the host session (Wayland: re-login or toggle User Themes off/on in Extensions app to reload CSS).
5. Commit small, coherent changes; push verified milestones only.
6. Update `docs/compatibility.md` and project roadmap as features complete.

## Release flow
- Tag `vX.Y`; run `tools/release.sh <version>`. The script generates:
  - Theme release bundle: `dist/<tech_name>-v<version>.tar.xz`
  - Standalone icons bundle: `dist/<tech_name>-icons-v<version>.tar.xz`
- Release notes are written for end users: what looks different, what got smoother, what was fixed — no internal identifiers or developer hashes.

## Repo rules
- Public GitHub repository (main branch).
- No force-push, no history rewrites after push; license/secrets check before every push.
