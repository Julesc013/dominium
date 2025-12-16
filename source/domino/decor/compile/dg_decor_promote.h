/*
FILE: source/domino/decor/compile/dg_decor_promote.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / decor/compile/dg_decor_promote
RESPONSIBILITY: Implements `dg_decor_promote`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* DECOR promotion plumbing (C89).
 *
 * Promotion is optional: decor defaults to render-only tiles/instances.
 * When promotion is requested for certain decor types, this module emits
 * stable ordered promotion requests suitable for feeding into the sorted
 * delta-commit pipeline.
 *
 * No gameplay semantics or handlers are implemented here.
 */
#ifndef DG_DECOR_PROMOTE_H
#define DG_DECOR_PROMOTE_H

#include "domino/core/types.h"

#include "core/dg_order_key.h"
#include "sim/pkt/dg_pkt_common.h"

#include "decor/model/dg_decor_ids.h"
#include "decor/compile/dg_decor_instances.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Promotion request delta type id (taxonomy placeholder). */
#define DG_DECOR_DELTA_PROMOTE ((dg_type_id)0x1001u)

typedef struct dg_decor_promotion_req {
    dg_order_key    key;
    dg_chunk_id     chunk_id;
    dg_decor_id      decor_id;
    dg_decor_type_id decor_type_id;
} dg_decor_promotion_req;

typedef struct dg_decor_promotion_list {
    dg_decor_promotion_req *items;
    u32                    count;
    u32                    capacity;
} dg_decor_promotion_list;

void dg_decor_promotion_list_init(dg_decor_promotion_list *l);
void dg_decor_promotion_list_free(dg_decor_promotion_list *l);
void dg_decor_promotion_list_clear(dg_decor_promotion_list *l);
int  dg_decor_promotion_list_reserve(dg_decor_promotion_list *l, u32 capacity);

/* Collect promotable instances into a canonical request list.
 *
 * Ordering is canonical dg_order_key order (ascending).
 */
int dg_decor_promote_collect(
    dg_decor_promotion_list *out,
    const dg_decor_instances *instances,
    dg_tick                   tick,
    dg_domain_id              domain_id
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_DECOR_PROMOTE_H */

