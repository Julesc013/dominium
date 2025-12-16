/*
FILE: source/domino/sim/pkt/idmap/dg_idmap.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/pkt/idmap/dg_idmap
RESPONSIBILITY: Implements `dg_idmap`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic ID remap tables (C89).
 *
 * Purpose:
 * - Map external IDs (e.g., pack IDs) to stable runtime IDs.
 * - Remaps are loaded from deterministic TLV blobs; no "allocate new IDs" in
 *   simulation determinism paths.
 *
 * This module does not define pack discovery or filesystem loading.
 */
#ifndef DG_IDMAP_H
#define DG_IDMAP_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_idmap_entry {
    u64 external_id;
    u64 runtime_id;
} dg_idmap_entry;

typedef struct dg_idmap {
    dg_idmap_entry *entries;
    u32             count;
    u32             capacity;
} dg_idmap;

/* TLV format tags */
#define DG_IDMAP_TLV_ENTRY 1u /* payload: external_id:u64_le, runtime_id:u64_le */

void dg_idmap_init(dg_idmap *m);
void dg_idmap_free(dg_idmap *m);

/* Load mapping from TLV bytes (replaces existing contents). */
int dg_idmap_load_tlv(dg_idmap *m, const unsigned char *tlv, u32 tlv_len);

/* Lookup external id; returns 0 if found, 1 if not found, <0 on error. */
int dg_idmap_lookup(const dg_idmap *m, u64 external_id, u64 *out_runtime_id);

u32 dg_idmap_count(const dg_idmap *m);
const dg_idmap_entry *dg_idmap_at(const dg_idmap *m, u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_IDMAP_H */

