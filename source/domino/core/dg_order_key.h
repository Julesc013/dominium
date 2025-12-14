/* Canonical deterministic ordering key (C89).
 *
 * This key defines the global stable total ordering used by scheduler-owned
 * queues and the sorted delta-commit pipeline.
 *
 * All fields are fixed-size integers; comparison is lexicographic in the
 * declaration order (ascending).
 *
 * See: docs/SPEC_SIM_SCHEDULER.md
 */
#ifndef DG_ORDER_KEY_H
#define DG_ORDER_KEY_H

#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_order_key {
    u16         phase;        /* dg_phase as integer */
    u16         _pad16;       /* reserved, must be zero */
    dg_domain_id domain_id;
    dg_chunk_id  chunk_id;
    dg_entity_id entity_id;
    u64          component_id; /* optional sub-identifier; 0 allowed */
    dg_type_id   type_id;      /* packet type / delta type */
    u32          seq;          /* monotonic per producer; last-resort tie-break */
    u32          _pad32;       /* reserved, must be zero */
} dg_order_key;

void dg_order_key_clear(dg_order_key *k);
dg_order_key dg_order_key_make(
    u16          phase,
    dg_domain_id domain_id,
    dg_chunk_id  chunk_id,
    dg_entity_id entity_id,
    u64          component_id,
    dg_type_id   type_id,
    u32          seq
);

/* Total order comparator: returns -1/0/1 like strcmp. */
int dg_order_key_cmp(const dg_order_key *a, const dg_order_key *b);

/* Convenience for deriving keys from packet headers. component_id may be 0. */
dg_order_key dg_order_key_from_pkt_hdr(u16 phase, const dg_pkt_hdr *hdr, u64 component_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_ORDER_KEY_H */

