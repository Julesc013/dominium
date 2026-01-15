#!/usr/bin/env bash
set -euo pipefail

APP_BUNDLE="${APP_BUNDLE:-}"
OUTPUT_DMG="${OUTPUT_DMG:-}"
VOLUME_NAME="${VOLUME_NAME:-Dominium}"
PKG_PATH="${PKG_PATH:-}"

if [[ -z "$APP_BUNDLE" || -z "$OUTPUT_DMG" ]]; then
  echo "Usage: APP_BUNDLE=/path/to/Dominium.app OUTPUT_DMG=/tmp/Dominium.dmg $(basename "$0")"
  exit 1
fi

if [[ ! -d "$APP_BUNDLE" ]]; then
  echo "APP_BUNDLE not found: $APP_BUNDLE" >&2
  exit 1
fi

WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/dominium-dmg-XXXXXX")"
trap 'rm -rf "$WORK_DIR"' EXIT

APP_NAME="$(basename "$APP_BUNDLE")"
ditto "$APP_BUNDLE" "$WORK_DIR/$APP_NAME"
ln -s /Applications "$WORK_DIR/Applications"

if [[ -n "$PKG_PATH" && -f "$PKG_PATH" ]]; then
  cp "$PKG_PATH" "$WORK_DIR/"
fi

hdiutil create -volname "$VOLUME_NAME" -srcfolder "$WORK_DIR" -ov -format UDZO "$OUTPUT_DMG"

echo "Built DMG: $OUTPUT_DMG"
