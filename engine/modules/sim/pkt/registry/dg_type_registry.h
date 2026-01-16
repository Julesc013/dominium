/*
FILE: source/domino/sim/pkt/registry/dg_type_registry.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/pkt/registry/dg_type_registry
RESPONSIBILITY: Defines internal contract for `dg_type_registry`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic type registries (C89).
 *
 * Registries are canonical sorted arrays of entries:
 *   primary: ascending type_id
 *   tie-break: ascending schema_id, then schema versions
 *
 * No hash-map iteration is permitted for determinism.
 */
#ifndef DG_TYPE_REGISTRY_H
#define DG_TYPE_REGISTRY_H

#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef int (*dg_type_validate_fn)(
    dg_type_id          type_id,
    dg_schema_id        schema_id,
    u16                 schema_ver,
    const unsigned char *payload,
    u32                 payload_len
);

typedef struct dg_type_registry_entry {
    dg_type_id           type_id;
    dg_schema_id         schema_id;
    u16                  schema_ver_min;
    u16                  schema_ver_max;
    const char          *name;        /* optional; not used for determinism */
    dg_type_validate_fn  validate_fn; /* optional; may be NULL */
} dg_type_registry_entry;

typedef struct dg_type_registry {
    dg_type_registry_entry *entries;
    u32                     count;
    u32                     capacity;
} dg_type_registry;

/* Category aliases (same mechanics, separate logical namespaces). */
typedef dg_type_registry dg_packet_type_registry;
typedef dg_type_registry dg_field_type_registry;
typedef dg_type_registry dg_event_type_registry;
typedef dg_type_registry dg_message_type_registry;
typedef dg_type_registry dg_observation_type_registry;
typedef dg_type_registry dg_intent_type_registry;
typedef dg_type_registry dg_delta_type_registry;
typedef dg_type_registry dg_probe_channel_registry;

void dg_type_registry_init(dg_type_registry *reg);
void dg_type_registry_free(dg_type_registry *reg);

/* Reserve internal storage (optional). */
int dg_type_registry_reserve(dg_type_registry *reg, u32 capacity);

/* Add an entry; maintains canonical sorted order. Returns 0 on success. */
int dg_type_registry_add(dg_type_registry *reg, const dg_type_registry_entry *entry);

u32 dg_type_registry_count(const dg_type_registry *reg);
const dg_type_registry_entry *dg_type_registry_at(const dg_type_registry *reg, u32 index);

/* Find an entry that supports (type_id, schema_id, schema_ver). Returns NULL if not found. */
const dg_type_registry_entry *dg_type_registry_find(
    const dg_type_registry *reg,
    dg_type_id              type_id,
    dg_schema_id            schema_id,
    u16                     schema_ver
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_TYPE_REGISTRY_H */

