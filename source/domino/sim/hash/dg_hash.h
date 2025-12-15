/* Canonical hashing framework (C89).
 *
 * This module defines stable hash-domain identifiers and snapshot types used
 * for deterministic replay validation. Hashes must be computed from
 * canonicalized inputs (sorted iteration; explicit endianness; TLV-canon).
 *
 * Forbidden:
 * - hashing raw struct memory (padding/endianness)
 * - hashing pointer values
 * - hashing container internal order (unordered iteration)
 */
#ifndef DG_HASH_DOMAIN_H
#define DG_HASH_DOMAIN_H

#include "domino/core/types.h"
#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 dg_hash_domain_id;
typedef u64 dg_hash_value;

/* Built-in domain identifiers (stable; do not renumber). */
enum {
    DG_HASH_DOMAIN_SCHEDULER_STATE      = 1u,
    DG_HASH_DOMAIN_PACKET_STREAMS      = 2u,
    DG_HASH_DOMAIN_DELTA_COMMIT_RESULTS = 3u,
    DG_HASH_DOMAIN_DOMAIN_STATES       = 4u,
    DG_HASH_DOMAIN_GRAPH_STATES        = 5u,
    DG_HASH_DOMAIN_BELIEF_DB           = 6u,
    DG_HASH_DOMAIN_COMMS_QUEUES        = 7u,
    DG_HASH_DOMAIN_PROMO_LOD_STATE     = 8u
};

/* Domain classification flags used by replay validation modes. */
#define DG_HASH_DOMAIN_F_STRUCTURAL (1u << 0)
#define DG_HASH_DOMAIN_F_BEHAVIORAL (1u << 1)

typedef struct dg_hash_snapshot_entry {
    dg_hash_domain_id domain_id;
    dg_hash_value     value;
} dg_hash_snapshot_entry;

typedef struct dg_hash_snapshot {
    dg_hash_snapshot_entry *entries; /* caller-owned storage */
    u32                     count;
    u32                     capacity;
} dg_hash_snapshot;

void dg_hash_snapshot_init(dg_hash_snapshot *s, dg_hash_snapshot_entry *storage, u32 capacity);
void dg_hash_snapshot_clear(dg_hash_snapshot *s);

const dg_hash_snapshot_entry *dg_hash_snapshot_at(const dg_hash_snapshot *s, u32 index);
const dg_hash_snapshot_entry *dg_hash_snapshot_find(const dg_hash_snapshot *s, dg_hash_domain_id domain_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_HASH_DOMAIN_H */

