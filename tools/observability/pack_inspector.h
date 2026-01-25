/*
FILE: tools/observability/pack_inspector.h
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / observability
RESPONSIBILITY: Read-only inspection of packs, capabilities, and overrides.
ALLOWED DEPENDENCIES: Engine public headers and tools headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic filtering and ordering.
*/
#ifndef DOMINIUM_TOOLS_OBSERVABILITY_PACK_INSPECTOR_H
#define DOMINIUM_TOOLS_OBSERVABILITY_PACK_INSPECTOR_H

#include "domino/core/types.h"
#include "observation_store.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct tool_pack_inspector {
    const tool_observation_store* store;
    u32 cursor;
} tool_pack_inspector;

int tool_pack_inspector_init(tool_pack_inspector* insp,
                             const tool_observation_store* store);
int tool_pack_inspector_next(tool_pack_inspector* insp,
                             tool_pack_record* out_pack);
int tool_pack_inspector_overrides(const tool_observation_store* store,
                                  tool_pack_record* out_packs,
                                  u32 max_packs,
                                  u32* out_count);
int tool_pack_inspector_pack_capabilities(const tool_observation_store* store,
                                          u64 pack_id,
                                          tool_capability_record* out_caps,
                                          u32 max_caps,
                                          u32* out_count);
int tool_pack_inspector_missing_capabilities(const tool_observation_store* store,
                                             const u64* required_ids,
                                             u32 required_count,
                                             u64* out_missing,
                                             u32 max_missing,
                                             u32* out_count);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_TOOLS_OBSERVABILITY_PACK_INSPECTOR_H */
