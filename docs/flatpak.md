# Flatpak compatibility

© Mayanktaker Computers & Web Development | https://mayanktaker.com

Status: Extension builds with `org.flatpak.Builder` (user-level, no root) and mounts inside Flatpak sandboxes.

## Architecture
- Flatpak GTK3 theme extensions match the host's `gtk-theme` gsettings key automatically.
- Extension point on modern runtimes (25.08, 26.08): `runtime/org.gtk.Gtk3theme.<tech_name>/x86_64/3.22`.
- Extension mount point: `/usr/share/runtime/share/themes/<tech_name>/gtk-3.0/`.

## Key Layout Rule
Modern Freedesktop runtimes mount with `subdirectory-suffix gtk-3.0`. The extension payload root must be the **contents of `gtk-3.0/`** (matching Adwaita-dark pattern) — containing `gtk.css`, `gtk-dark.css`, and `assets/`.

## Staging & Building
1. Stage the built GTK3 theme:
   ```bash
   bash tools/flatpak/stage.sh
   ```
2. Build and install user-level extension:
   ```bash
   flatpak-builder --user --install --force-clean flatpak/build flatpak/org.gtk.Gtk3theme.<tech_name>.json
   ```
