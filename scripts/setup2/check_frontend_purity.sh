#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/../.." && pwd)"
target_root="${root}/source/dominium/setup/frontends/adapters"

if ! command -v rg >/dev/null 2>&1; then
    echo "error: rg is required for frontend purity checks" >&2
    exit 1
fi

fail=0

check_pattern() {
    local pattern="$1"
    local label="$2"
    if rg -n -g "*.c" -g "*.cpp" -g "*.h" -g "*.m" -g "*.mm" "$pattern" "$target_root" >/dev/null; then
        echo "error: ${label}"
        rg -n -g "*.c" -g "*.cpp" -g "*.h" -g "*.m" -g "*.mm" "$pattern" "$target_root"
        fail=1
    fi
}

# Disallow kernel internals in UI adapters (use dominium-setup CLI instead).
check_pattern "setup/kernel/src" "kernel implementation includes detected in adapters"
check_pattern "setup/core/src" "core implementation includes detected in adapters"
check_pattern "setup/services/impl" "services implementation includes detected in adapters"
check_pattern "dsk_plan\\.h" "direct plan header include detected in adapters"
check_pattern "dsk_jobs\\.h" "direct jobs header include detected in adapters"
check_pattern "dsk_resume\\.h" "direct resume header include detected in adapters"
check_pattern "dsk_(install|upgrade|repair|uninstall|verify|status)_ex" "direct kernel execution calls detected in adapters"
check_pattern "dsk_apply_plan" "direct plan apply calls detected in adapters"

if [ "$fail" -ne 0 ]; then
    exit 1
fi
