#!/usr/bin/env bash
set -euo pipefail

ARTIFACT_ROOT=""
OUT_DIR=""
VERSION="0.0.0"
IDENTIFIER="com.dominium.setup"
INVOCATION=""
PLATFORM=""
SIGN_IDENTITY=""
REPRODUCIBLE=0

SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
PKG_ROOT="$(cd "${SCRIPTS_DIR}/.." && pwd)"
DIST_TEMPLATE="${PKG_ROOT}/Distribution.xml"

chmod +x "${SCRIPTS_DIR}/postinstall" || true

usage() {
  echo "Usage: build_pkg.sh --artifact-root <dir> --out <dir> --version <x.y.z> [--identifier <id>] [--invocation <file>] [--platform <triple>] [--sign <identity>]"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --artifact-root) ARTIFACT_ROOT="$2"; shift 2 ;;
    --out) OUT_DIR="$2"; shift 2 ;;
    --version) VERSION="$2"; shift 2 ;;
    --identifier) IDENTIFIER="$2"; shift 2 ;;
    --invocation) INVOCATION="$2"; shift 2 ;;
    --platform) PLATFORM="$2"; shift 2 ;;
    --sign) SIGN_IDENTITY="$2"; shift 2 ;;
    --reproducible) REPRODUCIBLE=1; shift ;;
    *) echo "Unknown arg: $1"; usage; exit 1 ;;
  esac
done

if [[ -z "$ARTIFACT_ROOT" || -z "$OUT_DIR" ]]; then
  usage
  exit 1
fi

if [[ ! -d "$ARTIFACT_ROOT" ]]; then
  echo "artifact root not found: $ARTIFACT_ROOT" >&2
  exit 1
fi

if [[ ! -f "$DIST_TEMPLATE" ]]; then
  echo "Distribution.xml not found: $DIST_TEMPLATE" >&2
  exit 1
fi

if [[ -z "$PLATFORM" ]]; then
  arch="$(uname -m)"
  if [[ "$arch" == "arm64" || "$arch" == "aarch64" ]]; then
    PLATFORM="macos-arm64"
  else
    PLATFORM="macos-x64"
  fi
fi

mkdir -p "$OUT_DIR"

WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/dominium-pkg-XXXXXX")"
trap 'rm -rf "$WORK_DIR"' EXIT

STAGE_ROOT="$WORK_DIR/pkgroot"
PAYLOAD_ROOT="$STAGE_ROOT/Library/Application Support/Dominium/setup/artifact_root"
INVOCATION_PATH="$STAGE_ROOT/Library/Application Support/Dominium/setup/invocation.tlv"

mkdir -p "$(dirname "$PAYLOAD_ROOT")"
cp -R "$ARTIFACT_ROOT" "$PAYLOAD_ROOT"

mkdir -p "$(dirname "$INVOCATION_PATH")"
if [[ -n "$INVOCATION" ]]; then
  cp "$INVOCATION" "$INVOCATION_PATH"
else
  CLI_BIN="$ARTIFACT_ROOT/setup/dominium-setup"
  if [[ ! -x "$CLI_BIN" ]]; then
    echo "setup core not executable: $CLI_BIN" >&2
    exit 1
  fi
  (
    cd "$ARTIFACT_ROOT"
    "$CLI_BIN" --deterministic 1 export-invocation \
      --manifest "setup/manifests/product.dsumanifest" \
      --op install \
      --scope system \
      --platform "$PLATFORM" \
      --install-root "/Applications/Dominium" \
      --ui-mode gui \
      --frontend-id pkg \
      --out "$INVOCATION_PATH"
  )
fi

if [[ -n "${SOURCE_DATE_EPOCH:-}" && "$REPRODUCIBLE" -eq 1 ]]; then
  PY_BIN="$(command -v python3 || command -v python || true)"
  if [[ -n "$PY_BIN" ]]; then
    export STAGE_ROOT
    "$PY_BIN" - <<'PY'
import os
epoch = int(os.environ.get("SOURCE_DATE_EPOCH", "0") or "0")
root = os.environ.get("STAGE_ROOT", "")
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

COMPONENT_PKG="$WORK_DIR/DominiumSetup-${VERSION}.component.pkg"
DIST_PKG="$OUT_DIR/DominiumSetup-${VERSION}.pkg"
DIST_XML="$WORK_DIR/Distribution.xml"

sed -e "s/@VERSION@/${VERSION}/g" \
    -e "s/@IDENTIFIER@/${IDENTIFIER}/g" \
    -e "s/@COMPONENT_PKG@/$(basename "$COMPONENT_PKG")/g" \
    "$DIST_TEMPLATE" > "$DIST_XML"

PKG_SIGN=()
if [[ -n "$SIGN_IDENTITY" ]]; then
  PKG_SIGN=(--sign "$SIGN_IDENTITY")
fi

pkgbuild \
  --root "$STAGE_ROOT" \
  --identifier "$IDENTIFIER" \
  --version "$VERSION" \
  --install-location "/" \
  --scripts "$SCRIPTS_DIR" \
  "${PKG_SIGN[@]}" \
  "$COMPONENT_PKG"

productbuild \
  --distribution "$DIST_XML" \
  --package-path "$WORK_DIR" \
  --identifier "$IDENTIFIER" \
  --version "$VERSION" \
  "${PKG_SIGN[@]}" \
  "$DIST_PKG"

echo "Built pkg: $DIST_PKG"
