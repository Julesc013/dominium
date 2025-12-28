#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAYOUT="${ROOT}/layout"
OUT_DIR="${OUT_DIR:-${ROOT}/out}"
VOL_NAME="${VOL_NAME:-DominiumSetup}"
IMG_PATH="${OUT_DIR}/${VOL_NAME}.img"

mkdir -p "${OUT_DIR}"

if command -v hdiutil >/dev/null 2>&1; then
    TZ=UTC hdiutil create \
        -fs HFS \
        -srcfolder "${LAYOUT}" \
        -volname "${VOL_NAME}" \
        -format UDRO \
        "${IMG_PATH}"
    echo "Image created: ${IMG_PATH}"
else
    echo "hdiutil not found; layout remains at ${LAYOUT}"
fi
