/*
FILE: tools/observability/institution_inspector.h
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / observability
RESPONSIBILITY: Read-only inspection of institution state, constraints, contracts, enforcement, and collapse.
ALLOWED DEPENDENCIES: Engine public headers and tools headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic filtering and iteration.
*/
#ifndef DOMINIUM_TOOLS_OBSERVABILITY_INSTITUTION_INSPECTOR_H
#define DOMINIUM_TOOLS_OBSERVABILITY_INSTITUTION_INSPECTOR_H

#include "domino/core/types.h"
#include "inspect_access.h"
#include "observation_store.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct tool_institution_inspector {
    const tool_observation_store* store;
    tool_access_context access;
    u64 institution_id;
    u32 constraint_cursor;
    u32 contract_cursor;
    u32 delegation_cursor;
    u32 enforcement_cursor;
    u32 collapse_cursor;
} tool_institution_inspector;

int tool_institution_inspector_init(tool_institution_inspector* insp,
                                    const tool_observation_store* store,
                                    const tool_access_context* access,
                                    u64 institution_id);
int tool_institution_inspector_reset(tool_institution_inspector* insp);
int tool_institution_inspector_state(const tool_institution_inspector* insp,
                                     tool_institution_state* out_state);
int tool_institution_inspector_next_constraint(tool_institution_inspector* insp,
                                               tool_constraint_record* out_record);
int tool_institution_inspector_next_contract(tool_institution_inspector* insp,
                                             tool_contract_record* out_record);
int tool_institution_inspector_next_delegation(tool_institution_inspector* insp,
                                               tool_delegation_record* out_record);
int tool_institution_inspector_next_enforcement(tool_institution_inspector* insp,
                                                tool_enforcement_record* out_record);
int tool_institution_inspector_next_collapse(tool_institution_inspector* insp,
                                             tool_institution_collapse_record* out_record);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_TOOLS_OBSERVABILITY_INSTITUTION_INSPECTOR_H */
