/*
FILE: source/domino/world/d_serialize.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/d_serialize
RESPONSIBILITY: Defines internal contract for `d_serialize`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Determinism-sensitive (serialized bytes may be replayed/hashed); see `docs/SPEC_DETERMINISM.md`.
VERSIONING / ABI / DATA FORMAT NOTES: Legacy subsystem TLV stream; see `docs/DATA_FORMATS.md` (Subsystem TLV containers).
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

/* d_serialize_save_chunk_all
 * Purpose: Serialize all registered subsystem chunk payloads into a single TLV stream.
 * Parameters:
 *   w: World instance (non-NULL).
 *   chunk: Chunk instance to serialize (non-NULL).
 *   out: Output blob (non-NULL). Must not already own an allocated buffer.
 *        On success, `out->ptr` is heap-allocated and must be freed by the caller.
 * Return values / errors:
 *   0 on success; non-zero on failure (subsystem hook errors may be forwarded).
 * Determinism:
 *   Output bytes participate in replay/hash inputs. Encoding notes: `docs/DATA_FORMATS.md`.
 */
int d_serialize_save_chunk_all(
    struct d_world    *w,
    struct d_chunk    *chunk,
    struct d_tlv_blob *out
);

/* d_serialize_load_chunk_all
 * Purpose: Dispatch a chunk TLV stream to all registered subsystems.
 * Parameters:
 *   w: World instance (non-NULL).
 *   chunk: Chunk instance to populate (non-NULL).
 *   in: Input TLV stream. If `in->ptr` is NULL or `in->len` is 0, this is a no-op.
 * Return values / errors:
 *   0 on success; non-zero on malformed input or subsystem hook failure.
 * Notes:
 *   Unknown tags are ignored; missing tags mean the subsystem contributed no data.
 */
int d_serialize_load_chunk_all(
    struct d_world          *w,
    struct d_chunk          *chunk,
    const struct d_tlv_blob *in
);

/* d_serialize_save_instance_all
 * Purpose: Serialize all registered subsystem instance/global payloads into a single TLV stream.
 * Parameters:
 *   w: World instance (non-NULL).
 *   out: Output blob (non-NULL). Must not already own an allocated buffer.
 *        On success, `out->ptr` is heap-allocated and must be freed by the caller.
 * Return values / errors:
 *   0 on success; non-zero on failure (subsystem hook errors may be forwarded).
 * Determinism:
 *   Output bytes participate in replay/hash inputs. Encoding notes: `docs/DATA_FORMATS.md`.
 */
int d_serialize_save_instance_all(
    struct d_world    *w,
    struct d_tlv_blob *out
);

/* d_serialize_load_instance_all
 * Purpose: Dispatch an instance/global TLV stream to all registered subsystems.
 * Parameters:
 *   w: World instance (non-NULL).
 *   in: Input TLV stream. If `in->ptr` is NULL or `in->len` is 0, this is a no-op.
 * Return values / errors:
 *   0 on success; non-zero on malformed input or subsystem hook failure.
 * Notes:
 *   Unknown tags are ignored; missing tags mean the subsystem contributed no data.
 */
int d_serialize_load_instance_all(
    struct d_world          *w,
    const struct d_tlv_blob *in
);

#ifdef __cplusplus
}
#endif

#endif /* D_SERIALIZE_H */
