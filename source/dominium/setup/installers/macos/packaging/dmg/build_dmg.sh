#!/usr/bin/env bash
set -euo pipefail

ARTIFACT_ROOT=""
OUT_DIR=""
VERSION="0.0.0"
PKG_PATH=""
VOLUME_NAME="Dominium Setup"
PORTABLE=""
DOCS_DIR=""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LAYOUT_DIR="${SCRIPT_DIR}/dmg_layout"

usage() {
  echo "Usage: build_dmg.sh --artifact-root <dir> --out <dir> --version <x.y.z> --pkg <pkg> [--volume-name <name>] [--portable <path>] [--docs <dir>]"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --artifact-root) ARTIFACT_ROOT="$2"; shift 2 ;;
    --out) OUT_DIR="$2"; shift 2 ;;
    --version) VERSION="$2"; shift 2 ;;
    --pkg) PKG_PATH="$2"; shift 2 ;;
    --volume-name) VOLUME_NAME="$2"; shift 2 ;;
    --portable) PORTABLE="$2"; shift 2 ;;
    --docs) DOCS_DIR="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; usage; exit 1 ;;
  esac
done

if [[ -z "$ARTIFACT_ROOT" || -z "$OUT_DIR" || -z "$PKG_PATH" ]]; then
  usage
  exit 1
fi

if [[ ! -d "$ARTIFACT_ROOT" ]]; then
  echo "artifact root not found: $ARTIFACT_ROOT" >&2
  exit 1
fi
if [[ ! -f "$PKG_PATH" ]]; then
  echo "pkg not found: $PKG_PATH" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/dominium-dmg-XXXXXX")"
trap 'rm -rf "$WORK_DIR"' EXIT

DMG_ROOT="$WORK_DIR/dmgroot"
mkdir -p "$DMG_ROOT"

cp "$PKG_PATH" "$DMG_ROOT/"

if [[ -n "$PORTABLE" && -f "$PORTABLE" ]]; then
  cp "$PORTABLE" "$DMG_ROOT/"
fi

if [[ -z "$DOCS_DIR" ]]; then
  DOCS_DIR="$ARTIFACT_ROOT/docs"
fi
if [[ -d "$DOCS_DIR" ]]; then
  cp -R "$DOCS_DIR" "$DMG_ROOT/docs"
fi

if [[ -f "$ARTIFACT_ROOT/setup/SHA256SUMS" ]]; then
  cp "$ARTIFACT_ROOT/setup/SHA256SUMS" "$DMG_ROOT/"
fi
if [[ -f "$ARTIFACT_ROOT/setup/artifact_manifest.json" ]]; then
  cp "$ARTIFACT_ROOT/setup/artifact_manifest.json" "$DMG_ROOT/"
fi

if [[ -d "$LAYOUT_DIR" ]]; then
  cp -R "$LAYOUT_DIR/." "$DMG_ROOT/"
fi

if [[ -n "${SOURCE_DATE_EPOCH:-}" ]]; then
  PY_BIN="$(command -v python3 || command -v python || true)"
  if [[ -n "$PY_BIN" ]]; then
    export DMG_ROOT
    "$PY_BIN" - <<'PY'
import os
epoch = int(os.environ.get("SOURCE_DATE_EPOCH", "0") or "0")
root = os.environ.get("DMG_ROOT", "")
if epoch > 0 and root:
    for cur_root, dirs, files in os.walk(root):
        for name in dirs + files:
            p = os.path.join(cur_root, name)
            try:
                os.utime(p, (epoch, epoch))
            except Exception:
                pass
    try:
        os.utime(root, (epoch, epoch))
    except Exception:
        pass
PY
  fi
fi

DMG_OUT="$OUT_DIR/DominiumSetup-${VERSION}.dmg"
hdiutil create -volname "$VOLUME_NAME" -srcfolder "$DMG_ROOT" -ov -format UDZO "$DMG_OUT"

echo "Built dmg: $DMG_OUT"
