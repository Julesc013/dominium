/* Propagator cache scaffolding (C89).
 *
 * Propagators may maintain derived caches for higher representations (R1–R3).
 * This module provides minimal bookkeeping helpers only (no semantics).
 */
#ifndef DG_PROP_CACHE_H
#define DG_PROP_CACHE_H

#include "domino/core/types.h"

#include "sim/lod/dg_rep.h"
#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_prop_cache {
    dg_rep_state rep_state;
    dg_tick      last_built_tick;
    u32          dirty; /* 0/1 */
} dg_prop_cache;

void dg_prop_cache_init(dg_prop_cache *c);
void dg_prop_cache_mark_dirty(dg_prop_cache *c);
void dg_prop_cache_mark_built(dg_prop_cache *c, dg_rep_state rep_state, dg_tick tick);
d_bool dg_prop_cache_is_dirty(const dg_prop_cache *c);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_PROP_CACHE_H */

