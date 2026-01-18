/*
FILE: game/rules/infrastructure/store_model.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / infrastructure
RESPONSIBILITY: Implements deterministic asset stores for production/logistics.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Store ordering and asset updates are deterministic.
*/
#include "dominium/rules/infrastructure/store_model.h"

#include <string.h>

void infra_store_registry_init(infra_store_registry* reg,
                               infra_store* storage,
                               u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->stores = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(infra_store) * (size_t)capacity);
    }
}

static u32 infra_store_find_index(const infra_store_registry* reg,
                                  u64 store_id,
                                  int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->stores) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->stores[i].store_id == store_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->stores[i].store_id > store_id) {
            break;
        }
    }
    return i;
}

int infra_store_register(infra_store_registry* reg,
                         u64 store_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    infra_store* entry;
    if (!reg || !reg->stores) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = infra_store_find_index(reg, store_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->stores[i] = reg->stores[i - 1u];
    }
    entry = &reg->stores[idx];
    memset(entry, 0, sizeof(*entry));
    entry->store_id = store_id;
    reg->count += 1u;
    return 0;
}

infra_store* infra_store_find(infra_store_registry* reg, u64 store_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->stores) {
        return 0;
    }
    idx = infra_store_find_index(reg, store_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->stores[idx];
}

const infra_store* infra_store_find_const(const infra_store_registry* reg, u64 store_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->stores) {
        return 0;
    }
    idx = infra_store_find_index(reg, store_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->stores[idx];
}

static u32 infra_store_asset_find_index(const infra_store* store,
                                        u64 asset_id,
                                        int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!store) {
        return 0u;
    }
    for (i = 0u; i < store->asset_count; ++i) {
        if (store->assets[i].asset_id == asset_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (store->assets[i].asset_id > asset_id) {
            break;
        }
    }
    return i;
}

int infra_store_get_qty(const infra_store_registry* reg,
                        u64 store_id,
                        u64 asset_id,
                        u32* out_qty)
{
    const infra_store* store;
    int found = 0;
    u32 idx;
    if (out_qty) {
        *out_qty = 0u;
    }
    if (!reg) {
        return -1;
    }
    store = infra_store_find_const(reg, store_id);
    if (!store) {
        return -2;
    }
    idx = infra_store_asset_find_index(store, asset_id, &found);
    if (!found) {
        return 0;
    }
    if (out_qty) {
        *out_qty = store->assets[idx].quantity;
    }
    return 0;
}

int infra_store_add(infra_store_registry* reg,
                    u64 store_id,
                    u64 asset_id,
                    u32 qty)
{
    infra_store* store;
    int found = 0;
    u32 idx;
    if (!reg || qty == 0u) {
        return 0;
    }
    store = infra_store_find(reg, store_id);
    if (!store) {
        return -1;
    }
    idx = infra_store_asset_find_index(store, asset_id, &found);
    if (found) {
        store->assets[idx].quantity += qty;
        return 0;
    }
    if (store->asset_count >= INFRA_STORE_MAX_ASSETS) {
        return -2;
    }
    if (idx < store->asset_count) {
        u32 j;
        for (j = store->asset_count; j > idx; --j) {
            store->assets[j] = store->assets[j - 1u];
        }
    }
    store->assets[idx].asset_id = asset_id;
    store->assets[idx].quantity = qty;
    store->asset_count += 1u;
    return 0;
}

int infra_store_consume(infra_store_registry* reg,
                        u64 store_id,
                        u64 asset_id,
                        u32 qty)
{
    infra_store* store;
    int found = 0;
    u32 idx;
    if (!reg || qty == 0u) {
        return 0;
    }
    store = infra_store_find(reg, store_id);
    if (!store) {
        return -1;
    }
    idx = infra_store_asset_find_index(store, asset_id, &found);
    if (!found) {
        return -2;
    }
    if (store->assets[idx].quantity < qty) {
        return -3;
    }
    store->assets[idx].quantity -= qty;
    if (store->assets[idx].quantity == 0u) {
        u32 j;
        for (j = idx + 1u; j < store->asset_count; ++j) {
            store->assets[j - 1u] = store->assets[j];
        }
        store->asset_count -= 1u;
    }
    return 0;
}

int infra_store_take(infra_store_registry* reg,
                     u64 store_id,
                     u64 asset_id,
                     u32 qty,
                     u32* out_taken)
{
    infra_store* store;
    int found = 0;
    u32 idx;
    u32 take;
    if (out_taken) {
        *out_taken = 0u;
    }
    if (!reg || qty == 0u) {
        return 0;
    }
    store = infra_store_find(reg, store_id);
    if (!store) {
        return -1;
    }
    idx = infra_store_asset_find_index(store, asset_id, &found);
    if (!found) {
        return 0;
    }
    take = store->assets[idx].quantity;
    if (take > qty) {
        take = qty;
    }
    store->assets[idx].quantity -= take;
    if (store->assets[idx].quantity == 0u) {
        u32 j;
        for (j = idx + 1u; j < store->asset_count; ++j) {
            store->assets[j - 1u] = store->assets[j];
        }
        store->asset_count -= 1u;
    }
    if (out_taken) {
        *out_taken = take;
    }
    return 0;
}

int infra_store_clear(infra_store_registry* reg, u64 store_id)
{
    infra_store* store = infra_store_find(reg, store_id);
    if (!store) {
        return -1;
    }
    memset(store->assets, 0, sizeof(store->assets));
    store->asset_count = 0u;
    return 0;
}
