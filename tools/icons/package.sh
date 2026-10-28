#!/bin/sh
# © Mayanktaker Computers & Web Development | https://mayanktaker.com
# Packages companion Icon and Cursor suite into a standalone .tar.xz archive.
# Usage: tools/icons/package.sh <version>  (e.g. tools/icons/package.sh 0.1.0)

set -eu

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

if [ -f "${REPO_ROOT}/palette/tokens.json" ]; then
  TECH_NAME="$(python3 -c "import json; print(json.load(open('${REPO_ROOT}/palette/tokens.json'))['meta']['tech_name'])" 2>/dev/null || echo "MT-Theme-Starter")"
  DISPLAY_NAME="$(python3 -c "import json; print(json.load(open('${REPO_ROOT}/palette/tokens.json'))['meta']['name'])" 2>/dev/null || echo "MT Theme Starter")"
  TECH_SLUG="$(python3 -c "import json; print(json.load(open('${REPO_ROOT}/palette/tokens.json'))['meta']['tech_name'].lower())" 2>/dev/null || echo "mt-theme-starter")"
else
  TECH_NAME="MT-Theme-Starter"
  DISPLAY_NAME="MT Theme Starter"
  TECH_SLUG="mt-theme-starter"
fi

VERSION="${1:-0.1.0}"
DIST_ROOT="${REPO_ROOT}/dist"
ICONS_NAME="${TECH_NAME}-Icons"
CURSORS_NAME="${TECH_NAME}-Cursors"
ICONS_DIST="${DIST_ROOT}/${TECH_SLUG}-icons-v${VERSION}"
TARBALL="${DIST_ROOT}/${TECH_SLUG}-icons-v${VERSION}.tar.xz"

# Ensure output directory exists
mkdir -p "${DIST_ROOT}"
rm -rf "${ICONS_DIST}"
mkdir -p "${ICONS_DIST}"

# Copy icon and cursor suites
cp -r "${REPO_ROOT}/src/icons/${ICONS_NAME}" "${ICONS_DIST}/"
cp -r "${REPO_ROOT}/src/cursors/${CURSORS_NAME}" "${ICONS_DIST}/"

# Copy licenses
mkdir -p "${ICONS_DIST}/LICENSES"
cp "${REPO_ROOT}/LICENSES/GPL-3.0.txt" "${ICONS_DIST}/LICENSES/"
cp "${REPO_ROOT}/LICENSES/CC-BY-SA-4.0.txt" "${ICONS_DIST}/LICENSES/"

# Create standalone installer script
cat <<EOF > "${ICONS_DIST}/install.sh"
#!/bin/sh
# © Mayanktaker Computers & Web Development | https://mayanktaker.com
# Standalone installer for ${ICONS_NAME} and ${CURSORS_NAME}
set -eu

ICONS_DIR="\${HOME}/.icons"
SCRIPT_DIR="\$(cd "\$(dirname "\$0")" && pwd)"

mkdir -p "\${ICONS_DIR}"

if [ -d "\${SCRIPT_DIR}/${ICONS_NAME}" ]; then
  echo "Installing ${ICONS_NAME}..."
  rm -rf "\${ICONS_DIR}/${ICONS_NAME}"
  cp -r "\${SCRIPT_DIR}/${ICONS_NAME}" "\${ICONS_DIR}/"
  if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "\${ICONS_DIR}/${ICONS_NAME}" >/dev/null 2>&1 || true
  fi
  if command -v gsettings >/dev/null 2>&1; then
    gsettings set org.gnome.desktop.interface icon-theme '${ICONS_NAME}' || true
  fi
  echo "  ✓ ${ICONS_NAME} installed to \${ICONS_DIR}/${ICONS_NAME}"
fi

if [ -d "\${SCRIPT_DIR}/${CURSORS_NAME}" ]; then
  echo "Installing ${CURSORS_NAME}..."
  rm -rf "\${ICONS_DIR}/${CURSORS_NAME}"
  cp -r "\${SCRIPT_DIR}/${CURSORS_NAME}" "\${ICONS_DIR}/"
  if command -v gsettings >/dev/null 2>&1; then
    gsettings set org.gnome.desktop.interface cursor-theme '${CURSORS_NAME}' || true
  fi
  echo "  ✓ ${CURSORS_NAME} installed to \${ICONS_DIR}/${CURSORS_NAME}"
fi

echo "Done! Icons and cursors have been successfully installed and activated."
EOF
chmod +x "${ICONS_DIST}/install.sh"

# Create standalone README
cat <<EOF > "${ICONS_DIST}/README.md"
# ${ICONS_NAME} & ${CURSORS_NAME}

© Mayanktaker Computers & Web Development | https://mayanktaker.com

Companion icon and cursor suite for ${DISPLAY_NAME}.

## Quick Installation

Run the included installer:
\`\`\`bash
./install.sh
\`\`\`

## Manual Installation

Copy both folders to your user \`~/.icons\` directory:
\`\`\`bash
mkdir -p ~/.icons
cp -r ${ICONS_NAME} ${CURSORS_NAME} ~/.icons/
gtk-update-icon-cache -f -t ~/.icons/${ICONS_NAME}
gsettings set org.gnome.desktop.interface icon-theme '${ICONS_NAME}'
gsettings set org.gnome.desktop.interface cursor-theme '${CURSORS_NAME}'
\`\`\`
EOF

# Pack into tar.xz
rm -f "${TARBALL}"
tar -C "${DIST_ROOT}" -cJf "${TARBALL}" "${TECH_SLUG}-icons-v${VERSION}"
rm -rf "${ICONS_DIST}"

echo "Icon pack ready: ${TARBALL}"
