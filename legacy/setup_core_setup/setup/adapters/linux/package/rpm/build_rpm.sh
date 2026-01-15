#!/usr/bin/env sh
set -eu

usage() {
  echo "Usage: $(basename "$0") --artifact-root DIR --out DIR --version X.Y.Z [--arch ARCH] [--release N] [--requires TEXT]"
}

ARTIFACT_ROOT=""
OUT_DIR=""
VERSION=""
ARCH="x86_64"
RELEASE="1"
REQUIRES=""

while [ $# -gt 0 ]; do
  case "$1" in
    --artifact-root) ARTIFACT_ROOT="${2:-}"; shift 2;;
    --out) OUT_DIR="${2:-}"; shift 2;;
    --version) VERSION="${2:-}"; shift 2;;
    --arch) ARCH="${2:-}"; shift 2;;
    --release) RELEASE="${2:-}"; shift 2;;
    --requires) REQUIRES="${2:-}"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1" >&2; usage; exit 1;;
  esac
done

if [ -z "$ARTIFACT_ROOT" ] || [ -z "$OUT_DIR" ] || [ -z "$VERSION" ]; then
  usage
  exit 1
fi

if ! command -v rpmbuild >/dev/null 2>&1; then
  echo "rpmbuild not found in PATH" >&2
  exit 1
fi

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
SPEC_TEMPLATE="$SCRIPT_DIR/dominium.spec"
TOPDIR="$OUT_DIR/_work_rpm"

mkdir -p "$OUT_DIR"
rm -rf "$TOPDIR"
mkdir -p "$TOPDIR/BUILD" "$TOPDIR/BUILDROOT" "$TOPDIR/RPMS" "$TOPDIR/SOURCES" "$TOPDIR/SPECS" "$TOPDIR/SRPMS"

mkdir -p "$TOPDIR/SOURCES/dominium/artifact_root"
cp -a "$ARTIFACT_ROOT/." "$TOPDIR/SOURCES/dominium/artifact_root/"

SPEC_PATH="$TOPDIR/SPECS/dominium.spec"
sed -e "s/@VERSION@/${VERSION}/g" \
    -e "s/@RELEASE@/${RELEASE}/g" \
    -e "s/@REQUIRES@/${REQUIRES}/g" \
    -e "s/@ARCH@/${ARCH}/g" \
    "$SPEC_TEMPLATE" > "$SPEC_PATH"

rpmbuild -bb "$SPEC_PATH" \
  --define "_topdir ${TOPDIR}" \
  --define "_sourcedir ${TOPDIR}/SOURCES" \
  --define "_rpmdir ${OUT_DIR}" \
  --define "_srcrpmdir ${OUT_DIR}" \
  --define "_builddir ${TOPDIR}/BUILD" \
  --define "_buildrootdir ${TOPDIR}/BUILDROOT"

echo "rpm artifacts staged under $OUT_DIR"
