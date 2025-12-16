/*
FILE: source/domino/sim/bus/dg_event_bus.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/bus/dg_event_bus
RESPONSIBILITY: Implements `dg_event_bus`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic event bus (C89).
 *
 * Events are immutable packets buffered during production phases and delivered
 * during a dedicated scheduler boundary (see docs/SPEC_FIELDS_EVENTS.md).
 */
#ifndef DG_EVENT_BUS_H
#define DG_EVENT_BUS_H

#include "sim/pkt/dg_pkt_event.h"
#include "sim/pkt/registry/dg_type_registry.h"
#include "sim/sched/dg_budget.h"
#include "sim/sched/dg_work_queue.h"

#ifdef __cplusplus
extern "C" {
#endif

struct dg_sched;

typedef void (*dg_event_bus_sub_fn)(const dg_pkt_event *ev, void *user_ctx);

typedef struct dg_event_bus_sub {
    dg_type_id           event_type_id;
    dg_event_bus_sub_fn  fn;
    void                *user_ctx;
    u64                  priority_key;
    u32                  insert_index;
} dg_event_bus_sub;

typedef struct dg_event_bus_record {
    dg_pkt_hdr      hdr;           /* copied */
    unsigned char  *payload_owned; /* owned; freed when fully delivered */
    u32             payload_len;
    d_bool          in_use;
} dg_event_bus_record;

typedef struct dg_event_bus {
    /* Optional type registry (when non-empty, publishes must validate). */
    dg_event_type_registry type_registry;

    dg_event_bus_sub *subs;
    u32               sub_count;
    u32               sub_capacity;
    u32               next_sub_insert;

    dg_event_bus_record *records;
    u32                  record_count;
    u32                  record_capacity;

    u32 *free_record_ids;
    u32  free_record_count;
    u32  free_record_capacity;

    dg_work_queue deliver_q; /* one item per pending event */

    /* Probes/counters (no logging). */
    u32 probe_events_published;
    u32 probe_events_delivered; /* subscriber deliveries */
    u32 probe_deferred_deliveries;
} dg_event_bus;

void dg_event_bus_init(dg_event_bus *bus);
void dg_event_bus_free(dg_event_bus *bus);

/* Preallocate bounded storage (optional; may be called with zeros). */
int dg_event_bus_reserve(dg_event_bus *bus, u32 subs_cap, u32 records_cap, u32 deliver_queue_cap);

/* Register an event type (optional). */
int dg_event_bus_register_type(dg_event_bus *bus, const dg_type_registry_entry *entry);

/* Subscribe to deliveries of a given event_type_id. */
int dg_event_bus_subscribe(
    dg_event_bus          *bus,
    dg_type_id             event_type_id,
    dg_event_bus_sub_fn    fn,
    u64                    priority_key,
    void                  *user_ctx
);

/* Publish an event packet (buffered; no immediate callbacks). */
int dg_event_bus_publish(dg_event_bus *bus, const dg_pkt_event *ev);

/* Deliver buffered events up to current_tick under budget (1 unit per delivery). */
u32 dg_event_bus_deliver(dg_event_bus *bus, dg_budget *budget, dg_tick current_tick);

/* Scheduler integration: installs delivery handler in PH_SENSE with priority_key. */
int dg_event_bus_install_sense(dg_event_bus *bus, struct dg_sched *sched, u64 priority_key);

u32 dg_event_bus_probe_events_published(const dg_event_bus *bus);
u32 dg_event_bus_probe_events_delivered(const dg_event_bus *bus);
u32 dg_event_bus_probe_deferred_deliveries(const dg_event_bus *bus);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_EVENT_BUS_H */

