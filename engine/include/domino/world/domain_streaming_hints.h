/*
FILE: include/domino/world/domain_streaming_hints.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/domain_streaming_hints
RESPONSIBILITY: Non-authoritative domain streaming and refinement hinting.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Deterministic ordering and budgeted emission only.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by DOMAIN3 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_DOMAIN_STREAMING_HINTS_H
#define DOMINO_WORLD_DOMAIN_STREAMING_HINTS_H

#include "domino/world/domain_query.h"

#ifdef __cplusplus
extern "C" {
#endif

enum dom_domain_streaming_hint_kind {
    DOM_DOMAIN_HINT_REFINE_SOON = 1,
    DOM_DOMAIN_HINT_COLLAPSE_OK = 2
};

enum dom_domain_streaming_hint_flags {
    DOM_DOMAIN_HINT_FLAG_ADVISORY = 1u << 0u
};

typedef struct dom_domain_streaming_hint {
    dom_domain_id   domain_id;
    u64             tile_id;
    u32             resolution; /* dom_domain_resolution */
    dom_domain_aabb bounds;
    u32             kind;        /* dom_domain_streaming_hint_kind */
    u32             priority;
    u32             flags;
} dom_domain_streaming_hint;

typedef struct dom_domain_streaming_hint_set {
    dom_domain_streaming_hint* hints;
    u32 count;
    u32 capacity;
    u32 overflow;
} dom_domain_streaming_hint_set;

void dom_domain_streaming_hint_set_init(dom_domain_streaming_hint_set* set,
                                        dom_domain_streaming_hint* storage,
                                        u32 capacity);
void dom_domain_streaming_hint_set_clear(dom_domain_streaming_hint_set* set);
int dom_domain_streaming_hint_set_add(dom_domain_streaming_hint_set* set,
                                      const dom_domain_streaming_hint* hint);

int dom_domain_streaming_emit_hints(const dom_domain_volume* volumes,
                                    u32 volume_count,
                                    dom_domain_budget* budget,
                                    dom_domain_streaming_hint_set* out_hints);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_DOMAIN_STREAMING_HINTS_H */
