/*
FILE: source/domino/decor/model/dg_decor_ids.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / decor/model/dg_decor_ids
RESPONSIBILITY: Implements `dg_decor_ids`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* DECOR stable identifiers (C89).
 *
 * Decor uses stable numeric IDs for deterministic generation, overrides, and
 * promotion links back to simulation entities.
 */
#ifndef DG_DECOR_IDS_H
#define DG_DECOR_IDS_H

#include "domino/core/types.h"

#include "core/det_invariants.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Stable decor item identifier (0 means invalid). */
typedef u64 dg_decor_id;

/* Content-defined decor type identifier (0 means invalid). */
typedef u64 dg_decor_type_id;

/* Content-defined rulepack identifier (0 means invalid). */
typedef u64 dg_decor_rulepack_id;

/* Stable override record identifier (0 means invalid). */
typedef u64 dg_decor_override_id;

/* Optional metadata tag identifier (0 means none). */
typedef u64 dg_decor_tag_id;

static int dg_decor_id_cmp(dg_decor_id a, dg_decor_id b) { return D_DET_CMP_U64(a, b); }
static int dg_decor_type_id_cmp(dg_decor_type_id a, dg_decor_type_id b) { return D_DET_CMP_U64(a, b); }
static int dg_decor_rulepack_id_cmp(dg_decor_rulepack_id a, dg_decor_rulepack_id b) { return D_DET_CMP_U64(a, b); }
static int dg_decor_override_id_cmp(dg_decor_override_id a, dg_decor_override_id b) { return D_DET_CMP_U64(a, b); }

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_DECOR_IDS_H */

