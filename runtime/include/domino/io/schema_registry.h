/*
FILE: include/domino/io/schema_registry.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / io/schema_registry
RESPONSIBILITY: Defines the public contract for `schema_registry` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Determinism-supporting (schema ids and tag sets are hashed/validated); see `docs/specs/SPEC_CONTAINER_TLV.md` and `docs/specs/SPEC_DETERMINISM.md`.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_IO_SCHEMA_REGISTRY_H_INCLUDED
#define DOMINO_IO_SCHEMA_REGISTRY_H_INCLUDED
/*
 * Deterministic serialization schema registry (C89/C++98 visible).
 *
 * Treat all serialization as ABI: chunk type IDs, chunk versions, and TLV tag
 * IDs are stable contracts.
 */

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/*------------------------------------------------------------
 * Registry domains (bitmask)
 *------------------------------------------------------------*/

#define DOM_SCHEMA_DOMAIN_SIM     ((u32)0x00000001u)
#define DOM_SCHEMA_DOMAIN_CONTENT ((u32)0x00000002u)
#define DOM_SCHEMA_DOMAIN_CONFIG  ((u32)0x00000004u)
#define DOM_SCHEMA_DOMAIN_NET     ((u32)0x00000008u)

/*------------------------------------------------------------
 * Chunk type IDs (u32, stable; do not renumber)
 *------------------------------------------------------------*/

enum {
    /* Config/profile persistence */
    DOM_CHUNK_INSTANCE_CONFIG_V1 = 0x00001001u,

    /* Saves */
    DOM_CHUNK_SAVE_INSTANCE_V1 = 0x00002001u,

    /* Replays */
    DOM_CHUNK_REPLAY_V1 = 0x00003001u,

    /* Packs/mods/manifests (record streams of schema-id-tagged records) */
    DOM_CHUNK_CONTENT_STREAM_V1 = 0x00004001u,

    /* Net handshake payload */
    DOM_CHUNK_NET_HANDSHAKE_V1 = 0x00005001u
};

/*------------------------------------------------------------
 * Chunk-local TLV tag IDs (stable)
 *------------------------------------------------------------*/

/* Instance config payload tags (within DOM_CHUNK_INSTANCE_CONFIG_V1). */
enum {
    DOM_TAG_INSTANCE_ID            = 1u,
    DOM_TAG_WORLD_SEED             = 2u,
    DOM_TAG_WORLD_SIZE_M           = 3u,
    DOM_TAG_VERTICAL_MIN_M         = 4u,
    DOM_TAG_VERTICAL_MAX_M         = 5u,
    DOM_TAG_SUITE_VERSION          = 6u,
    DOM_TAG_CORE_VERSION           = 7u,
    DOM_TAG_PACK_ENTRY             = 20u,
    DOM_TAG_MOD_ENTRY              = 21u,
    DOM_TAG_LAST_PRODUCT           = 30u,
    DOM_TAG_LAST_PRODUCT_VERSION   = 31u
};

/* Replay payload tags (within DOM_CHUNK_REPLAY_V1). */
enum {
    DOM_TAG_REPLAY_FRAME = 1u
};

/* Handshake payload tags (within DOM_CHUNK_NET_HANDSHAKE_V1). */
enum {
    DOM_TAG_HANDSHAKE_ENGINE_BUILD_ID         = 1u,  /* UTF-8 + NUL */
    DOM_TAG_HANDSHAKE_ENGINE_GIT_HASH         = 2u,  /* UTF-8 + NUL (optional) */
    DOM_TAG_HANDSHAKE_SIM_SCHEMA_ID           = 3u,  /* u64_le */
    DOM_TAG_HANDSHAKE_SIM_SCHEMA_VERSION      = 4u,  /* u32_le (optional) */
    DOM_TAG_HANDSHAKE_DET_GRADE               = 5u,  /* u32_le (dom_det_grade) */
    DOM_TAG_HANDSHAKE_LOCKSTEP_STRICT         = 6u,  /* u32_le (0/1) */
    DOM_TAG_HANDSHAKE_CONTENT_HASH            = 7u   /* repeated u64_le */
};

/*------------------------------------------------------------
 * Registry API
 *------------------------------------------------------------*/

/* dom_chunk_schema_desc
 * Purpose: Descriptor for one chunk schema (type id + version) and its TLV tag set.
 * Fields:
 *   chunk_type_id: Stable chunk type id (`u32` ABI).
 *   chunk_version: Stable chunk schema version (`u16` ABI).
 *   domain_mask: Bitmask of `DOM_SCHEMA_DOMAIN_*` describing the usage domain(s).
 *   tlv_tags/tlv_tag_count: Optional list of chunk-local TLV tag ids used for schema hashing.
 * Notes:
 * - For deterministic schema id hashing, tags are treated as a set (sorted before hashing).
 * - Serialization ABI rules are specified in `docs/specs/SPEC_CONTAINER_TLV.md`.
 */
typedef struct dom_chunk_schema_desc {
    u32        chunk_type_id;
    u16        chunk_version;
    u32        domain_mask;
    const u32* tlv_tags;
    u32        tlv_tag_count;
} dom_chunk_schema_desc;

/* dom_schema_registry
 * Purpose: Return a stable pointer to the compiled-in schema registry list.
 * Parameters:
 *   out_count (out, optional): Receives number of entries when non-NULL.
 * Returns:
 *   Pointer to an internal static array of `dom_chunk_schema_desc`.
 * Ownership:
 *   Returned pointer is borrowed and valid for the lifetime of the process.
 */
const dom_chunk_schema_desc* dom_schema_registry(u32* out_count);

/* Compute a deterministic schema id (FNV-1a 64-bit) over registry entries
 * matching domain_mask, independent of registry declaration order.
 */
/* dom_schema_id_for_domain
 * Purpose: Compute a deterministic schema id for a domain mask.
 * Parameters:
 *   domain_mask (in): Domain selector bitmask (`DOM_SCHEMA_DOMAIN_*`).
 * Returns:
 *   64-bit schema id, or 0 on allocation failure / no matching entries.
 * Determinism:
 *   Hash input uses explicit little-endian encodings and sorted tag sets.
 */
u64 dom_schema_id_for_domain(u32 domain_mask);

/* dom_sim_schema_id
 * Purpose: Convenience for `dom_schema_id_for_domain(DOM_SCHEMA_DOMAIN_SIM)`.
 * Returns:
 *   64-bit schema id, or 0 on allocation failure / empty registry.
 */
u64 dom_sim_schema_id(void);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_IO_SCHEMA_REGISTRY_H_INCLUDED */
