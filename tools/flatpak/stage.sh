#!/bin/sh
# © Mayanktaker Computers & Web Development | https://mayanktaker.com
# Stage the GTK3 theme for the Flatpak theme extension (consumed by the manifest's dir source).
# Re-run after rebuilding the GTK theme.

set -eu

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

if [ -f "${REPO_ROOT}/palette/tokens.json" ]; then
  TECH_NAME="$(python3 -c "import json; print(json.load(open('${REPO_ROOT}/palette/tokens.json'))['meta']['tech_name'])" 2>/dev/null || echo "MT-Theme-Starter")"
else
  TECH_NAME="MT-Theme-Starter"
fi

STAGE="${REPO_ROOT}/flatpak/stage/${TECH_NAME}"

[ -f "${REPO_ROOT}/build/theme/gtk-3.0/gtk-dark.css" ] || python3 "${REPO_ROOT}/tools/gtk/build.py"

rm -rf "${REPO_ROOT}/flatpak/stage"
mkdir -p "${STAGE}/gtk-3.0"
cp "${REPO_ROOT}/build/theme/gtk-3.0/gtk.css" "${REPO_ROOT}/build/theme/gtk-3.0/gtk-dark.css" "${STAGE}/gtk-3.0/"
cp -r "${REPO_ROOT}/build/theme/gtk-3.0/assets" "${STAGE}/gtk-3.0/"
cp "${REPO_ROOT}/src/index.theme" "${STAGE}/index.theme"
echo "staged GTK3 theme at ${REPO_ROOT}/flatpak/stage for ${TECH_NAME}"
