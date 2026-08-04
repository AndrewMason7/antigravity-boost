#!/usr/bin/env bash
#
# antigravity-boost 1-Line Installer
#

set -e

DEST_DIR="$HOME/.gemini/config/plugins/antigravity-boost"

echo "🚀 Installing antigravity-boost plugin..."
mkdir -p "$HOME/.gemini/config/plugins"

# Remove existing installation safely
rm -rf "$DEST_DIR"

# Download repository into DEST_DIR (works cleanly whether piped via curl or run locally)
if command -v git >/dev/null 2>&1; then
    git clone --depth 1 https://github.com/AndrewMason7/antigravity-boost.git "$DEST_DIR"
else
    mkdir -p "$DEST_DIR"
    curl -sSL https://github.com/AndrewMason7/antigravity-boost/archive/refs/heads/main.tar.gz | tar -xz -C "$DEST_DIR" --strip-components=1
fi

chmod +x "$DEST_DIR/scripts/"*.py "$DEST_DIR/scripts/core/"*.py 2>/dev/null || true

echo "✅ antigravity-boost installed successfully to $DEST_DIR"
echo "💡 Start Antigravity and type '/boost' anytime to check status!"
