# Design System Guide

© Mayanktaker Computers & Web Development | https://mayanktaker.com

Single source of truth for colors: `palette/tokens.json` (do not hardcode hex values elsewhere).

## Principles
- **Dark-first, quiet surfaces:** balanced dark bases refined for visual comfort; menus and dialogs stay opaque and readable.
- **Accented focus:** single clear accent color for primary actions, focus rings, and active selections.
- **Familiar GNOME shape:** upstream layout, geometry, and spacing are respected while elevating palette harmony.
- **Contrast is a gate:** `tools/dev/check_contrast.py` must pass (WCAG ≥4.5 body text, ≥7 preferred) before any milestone commit.
- **System fonts**, no intrusive custom typography in the theme itself.

## Tokens (Starter Baseline)
| Token | Starter Value | Use |
|---|---|---|
| `bg.base` | #111418 | Main panels, dialogs, cards |
| `bg.base_darker` | #0C0E12 | Overview backdrop, OSD base |
| `bg.oled` | #060709 | True pitch-black OLED background (`--tweaks black`) |
| `bg.tile` | #181E26 | Quick-settings tiles, list rows |
| `bg.surface` / `hover` / `active` | #222B38 / #2B3747 / #354457 | Raised surfaces and interactive states |
| `accent.base` / `strong` / `dim` | #4597F7 / #68ADFB / #2C69B3 | Focus rings, selected items, sliders, links |
| `accent_flavors.cyan` | #26B5CE | Cyan accent flavor |
| `accent_flavors.purple` | #B57EDC | Purple accent flavor |
| `accent_flavors.amber` | #F09838 | Amber accent flavor |
| `window_controls` close/min/max | #E05F65 / #E5A54B / #57AB5A | Window titlebar controls |
| `text.primary` / `secondary` / `disabled` | #ECEFF4 / #A0ABB8 / #7E8B9B | Foreground typography tiers |
| `status` destructive/success/warning | #E05F65 / #57AB5A / #E5A54B | Semantic indicators and warnings |
| `border.default` / `subtle` | #2E3744 / #222933 | Separators, container edges |

All text/accent pairs verified ≥4.5:1 on their backgrounds (most ≥7:1 to 16:1).

## Modular Tweaks System
- **Panel styles**: `round-island`, `pill`, `bottom-round`, `flat`.
- **Window controls**: `standard`, `macos` (traffic lights).
- **Theme sizing**: `standard`, `compact`.
- **Display tweaks**: `--blur` / `--no-blur`, `--gtk4-libadwaita`.

## Wallpaper Generation Rules
Original procedural artworks generated via `tools/wallpaper/generate.py`:
1. **Atmospheric Canopy (Art 1)**: Silhouetted organic canopy foliage with glowing palette gradient.
2. **Radiant Aurora (Art 2)**: Northern lights atmospheric gradient with starfield and forest silhouette.
3. **Geometric Flow (Art 3)**: Bauhaus-inspired geometric contours in theme tones.
4. **Minimal Horizon (Art 4)**: Topographic isolines with glowing theme mineral veins.
