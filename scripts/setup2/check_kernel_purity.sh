#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)
KERNEL_DIR="$ROOT_DIR/source/dominium/setup/kernel"

FAIL=0
for hdr in windows.h unistd.h sys/stat.h sys/types.h sys/wait.h; do
    if grep -R -n -I -F "$hdr" "$KERNEL_DIR" >/dev/null 2>&1; then
        echo "Forbidden header $hdr referenced:"
        grep -R -n -I -F "$hdr" "$KERNEL_DIR" || true
        FAIL=1
    fi
done

exit $FAIL
