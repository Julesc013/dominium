/*
FILE: engine/modules/scale/d_macro_schedule_store.c
RESPONSIBILITY: Deterministic macro schedule storage and TLV payload encoding.
*/
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#include "domino/scale/macro_schedule_store.h"
#include "scale/d_macro_schedule_store.h"

enum {
    D_MACRO_SCHEDULE_STORE_VERSION = 1u
};

static void d_macro_schedule_entry_reset(d_macro_schedule_entry* entry)
{
    if (!entry) {
        return;
    }
    memset(entry, 0, sizeof(*entry));
}

void d_macro_schedule_store_init(d_world* world)
{
    if (!world) {
        return;
    }
    world->macro_schedules = (d_macro_schedule_entry*)0;
    world->macro_schedule_count = 0u;
    world->macro_schedule_capacity = 0u;
}

void d_macro_schedule_store_free(d_world* world)
{
    if (!world) {
        return;
    }
    if (world->macro_schedules) {
        free(world->macro_schedules);
    }
    world->macro_schedules = (d_macro_schedule_entry*)0;
    world->macro_schedule_count = 0u;
    world->macro_schedule_capacity = 0u;
}

static int d_macro_schedule_reserve(d_world* world, u32 capacity)
{
    d_macro_schedule_entry* new_entries;
    u32 old_capacity;
    u32 i;
    if (!world) {
        return -1;
    }
    if (capacity <= world->macro_schedule_capacity) {
        return 0;
    }
    new_entries = (d_macro_schedule_entry*)realloc(world->macro_schedules,
                                                   sizeof(d_macro_schedule_entry) * (size_t)capacity);
    if (!new_entries) {
        return -1;
    }
    old_capacity = world->macro_schedule_capacity;
    world->macro_schedules = new_entries;
    world->macro_schedule_capacity = capacity;
    for (i = old_capacity; i < world->macro_schedule_capacity; ++i) {
        memset(&world->macro_schedules[i], 0, sizeof(world->macro_schedules[i]));
    }
    return 0;
}

static u32 d_macro_schedule_find_index(const d_world* world, u64 domain_id, int* out_found)
{
    u32 low = 0u;
    u32 high;
    if (out_found) {
        *out_found = 0;
    }
    if (!world || !world->macro_schedules || world->macro_schedule_count == 0u) {
        return 0u;
    }
    high = world->macro_schedule_count;
    while (low < high) {
        u32 mid = low + (u32)((high - low) / 2u);
        const d_macro_schedule_entry* entry = &world->macro_schedules[mid];
        if (entry->domain_id == domain_id) {
            if (out_found) {
                *out_found = 1;
            }
            return mid;
        }
        if (entry->domain_id < domain_id) {
            low = mid + 1u;
        } else {
            high = mid;
        }
    }
    return low;
}

static int d_macro_schedule_insert_at(d_world* world, u32 index)
{
    u32 i;
    if (!world || index > world->macro_schedule_count) {
        return -1;
    }
    if (world->macro_schedule_count >= world->macro_schedule_capacity) {
        u32 new_capacity = world->macro_schedule_capacity ? (world->macro_schedule_capacity * 2u) : 4u;
        if (new_capacity < world->macro_schedule_capacity) {
            return -1;
        }
        if (d_macro_schedule_reserve(world, new_capacity) != 0) {
            return -1;
        }
    }
    for (i = world->macro_schedule_count; i > index; --i) {
        world->macro_schedules[i] = world->macro_schedules[i - 1u];
    }
    memset(&world->macro_schedules[index], 0, sizeof(world->macro_schedules[index]));
    world->macro_schedule_count += 1u;
    return 0;
}

int dom_macro_schedule_store_set(d_world* world, const dom_macro_schedule_entry* entry)
{
    int found = 0;
    u32 index;
    d_macro_schedule_entry* dst;
    if (!world || !entry || entry->domain_id == 0u) {
        return -1;
    }
    index = d_macro_schedule_find_index(world, entry->domain_id, &found);
    if (!found) {
        if (d_macro_schedule_insert_at(world, index) != 0) {
            return -2;
        }
    }
    dst = &world->macro_schedules[index];
    d_macro_schedule_entry_reset(dst);
    dst->domain_id = entry->domain_id;
    dst->capsule_id = entry->capsule_id;
    dst->last_event_time = entry->last_event_time;
    dst->next_event_time = entry->next_event_time;
    dst->interval_ticks = entry->interval_ticks;
    dst->order_key_seed = entry->order_key_seed;
    dst->executed_events = entry->executed_events;
    dst->narrative_events = entry->narrative_events;
    dst->compacted_through_time = entry->compacted_through_time;
    dst->compaction_count = entry->compaction_count;
    dst->in_use = 1u;
    return 0;
}

int dom_macro_schedule_store_get(const d_world* world,
                                 u64 domain_id,
                                 dom_macro_schedule_entry* out_entry)
{
    int found = 0;
    u32 index;
    const d_macro_schedule_entry* src;
    if (!world || !out_entry || domain_id == 0u) {
        return -1;
    }
    index = d_macro_schedule_find_index(world, domain_id, &found);
    if (!found) {
        return -2;
    }
    src = &world->macro_schedules[index];
    out_entry->domain_id = src->domain_id;
    out_entry->capsule_id = src->capsule_id;
    out_entry->last_event_time = src->last_event_time;
    out_entry->next_event_time = src->next_event_time;
    out_entry->interval_ticks = src->interval_ticks;
    out_entry->order_key_seed = src->order_key_seed;
    out_entry->executed_events = src->executed_events;
    out_entry->narrative_events = src->narrative_events;
    out_entry->compacted_through_time = src->compacted_through_time;
    out_entry->compaction_count = src->compaction_count;
    return 0;
}

int dom_macro_schedule_store_remove(d_world* world, u64 domain_id)
{
    int found = 0;
    u32 index;
    u32 i;
    if (!world || domain_id == 0u || world->macro_schedule_count == 0u) {
        return -1;
    }
    index = d_macro_schedule_find_index(world, domain_id, &found);
    if (!found) {
        return -2;
    }
    for (i = index; i + 1u < world->macro_schedule_count; ++i) {
        world->macro_schedules[i] = world->macro_schedules[i + 1u];
    }
    world->macro_schedule_count -= 1u;
    if (world->macro_schedule_count < world->macro_schedule_capacity) {
        d_macro_schedule_entry_reset(&world->macro_schedules[world->macro_schedule_count]);
    }
    return 0;
}

u32 dom_macro_schedule_store_count(const d_world* world)
{
    if (!world) {
        return 0u;
    }
    return world->macro_schedule_count;
}

int dom_macro_schedule_store_get_by_index(const d_world* world,
                                          u32 index,
                                          dom_macro_schedule_entry* out_entry)
{
    const d_macro_schedule_entry* src;
    if (!world || !out_entry || index >= world->macro_schedule_count) {
        return -1;
    }
    src = &world->macro_schedules[index];
    if (!src->in_use) {
        return -2;
    }
    out_entry->domain_id = src->domain_id;
    out_entry->capsule_id = src->capsule_id;
    out_entry->last_event_time = src->last_event_time;
    out_entry->next_event_time = src->next_event_time;
    out_entry->interval_ticks = src->interval_ticks;
    out_entry->order_key_seed = src->order_key_seed;
    out_entry->executed_events = src->executed_events;
    out_entry->narrative_events = src->narrative_events;
    out_entry->compacted_through_time = src->compacted_through_time;
    out_entry->compaction_count = src->compaction_count;
    return 0;
}

void dom_macro_schedule_store_clear(d_world* world)
{
    u32 i;
    if (!world || !world->macro_schedules) {
        return;
    }
    for (i = 0u; i < world->macro_schedule_count; ++i) {
        d_macro_schedule_entry_reset(&world->macro_schedules[i]);
    }
    world->macro_schedule_count = 0u;
}

static int d_macro_schedule_write_bytes(unsigned char* dst,
                                        u32 dst_cap,
                                        u32* in_out_offset,
                                        const void* src,
                                        u32 size)
{
    u32 off;
    if (!dst || !in_out_offset || (!src && size > 0u)) {
        return -1;
    }
    off = *in_out_offset;
    if (size > dst_cap - off) {
        return -2;
    }
    if (size > 0u) {
        memcpy(dst + off, src, (size_t)size);
    }
    *in_out_offset = off + size;
    return 0;
}

static int d_macro_schedule_read_bytes(const unsigned char* src,
                                       u32 src_len,
                                       u32* in_out_offset,
                                       void* dst,
                                       u32 size)
{
    u32 off;
    if (!src || !in_out_offset || (!dst && size > 0u)) {
        return -1;
    }
    off = *in_out_offset;
    if (size > src_len - off) {
        return -2;
    }
    if (size > 0u) {
        memcpy(dst, src + off, (size_t)size);
    }
    *in_out_offset = off + size;
    return 0;
}

int d_macro_schedule_store_serialize(const d_world* world, d_tlv_blob* out_blob)
{
    u64 total_len64;
    u32 total_len;
    u32 offset = 0u;
    u32 i;
    u32 version = D_MACRO_SCHEDULE_STORE_VERSION;
    unsigned char* buffer;
    const u32 entry_size = 68u;
    if (!out_blob) {
        return -1;
    }
    out_blob->ptr = (unsigned char*)0;
    out_blob->len = 0u;
    if (!world || world->macro_schedule_count == 0u) {
        return 0;
    }

    total_len64 = 8u + (u64)world->macro_schedule_count * (u64)entry_size;
    if (total_len64 > 0xFFFFFFFFu) {
        return -2;
    }
    total_len = (u32)total_len64;
    buffer = (unsigned char*)malloc((size_t)total_len);
    if (!buffer) {
        return -3;
    }

    if (d_macro_schedule_write_bytes(buffer, total_len, &offset, &version, 4u) != 0 ||
        d_macro_schedule_write_bytes(buffer, total_len, &offset,
                                     &world->macro_schedule_count, 4u) != 0) {
        free(buffer);
        return -4;
    }

    for (i = 0u; i < world->macro_schedule_count; ++i) {
        const d_macro_schedule_entry* entry = &world->macro_schedules[i];
        if (d_macro_schedule_write_bytes(buffer, total_len, &offset, &entry->domain_id, 8u) != 0 ||
            d_macro_schedule_write_bytes(buffer, total_len, &offset, &entry->capsule_id, 8u) != 0 ||
            d_macro_schedule_write_bytes(buffer, total_len, &offset, &entry->last_event_time, 8u) != 0 ||
            d_macro_schedule_write_bytes(buffer, total_len, &offset, &entry->next_event_time, 8u) != 0 ||
            d_macro_schedule_write_bytes(buffer, total_len, &offset, &entry->interval_ticks, 8u) != 0 ||
            d_macro_schedule_write_bytes(buffer, total_len, &offset, &entry->order_key_seed, 8u) != 0 ||
            d_macro_schedule_write_bytes(buffer, total_len, &offset, &entry->executed_events, 4u) != 0 ||
            d_macro_schedule_write_bytes(buffer, total_len, &offset, &entry->narrative_events, 4u) != 0 ||
            d_macro_schedule_write_bytes(buffer, total_len, &offset, &entry->compacted_through_time, 8u) != 0 ||
            d_macro_schedule_write_bytes(buffer, total_len, &offset, &entry->compaction_count, 4u) != 0) {
            free(buffer);
            return -5;
        }
    }

    out_blob->ptr = buffer;
    out_blob->len = total_len;
    return 0;
}

int d_macro_schedule_store_deserialize(d_world* world, const d_tlv_blob* in_blob)
{
    u32 offset = 0u;
    u32 version = 0u;
    u32 count = 0u;
    u32 i;
    if (!world || !in_blob) {
        return -1;
    }
    if (in_blob->len > 0u && !in_blob->ptr) {
        return -2;
    }
    if (!in_blob->ptr || in_blob->len == 0u) {
        return 0;
    }
    dom_macro_schedule_store_clear(world);
    if (d_macro_schedule_read_bytes(in_blob->ptr, in_blob->len, &offset, &version, 4u) != 0 ||
        d_macro_schedule_read_bytes(in_blob->ptr, in_blob->len, &offset, &count, 4u) != 0) {
        return -3;
    }
    if (version != D_MACRO_SCHEDULE_STORE_VERSION) {
        return -4;
    }
    for (i = 0u; i < count; ++i) {
        dom_macro_schedule_entry entry;
        memset(&entry, 0, sizeof(entry));
        if (d_macro_schedule_read_bytes(in_blob->ptr, in_blob->len, &offset, &entry.domain_id, 8u) != 0 ||
            d_macro_schedule_read_bytes(in_blob->ptr, in_blob->len, &offset, &entry.capsule_id, 8u) != 0 ||
            d_macro_schedule_read_bytes(in_blob->ptr, in_blob->len, &offset, &entry.last_event_time, 8u) != 0 ||
            d_macro_schedule_read_bytes(in_blob->ptr, in_blob->len, &offset, &entry.next_event_time, 8u) != 0 ||
            d_macro_schedule_read_bytes(in_blob->ptr, in_blob->len, &offset, &entry.interval_ticks, 8u) != 0 ||
            d_macro_schedule_read_bytes(in_blob->ptr, in_blob->len, &offset, &entry.order_key_seed, 8u) != 0 ||
            d_macro_schedule_read_bytes(in_blob->ptr, in_blob->len, &offset, &entry.executed_events, 4u) != 0 ||
            d_macro_schedule_read_bytes(in_blob->ptr, in_blob->len, &offset, &entry.narrative_events, 4u) != 0 ||
            d_macro_schedule_read_bytes(in_blob->ptr, in_blob->len, &offset, &entry.compacted_through_time, 8u) != 0 ||
            d_macro_schedule_read_bytes(in_blob->ptr, in_blob->len, &offset, &entry.compaction_count, 4u) != 0) {
            return -5;
        }
        if (dom_macro_schedule_store_set(world, &entry) != 0) {
            return -6;
        }
    }
    if (offset != in_blob->len) {
        return -7;
    }
    return 0;
}
