#!/usr/bin/env sh
set -eu

usage() {
  echo "Usage: $(basename "$0") --artifact-root DIR --out DIR --version X.Y.Z [--arch ARCH] [--maintainer TEXT] [--depends TEXT]"
}

ARTIFACT_ROOT=""
OUT_DIR=""
VERSION=""
ARCH="amd64"
MAINTAINER="Dominium <support@dominium.invalid>"
DEPENDS=""

while [ $# -gt 0 ]; do
  case "$1" in
    --artifact-root) ARTIFACT_ROOT="${2:-}"; shift 2;;
    --out) OUT_DIR="${2:-}"; shift 2;;
    --version) VERSION="${2:-}"; shift 2;;
    --arch) ARCH="${2:-}"; shift 2;;
    --maintainer) MAINTAINER="${2:-}"; shift 2;;
    --depends) DEPENDS="${2:-}"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1" >&2; usage; exit 1;;
  esac
done

if [ -z "$ARTIFACT_ROOT" ] || [ -z "$OUT_DIR" ] || [ -z "$VERSION" ]; then
  usage
  exit 1
fi

if ! command -v dpkg-deb >/dev/null 2>&1; then
  echo "dpkg-deb not found in PATH" >&2
  exit 1
fi

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
DEBIAN_DIR="$SCRIPT_DIR/debian"
WORK_ROOT="$OUT_DIR/_work_deb/root"
PKG_PATH="$OUT_DIR/dominium_${VERSION}_${ARCH}.deb"

mkdir -p "$OUT_DIR"
rm -rf "$WORK_ROOT"
mkdir -p "$WORK_ROOT/DEBIAN"
mkdir -p "$WORK_ROOT/opt/dominium/artifact_root"
cp -a "$ARTIFACT_ROOT/." "$WORK_ROOT/opt/dominium/artifact_root/"

sed -e "s/@VERSION@/${VERSION}/g" \
    -e "s/@ARCH@/${ARCH}/g" \
    -e "s/@MAINTAINER@/${MAINTAINER}/g" \
    -e "s/@DEPENDS@/${DEPENDS}/g" \
    "$DEBIAN_DIR/control" > "$WORK_ROOT/DEBIAN/control"

for f in postinst prerm postrm; do
  cp "$DEBIAN_DIR/$f" "$WORK_ROOT/DEBIAN/$f"
  chmod 0755 "$WORK_ROOT/DEBIAN/$f"
done

dpkg-deb --build "$WORK_ROOT" "$PKG_PATH"
echo "wrote $PKG_PATH"
