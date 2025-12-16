/*
FILE: source/domino/decor/model/dg_decor_rulepack.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / decor/model/dg_decor_rulepack
RESPONSIBILITY: Defines internal contract for `dg_decor_rulepack`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* DECOR rulepacks (C89).
 *
 * Rulepacks deterministically generate baseline decor items over host catalogs.
 */
#ifndef DG_DECOR_RULEPACK_H
#define DG_DECOR_RULEPACK_H

#include "domino/core/types.h"

#include "core/dg_pose.h"

#include "decor/model/dg_decor_ids.h"
#include "decor/model/dg_decor_item.h"
#include "decor/model/dg_decor_host.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_decor_host_selector {
    dg_decor_host_kind host_kind;
    d_bool             match_all_of_kind;
    dg_decor_host       exact; /* used when match_all_of_kind == D_FALSE */
} dg_decor_host_selector;

typedef struct dg_decor_spawn_template {
    dg_decor_type_id decor_type_id;
    u32              flags; /* DG_DECOR_ITEM_F_* subset */
    dg_pose          local_offset;
    dg_decor_tlv     params;
} dg_decor_spawn_template;

typedef struct dg_decor_rulepack {
    dg_decor_rulepack_id id;

    dg_decor_host_selector selector;

    /* Primary repeat interval in the host's param space (Q48.16).
     * interval_q <= 0 means: generate a single item at start_q.
     */
    dg_q interval_q;
    dg_q start_q;

    dg_decor_spawn_template *spawns; /* sorted by decor_type_id */
    u32                      spawn_count;
    u32                      spawn_capacity;
} dg_decor_rulepack;

void dg_decor_rulepack_init(dg_decor_rulepack *rp);
void dg_decor_rulepack_free(dg_decor_rulepack *rp);

int dg_decor_rulepack_reserve_spawns(dg_decor_rulepack *rp, u32 capacity);

/* Add or update a spawn template by decor_type_id (canonical order maintained). */
int dg_decor_rulepack_set_spawn(dg_decor_rulepack *rp, const dg_decor_spawn_template *st);

/* Deterministic host selector. */
d_bool dg_decor_rulepack_matches_host(const dg_decor_rulepack *rp, const dg_decor_host *host);

/* Content hash used for dirty tracking. */
u64 dg_decor_rulepack_hash(const dg_decor_rulepack *rp);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_DECOR_RULEPACK_H */

