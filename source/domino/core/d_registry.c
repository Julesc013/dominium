#include <stdio.h>

#include "d_registry.h"

void d_registry_init(
    d_registry       *reg,
    d_registry_entry *storage,
    u32               capacity,
    u32               first_id
) {
    if (!reg) {
        return;
    }
    reg->entries = storage;
    reg->capacity = capacity;
    reg->count = 0u;
    reg->next_id = first_id ? first_id : 1u;
    if (reg->next_id == 0u) {
        reg->next_id = 1u;
    }
}

u32 d_registry_add(d_registry *reg, void *ptr) {
    d_registry_entry *entry;
    if (!reg || !reg->entries) {
        fprintf(stderr, "d_registry_add: registry not initialized\n");
        return 0u;
    }
    if (reg->count >= reg->capacity) {
        fprintf(stderr, "d_registry_add: registry full\n");
        return 0u;
    }
    if (reg->next_id == 0u || reg->next_id == 0xFFFFFFFFu) {
        fprintf(stderr, "d_registry_add: id overflow\n");
        return 0u;
    }

    entry = &reg->entries[reg->count];
    entry->id = reg->next_id;
    entry->ptr = ptr;
    reg->count += 1u;
    reg->next_id += 1u;
    /* TODO: upgrade to open-addressing or sorted lookup if hot. */
    return entry->id;
}

u32 d_registry_add_with_id(d_registry *reg, u32 id, void *ptr) {
    u32 i;
    d_registry_entry *entry;
    if (!reg || !reg->entries) {
        fprintf(stderr, "d_registry_add_with_id: registry not initialized\n");
        return 0u;
    }
    if (reg->count >= reg->capacity) {
        fprintf(stderr, "d_registry_add_with_id: registry full\n");
        return 0u;
    }
    if (id == 0u || id == 0xFFFFFFFFu) {
        fprintf(stderr, "d_registry_add_with_id: invalid id\n");
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->entries[i].id == id) {
            fprintf(stderr, "d_registry_add_with_id: duplicate id %u\n", (unsigned int)id);
            return 0u;
        }
    }

    entry = &reg->entries[reg->count];
    entry->id = id;
    entry->ptr = ptr;
    reg->count += 1u;
    if (id >= reg->next_id) {
        reg->next_id = id + 1u;
    }
    return entry->id;
}

void *d_registry_get(const d_registry *reg, u32 id) {
    u32 i;
    if (!reg || !reg->entries) {
        return (void *)0;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->entries[i].id == id) {
            return reg->entries[i].ptr;
        }
    }
    return (void *)0;
}

d_registry_entry *d_registry_get_by_index(d_registry *reg, u32 index) {
    if (!reg || !reg->entries) {
        return (d_registry_entry *)0;
    }
    if (index >= reg->count) {
        return (d_registry_entry *)0;
    }
    return &reg->entries[index];
}
