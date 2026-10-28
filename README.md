# MT GNOME Theme Suite Boilerplate

© Mayanktaker Computers & Web Development | https://mayanktaker.com

A production-grade boilerplate and wireframe scaffold for creating unified GNOME desktop suites: **Theme + Companion Icons + Custom Cursors + Procedural Wallpapers + App Ecosystem**.

---

## ⚡ Quick Start: Creating a New Theme

### 1. Clone or Copy this Boilerplate
```bash
# Option A: From GitHub Template (Recommended)
gh repo create Mayanktaker/my-new-theme --template Mayanktaker/mt-gnome-suite-boilerplate
git clone https://github.com/Mayanktaker/my-new-theme.git
cd my-new-theme

# Option B: Local Copy
cp -r "/mnt/Development/Linux_Projects/Gnome-Themes/MT-Gnome-Suite-Boilerplate" \
      "/mnt/Development/Linux_Projects/Gnome-Themes/MT-My-New-Theme"
cd "/mnt/Development/Linux_Projects/Gnome-Themes/MT-My-New-Theme"
```

### 2. Initialize and Rebrand
Run the interactive initializer wizard:
```bash
python3 init_theme.py
```
Or initialize instantly using one of the curated presets:
```bash
# Available presets: nordic-frost, cyberpunk-neon, amber-sunset, monochrome-oled, verdant-canopy
python3 init_theme.py --preset nordic-frost

# Or with custom brand overrides:
python3 init_theme.py \
  --name "MT Cyberpunk Neon" \
  --tech-name "MT-Cyberpunk-Neon" \
  --direction "High-tech synthwave dark" \
  --accent "#00F0FF"
```
The initializer automatically:
- Updates `palette/tokens.json` metadata and primary accent.
- Updates `src/index.theme`.
- Rebrands and renames Flatpak manifests in `flatpak/`.
- Updates `AGENTS.md`.
- Runs WCAG contrast checks to ensure your colors meet accessibility standards.

### 3. Build the Entire Trio in One Command
```bash
python3 build_all.py
```
*(Optionally pass `--skip-wallpapers`, `--skip-icons`, or `--skip-cursors` if doing quick iterations).*

### 4. Install & Test
Launch the interactive installer wizard:
```bash
./install.sh
```
Or run headlessly:
```bash
./install.sh --panel round-island --controls macos --icons --wallpaper 1
```

---

## 🎨 Curated Palette Presets

Located in [`palette/presets/`](file:///mnt/Development/Linux_Projects/Gnome-Themes/MT-Gnome-Suite-Boilerplate/palette/presets):

| Preset | Mood / Direction | Primary Accent |
| :--- | :--- | :--- |
| **`nordic-frost`** | Arctic polar night, deep slate & ice cyan | `#88C0D0` |
| **`cyberpunk-neon`** | High-tech synthwave dark, obsidian & electric cyan | `#00E5FF` |
| **`amber-sunset`** | Warm glowing ember & dusk espresso | `#F59E0B` |
| **`monochrome-oled`** | Pure pitch-black OLED & platinum minimalism | `#E5E5E5` |
| **`verdant-canopy`** | Botanical canopy, dark teal & sage foliage | `#8FB8A6` |

---

## 🏗️ Architecture & Single Source of Truth

Every color across the entire desktop environment flows from **`palette/tokens.json`**:

```
                 palette/tokens.json (Single Source of Truth)
                                │
        ┌───────────────────────┼───────────────────────────┐
        ▼                       ▼                           ▼
  GTK 3 & 4 Themes      GNOME Shell Themes          Icons & Cursors
 (tools/gtk/build.py)  (tools/shell/build.py)   (tools/icons/generate_*)
        │                       │                           │
        ▼                       ▼                           ▼
~/.themes/<theme>/       ~/.themes/<theme>/          ~/.icons/<theme>-*/
```

- **`palette/tokens.json`**: Background shades, surface hierarchies, primary accent, accent flavors, status indicators, and WCAG contrast rules.
- **`src/gtk-3.0/` & `src/gtk-4.0/`**: Upstream SASS template patched dynamically with token values; compiled via `sassc`.
- **`src/shell/`**: Shell recoloring engine based on upstream GNOME Shell CSS colormaps for major versions (50.x and 51.x).
- **`src/icons/` & `src/cursors/`**: High-definition vector icons and custom aerodynamic cursors dynamically rendered using your theme tokens.
- **`tools/wallpaper/`**: Deterministic procedural 4K wallpaper generator driven by palette tokens.
- **`extras/`**: Color schemes for terminals (Ghostty, Kitty, Alacritty, Foot, GNOME Terminal), shells (Fish), text editors, KDE Plasma, GDM, SDDM, GRUB, and Plymouth.

---

## 🛠️ Project Tooling

| Command | Purpose |
| :--- | :--- |
| `python3 init_theme.py [--preset <name>]` | Scaffold / rebrand project with new name, tech-id, and preset |
| `python3 build_all.py` | Unified master build: builds GTK, Shell, Icons, Cursors, and Wallpapers |
| `python3 tools/dev/check_contrast.py` | WCAG contrast audit across all background & text pairs |
| `python3 tools/gtk/build.py` | Compile GTK3 and GTK4 theme variants |
| `python3 tools/shell/build.py --all` | Build GNOME Shell theme for all supported major versions |
| `python3 tools/icons/generate_icons.py` | Render places, apps, devices, and symbolic icons |
| `python3 tools/icons/generate_cursors.py` | Render multi-resolution (24, 32, 48) animated Xcursor pack |
| `python3 tools/wallpaper/generate.py` | Generate 4 distinct procedural 4K wallpapers |
| `./install.sh` | Interactive installer into `~/.themes` and `~/.icons` |
| `tools/extras/install-all.sh` | Install matching themes for all detected third-party apps |
| `tools/release.sh <version>` | Package complete release tarball and standalone icon pack into `dist/` |

---

## 📜 Policies & Standards

- **Install policy**: User themes install into `~/.themes` ONLY; icons and cursors install into `~/.icons` ONLY. Never pollute root or `/usr/local/share`.
- **No hard deletions**: Archived versions or removed configurations move to `deleted_files_folders/`.
- **Licensing**: GPL-3.0 for code/CSS (`LICENSES/GPL-3.0.txt`), CC BY-SA 4.0 for artwork and renders (`LICENSES/CC-BY-SA-4.0.txt`).
