#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)
KERNEL_DIR="$ROOT_DIR/source/dominium/setup/kernel"

FAIL=0
for hdr in windows.h unistd.h sys/stat.h sys/types.h sys/wait.h; do
    matches=$(grep -R -n -I -F "$hdr" "$KERNEL_DIR" | grep -v "dsk_forbidden_includes.h" || true)
    if [ -n "$matches" ]; then
        echo "Forbidden header $hdr referenced:"
        printf "%s\n" "$matches"
        FAIL=1
    fi
done

exit $FAIL
