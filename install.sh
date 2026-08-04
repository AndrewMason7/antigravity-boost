#!/usr/bin/env bash
#
# antigravity-boost 1-Line Installer
#

set -e

DEST_DIR="$HOME/.gemini/config/plugins/antigravity-boost"

echo "🚀 Installing antigravity-boost plugin..."
mkdir -p "$HOME/.gemini/config/plugins"
rm -rf "$DEST_DIR"
cp -r "$(cd "$(dirname "$0")" && pwd)" "$DEST_DIR"
chmod +x "$DEST_DIR/scripts/"*.py "$DEST_DIR/scripts/core/"*.py 2>/dev/null || true

echo "✅ antigravity-boost installed successfully to $DEST_DIR"
echo "💡 Start Antigravity and type '/boost' anytime to check status!"
