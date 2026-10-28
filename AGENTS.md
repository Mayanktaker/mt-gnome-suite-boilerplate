# AGENTS.md — MT Theme Starter

© Mayanktaker Computers & Web Development | https://mayanktaker.com

GNOME dark theme suite starter: Shell + GTK3 + GTK4 (best-effort) + Flatpak GTK3 extension + Companion Icon Pack + Cursor Pack + Procedural Wallpapers + App Extras.
Display name **MT Theme Starter**, technical/theme-dir name `MT-Theme-Starter`.

## Stack & toolchain (verify before assuming; update when versions change)
- Targets: GNOME Shell 50.x and 51.x (Wayland/X11).
- Build: `sassc` (libsass 3.6.6), Python 3 + `numpy` 2.5.4 + `Pillow` 13.0.0 + `pycairo` + `PyGObject` (Rsvg, Gio).
- Repo: git 2.56, `gh` authenticated as `Mayanktaker`.
- **Installation policy:** ALWAYS install user themes into the user's `~/.themes` (e.g. `/home/<user>/.themes`) ONLY, and user icon/cursor packs into the user's `~/.icons` (e.g. `/home/<user>/.icons`) ONLY — never `~/.local/share/themes`, `~/.local/share/icons`, or system dirs. `tools/install.sh` implements and must keep this. Shell activation needs the **User Themes** extension (`user-theme@gnome-shell-extensions.gcampax.github.com`).
- **Installer behavior:** `tools/install.sh` detects distro (`/etc/os-release`) + GNOME Shell major (gate ≥50 with a matching colormap), checks missing packages/modules per distro (python3, gi, sassc, numpy, Pillow, User Themes extension) — only for parts it will actually build — prints the exact distro install command, and uses **sudo only for system package installs** via `--install-deps`; the theme install itself never needs root. Old installs under `~/.local/share/themes` are moved to `deleted_files_folders/`, never deleted.

## Single source of truth
- `palette/tokens.json` — every color in CSS/wallpaper/builds comes from here. No new magic values; add tokens instead.
- `palette/presets/` — curated starting configurations (nordic-frost, cyberpunk-neon, amber-sunset, monochrome-oled, verdant-canopy).
- Shell theme is derived from upstream GNOME Shell CSS per major version, recolored via `src/shell/` maps (never hand-edit generated CSS).
- Icons & Cursors dynamically draw gradients and geometry fills from `palette/tokens.json`.

## Quick Scaffold / Initialization
- Rebrand the project: `python3 init_theme.py [--preset <name>] [--name "Theme Name"] [--accent "#HEX"]`

## Build & Test Commands
- Unified master build: `python3 build_all.py` (runs contrast gate, GTK, Shell 50/51, icons, cursors, wallpapers in sequence).
- Contrast gate: `python3 tools/dev/check_contrast.py` (must pass before commits).
- GTK build: `python3 tools/gtk/build.py` → `build/theme/gtk-{3,4}.0/`.
- Shell build: `python3 tools/shell/build.py [--major N | --all]` (extracts host CSS or uses `src/shell/upstream-<major>/`).
- Icons build: `python3 tools/icons/generate_icons.py` → `src/icons/<tech_name>-Icons/`.
- Cursors build: `python3 tools/icons/generate_cursors.py` → `src/cursors/<tech_name>-Cursors/`.
- Wallpaper suite: `python3 tools/wallpaper/generate.py [--which 1|2|3|4|all]` (dark) and `python3 tools/wallpaper/process_light.py` (light).
- Install suite: `./install.sh` (interactive CLI wizard) or `tools/install.sh [--panel round-island|pill|bottom-round|flat] [--controls standard|macos] [--icons] [--gtk4-libadwaita] [--wallpaper all]`.
- App ecosystem install: `tools/extras/install-all.sh`.
- Package release: `tools/release.sh <version>`.

## Layout
- `palette/` tokens (`tokens.json` single source of truth) + `presets/` library
- `src/` source layers (gtk-2.0, gtk-3.0, gtk-4.0, shell colormaps, tweaks, icons, cursors)
- `tools/` build engines (gtk, shell, icons, wallpapers, dev contrast gate, installer, packager)
- `extras/` application themes (terminals, shells, editors, KDE, GDM, SDDM, GRUB, Plymouth)
- `flatpak/` extension manifest + appdata
- `docs/` documentation (`workflow.md`, `design.md`, `compatibility.md`, `flatpak.md`)
- `init_theme.py` rapid rebranding & setup script
- `build_all.py` master build runner

## Documentation pointers (do not duplicate content here)
- `docs/design.md` — design direction, token table, wallpaper rules
- `docs/compatibility.md` — GNOME version matrix + test checklist
- `docs/flatpak.md` — Flatpak GTK3 theme extension plan & status
- `docs/workflow.md` — build/release workflow

## Conventions
- Every file starts with the © header: `© Mayanktaker Computers & Web Development | https://mayanktaker.com`.
- Every function/block gets ≤1-line comment.
- License: GPL-3.0 (code/CSS) + CC BY-SA 4.0 (artwork). See `LICENSES/`.
