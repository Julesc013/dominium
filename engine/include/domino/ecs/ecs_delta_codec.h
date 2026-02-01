/*
FILE: include/domino/ecs/ecs_delta_codec.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / ecs/delta_codec
RESPONSIBILITY: Defines deterministic delta encoding over packed views.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Stable ordering and explicit byte layout.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md`.
*/
#ifndef DOMINO_ECS_DELTA_CODEC_H
#define DOMINO_ECS_DELTA_CODEC_H

#include "domino/ecs/ecs_packed_view.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_packed_delta_info {
    u64 view_id;
    u64 baseline_id;
    u32 entity_count;
    u32 stride;
    u32 changed_count;
    u32 bitmask_bytes;
    u32 payload_bytes;
    u32 total_bytes;
} dom_packed_delta_info;

int dom_delta_build(const dom_packed_view* baseline,
                    const dom_packed_view* current,
                    unsigned char* out_bytes,
                    u32 out_capacity,
                    dom_packed_delta_info* out_info);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_ECS_DELTA_CODEC_H */
