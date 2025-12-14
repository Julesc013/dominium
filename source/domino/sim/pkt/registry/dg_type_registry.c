#include <stdlib.h>
#include <string.h>

#include "sim/pkt/registry/dg_type_registry.h"

static int dg_type_entry_cmp(const dg_type_registry_entry *a, const dg_type_registry_entry *b) {
    if (a->type_id < b->type_id) return -1;
    if (a->type_id > b->type_id) return 1;
    if (a->schema_id < b->schema_id) return -1;
    if (a->schema_id > b->schema_id) return 1;
    if (a->schema_ver_min < b->schema_ver_min) return -1;
    if (a->schema_ver_min > b->schema_ver_min) return 1;
    if (a->schema_ver_max < b->schema_ver_max) return -1;
    if (a->schema_ver_max > b->schema_ver_max) return 1;
    return 0;
}

static int dg_type_entry_ranges_overlap(const dg_type_registry_entry *a, const dg_type_registry_entry *b) {
    if (a->schema_ver_min > b->schema_ver_max) return 0;
    if (b->schema_ver_min > a->schema_ver_max) return 0;
    return 1;
}

void dg_type_registry_init(dg_type_registry *reg) {
    if (!reg) {
        return;
    }
    reg->entries = (dg_type_registry_entry *)0;
    reg->count = 0u;
    reg->capacity = 0u;
}

void dg_type_registry_free(dg_type_registry *reg) {
    if (!reg) {
        return;
    }
    if (reg->entries) {
        free(reg->entries);
    }
    reg->entries = (dg_type_registry_entry *)0;
    reg->count = 0u;
    reg->capacity = 0u;
}

int dg_type_registry_reserve(dg_type_registry *reg, u32 capacity) {
    dg_type_registry_entry *new_entries;
    if (!reg) {
        return -1;
    }
    if (capacity <= reg->capacity) {
        return 0;
    }
    new_entries = (dg_type_registry_entry *)realloc(reg->entries, sizeof(dg_type_registry_entry) * (size_t)capacity);
    if (!new_entries) {
        return -2;
    }
    reg->entries = new_entries;
    reg->capacity = capacity;
    return 0;
}

static u32 dg_type_registry_lower_bound(const dg_type_registry *reg, const dg_type_registry_entry *key, int *out_found) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    int cmp;

    if (out_found) {
        *out_found = 0;
    }

    if (!reg || reg->count == 0u) {
        return 0u;
    }

    hi = reg->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        cmp = dg_type_entry_cmp(&reg->entries[mid], key);
        if (cmp < 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }

    if (lo < reg->count) {
        cmp = dg_type_entry_cmp(&reg->entries[lo], key);
        if (cmp == 0 && out_found) {
            *out_found = 1;
        }
    }
    return lo;
}

static int dg_type_registry_check_overlap_near(
    const dg_type_registry *reg,
    u32                    insert_index,
    const dg_type_registry_entry *entry
) {
    u32 i;

    if (!reg || !entry) {
        return -1;
    }

    /* Scan backwards while keys match (type_id, schema_id). */
    i = insert_index;
    while (i > 0u) {
        const dg_type_registry_entry *e = &reg->entries[i - 1u];
        if (e->type_id != entry->type_id || e->schema_id != entry->schema_id) {
            break;
        }
        if (dg_type_entry_ranges_overlap(e, entry)) {
            return -2;
        }
        i -= 1u;
    }

    /* Scan forward while keys match (type_id, schema_id). */
    for (i = insert_index; i < reg->count; ++i) {
        const dg_type_registry_entry *e = &reg->entries[i];
        if (e->type_id != entry->type_id || e->schema_id != entry->schema_id) {
            break;
        }
        if (dg_type_entry_ranges_overlap(e, entry)) {
            return -2;
        }
    }

    return 0;
}

int dg_type_registry_add(dg_type_registry *reg, const dg_type_registry_entry *entry) {
    dg_type_registry_entry key;
    u32 idx;
    int found;
    int rc;

    if (!reg || !entry) {
        return -1;
    }
    if (entry->schema_ver_min > entry->schema_ver_max) {
        return -2;
    }

    key = *entry;
    idx = dg_type_registry_lower_bound(reg, &key, &found);
    if (found) {
        return -3; /* duplicate exact entry */
    }

    rc = dg_type_registry_check_overlap_near(reg, idx, entry);
    if (rc != 0) {
        return -4; /* overlapping version ranges for same type/schema */
    }

    if (reg->count >= reg->capacity) {
        u32 new_cap = (reg->capacity == 0u) ? 16u : (reg->capacity * 2u);
        rc = dg_type_registry_reserve(reg, new_cap);
        if (rc != 0) {
            return -5;
        }
    }

    if (idx < reg->count) {
        memmove(&reg->entries[idx + 1u], &reg->entries[idx],
                sizeof(dg_type_registry_entry) * (size_t)(reg->count - idx));
    }
    reg->entries[idx] = *entry;
    reg->count += 1u;
    return 0;
}

u32 dg_type_registry_count(const dg_type_registry *reg) {
    return reg ? reg->count : 0u;
}

const dg_type_registry_entry *dg_type_registry_at(const dg_type_registry *reg, u32 index) {
    if (!reg || index >= reg->count) {
        return (const dg_type_registry_entry *)0;
    }
    return &reg->entries[index];
}

const dg_type_registry_entry *dg_type_registry_find(
    const dg_type_registry *reg,
    dg_type_id              type_id,
    dg_schema_id            schema_id,
    u16                     schema_ver
) {
    u32 lo, hi, mid;

    if (!reg || !reg->entries || reg->count == 0u) {
        return (const dg_type_registry_entry *)0;
    }

    /* Binary search for first entry with type_id (lower bound on type_id). */
    lo = 0u;
    hi = reg->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (reg->entries[mid].type_id < type_id) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }

    /* Scan forward for matching schema_id + version range. */
    for (; lo < reg->count; ++lo) {
        const dg_type_registry_entry *e = &reg->entries[lo];
        if (e->type_id != type_id) {
            break;
        }
        if (e->schema_id != schema_id) {
            continue;
        }
        if (schema_ver < e->schema_ver_min || schema_ver > e->schema_ver_max) {
            continue;
        }
        return e;
    }

    return (const dg_type_registry_entry *)0;
}

