#!/bin/sh
set -e

TARGET="${1:-all}"
BUILD_DIR="${2:-build/msvc-debug}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LEGACY_SRC="$ROOT/source/dominium/setup/installers/windows_legacy"
OUT_DIR="$ROOT/dist/legacy/windows"

build_win9x() {
  echo "Building Win9x installer via CMake target legacy_win9x_installer"
  cmake --build "$BUILD_DIR" --target legacy_win9x_installer
}

build_dos() {
  if [ -z "${WATCOM:-}" ]; then
    echo "WATCOM not set. Install OpenWatcom and set WATCOM to the root path."
    exit 1
  fi
  mkdir -p "$OUT_DIR"
  WCL="$WATCOM/binw/wcl"
  if [ ! -x "$WCL" ]; then
    WCL="$WATCOM/binnt/wcl"
  fi
  if [ ! -x "$WCL" ]; then
    echo "wcl not found in $WATCOM"
    exit 1
  fi
  echo "Building DOS installer (INSTALL.EXE)..."
  "$WCL" -bt=dos -fe="$OUT_DIR/INSTALL.EXE" \
    "$LEGACY_SRC/dos/src/dos_main.c" \
    "$LEGACY_SRC/dos/src/dos_tui.c" \
    "$LEGACY_SRC/dos/src/dos_extract.c" \
    "$LEGACY_SRC/legacy_core/src/legacy_fs_dos.c" \
    "$LEGACY_SRC/legacy_core/src/legacy_invocation.c" \
    "$LEGACY_SRC/legacy_core/src/legacy_log.c" \
    "$LEGACY_SRC/legacy_core/src/legacy_manifest.c" \
    "$LEGACY_SRC/legacy_core/src/legacy_state.c" \
    "$LEGACY_SRC/legacy_core/src/legacy_txn.c" \
    "$LEGACY_SRC/legacy_core/src/legacy_uninstall.c" \
    "$LEGACY_SRC/legacy_core/src/legacy_verify.c"
}

build_win16() {
  if [ -z "${WATCOM:-}" ]; then
    echo "WATCOM not set. Install OpenWatcom and set WATCOM to the root path."
    exit 1
  fi
  mkdir -p "$OUT_DIR"
  WCL="$WATCOM/binw/wcl"
  WRC="$WATCOM/binw/wrc"
  if [ ! -x "$WCL" ]; then
    WCL="$WATCOM/binnt/wcl"
  fi
  if [ ! -x "$WRC" ]; then
    WRC="$WATCOM/binnt/wrc"
  fi
  if [ ! -x "$WCL" ] || [ ! -x "$WRC" ]; then
    echo "wcl/wrc not found in $WATCOM"
    exit 1
  fi
  echo "Building Win16 installer (SETUP.EXE)..."
  "$WRC" -r -fo="$OUT_DIR/win16_resources.res" "$LEGACY_SRC/win16/src/win16_resources.rc"
  "$WCL" -bt=windows -fe="$OUT_DIR/SETUP.EXE" \
    "$LEGACY_SRC/win16/src/win16_main.c" \
    "$LEGACY_SRC/win16/src/win16_gui.c" \
    "$OUT_DIR/win16_resources.res" \
    "$LEGACY_SRC/legacy_core/src/legacy_fs_win16.c" \
    "$LEGACY_SRC/legacy_core/src/legacy_invocation.c" \
    "$LEGACY_SRC/legacy_core/src/legacy_log.c" \
    "$LEGACY_SRC/legacy_core/src/legacy_manifest.c" \
    "$LEGACY_SRC/legacy_core/src/legacy_state.c" \
    "$LEGACY_SRC/legacy_core/src/legacy_txn.c" \
    "$LEGACY_SRC/legacy_core/src/legacy_uninstall.c" \
    "$LEGACY_SRC/legacy_core/src/legacy_verify.c"
}

case "$TARGET" in
  win9x) build_win9x ;;
  dos) build_dos ;;
  win16) build_win16 ;;
  all)
    build_win9x
    build_dos
    build_win16
    ;;
  *)
    echo "Unknown target: $TARGET"
    echo "Valid: dos | win16 | win9x | all"
    exit 1
    ;;
esac
