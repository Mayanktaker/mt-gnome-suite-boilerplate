#!/usr/bin/env python3
# © Mayanktaker Computers & Web Development | https://mayanktaker.com
# Master build orchestrator: builds GTK theme, Shell theme, icons, cursors, and wallpapers in one pass.

import argparse
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def run_step(step_num: int, total_steps: int, label: str, cmd: list[str]) -> bool:
    # Execute one build step with formatted logging and runtime measurement.
    print(f"\n[{step_num}/{total_steps}] ⏳ {label}...")
    start_time = time.time()
    res = subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=True)
    duration = time.time() - start_time

    if res.returncode == 0:
        print(f"[{step_num}/{total_steps}] ✓ {label} completed in {duration:.2f}s")
        if res.stdout.strip():
            for line in res.stdout.strip().splitlines()[-3:]:
                print(f"    {line}")
        return True

    print(f"[{step_num}/{total_steps}] ✗ {label} FAILED in {duration:.2f}s (code {res.returncode})", file=sys.stderr)
    if res.stdout:
        print(f"--- stdout ---\n{res.stdout}", file=sys.stderr)
    if res.stderr:
        print(f"--- stderr ---\n{res.stderr}", file=sys.stderr)
    return False


def main() -> int:
    # Orchestrate the entire desktop trio build pipeline.
    parser = argparse.ArgumentParser(description="Build complete GNOME theme suite (GTK, Shell, Icons, Cursors, Wallpapers).")
    parser.add_argument("--skip-wallpapers", action="store_true", help="Skip rendering 4K wallpapers")
    parser.add_argument("--skip-icons", action="store_true", help="Skip generating icon pack")
    parser.add_argument("--skip-cursors", action="store_true", help="Skip generating cursor pack")
    parser.add_argument("--shell-host-only", action="store_true", help="Build GNOME Shell theme for host only instead of --all")
    args = parser.parse_args()

    steps = [
        ("Validating token WCAG contrast ratios", [sys.executable, "tools/dev/check_contrast.py"]),
        ("Building GTK3 & GTK4 themes", [sys.executable, "tools/gtk/build.py"]),
        (
            "Building GNOME Shell stylesheets",
            [sys.executable, "tools/shell/build.py"] + (["--all"] if not args.shell_host_only else [])
        ),
    ]

    if not args.skip_icons:
        steps.append(("Generating vector SVGs & multi-resolution Icon suite", [sys.executable, "tools/icons/generate_icons.py"]))

    if not args.skip_cursors:
        steps.append(("Generating multi-resolution animated Cursor suite", [sys.executable, "tools/icons/generate_cursors.py"]))

    if not args.skip_wallpapers:
        steps.append(("Generating procedural 4K Wallpapers suite", [sys.executable, "tools/wallpaper/generate.py", "--which", "all"]))

    total_steps = len(steps)
    overall_start = time.time()

    print("================================================================")
    print(" 🛠️  MT GNOME Theme Suite — Master Build Orchestrator")
    print(f" Total pipeline steps: {total_steps}")
    print("================================================================")

    for idx, (label, cmd) in enumerate(steps, 1):
        success = run_step(idx, total_steps, label, cmd)
        if not success:
            print(f"\n❌ Pipeline aborted due to failure in step: {label}", file=sys.stderr)
            return 1

    total_duration = time.time() - overall_start
    print("\n================================================================")
    print(f" 🎉 Complete suite built successfully in {total_duration:.2f}s!")
    print("================================================================")
    print("Next steps:")
    print("  - Test locally:    ./install.sh")
    print("  - Package release: tools/release.sh 0.1.0\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
