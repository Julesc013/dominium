/*
FILE: tools/inspect/ledger_inspector.h
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / inspect
RESPONSIBILITY: Ledger inspection helpers for deterministic conservation checks.
ALLOWED DEPENDENCIES: Engine public headers and C89/C++98 standard headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic aggregation and ordering.
*/
#ifndef DOMINIUM_TOOLS_INSPECT_LEDGER_INSPECTOR_H
#define DOMINIUM_TOOLS_INSPECT_LEDGER_INSPECTOR_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "inspect_access.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct tool_ledger_entry {
    u64 entry_id;
    u64 asset_id;
    i64 delta;
    dom_act_time_t act;
    u32 required_knowledge;
} tool_ledger_entry;

typedef struct tool_ledger_inspector {
    const tool_ledger_entry* entries;
    u32 entry_count;
} tool_ledger_inspector;

typedef struct tool_ledger_balance_summary {
    i64 net;
    i64 inflow;
    i64 outflow;
    u32 entry_count;
} tool_ledger_balance_summary;

int tool_ledger_balance(const tool_ledger_inspector* insp,
                        u64 asset_id,
                        const tool_access_context* access,
                        tool_ledger_balance_summary* out_summary,
                        int* out_result);

int tool_ledger_is_balanced(const tool_ledger_inspector* insp,
                            u64 asset_id,
                            const tool_access_context* access,
                            d_bool* out_balanced,
                            int* out_result);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_TOOLS_INSPECT_LEDGER_INSPECTOR_H */
