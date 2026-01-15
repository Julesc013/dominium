#!/bin/sh
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
PKG_DIR="${ROOT_DIR}/pkg"
OUT_DIR="${ROOT_DIR}/out"

mkdir -p "${OUT_DIR}"

echo "Stub build: stage pkg layout under ${PKG_DIR} and run pkgbuild/productbuild here."
echo "This script is a placeholder for SR-7; it does not invoke packaging tools."
