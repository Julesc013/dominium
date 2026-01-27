/*
FILE: server/shard/dom_shard_lifecycle.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Deterministic shard lifecycle state machine and logging.
*/
#include "dom_shard_lifecycle.h"

#ifdef __cplusplus
extern "C" {
#endif

static u64 dom_shard_lifecycle_hash_mix(u64 hash, u64 value)
{
    u32 i;
    for (i = 0u; i < 8u; ++i) {
        hash ^= (u64)((value >> (i * 8u)) & 0xFFu);
        hash *= 1099511628211ULL;
    }
    return hash;
}

void dom_shard_lifecycle_log_init(dom_shard_lifecycle_log* log,
                                  dom_shard_lifecycle_entry* storage,
                                  u32 capacity)
{
    if (!log) {
        return;
    }
    log->entries = storage;
    log->count = 0u;
    log->capacity = capacity;
    log->overflow = 0u;
}

void dom_shard_lifecycle_log_clear(dom_shard_lifecycle_log* log)
{
    if (!log) {
        return;
    }
    log->count = 0u;
    log->overflow = 0u;
}

int dom_shard_lifecycle_transition_allowed(u32 from_state, u32 to_state)
{
    if (from_state == to_state) {
        return 1;
    }
    switch (from_state) {
    case DOM_SHARD_LIFECYCLE_INITIALIZING:
        return (to_state == DOM_SHARD_LIFECYCLE_ACTIVE ||
                to_state == DOM_SHARD_LIFECYCLE_FROZEN ||
                to_state == DOM_SHARD_LIFECYCLE_OFFLINE)
                   ? 1
                   : 0;
    case DOM_SHARD_LIFECYCLE_ACTIVE:
        return (to_state == DOM_SHARD_LIFECYCLE_DRAINING ||
                to_state == DOM_SHARD_LIFECYCLE_FROZEN ||
                to_state == DOM_SHARD_LIFECYCLE_OFFLINE)
                   ? 1
                   : 0;
    case DOM_SHARD_LIFECYCLE_DRAINING:
        return (to_state == DOM_SHARD_LIFECYCLE_ACTIVE ||
                to_state == DOM_SHARD_LIFECYCLE_FROZEN ||
                to_state == DOM_SHARD_LIFECYCLE_OFFLINE)
                   ? 1
                   : 0;
    case DOM_SHARD_LIFECYCLE_FROZEN:
        return (to_state == DOM_SHARD_LIFECYCLE_INITIALIZING ||
                to_state == DOM_SHARD_LIFECYCLE_ACTIVE ||
                to_state == DOM_SHARD_LIFECYCLE_OFFLINE)
                   ? 1
                   : 0;
    case DOM_SHARD_LIFECYCLE_OFFLINE:
        return (to_state == DOM_SHARD_LIFECYCLE_INITIALIZING ||
                to_state == DOM_SHARD_LIFECYCLE_FROZEN)
                   ? 1
                   : 0;
    default:
        break;
    }
    return 0;
}

int dom_shard_lifecycle_log_transition(dom_shard_lifecycle_log* log,
                                       dom_shard_id shard_id,
                                       dom_act_time_t tick,
                                       u32 from_state,
                                       u32 to_state,
                                       u32 reason_code)
{
    dom_shard_lifecycle_entry entry;
    if (!log) {
        return -1;
    }
    if (!dom_shard_lifecycle_transition_allowed(from_state, to_state)) {
        return -2;
    }
    if (!log->entries || log->capacity == 0u) {
        log->overflow += 1u;
        return -3;
    }
    if (log->count >= log->capacity) {
        log->overflow += 1u;
        return -4;
    }
    entry.shard_id = shard_id;
    entry.tick = tick;
    entry.from_state = from_state;
    entry.to_state = to_state;
    entry.reason_code = reason_code;
    log->entries[log->count] = entry;
    log->count += 1u;
    return 0;
}

const char* dom_shard_lifecycle_state_name(u32 state)
{
    switch (state) {
    case DOM_SHARD_LIFECYCLE_INITIALIZING: return "INITIALIZING";
    case DOM_SHARD_LIFECYCLE_ACTIVE: return "ACTIVE";
    case DOM_SHARD_LIFECYCLE_DRAINING: return "DRAINING";
    case DOM_SHARD_LIFECYCLE_FROZEN: return "FROZEN";
    case DOM_SHARD_LIFECYCLE_OFFLINE: return "OFFLINE";
    default: break;
    }
    return "UNKNOWN";
}

u64 dom_shard_lifecycle_log_hash(const dom_shard_lifecycle_log* log)
{
    u64 hash = 1469598103934665603ULL;
    u32 i;
    if (!log) {
        return hash;
    }
    hash = dom_shard_lifecycle_hash_mix(hash, log->count);
    hash = dom_shard_lifecycle_hash_mix(hash, log->capacity);
    hash = dom_shard_lifecycle_hash_mix(hash, log->overflow);
    if (!log->entries) {
        return hash;
    }
    for (i = 0u; i < log->count; ++i) {
        const dom_shard_lifecycle_entry* entry = &log->entries[i];
        hash = dom_shard_lifecycle_hash_mix(hash, entry->shard_id);
        hash = dom_shard_lifecycle_hash_mix(hash, (u64)entry->tick);
        hash = dom_shard_lifecycle_hash_mix(hash, entry->from_state);
        hash = dom_shard_lifecycle_hash_mix(hash, entry->to_state);
        hash = dom_shard_lifecycle_hash_mix(hash, entry->reason_code);
    }
    return hash;
}

#ifdef __cplusplus
} /* extern "C" */
#endif

