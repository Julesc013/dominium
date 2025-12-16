/*
FILE: source/domino/world/d_serialize.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/d_serialize
RESPONSIBILITY: Implements `d_serialize`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Unified subsystem serialization orchestrator (C89). */
#ifndef D_SERIALIZE_H
#define D_SERIALIZE_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"

#ifdef __cplusplus
extern "C" {
#endif

struct d_world;
struct d_chunk;

/* Save all subsystems’ chunk data into a container buffer. */
int d_serialize_save_chunk_all(
    struct d_world    *w,
    struct d_chunk    *chunk,
    struct d_tlv_blob *out
);

/* Load all subsystems’ chunk data from a container buffer. */
int d_serialize_load_chunk_all(
    struct d_world          *w,
    struct d_chunk          *chunk,
    const struct d_tlv_blob *in
);

/* Save all subsystems’ instance/global data. */
int d_serialize_save_instance_all(
    struct d_world    *w,
    struct d_tlv_blob *out
);

/* Load all subsystems’ instance/global data. */
int d_serialize_load_instance_all(
    struct d_world          *w,
    const struct d_tlv_blob *in
);

#ifdef __cplusplus
}
#endif

#endif /* D_SERIALIZE_H */
