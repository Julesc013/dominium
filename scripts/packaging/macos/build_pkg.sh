#!/usr/bin/env bash
set -euo pipefail

APP_BUNDLE="${APP_BUNDLE:-}"
IDENTIFIER="${IDENTIFIER:-com.yourorg.dominium}"
VERSION="${VERSION:-0.0.0}"
OUT_DIR="${OUT_DIR:-}"
SCRIPTS_DIR="${SCRIPTS_DIR:-$(cd "$(dirname "$0")" && pwd)}"
INSTALL_LOCATION="${INSTALL_LOCATION:-/}"
SIGN_IDENTITY="${SIGN_IDENTITY:-}"

if [[ -z "$APP_BUNDLE" || -z "$OUT_DIR" ]]; then
  echo "Usage: APP_BUNDLE=/path/to/Dominium.app VERSION=1.0.0 OUT_DIR=/tmp/out $(basename "$0")"
  exit 1
fi

if [[ ! -d "$APP_BUNDLE" ]]; then
  echo "APP_BUNDLE not found: $APP_BUNDLE" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

STAGE_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/dominium-pkg-XXXXXX")"
trap 'rm -rf "$STAGE_ROOT"' EXIT

mkdir -p "$STAGE_ROOT/Applications"
ditto "$APP_BUNDLE" "$STAGE_ROOT/Applications/$(basename "$APP_BUNDLE")"

COMPONENT_PKG="$OUT_DIR/Dominium-${VERSION}.pkg"
DISTRIBUTION_PKG="$OUT_DIR/Dominium-${VERSION}-installer.pkg"

PKG_SCRIPTS=()
if [[ -x "$SCRIPTS_DIR/postinstall" ]]; then
  PKG_SCRIPTS=(--scripts "$SCRIPTS_DIR")
fi

PKG_SIGN=()
if [[ -n "$SIGN_IDENTITY" ]]; then
  PKG_SIGN=(--sign "$SIGN_IDENTITY")
fi

pkgbuild \
  --root "$STAGE_ROOT" \
  --identifier "$IDENTIFIER" \
  --version "$VERSION" \
  --install-location "$INSTALL_LOCATION" \
  "${PKG_SCRIPTS[@]}" \
  "${PKG_SIGN[@]}" \
  "$COMPONENT_PKG"

productbuild \
  --identifier "$IDENTIFIER" \
  --version "$VERSION" \
  --package "$COMPONENT_PKG" \
  "${PKG_SIGN[@]}" \
  "$DISTRIBUTION_PKG"

echo "Built component pkg: $COMPONENT_PKG"
echo "Built distribution pkg: $DISTRIBUTION_PKG"
