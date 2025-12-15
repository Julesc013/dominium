/* Hash domain registry (C89).
 *
 * Domains are computed in canonical ascending domain_id order.
 */
#ifndef DG_HASH_REGISTRY_H
#define DG_HASH_REGISTRY_H

#include "domino/core/types.h"
#include "sim/pkt/dg_pkt_common.h"

#include "sim/hash/dg_hash.h"
#include "sim/hash/dg_hash_stream.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*dg_hash_domain_fn)(dg_hash_stream *s, dg_tick tick, void *user_ctx);

typedef struct dg_hash_registry_entry {
    dg_hash_domain_id domain_id;
    u32               flags; /* DG_HASH_DOMAIN_F_* */
    dg_hash_domain_fn fn;
    void             *user_ctx;
    u32               insert_index; /* stable tie-break */
} dg_hash_registry_entry;

typedef struct dg_hash_registry {
    dg_hash_registry_entry *entries;
    u32                     count;
    u32                     capacity;
    u32                     next_insert_index;
    u32                     probe_refused;
} dg_hash_registry;

void dg_hash_registry_init(dg_hash_registry *r);
void dg_hash_registry_free(dg_hash_registry *r);
int  dg_hash_registry_reserve(dg_hash_registry *r, u32 capacity);

int dg_hash_registry_add_domain(
    dg_hash_registry   *r,
    dg_hash_domain_id   domain_id,
    u32                 flags,
    dg_hash_domain_fn   fn,
    void               *user_ctx
);

u32 dg_hash_registry_count(const dg_hash_registry *r);
const dg_hash_registry_entry *dg_hash_registry_at(const dg_hash_registry *r, u32 index);
const dg_hash_registry_entry *dg_hash_registry_find(const dg_hash_registry *r, dg_hash_domain_id domain_id);
u32 dg_hash_registry_probe_refused(const dg_hash_registry *r);

/* Compute hashes for all registered domains for a tick.
 * out_snapshot must have caller-owned storage; entries are written in canonical
 * registry order (ascending domain_id).
 * Returns:
 *  0: success
 *  1: truncated (out_snapshot capacity < registry count)
 * <0: error
 */
int dg_hash_registry_compute_tick(
    const dg_hash_registry *r,
    dg_tick                 tick,
    dg_hash_snapshot       *out_snapshot
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_HASH_REGISTRY_H */

