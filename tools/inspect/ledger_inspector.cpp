/*
FILE: tools/inspect/ledger_inspector.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / inspect
RESPONSIBILITY: Implements deterministic ledger inspection utilities.
ALLOWED DEPENDENCIES: Engine public headers and C++98 standard headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic aggregation and ordering.
*/
#include "ledger_inspector.h"

int tool_ledger_balance(const tool_ledger_inspector* insp,
                        u64 asset_id,
                        const tool_access_context* access,
                        tool_ledger_balance_summary* out_summary,
                        int* out_result) {
    u32 i;
    i64 net = 0;
    i64 inflow = 0;
    i64 outflow = 0;
    u32 count = 0u;

    if (!insp || !out_summary || !out_result) {
        if (out_result) {
            *out_result = TOOL_INSPECT_INVALID;
        }
        return TOOL_INSPECT_INVALID;
    }
    if (!insp->entries || insp->entry_count == 0u) {
        *out_result = TOOL_INSPECT_NO_DATA;
        return TOOL_INSPECT_NO_DATA;
    }

    for (i = 0u; i < insp->entry_count; ++i) {
        const tool_ledger_entry* entry = &insp->entries[i];
        if (entry->asset_id != asset_id) {
            continue;
        }
        if (!tool_inspect_access_allows(access, entry->required_knowledge)) {
            *out_result = TOOL_INSPECT_REFUSED;
            return TOOL_INSPECT_REFUSED;
        }
        net += entry->delta;
        if (entry->delta >= 0) {
            inflow += entry->delta;
        } else {
            outflow += entry->delta;
        }
        count += 1u;
    }

    if (count == 0u) {
        *out_result = TOOL_INSPECT_NO_DATA;
        return TOOL_INSPECT_NO_DATA;
    }

    out_summary->net = net;
    out_summary->inflow = inflow;
    out_summary->outflow = outflow;
    out_summary->entry_count = count;
    *out_result = TOOL_INSPECT_OK;
    return TOOL_INSPECT_OK;
}

int tool_ledger_is_balanced(const tool_ledger_inspector* insp,
                            u64 asset_id,
                            const tool_access_context* access,
                            d_bool* out_balanced,
                            int* out_result) {
    tool_ledger_balance_summary summary;
    int res;
    if (!out_balanced) {
        if (out_result) {
            *out_result = TOOL_INSPECT_INVALID;
        }
        return TOOL_INSPECT_INVALID;
    }
    res = tool_ledger_balance(insp, asset_id, access, &summary, out_result);
    if (res != TOOL_INSPECT_OK) {
        return res;
    }
    *out_balanced = (summary.net == 0) ? D_TRUE : D_FALSE;
    return TOOL_INSPECT_OK;
}
