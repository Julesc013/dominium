/*
FILE: engine/modules/scale/d_macro_capsule_store.c
RESPONSIBILITY: Deterministic macro capsule storage and TLV payload encoding.
*/
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#include "domino/scale/macro_capsule_store.h"
#include "scale/d_macro_capsule_store.h"

enum {
    D_MACRO_CAPSULE_STORE_VERSION = 1u
};

static void d_macro_capsule_entry_reset(d_macro_capsule_entry* entry)
{
    if (!entry) {
        return;
    }
    if (entry->bytes) {
        free(entry->bytes);
    }
    memset(entry, 0, sizeof(*entry));
}

void d_macro_capsule_store_init(d_world* world)
{
    if (!world) {
        return;
    }
    world->macro_capsules = (d_macro_capsule_entry*)0;
    world->macro_capsule_count = 0u;
    world->macro_capsule_capacity = 0u;
}

void d_macro_capsule_store_free(d_world* world)
{
    u32 i;
    if (!world) {
        return;
    }
    if (world->macro_capsules) {
        for (i = 0u; i < world->macro_capsule_count; ++i) {
            d_macro_capsule_entry_reset(&world->macro_capsules[i]);
        }
        free(world->macro_capsules);
    }
    world->macro_capsules = (d_macro_capsule_entry*)0;
    world->macro_capsule_count = 0u;
    world->macro_capsule_capacity = 0u;
}

static int d_macro_capsule_reserve(d_world* world, u32 capacity)
{
    d_macro_capsule_entry* new_entries;
    u32 old_capacity;
    u32 i;
    if (!world) {
        return -1;
    }
    if (capacity <= world->macro_capsule_capacity) {
        return 0;
    }
    new_entries = (d_macro_capsule_entry*)realloc(world->macro_capsules,
                                                  sizeof(d_macro_capsule_entry) * (size_t)capacity);
    if (!new_entries) {
        return -1;
    }
    old_capacity = world->macro_capsule_capacity;
    world->macro_capsules = new_entries;
    world->macro_capsule_capacity = capacity;
    for (i = old_capacity; i < world->macro_capsule_capacity; ++i) {
        memset(&world->macro_capsules[i], 0, sizeof(world->macro_capsules[i]));
    }
    return 0;
}

static u32 d_macro_capsule_find_index(const d_world* world, u64 capsule_id, int* out_found)
{
    u32 low = 0u;
    u32 high;
    if (out_found) {
        *out_found = 0;
    }
    if (!world || !world->macro_capsules || world->macro_capsule_count == 0u) {
        return 0u;
    }
    high = world->macro_capsule_count;
    while (low < high) {
        u32 mid = low + (u32)((high - low) / 2u);
        const d_macro_capsule_entry* entry = &world->macro_capsules[mid];
        if (entry->capsule_id == capsule_id) {
            if (out_found) {
                *out_found = 1;
            }
            return mid;
        }
        if (entry->capsule_id < capsule_id) {
            low = mid + 1u;
        } else {
            high = mid;
        }
    }
    return low;
}

static int d_macro_capsule_insert_at(d_world* world, u32 index)
{
    u32 i;
    if (!world || index > world->macro_capsule_count) {
        return -1;
    }
    if (world->macro_capsule_count >= world->macro_capsule_capacity) {
        u32 new_capacity = world->macro_capsule_capacity ? (world->macro_capsule_capacity * 2u) : 4u;
        if (new_capacity < world->macro_capsule_capacity) {
            return -1;
        }
        if (d_macro_capsule_reserve(world, new_capacity) != 0) {
            return -1;
        }
    }
    for (i = world->macro_capsule_count; i > index; --i) {
        world->macro_capsules[i] = world->macro_capsules[i - 1u];
    }
    memset(&world->macro_capsules[index], 0, sizeof(world->macro_capsules[index]));
    world->macro_capsule_count += 1u;
    return 0;
}

int dom_macro_capsule_store_set_blob(d_world* world,
                                     u64 capsule_id,
                                     u64 domain_id,
                                     dom_act_time_t source_tick,
                                     const unsigned char* bytes,
                                     u32 byte_count)
{
    int found = 0;
    u32 index;
    d_macro_capsule_entry* entry;
    unsigned char* copy = (unsigned char*)0;
    if (!world || capsule_id == 0u) {
        return -1;
    }
    if (byte_count > 0u && !bytes) {
        return -2;
    }
    if (byte_count > 0u) {
        copy = (unsigned char*)malloc((size_t)byte_count);
        if (!copy) {
            return -3;
        }
        memcpy(copy, bytes, (size_t)byte_count);
    }

    index = d_macro_capsule_find_index(world, capsule_id, &found);
    if (!found) {
        if (d_macro_capsule_insert_at(world, index) != 0) {
            if (copy) {
                free(copy);
            }
            return -4;
        }
    }
    entry = &world->macro_capsules[index];
    d_macro_capsule_entry_reset(entry);
    entry->capsule_id = capsule_id;
    entry->domain_id = domain_id;
    entry->source_tick = source_tick;
    entry->bytes = copy;
    entry->byte_count = byte_count;
    entry->capacity = byte_count;
    entry->in_use = 1u;
    return 0;
}

int dom_macro_capsule_store_get_blob(const d_world* world,
                                     u64 capsule_id,
                                     dom_macro_capsule_blob* out_blob)
{
    int found = 0;
    u32 index;
    const d_macro_capsule_entry* entry;
    if (!world || !out_blob || capsule_id == 0u) {
        return -1;
    }
    index = d_macro_capsule_find_index(world, capsule_id, &found);
    if (!found) {
        return -2;
    }
    entry = &world->macro_capsules[index];
    out_blob->capsule_id = entry->capsule_id;
    out_blob->domain_id = entry->domain_id;
    out_blob->source_tick = entry->source_tick;
    out_blob->bytes = entry->bytes;
    out_blob->byte_count = entry->byte_count;
    return 0;
}

u32 dom_macro_capsule_store_count(const d_world* world)
{
    if (!world) {
        return 0u;
    }
    return world->macro_capsule_count;
}

int dom_macro_capsule_store_get_by_index(const d_world* world,
                                         u32 index,
                                         dom_macro_capsule_blob* out_blob)
{
    const d_macro_capsule_entry* entry;
    if (!world || !out_blob || index >= world->macro_capsule_count) {
        return -1;
    }
    entry = &world->macro_capsules[index];
    if (!entry->in_use) {
        return -2;
    }
    out_blob->capsule_id = entry->capsule_id;
    out_blob->domain_id = entry->domain_id;
    out_blob->source_tick = entry->source_tick;
    out_blob->bytes = entry->bytes;
    out_blob->byte_count = entry->byte_count;
    return 0;
}

void dom_macro_capsule_store_clear(d_world* world)
{
    u32 i;
    if (!world || !world->macro_capsules) {
        return;
    }
    for (i = 0u; i < world->macro_capsule_count; ++i) {
        d_macro_capsule_entry_reset(&world->macro_capsules[i]);
    }
    world->macro_capsule_count = 0u;
}

static int d_macro_capsule_write_bytes(unsigned char* dst,
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

static int d_macro_capsule_read_bytes(const unsigned char* src,
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

int d_macro_capsule_store_serialize(const d_world* world, d_tlv_blob* out_blob)
{
    u64 total_len64;
    u32 total_len;
    u32 offset = 0u;
    u32 i;
    u32 version = D_MACRO_CAPSULE_STORE_VERSION;
    unsigned char* buffer;
    if (!out_blob) {
        return -1;
    }
    out_blob->ptr = (unsigned char*)0;
    out_blob->len = 0u;
    if (!world || world->macro_capsule_count == 0u) {
        return 0;
    }

    total_len64 = 8u;
    for (i = 0u; i < world->macro_capsule_count; ++i) {
        const d_macro_capsule_entry* entry = &world->macro_capsules[i];
        total_len64 += 8u + 8u + 8u + 4u;
        total_len64 += (u64)entry->byte_count;
    }
    if (total_len64 > 0xFFFFFFFFu) {
        return -2;
    }
    total_len = (u32)total_len64;
    buffer = (unsigned char*)malloc((size_t)total_len);
    if (!buffer) {
        return -3;
    }

    if (d_macro_capsule_write_bytes(buffer, total_len, &offset, &version, 4u) != 0 ||
        d_macro_capsule_write_bytes(buffer, total_len, &offset,
                                    &world->macro_capsule_count, 4u) != 0) {
        free(buffer);
        return -4;
    }

    for (i = 0u; i < world->macro_capsule_count; ++i) {
        const d_macro_capsule_entry* entry = &world->macro_capsules[i];
        if (d_macro_capsule_write_bytes(buffer, total_len, &offset, &entry->capsule_id, 8u) != 0 ||
            d_macro_capsule_write_bytes(buffer, total_len, &offset, &entry->domain_id, 8u) != 0 ||
            d_macro_capsule_write_bytes(buffer, total_len, &offset, &entry->source_tick, 8u) != 0 ||
            d_macro_capsule_write_bytes(buffer, total_len, &offset, &entry->byte_count, 4u) != 0 ||
            d_macro_capsule_write_bytes(buffer, total_len, &offset, entry->bytes, entry->byte_count) != 0) {
            free(buffer);
            return -5;
        }
    }

    out_blob->ptr = buffer;
    out_blob->len = total_len;
    return 0;
}

int d_macro_capsule_store_deserialize(d_world* world, const d_tlv_blob* in_blob)
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
    dom_macro_capsule_store_clear(world);
    if (d_macro_capsule_read_bytes(in_blob->ptr, in_blob->len, &offset, &version, 4u) != 0 ||
        d_macro_capsule_read_bytes(in_blob->ptr, in_blob->len, &offset, &count, 4u) != 0) {
        return -3;
    }
    if (version != D_MACRO_CAPSULE_STORE_VERSION) {
        return -4;
    }
    for (i = 0u; i < count; ++i) {
        u64 capsule_id = 0u;
        u64 domain_id = 0u;
        dom_act_time_t source_tick = 0;
        u32 byte_count = 0u;
        const unsigned char* bytes;
        if (d_macro_capsule_read_bytes(in_blob->ptr, in_blob->len, &offset, &capsule_id, 8u) != 0 ||
            d_macro_capsule_read_bytes(in_blob->ptr, in_blob->len, &offset, &domain_id, 8u) != 0 ||
            d_macro_capsule_read_bytes(in_blob->ptr, in_blob->len, &offset, &source_tick, 8u) != 0 ||
            d_macro_capsule_read_bytes(in_blob->ptr, in_blob->len, &offset, &byte_count, 4u) != 0) {
            return -5;
        }
        if (byte_count > in_blob->len - offset) {
            return -6;
        }
        bytes = in_blob->ptr + offset;
        offset += byte_count;
        if (dom_macro_capsule_store_set_blob(world,
                                             capsule_id,
                                             domain_id,
                                             source_tick,
                                             bytes,
                                             byte_count) != 0) {
            return -7;
        }
    }
    if (offset != in_blob->len) {
        return -8;
    }
    return 0;
}
