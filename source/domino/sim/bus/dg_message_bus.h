/* Deterministic message bus (C89).
 *
 * Messages are addressed packets routed deterministically to registered
 * subscribers. No direct cross-system calls are permitted outside this bus.
 */
#ifndef DG_MESSAGE_BUS_H
#define DG_MESSAGE_BUS_H

#include "sim/pkt/dg_pkt_message.h"
#include "sim/pkt/registry/dg_type_registry.h"
#include "sim/sched/dg_budget.h"
#include "sim/sched/dg_work_queue.h"

#ifdef __cplusplus
extern "C" {
#endif

struct dg_sched;

typedef void (*dg_message_bus_sub_fn)(const dg_pkt_message *msg, void *user_ctx);

typedef struct dg_message_bus_sub {
    dg_entity_id          dst_id; /* entity/group/endpoint id space */
    dg_type_id            message_type_id;
    dg_message_bus_sub_fn fn;
    void                 *user_ctx;
    u64                   priority_key;
    u32                   insert_index;
} dg_message_bus_sub;

typedef struct dg_message_bus_record {
    dg_pkt_hdr      hdr;           /* copied */
    unsigned char  *payload_owned; /* owned; freed when fully delivered */
    u32             payload_len;
    d_bool          in_use;
} dg_message_bus_record;

typedef struct dg_message_bus {
    /* Optional type registry (when non-empty, sends must validate). */
    dg_message_type_registry type_registry;

    dg_message_bus_sub *subs;
    u32                 sub_count;
    u32                 sub_capacity;
    u32                 next_sub_insert;

    dg_message_bus_record *records;
    u32                    record_count;
    u32                    record_capacity;

    u32 *free_record_ids;
    u32  free_record_count;
    u32  free_record_capacity;

    dg_work_queue deliver_q; /* one item per pending message */

    /* Probes/counters (no logging). */
    u32 probe_messages_delivered; /* subscriber deliveries */
    u32 probe_deferred_deliveries;
} dg_message_bus;

void dg_message_bus_init(dg_message_bus *bus);
void dg_message_bus_free(dg_message_bus *bus);

int dg_message_bus_reserve(dg_message_bus *bus, u32 subs_cap, u32 records_cap, u32 deliver_queue_cap);

int dg_message_bus_register_type(dg_message_bus *bus, const dg_type_registry_entry *entry);

int dg_message_bus_subscribe(
    dg_message_bus        *bus,
    dg_entity_id           dst_id,
    dg_type_id             message_type_id,
    dg_message_bus_sub_fn  fn,
    u64                    priority_key,
    void                  *user_ctx
);

/* Send a message packet (buffered; no immediate callbacks). */
int dg_message_bus_send(dg_message_bus *bus, const dg_pkt_message *msg);

/* Deliver buffered messages up to current_tick under budget (1 unit per delivery). */
u32 dg_message_bus_deliver(dg_message_bus *bus, dg_budget *budget, dg_tick current_tick);

/* Scheduler integration: installs delivery handler in PH_SENSE with priority_key. */
int dg_message_bus_install_sense(dg_message_bus *bus, struct dg_sched *sched, u64 priority_key);

u32 dg_message_bus_probe_messages_delivered(const dg_message_bus *bus);
u32 dg_message_bus_probe_deferred_deliveries(const dg_message_bus *bus);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_MESSAGE_BUS_H */

