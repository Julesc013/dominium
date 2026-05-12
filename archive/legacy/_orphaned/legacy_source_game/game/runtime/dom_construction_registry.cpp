/*
FILE: source/dominium/game/runtime/dom_construction_registry.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/construction_registry
RESPONSIBILITY: Deterministic construction registry (instances + occupancy).
*/
#include "runtime/dom_construction_registry.h"

#include <algorithm>
#include <vector>
#include <cstring>

namespace {

struct DomConstructionCell {
    i32 x;
    i32 y;
};

struct DomConstructionChunk {
    dom_surface_chunk_key key;
    std::vector<DomConstructionCell> cells;
};

static bool chunk_key_less(const dom_surface_chunk_key &a, const dom_surface_chunk_key &b) {
    if (a.body_id != b.body_id) {
        return a.body_id < b.body_id;
    }
    if (a.step_turns_q16 != b.step_turns_q16) {
        return a.step_turns_q16 < b.step_turns_q16;
    }
    if (a.lat_index != b.lat_index) {
        return a.lat_index < b.lat_index;
    }
    return a.lon_index < b.lon_index;
}

static bool chunk_key_equal(const dom_surface_chunk_key &a, const dom_surface_chunk_key &b) {
    return a.body_id == b.body_id &&
           a.step_turns_q16 == b.step_turns_q16 &&
           a.lat_index == b.lat_index &&
           a.lon_index == b.lon_index;
}

static bool cell_less(const DomConstructionCell &a, const DomConstructionCell &b) {
    if (a.x != b.x) {
        return a.x < b.x;
    }
    return a.y < b.y;
}

static bool cell_equal(const DomConstructionCell &a, const DomConstructionCell &b) {
    return a.x == b.x && a.y == b.y;
}

static int find_instance_index(const std::vector<dom_construction_instance> &list,
                               dom_construction_instance_id id) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].instance_id == id) {
            return (int)i;
        }
    }
    return -1;
}

static DomConstructionChunk *find_chunk(std::vector<DomConstructionChunk> &chunks,
                                        const dom_surface_chunk_key &key,
                                        size_t *out_index) {
    size_t i;
    for (i = 0u; i < chunks.size(); ++i) {
        if (chunk_key_equal(chunks[i].key, key)) {
            if (out_index) {
                *out_index = i;
            }
            return &chunks[i];
        }
    }
    return 0;
}

static void insert_chunk_sorted(std::vector<DomConstructionChunk> &chunks,
                                const DomConstructionChunk &chunk) {
    size_t i = 0u;
    while (i < chunks.size() && chunk_key_less(chunks[i].key, chunk.key)) {
        ++i;
    }
    chunks.insert(chunks.begin() + (std::vector<DomConstructionChunk>::difference_type)i, chunk);
}

static bool cell_exists(const std::vector<DomConstructionCell> &cells, const DomConstructionCell &cell) {
    size_t i;
    for (i = 0u; i < cells.size(); ++i) {
        if (cell_equal(cells[i], cell)) {
            return true;
        }
    }
    return false;
}

static void remove_cell(std::vector<DomConstructionCell> &cells, const DomConstructionCell &cell) {
    size_t i = 0u;
    while (i < cells.size()) {
        if (cell_equal(cells[i], cell)) {
            cells.erase(cells.begin() + (std::vector<DomConstructionCell>::difference_type)i);
            return;
        }
        ++i;
    }
}

static bool instance_less(const dom_construction_instance &a,
                          const dom_construction_instance &b) {
    return a.instance_id < b.instance_id;
}

} // namespace

struct dom_construction_registry {
    std::vector<dom_construction_instance> instances;
    std::vector<DomConstructionChunk> chunks;
    dom_construction_instance_id next_id;
};

dom_construction_registry *dom_construction_registry_create(void) {
    dom_construction_registry *registry = new dom_construction_registry();
    if (!registry) {
        return 0;
    }
    (void)dom_construction_registry_init(registry);
    return registry;
}

void dom_construction_registry_destroy(dom_construction_registry *registry) {
    if (!registry) {
        return;
    }
    delete registry;
}

int dom_construction_registry_init(dom_construction_registry *registry) {
    if (!registry) {
        return DOM_CONSTRUCTION_INVALID_ARGUMENT;
    }
    registry->instances.clear();
    registry->chunks.clear();
    registry->next_id = 1ull;
    return DOM_CONSTRUCTION_OK;
}

int dom_construction_register_instance(dom_construction_registry *registry,
                                       const dom_construction_instance *inst,
                                       dom_construction_instance_id *out_id) {
    dom_construction_instance entry;
    DomConstructionChunk chunk_entry;
    DomConstructionChunk *chunk;
    DomConstructionCell cell;
    size_t chunk_index = 0u;
    if (!registry || !inst) {
        return DOM_CONSTRUCTION_INVALID_ARGUMENT;
    }
    if (inst->type_id == 0u || inst->body_id == 0ull) {
        return DOM_CONSTRUCTION_INVALID_ARGUMENT;
    }
    if (inst->chunk_key.body_id == 0ull) {
        return DOM_CONSTRUCTION_INVALID_ARGUMENT;
    }

    entry = *inst;

    if (entry.instance_id == 0ull) {
        entry.instance_id = registry->next_id ? registry->next_id : 1ull;
        registry->next_id = entry.instance_id + 1ull;
    } else {
        if (find_instance_index(registry->instances, entry.instance_id) >= 0) {
            return DOM_CONSTRUCTION_DUPLICATE_ID;
        }
        if (entry.instance_id >= registry->next_id) {
            registry->next_id = entry.instance_id + 1ull;
        }
    }

    cell.x = entry.cell_x;
    cell.y = entry.cell_y;

    chunk = find_chunk(registry->chunks, entry.chunk_key, &chunk_index);
    if (!chunk) {
        std::memset(&chunk_entry, 0, sizeof(chunk_entry));
        chunk_entry.key = entry.chunk_key;
        insert_chunk_sorted(registry->chunks, chunk_entry);
        chunk = find_chunk(registry->chunks, entry.chunk_key, &chunk_index);
        if (!chunk) {
            return DOM_CONSTRUCTION_ERR;
        }
    }
    if (cell_exists(chunk->cells, cell)) {
        return DOM_CONSTRUCTION_OVERLAP;
    }
    chunk->cells.push_back(cell);
    std::sort(chunk->cells.begin(), chunk->cells.end(), cell_less);

    registry->instances.push_back(entry);
    std::sort(registry->instances.begin(), registry->instances.end(), instance_less);

    if (out_id) {
        *out_id = entry.instance_id;
    }
    return DOM_CONSTRUCTION_OK;
}

int dom_construction_remove_instance(dom_construction_registry *registry,
                                     dom_construction_instance_id id) {
    int idx;
    if (!registry || id == 0ull) {
        return DOM_CONSTRUCTION_INVALID_ARGUMENT;
    }
    idx = find_instance_index(registry->instances, id);
    if (idx < 0) {
        return DOM_CONSTRUCTION_NOT_FOUND;
    }
    {
        const dom_construction_instance &entry = registry->instances[(size_t)idx];
        DomConstructionChunk *chunk = 0;
        size_t chunk_index = 0u;
        DomConstructionCell cell;
        cell.x = entry.cell_x;
        cell.y = entry.cell_y;
        chunk = find_chunk(registry->chunks, entry.chunk_key, &chunk_index);
        if (chunk) {
            remove_cell(chunk->cells, cell);
            if (chunk->cells.empty()) {
                registry->chunks.erase(
                    registry->chunks.begin() +
                    (std::vector<DomConstructionChunk>::difference_type)chunk_index);
            }
        }
    }
    registry->instances.erase(registry->instances.begin() + (std::vector<dom_construction_instance>::difference_type)idx);
    return DOM_CONSTRUCTION_OK;
}

int dom_construction_get(const dom_construction_registry *registry,
                         dom_construction_instance_id id,
                         dom_construction_instance *out_instance) {
    int idx;
    if (!registry || !out_instance || id == 0ull) {
        return DOM_CONSTRUCTION_INVALID_ARGUMENT;
    }
    idx = find_instance_index(registry->instances, id);
    if (idx < 0) {
        return DOM_CONSTRUCTION_NOT_FOUND;
    }
    *out_instance = registry->instances[(size_t)idx];
    return DOM_CONSTRUCTION_OK;
}

int dom_construction_list(const dom_construction_registry *registry,
                          dom_construction_instance *out_list,
                          u32 max_entries,
                          u32 *out_count) {
    u32 count = 0u;
    size_t i;
    if (!registry || !out_count) {
        return DOM_CONSTRUCTION_INVALID_ARGUMENT;
    }
    count = (u32)registry->instances.size();
    if (out_list && max_entries > 0u) {
        const u32 limit = (count < max_entries) ? count : max_entries;
        for (i = 0u; i < limit; ++i) {
            out_list[i] = registry->instances[i];
        }
    }
    *out_count = count;
    return DOM_CONSTRUCTION_OK;
}

u32 dom_construction_count(const dom_construction_registry *registry) {
    if (!registry) {
        return 0u;
    }
    return (u32)registry->instances.size();
}
