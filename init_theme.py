#!/usr/bin/env python3
# © Mayanktaker Computers & Web Development | https://mayanktaker.com
# Interactive and CLI tool to initialize or rebrand a GNOME Theme + Icon + Cursor trio project.
# Supports curated palette presets, token generation, index.theme, flatpak manifests, and WCAG check.

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
PRESETS_DIR = REPO_ROOT / "palette" / "presets"


def slugify(name: str) -> str:
    # Convert display name into a standardized tech-name directory string.
    cleaned = re.sub(r"[^\w\s-]", "", name).strip()
    return re.sub(r"[-\s]+", "-", cleaned)


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    # Parse a #RRGGBB hex string into an integer RGB tuple.
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    # Format RGB integers into uppercase #RRGGBB format.
    return f"#{max(0, min(255, int(r))):02X}{max(0, min(255, int(g))):02X}{max(0, min(255, int(b))):02X}"


def adjust_brightness(hex_color: str, factor: float) -> str:
    # Lighten (>1.0) or darken (<1.0) a hex color.
    r, g, b = hex_to_rgb(hex_color)
    return rgb_to_hex(r * factor, g * factor, b * factor)


def get_available_presets() -> dict[str, Path]:
    # Locate all available curated preset JSON configurations.
    if not PRESETS_DIR.exists():
        return {}
    return {p.stem: p for p in sorted(PRESETS_DIR.glob("*.json"))}


def prompt_user() -> dict[str, str]:
    # Interactive wizard prompting developer for theme preset or custom values.
    print("================================================================")
    print(" 🎨 MT GNOME Theme Suite Starter — New Project Initializer")
    print("================================================================\n")

    presets = get_available_presets()
    preset_names = list(presets.keys())

    print("Choose a Starting Palette:")
    print("  [0] Default Starter (Slate Dark & Azure Blue)")
    for i, p_name in enumerate(preset_names, 1):
        try:
            p_data = json.loads(presets[p_name].read_text())
            d_name = p_data.get("meta", {}).get("name", p_name)
            d_dir = p_data.get("meta", {}).get("direction", "")
            print(f"  [{i}] {d_name} — {d_dir}")
        except Exception:
            print(f"  [{i}] {p_name}")
    print(f"  [{len(preset_names) + 1}] Custom Palette (Configure everything from scratch)\n")

    choice_str = input(f"Select option [0-{len(preset_names) + 1}, default=0]: ").strip() or "0"
    try:
        choice = int(choice_str)
    except ValueError:
        choice = 0

    chosen_preset_file = None
    if 1 <= choice <= len(preset_names):
        chosen_preset_name = preset_names[choice - 1]
        chosen_preset_file = presets[chosen_preset_name]

    if chosen_preset_file:
        p_data = json.loads(chosen_preset_file.read_text())
        default_name = p_data.get("meta", {}).get("name", "My Theme")
        default_tech = p_data.get("meta", {}).get("tech_name", slugify(default_name))
        default_dir = p_data.get("meta", {}).get("direction", "Modern Dark")
        default_accent = p_data.get("color", {}).get("accent", {}).get("base", "#4597F7")

        print(f"\nLoaded Preset: {default_name}")
        name = input(f"Theme Display Name [{default_name}]: ").strip() or default_name
        tech_name = input(f"Technical Identifier [{default_tech}]: ").strip() or default_tech
        direction = input(f"Design Direction / Mood [{default_dir}]: ").strip() or default_dir
        accent = input(f"Primary Accent Hex [{default_accent}]: ").strip() or default_accent
        if not accent.startswith("#"):
            accent = f"#{accent}"

        return {
            "name": name,
            "tech_name": tech_name,
            "direction": direction,
            "accent": accent,
            "preset_file": str(chosen_preset_file),
        }

    # Custom or Default
    print("\nConfigure Theme Identity:")
    name = input("Theme Display Name (e.g. MT Cyberpunk Neon): ").strip() or "MT Theme Starter"
    default_tech = slugify(name)
    tech_name = input(f"Technical Identifier [{default_tech}]: ").strip() or default_tech
    direction = input("Design Direction / Mood [Modern Dark]: ").strip() or "Modern Dark"
    accent = input("Primary Accent Hex Color [#4597F7]: ").strip() or "#4597F7"
    if not accent.startswith("#"):
        accent = f"#{accent}"

    return {
        "name": name,
        "tech_name": tech_name,
        "direction": direction,
        "accent": accent,
        "preset_file": "",
    }


def update_tokens(config: dict[str, str]) -> None:
    # Update palette/tokens.json from preset or template, then patch metadata.
    tokens_file = REPO_ROOT / "palette" / "tokens.json"

    if config.get("preset_file") and Path(config["preset_file"]).exists():
        data = json.loads(Path(config["preset_file"]).read_text())
    else:
        data = json.loads(tokens_file.read_text())

    data["meta"]["name"] = config["name"]
    data["meta"]["tech_name"] = config["tech_name"]
    data["meta"]["direction"] = config["direction"]
    data["meta"]["version"] = "0.1.0"

    accent = config["accent"]
    data["color"]["accent"]["base"] = accent
    data["color"]["accent"]["strong"] = adjust_brightness(accent, 1.15)
    data["color"]["accent"]["dim"] = adjust_brightness(accent, 0.75)
    data["color"]["border"]["focus"] = accent

    tokens_file.write_text(json.dumps(data, indent=2) + "\n")
    print(f"  ✓ Updated {tokens_file.relative_to(REPO_ROOT)}")


def update_index_theme(config: dict[str, str]) -> None:
    # Update src/index.theme with the new suite technical names.
    index_file = REPO_ROOT / "src" / "index.theme"
    content = f"""[Desktop Entry]
Type=X-GNOME-Metatheme
Name={config['tech_name']}
Comment={config['name']} — modular GNOME dark theme suite by Mayanktaker (https://mayanktaker.com)
Encoding=UTF-8

[X-GNOME-Metatheme]
GtkTheme={config['tech_name']}
MetacityTheme=Adwaita
IconTheme={config['tech_name']}-Icons
CursorTheme={config['tech_name']}-Cursors
ButtonLayout=:minimize,maximize,close
"""
    index_file.write_text(content)
    print(f"  ✓ Updated {index_file.relative_to(REPO_ROOT)}")


def update_flatpak(config: dict[str, str]) -> None:
    # Update Flatpak manifest and AppData metadata, renaming files to match tech_name.
    flatpak_dir = REPO_ROOT / "flatpak"
    tech_name = config["tech_name"]
    display_name = config["name"]

    # Remove existing manifests
    for f in flatpak_dir.glob("org.gtk.Gtk3theme.*"):
        f.unlink()

    json_path = flatpak_dir / f"org.gtk.Gtk3theme.{tech_name}.json"
    appdata_path = flatpak_dir / f"org.gtk.Gtk3theme.{tech_name}.appdata.xml"

    json_data = {
        "id": f"org.gtk.Gtk3theme.{tech_name}",
        "branch": "3.22",
        "runtime": "org.freedesktop.Platform",
        "sdk": "org.freedesktop.Sdk",
        "runtime-version": "26.08",
        "build-extension": True,
        "appstream-compose": False,
        "separate-locales": False,
        "modules": [
            {
                "name": tech_name.lower(),
                "buildsystem": "simple",
                "build-commands": [
                    f"cp -a {tech_name}/gtk-3.0/. ${{FLATPAK_DEST}}/"
                ],
                "sources": [
                    {
                        "type": "dir",
                        "path": "stage",
                        "skip": [".git"]
                    }
                ]
            },
            {
                "name": "appdata",
                "buildsystem": "simple",
                "build-commands": [
                    "mkdir -p ${FLATPAK_DEST}/share/appdata",
                    f"cp org.gtk.Gtk3theme.{tech_name}.appdata.xml ${{FLATPAK_DEST}}/share/appdata"
                ],
                "sources": [
                    {
                        "type": "file",
                        "path": f"org.gtk.Gtk3theme.{tech_name}.appdata.xml"
                    }
                ]
            }
        ]
    }
    json_path.write_text(json.dumps(json_data, indent=2) + "\n")

    appdata_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- © Mayanktaker Computers & Web Development | https://mayanktaker.com -->
<component type="runtime">
  <id>org.gtk.Gtk3theme.{tech_name}</id>
  <metadata_license>CC0-1.0</metadata_license>
  <project_license>GPL-3.0+</project_license>
  <name>{display_name} GTK3 theme</name>
  <summary>Modular GNOME dark theme for GTK3 Flatpak apps</summary>
  <description>
    <p>GTK3 theme extension so sandboxed Flatpak apps follow the {display_name} desktop theme. Installed automatically when the host GTK theme is set to {tech_name}.</p>
  </description>
  <url type="homepage">https://mayanktaker.com</url>
  <developer_name>Mayanktaker Computers &amp; Web Development</developer_name>
  <releases>
    <release version="0.1.0" date="2026-10-28">
      <description><p>Initial release of {display_name} suite.</p></description>
    </release>
  </releases>
</component>
"""
    appdata_path.write_text(appdata_xml)
    print(f"  ✓ Configured Flatpak manifests for org.gtk.Gtk3theme.{tech_name}")


def update_agents_md(config: dict[str, str]) -> None:
    # Update AGENTS.md operating map with the project's new identity.
    agents_file = REPO_ROOT / "AGENTS.md"
    if not agents_file.exists():
        return
    text = agents_file.read_text()
    text = re.sub(r"# AGENTS\.md — .*", f"# AGENTS.md — {config['name']}", text)
    text = re.sub(r"Display name \*\*.*?\*\*, technical/theme-dir name `.*?`",
                  f"Display name **{config['name']}**, technical/theme-dir name `{config['tech_name']}`", text)
    agents_file.write_text(text)
    print(f"  ✓ Updated {agents_file.relative_to(REPO_ROOT)}")


def run_contrast_check() -> None:
    # Execute the contrast validator to verify token compliance.
    check_script = REPO_ROOT / "tools" / "dev" / "check_contrast.py"
    if check_script.exists():
        print("\n🔍 Validating token WCAG contrast ratios...")
        res = subprocess.run([sys.executable, str(check_script)], capture_output=True, text=True)
        print(res.stdout)
        if res.returncode != 0:
            print("⚠️ Warning: Some token contrast ratios did not pass WCAG minimums.", file=sys.stderr)


def main() -> int:
    # Entrypoint orchestrating project initialization.
    parser = argparse.ArgumentParser(description="Initialize a new GNOME theme suite project from boilerplate.")
    parser.add_argument("--preset", help="Name of a curated preset (e.g. 'nordic-frost', 'cyberpunk-neon')")
    parser.add_argument("--name", help="Theme display name (e.g. 'MT Cyan Horizon')")
    parser.add_argument("--tech-name", help="Theme technical name (e.g. 'MT-Cyan-Horizon')")
    parser.add_argument("--direction", help="Design direction mood or description")
    parser.add_argument("--accent", help="Primary accent hex color (e.g. '#26B5CE')")
    args = parser.parse_args()

    presets = get_available_presets()

    if args.preset:
        preset_key = args.preset.lower().replace(".json", "")
        if preset_key not in presets:
            print(f"Error: Unknown preset '{args.preset}'. Available presets: {list(presets.keys())}", file=sys.stderr)
            return 1
        p_file = presets[preset_key]
        p_data = json.loads(p_file.read_text())
        name = args.name or p_data.get("meta", {}).get("name", "My Theme")
        tech = args.tech_name or p_data.get("meta", {}).get("tech_name", slugify(name))
        direction = args.direction or p_data.get("meta", {}).get("direction", "Modern Dark")
        accent = args.accent or p_data.get("color", {}).get("accent", {}).get("base", "#4597F7")
        config = {
            "name": name,
            "tech_name": tech,
            "direction": direction,
            "accent": accent,
            "preset_file": str(p_file),
        }
    elif args.name:
        tech = args.tech_name or slugify(args.name)
        config = {
            "name": args.name,
            "tech_name": tech,
            "direction": args.direction or "Modern Dark",
            "accent": args.accent or "#4597F7",
            "preset_file": "",
        }
    else:
        config = prompt_user()

    print(f"\n🚀 Initializing '{config['name']}' ({config['tech_name']})...")
    update_tokens(config)
    update_index_theme(config)
    update_flatpak(config)
    update_agents_md(config)
    run_contrast_check()

    print("\n================================================================")
    print(f" ✨ {config['name']} suite initialized successfully!")
    print("================================================================")
    print("Next step: build the complete suite in one command:\n")
    print("  python3 build_all.py")
    print("  ./install.sh\n")
    print("================================================================\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
