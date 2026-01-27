/*
FILE: engine/modules/scale/d_macro_event_queue_store.c
RESPONSIBILITY: Deterministic macro event queue storage and TLV payload encoding.
*/
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#include "domino/scale/macro_event_queue.h"
#include "scale/d_macro_event_queue_store.h"

enum {
    D_MACRO_EVENT_QUEUE_VERSION = 1u
};

static void d_macro_event_entry_reset(d_macro_event_entry* entry)
{
    if (!entry) {
        return;
    }
    memset(entry, 0, sizeof(*entry));
}

void d_macro_event_queue_store_init(d_world* world)
{
    if (!world) {
        return;
    }
    world->macro_events = (d_macro_event_entry*)0;
    world->macro_event_count = 0u;
    world->macro_event_capacity = 0u;
    world->macro_event_sequence = 0u;
}

void d_macro_event_queue_store_free(d_world* world)
{
    if (!world) {
        return;
    }
    if (world->macro_events) {
        free(world->macro_events);
    }
    world->macro_events = (d_macro_event_entry*)0;
    world->macro_event_count = 0u;
    world->macro_event_capacity = 0u;
    world->macro_event_sequence = 0u;
}

static int d_macro_event_reserve(d_world* world, u32 capacity)
{
    d_macro_event_entry* new_entries;
    u32 old_capacity;
    u32 i;
    if (!world) {
        return -1;
    }
    if (capacity <= world->macro_event_capacity) {
        return 0;
    }
    new_entries = (d_macro_event_entry*)realloc(world->macro_events,
                                                sizeof(d_macro_event_entry) * (size_t)capacity);
    if (!new_entries) {
        return -1;
    }
    old_capacity = world->macro_event_capacity;
    world->macro_events = new_entries;
    world->macro_event_capacity = capacity;
    for (i = old_capacity; i < world->macro_event_capacity; ++i) {
        memset(&world->macro_events[i], 0, sizeof(world->macro_events[i]));
    }
    return 0;
}

static int d_macro_event_cmp(const d_macro_event_entry* a, const d_macro_event_entry* b)
{
    if (!a || !b) {
        return a ? 1 : (b ? -1 : 0);
    }
    if (a->event_time < b->event_time) return -1;
    if (a->event_time > b->event_time) return 1;
    if (a->order_key < b->order_key) return -1;
    if (a->order_key > b->order_key) return 1;
    if (a->domain_id < b->domain_id) return -1;
    if (a->domain_id > b->domain_id) return 1;
    if (a->event_id < b->event_id) return -1;
    if (a->event_id > b->event_id) return 1;
    if (a->sequence < b->sequence) return -1;
    if (a->sequence > b->sequence) return 1;
    return 0;
}

static void d_macro_event_recompute_sequence(d_world* world)
{
    u64 max_sequence = 0u;
    u32 i;
    if (!world || !world->macro_events) {
        if (world) {
            world->macro_event_sequence = 0u;
        }
        return;
    }
    for (i = 0u; i < world->macro_event_count; ++i) {
        const d_macro_event_entry* entry = &world->macro_events[i];
        if (entry->sequence > max_sequence) {
            max_sequence = entry->sequence;
        }
    }
    world->macro_event_sequence = max_sequence;
}

static int d_macro_event_remove_index(d_world* world, u32 index)
{
    u32 i;
    if (!world || index >= world->macro_event_count) {
        return -1;
    }
    for (i = index; i + 1u < world->macro_event_count; ++i) {
        world->macro_events[i] = world->macro_events[i + 1u];
    }
    world->macro_event_count -= 1u;
    if (world->macro_event_count < world->macro_event_capacity) {
        d_macro_event_entry_reset(&world->macro_events[world->macro_event_count]);
    }
    d_macro_event_recompute_sequence(world);
    return 0;
}

static int d_macro_event_find_duplicate(const d_world* world,
                                        u64 event_id,
                                        u64 domain_id,
                                        u32* out_index)
{
    u32 i;
    if (!world || !out_index || event_id == 0u) {
        return 0;
    }
    for (i = 0u; i < world->macro_event_count; ++i) {
        const d_macro_event_entry* entry = &world->macro_events[i];
        if (entry->event_id == event_id &&
            (domain_id == 0u || entry->domain_id == domain_id)) {
            *out_index = i;
            return 1;
        }
    }
    return 0;
}

static int d_macro_event_insert_sorted(d_world* world, const d_macro_event_entry* entry)
{
    u32 i;
    u32 insert_at = world ? world->macro_event_count : 0u;
    if (!world || !entry) {
        return -1;
    }
    if (world->macro_event_count >= world->macro_event_capacity) {
        u32 new_capacity = world->macro_event_capacity ? (world->macro_event_capacity * 2u) : 8u;
        if (new_capacity < world->macro_event_capacity) {
            return -1;
        }
        if (d_macro_event_reserve(world, new_capacity) != 0) {
            return -1;
        }
    }
    for (i = 0u; i < world->macro_event_count; ++i) {
        if (d_macro_event_cmp(entry, &world->macro_events[i]) < 0) {
            insert_at = i;
            break;
        }
    }
    for (i = world->macro_event_count; i > insert_at; --i) {
        world->macro_events[i] = world->macro_events[i - 1u];
    }
    world->macro_events[insert_at] = *entry;
    world->macro_events[insert_at].in_use = 1u;
    world->macro_event_count += 1u;
    d_macro_event_recompute_sequence(world);
    return 0;
}

int dom_macro_event_queue_schedule(d_world* world, const dom_macro_event_entry* entry)
{
    d_macro_event_entry copy;
    u32 dup_index = 0u;
    if (!world || !entry || entry->event_id == 0u || entry->domain_id == 0u) {
        return -1;
    }
    if (d_macro_event_find_duplicate(world, entry->event_id, entry->domain_id, &dup_index)) {
        (void)d_macro_event_remove_index(world, dup_index);
    }
    memset(&copy, 0, sizeof(copy));
    copy.event_id = entry->event_id;
    copy.domain_id = entry->domain_id;
    copy.capsule_id = entry->capsule_id;
    copy.event_time = entry->event_time;
    copy.order_key = entry->order_key;
    copy.sequence = entry->sequence ? entry->sequence : entry->event_id;
    copy.event_kind = entry->event_kind;
    copy.flags = entry->flags;
    copy.payload0 = entry->payload0;
    copy.payload1 = entry->payload1;
    if (d_macro_event_insert_sorted(world, &copy) != 0) {
        return -2;
    }
    return 0;
}

int dom_macro_event_queue_peek_next(const d_world* world, dom_macro_event_entry* out_entry)
{
    const d_macro_event_entry* src;
    if (!world || !out_entry || world->macro_event_count == 0u) {
        return 0;
    }
    src = &world->macro_events[0];
    if (!src->in_use) {
        return 0;
    }
    out_entry->event_id = src->event_id;
    out_entry->domain_id = src->domain_id;
    out_entry->capsule_id = src->capsule_id;
    out_entry->event_time = src->event_time;
    out_entry->order_key = src->order_key;
    out_entry->sequence = src->sequence;
    out_entry->event_kind = src->event_kind;
    out_entry->flags = src->flags;
    out_entry->payload0 = src->payload0;
    out_entry->payload1 = src->payload1;
    return 1;
}

int dom_macro_event_queue_pop_next(d_world* world,
                                   dom_act_time_t up_to_time,
                                   dom_macro_event_entry* out_entry)
{
    d_macro_event_entry src;
    if (!world || world->macro_event_count == 0u) {
        return 0;
    }
    src = world->macro_events[0];
    if (!src.in_use || src.event_time > up_to_time) {
        return 0;
    }
    if (out_entry) {
        out_entry->event_id = src.event_id;
        out_entry->domain_id = src.domain_id;
        out_entry->capsule_id = src.capsule_id;
        out_entry->event_time = src.event_time;
        out_entry->order_key = src.order_key;
        out_entry->sequence = src.sequence;
        out_entry->event_kind = src.event_kind;
        out_entry->flags = src.flags;
        out_entry->payload0 = src.payload0;
        out_entry->payload1 = src.payload1;
    }
    (void)d_macro_event_remove_index(world, 0u);
    return 1;
}

int dom_macro_event_queue_remove_domain(d_world* world, u64 domain_id)
{
    u32 i = 0u;
    int removed_any = 0;
    if (!world || domain_id == 0u) {
        return -1;
    }
    while (i < world->macro_event_count) {
        if (world->macro_events[i].domain_id == domain_id) {
            (void)d_macro_event_remove_index(world, i);
            removed_any = 1;
            continue;
        }
        ++i;
    }
    return removed_any ? 0 : -2;
}

u32 dom_macro_event_queue_count(const d_world* world)
{
    if (!world) {
        return 0u;
    }
    return world->macro_event_count;
}

int dom_macro_event_queue_get_by_index(const d_world* world,
                                       u32 index,
                                       dom_macro_event_entry* out_entry)
{
    const d_macro_event_entry* src;
    if (!world || !out_entry || index >= world->macro_event_count) {
        return -1;
    }
    src = &world->macro_events[index];
    if (!src->in_use) {
        return -2;
    }
    out_entry->event_id = src->event_id;
    out_entry->domain_id = src->domain_id;
    out_entry->capsule_id = src->capsule_id;
    out_entry->event_time = src->event_time;
    out_entry->order_key = src->order_key;
    out_entry->sequence = src->sequence;
    out_entry->event_kind = src->event_kind;
    out_entry->flags = src->flags;
    out_entry->payload0 = src->payload0;
    out_entry->payload1 = src->payload1;
    return 0;
}

void dom_macro_event_queue_clear(d_world* world)
{
    u32 i;
    if (!world || !world->macro_events) {
        return;
    }
    for (i = 0u; i < world->macro_event_count; ++i) {
        d_macro_event_entry_reset(&world->macro_events[i]);
    }
    world->macro_event_count = 0u;
    d_macro_event_recompute_sequence(world);
}

static int d_macro_event_write_bytes(unsigned char* dst,
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

static int d_macro_event_read_bytes(const unsigned char* src,
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

int d_macro_event_queue_store_serialize(const d_world* world, d_tlv_blob* out_blob)
{
    u64 total_len64;
    u32 total_len;
    u32 offset = 0u;
    u32 i;
    u32 version = D_MACRO_EVENT_QUEUE_VERSION;
    unsigned char* buffer;
    const u32 entry_size = 64u;
    if (!out_blob) {
        return -1;
    }
    out_blob->ptr = (unsigned char*)0;
    out_blob->len = 0u;
    if (!world || world->macro_event_count == 0u) {
        return 0;
    }

    total_len64 = 16u + (u64)world->macro_event_count * (u64)entry_size;
    if (total_len64 > 0xFFFFFFFFu) {
        return -2;
    }
    total_len = (u32)total_len64;
    buffer = (unsigned char*)malloc((size_t)total_len);
    if (!buffer) {
        return -3;
    }

    if (d_macro_event_write_bytes(buffer, total_len, &offset, &version, 4u) != 0 ||
        d_macro_event_write_bytes(buffer, total_len, &offset,
                                  &world->macro_event_count, 4u) != 0 ||
        d_macro_event_write_bytes(buffer, total_len, &offset,
                                  &world->macro_event_sequence, 8u) != 0) {
        free(buffer);
        return -4;
    }

    for (i = 0u; i < world->macro_event_count; ++i) {
        const d_macro_event_entry* entry = &world->macro_events[i];
        if (d_macro_event_write_bytes(buffer, total_len, &offset, &entry->event_id, 8u) != 0 ||
            d_macro_event_write_bytes(buffer, total_len, &offset, &entry->domain_id, 8u) != 0 ||
            d_macro_event_write_bytes(buffer, total_len, &offset, &entry->capsule_id, 8u) != 0 ||
            d_macro_event_write_bytes(buffer, total_len, &offset, &entry->event_time, 8u) != 0 ||
            d_macro_event_write_bytes(buffer, total_len, &offset, &entry->order_key, 8u) != 0 ||
            d_macro_event_write_bytes(buffer, total_len, &offset, &entry->sequence, 8u) != 0 ||
            d_macro_event_write_bytes(buffer, total_len, &offset, &entry->event_kind, 4u) != 0 ||
            d_macro_event_write_bytes(buffer, total_len, &offset, &entry->flags, 4u) != 0 ||
            d_macro_event_write_bytes(buffer, total_len, &offset, &entry->payload0, 4u) != 0 ||
            d_macro_event_write_bytes(buffer, total_len, &offset, &entry->payload1, 4u) != 0) {
            free(buffer);
            return -5;
        }
    }

    out_blob->ptr = buffer;
    out_blob->len = total_len;
    return 0;
}

int d_macro_event_queue_store_deserialize(d_world* world, const d_tlv_blob* in_blob)
{
    u32 offset = 0u;
    u32 version = 0u;
    u32 count = 0u;
    u64 sequence = 0u;
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
    dom_macro_event_queue_clear(world);
    if (d_macro_event_read_bytes(in_blob->ptr, in_blob->len, &offset, &version, 4u) != 0 ||
        d_macro_event_read_bytes(in_blob->ptr, in_blob->len, &offset, &count, 4u) != 0 ||
        d_macro_event_read_bytes(in_blob->ptr, in_blob->len, &offset, &sequence, 8u) != 0) {
        return -3;
    }
    if (version != D_MACRO_EVENT_QUEUE_VERSION) {
        return -4;
    }
    for (i = 0u; i < count; ++i) {
        dom_macro_event_entry entry;
        memset(&entry, 0, sizeof(entry));
        if (d_macro_event_read_bytes(in_blob->ptr, in_blob->len, &offset, &entry.event_id, 8u) != 0 ||
            d_macro_event_read_bytes(in_blob->ptr, in_blob->len, &offset, &entry.domain_id, 8u) != 0 ||
            d_macro_event_read_bytes(in_blob->ptr, in_blob->len, &offset, &entry.capsule_id, 8u) != 0 ||
            d_macro_event_read_bytes(in_blob->ptr, in_blob->len, &offset, &entry.event_time, 8u) != 0 ||
            d_macro_event_read_bytes(in_blob->ptr, in_blob->len, &offset, &entry.order_key, 8u) != 0 ||
            d_macro_event_read_bytes(in_blob->ptr, in_blob->len, &offset, &entry.sequence, 8u) != 0 ||
            d_macro_event_read_bytes(in_blob->ptr, in_blob->len, &offset, &entry.event_kind, 4u) != 0 ||
            d_macro_event_read_bytes(in_blob->ptr, in_blob->len, &offset, &entry.flags, 4u) != 0 ||
            d_macro_event_read_bytes(in_blob->ptr, in_blob->len, &offset, &entry.payload0, 4u) != 0 ||
            d_macro_event_read_bytes(in_blob->ptr, in_blob->len, &offset, &entry.payload1, 4u) != 0) {
            return -5;
        }
        if (dom_macro_event_queue_schedule(world, &entry) != 0) {
            return -6;
        }
    }
    world->macro_event_sequence = sequence;
    if (offset != in_blob->len) {
        return -7;
    }
    return 0;
}
