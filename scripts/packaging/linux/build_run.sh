#!/usr/bin/env bash
set -euo pipefail

DIST_DIR="${DIST_DIR:-}"
VERSION="${VERSION:-0.0.0}"
OUT_DIR="${OUT_DIR:-}"
STUB_TEMPLATE="${STUB_TEMPLATE:-$(cd "$(dirname "$0")" && pwd)/dominium-installer.sh.in}"

if [[ -z "$DIST_DIR" || -z "$OUT_DIR" ]]; then
  echo "Usage: DIST_DIR=/path/to/stage OUT_DIR=/path/to/out VERSION=1.0.0 $(basename "$0")"
  exit 1
fi

if [[ ! -d "$DIST_DIR" ]]; then
  echo "DIST_DIR not found: $DIST_DIR" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/dominium-run-XXXXXX")"
trap 'rm -rf "$WORK_DIR"' EXIT

STUB="$WORK_DIR/installer.sh"
sed "s/@DOMINIUM_VERSION@/${VERSION}/g" "$STUB_TEMPLATE" > "$STUB"
chmod +x "$STUB"

PAYLOAD="$WORK_DIR/payload.tar.gz"
tar -C "$DIST_DIR" -czf "$PAYLOAD" .

OUT_RUN="$OUT_DIR/Dominium-${VERSION}.run"
cat "$STUB" > "$OUT_RUN"
echo "__DOMINIUM_ARCHIVE_BELOW__" >> "$OUT_RUN"
cat "$PAYLOAD" >> "$OUT_RUN"
chmod +x "$OUT_RUN"

echo "Built self-extracting installer: $OUT_RUN"
