#include "dom_sim_events.h"
#include <string.h>

#define DOM_SIM_EVENT_LOCAL_BUCKETS   64
#define DOM_SIM_EVENT_LOCAL_CAPACITY  32
#define DOM_SIM_EVENT_LANE_CAPACITY   128
#define DOM_SIM_EVENT_CROSS_CAPACITY  128
#define DOM_SIM_EVENT_GLOBAL_CAPACITY 256
#define DOM_SIM_COMMAND_CAPACITY      128

typedef struct DomSimRing {
    DomSimMessage *buffer;
    dom_u32        capacity;
    dom_u32        head;
    dom_u32        count;
    dom_bool8      overflowed;
} DomSimRing;

typedef struct DomSimCommandRing {
    DomSimCommand *buffer;
    dom_u32        capacity;
    dom_u32        head;
    dom_u32        count;
    dom_bool8      overflowed;
} DomSimCommandRing;

static struct {
    DomSimRing local[DOM_SIM_EVENT_LOCAL_BUCKETS];
    DomSimMessage local_storage[DOM_SIM_EVENT_LOCAL_BUCKETS][DOM_SIM_EVENT_LOCAL_CAPACITY];

    DomSimRing lane[DOM_SIM_MAX_LANES];
    DomSimMessage lane_storage[DOM_SIM_MAX_LANES][DOM_SIM_EVENT_LANE_CAPACITY];

    DomSimRing cross_curr[DOM_SIM_MAX_LANES];
    DomSimRing cross_next[DOM_SIM_MAX_LANES];
    DomSimMessage cross_curr_storage[DOM_SIM_MAX_LANES][DOM_SIM_EVENT_CROSS_CAPACITY];
    DomSimMessage cross_next_storage[DOM_SIM_MAX_LANES][DOM_SIM_EVENT_CROSS_CAPACITY];

    DomSimRing global_curr;
    DomSimRing global_next;
    DomSimMessage global_curr_storage[DOM_SIM_EVENT_GLOBAL_CAPACITY];
    DomSimMessage global_next_storage[DOM_SIM_EVENT_GLOBAL_CAPACITY];

    DomSimCommandRing commands[DOM_SIM_MAX_LANES];
    DomSimCommand command_storage[DOM_SIM_MAX_LANES][DOM_SIM_COMMAND_CAPACITY];
} g_events;

static void dom_sim_ring_init(DomSimRing *r, DomSimMessage *storage, dom_u32 cap)
{
    if (!r) return;
    r->buffer = storage;
    r->capacity = cap;
    r->head = 0;
    r->count = 0;
    r->overflowed = 0;
}

static void dom_sim_ring_clear(DomSimRing *r)
{
    if (!r) return;
    r->head = 0;
    r->count = 0;
    r->overflowed = 0;
}

static void dom_sim_ring_push(DomSimRing *r, const DomSimMessage *msg)
{
    dom_u32 tail;
    if (!r || !msg) return;
    if (r->capacity == 0) return;
    if (r->count == r->capacity) {
        r->head = (r->head + 1) % r->capacity;
        r->count -= 1;
        r->overflowed = 1;
    }
    tail = (r->head + r->count) % r->capacity;
    r->buffer[tail] = *msg;
    r->count += 1;
}

static dom_bool8 dom_sim_ring_pop(DomSimRing *r, DomSimMessage *out_msg)
{
    if (!r || !out_msg) return 0;
    if (r->count == 0) return 0;
    *out_msg = r->buffer[r->head];
    r->head = (r->head + 1) % r->capacity;
    r->count -= 1;
    return 1;
}

static void dom_sim_command_ring_init(DomSimCommandRing *r, DomSimCommand *storage, dom_u32 cap)
{
    if (!r) return;
    r->buffer = storage;
    r->capacity = cap;
    r->head = 0;
    r->count = 0;
    r->overflowed = 0;
}

static void dom_sim_command_ring_clear(DomSimCommandRing *r)
{
    if (!r) return;
    r->head = 0;
    r->count = 0;
    r->overflowed = 0;
}

static void dom_sim_command_ring_push(DomSimCommandRing *r, const DomSimCommand *cmd)
{
    dom_u32 tail;
    if (!r || !cmd) return;
    if (r->capacity == 0) return;
    if (r->count == r->capacity) {
        r->head = (r->head + 1) % r->capacity;
        r->count -= 1;
        r->overflowed = 1;
    }
    tail = (r->head + r->count) % r->capacity;
    r->buffer[tail] = *cmd;
    r->count += 1;
}

static dom_bool8 dom_sim_command_ring_pop(DomSimCommandRing *r, DomSimCommand *out_cmd)
{
    if (!r || !out_cmd) return 0;
    if (r->count == 0) return 0;
    *out_cmd = r->buffer[r->head];
    r->head = (r->head + 1) % r->capacity;
    r->count -= 1;
    return 1;
}

static dom_u32 dom_sim_events_lane_limit(void)
{
    dom_u32 lanes = dom_sim_tick_lane_count();
    if (lanes > DOM_SIM_MAX_LANES) lanes = DOM_SIM_MAX_LANES;
    if (lanes == 0) lanes = 1;
    return lanes;
}

static void dom_sim_events_init_rings(void)
{
    dom_u32 i;
    dom_u32 lanes = dom_sim_events_lane_limit();
    for (i = 0; i < DOM_SIM_EVENT_LOCAL_BUCKETS; ++i) {
        dom_sim_ring_init(&g_events.local[i], g_events.local_storage[i], DOM_SIM_EVENT_LOCAL_CAPACITY);
    }
    for (i = 0; i < DOM_SIM_MAX_LANES; ++i) {
        dom_sim_ring_init(&g_events.lane[i], g_events.lane_storage[i], DOM_SIM_EVENT_LANE_CAPACITY);
        dom_sim_ring_init(&g_events.cross_curr[i], g_events.cross_curr_storage[i], DOM_SIM_EVENT_CROSS_CAPACITY);
        dom_sim_ring_init(&g_events.cross_next[i], g_events.cross_next_storage[i], DOM_SIM_EVENT_CROSS_CAPACITY);
        dom_sim_command_ring_init(&g_events.commands[i], g_events.command_storage[i], DOM_SIM_COMMAND_CAPACITY);
    }
    g_events.global_curr.buffer = g_events.global_curr_storage;
    dom_sim_ring_init(&g_events.global_curr, g_events.global_curr_storage, DOM_SIM_EVENT_GLOBAL_CAPACITY);
    dom_sim_ring_init(&g_events.global_next, g_events.global_next_storage, DOM_SIM_EVENT_GLOBAL_CAPACITY);
    (void)lanes;
}

dom_err_t dom_sim_events_init(void)
{
    dom_sim_events_init_rings();
    return DOM_OK;
}

void dom_sim_events_reset(void)
{
    dom_sim_events_init_rings();
}

static dom_u32 dom_sim_events_local_bucket(dom_entity_id entity)
{
    dom_u32 idx = dom_entity_index(entity);
    return idx % DOM_SIM_EVENT_LOCAL_BUCKETS;
}

dom_err_t dom_sim_events_local_emit(dom_entity_id entity, const DomSimMessage *msg)
{
    dom_u32 bucket;
    if (!msg) return DOM_ERR_INVALID_ARG;
    bucket = dom_sim_events_local_bucket(entity);
    dom_sim_ring_push(&g_events.local[bucket], msg);
    return DOM_OK;
}

dom_err_t dom_sim_events_local_consume(dom_entity_id entity, DomSimMessage *out_msg)
{
    dom_u32 bucket;
    if (!out_msg) return DOM_ERR_INVALID_ARG;
    bucket = dom_sim_events_local_bucket(entity);
    if (!dom_sim_ring_pop(&g_events.local[bucket], out_msg)) return DOM_ERR_NOT_FOUND;
    return DOM_OK;
}

dom_err_t dom_sim_events_lane_emit(DomLaneId lane, const DomSimMessage *msg)
{
    dom_u32 lanes = dom_sim_events_lane_limit();
    if (!msg) return DOM_ERR_INVALID_ARG;
    if (lane >= lanes) return DOM_ERR_BOUNDS;
    dom_sim_ring_push(&g_events.lane[lane], msg);
    return DOM_OK;
}

dom_err_t dom_sim_events_lane_consume(DomLaneId lane, DomSimMessage *out_msg)
{
    dom_u32 lanes = dom_sim_events_lane_limit();
    if (!out_msg) return DOM_ERR_INVALID_ARG;
    if (lane >= lanes) return DOM_ERR_BOUNDS;
    if (!dom_sim_ring_pop(&g_events.lane[lane], out_msg)) return DOM_ERR_NOT_FOUND;
    return DOM_OK;
}

dom_err_t dom_sim_events_cross_emit(DomLaneId target_lane, const DomSimMessage *msg)
{
    dom_u32 lanes = dom_sim_events_lane_limit();
    if (!msg) return DOM_ERR_INVALID_ARG;
    if (target_lane >= lanes) return DOM_ERR_BOUNDS;
    dom_sim_ring_push(&g_events.cross_next[target_lane], msg);
    return DOM_OK;
}

dom_err_t dom_sim_events_global_emit(const DomSimMessage *msg)
{
    if (!msg) return DOM_ERR_INVALID_ARG;
    dom_sim_ring_push(&g_events.global_next, msg);
    return DOM_OK;
}

void dom_sim_events_phase_pre_state(void)
{
    DomSimMessage msg;
    dom_u32 lane;
    dom_u32 lanes = dom_sim_events_lane_limit();
    for (lane = 0; lane < lanes; ++lane) {
        while (dom_sim_ring_pop(&g_events.cross_curr[lane], &msg)) {
            dom_sim_ring_push(&g_events.lane[lane], &msg);
        }
    }
    while (dom_sim_ring_pop(&g_events.global_curr, &msg)) {
        for (lane = 0; lane < lanes; ++lane) {
            dom_sim_ring_push(&g_events.lane[lane], &msg);
        }
    }
}

void dom_sim_events_phase_merge(void)
{
    /* No-op placeholder: cross-lane queues are already collected for next tick. */
}

void dom_sim_events_phase_finalize(void)
{
    DomSimMessage msg;
    dom_u32 lane;
    dom_u32 lanes = dom_sim_events_lane_limit();
    for (lane = 0; lane < lanes; ++lane) {
        while (dom_sim_ring_pop(&g_events.cross_next[lane], &msg)) {
            dom_sim_ring_push(&g_events.cross_curr[lane], &msg);
        }
    }
    while (dom_sim_ring_pop(&g_events.global_next, &msg)) {
        dom_sim_ring_push(&g_events.global_curr, &msg);
    }
}

dom_err_t dom_sim_command_emit(DomLaneId lane, const DomSimCommand *cmd)
{
    dom_u32 lanes = dom_sim_events_lane_limit();
    if (!cmd) return DOM_ERR_INVALID_ARG;
    if (lane >= lanes) return DOM_ERR_BOUNDS;
    dom_sim_command_ring_push(&g_events.commands[lane], cmd);
    return DOM_OK;
}

void dom_sim_command_drain_for_lane(DomLaneId lane)
{
    DomSimCommand cmd;
    dom_u32 lanes = dom_sim_events_lane_limit();
    if (lane >= lanes) return;
    while (dom_sim_command_ring_pop(&g_events.commands[lane], &cmd)) {
        (void)cmd;
    }
}
