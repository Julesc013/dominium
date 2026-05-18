#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$root"

"$root/scripts/setup/check_kernel_purity.sh"
"$root/scripts/setup/doc_lint.sh"
"$root/scripts/setup/schema_freeze_check.sh"

registry="$root/source/dominium/setup/kernel/src/splat/dsk_splat_registry.cpp"
doc="$root/docs/setup/SPLAT_REGISTRY.md"

missing=0
if command -v rg >/dev/null 2>&1; then
    while IFS= read -r id; do
        if [[ -z "$id" ]]; then
            continue
        fi
        if ! rg -q "$id" "$doc"; then
            echo "MISSING SPLAT DOC: $id"
            missing=1
        fi
    done < <(rg -o "splat_[a-z0-9_]+" "$registry" | sort -u)
else
    echo "rg not found; skipping SPLAT registry doc scan"
fi
if [[ $missing -ne 0 ]]; then
    exit 1
fi

base="${SETUP_DOC_BASE:-HEAD~1}"
if git rev-parse "$base" >/dev/null 2>&1; then
    changed="$(git diff --name-only "$base" --)"
    tlv_changed=0
    doc_changed=0
    if echo "$changed" | rg -q "source/dominium/setup/kernel/include/dsk/dsk_contracts.h|include/dominium/core_installed_state.h"; then
        tlv_changed=1
    fi
    if echo "$changed" | rg -q "docs/setup/TLV_"; then
        doc_changed=1
    fi
    if [[ $tlv_changed -eq 1 && $doc_changed -eq 0 ]]; then
        echo "TLV schema changed without TLV docs update"
        exit 1
    fi
fi
