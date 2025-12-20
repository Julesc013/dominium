#!/usr/bin/env sh
set -eu

BUILD_DIR="${1:-build/debug}"
VERSION="${2:-0.1.0}"

ARTIFACT_DIR="dist/artifacts/dominium-${VERSION}"
PORTABLE_OUT="dist/portable"

python scripts/packaging/pipeline.py assemble --build-dir "${BUILD_DIR}" --out "${ARTIFACT_DIR}" --version "${VERSION}" --manifest-template assets/setup/manifests/product.template.json
python scripts/packaging/pipeline.py portable --artifact "${ARTIFACT_DIR}" --out "${PORTABLE_OUT}" --version "${VERSION}"
