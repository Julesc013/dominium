/*
FILE: source/dominium/game/runtime/dom_belief_store.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/belief_store
RESPONSIBILITY: Deterministic belief record store (derived cache).
*/
#include "runtime/dom_belief_store.h"

#include <vector>

namespace {

static int compare_record(const dom_belief_record &a, const dom_belief_record &b) {
    if (a.capability_id != b.capability_id) {
        return (a.capability_id < b.capability_id) ? -1 : 1;
    }
    if (a.subject.kind != b.subject.kind) {
        return (a.subject.kind < b.subject.kind) ? -1 : 1;
    }
    if (a.subject.id != b.subject.id) {
        return (a.subject.id < b.subject.id) ? -1 : 1;
    }
    if (a.record_id != b.record_id) {
        return (a.record_id < b.record_id) ? -1 : 1;
    }
    return 0;
}

static int find_record_index(const std::vector<dom_belief_record> &records,
                             u64 record_id) {
    for (size_t i = 0u; i < records.size(); ++i) {
        if (records[i].record_id == record_id) {
            return (int)i;
        }
    }
    return -1;
}

static void insert_record_sorted(std::vector<dom_belief_record> &records,
                                 const dom_belief_record &record) {
    size_t i = 0u;
    while (i < records.size() && compare_record(records[i], record) < 0) {
        ++i;
    }
    records.insert(records.begin() + (std::vector<dom_belief_record>::difference_type)i, record);
}

} // namespace

struct dom_belief_store {
    std::vector<dom_belief_record> records;
    u64 revision;
};

dom_belief_store *dom_belief_store_create(void) {
    dom_belief_store *store = new dom_belief_store();
    if (!store) {
        return 0;
    }
    if (dom_belief_store_init(store) != DOM_BELIEF_OK) {
        delete store;
        return 0;
    }
    return store;
}

void dom_belief_store_destroy(dom_belief_store *store) {
    if (!store) {
        return;
    }
    delete store;
}

int dom_belief_store_init(dom_belief_store *store) {
    if (!store) {
        return DOM_BELIEF_INVALID_ARGUMENT;
    }
    store->records.clear();
    store->revision = 0u;
    return DOM_BELIEF_OK;
}

int dom_belief_store_add_record(dom_belief_store *store,
                                const dom_belief_record *record) {
    if (!store || !record) {
        return DOM_BELIEF_INVALID_ARGUMENT;
    }
    if (record->record_id == 0ull || record->capability_id == 0u) {
        return DOM_BELIEF_INVALID_ARGUMENT;
    }
    if (record->subject.kind != DOM_CAP_SUBJECT_NONE && record->subject.id == 0ull) {
        return DOM_BELIEF_INVALID_ARGUMENT;
    }
    if (find_record_index(store->records, record->record_id) >= 0) {
        return DOM_BELIEF_DUPLICATE_ID;
    }
    insert_record_sorted(store->records, *record);
    store->revision += 1u;
    return DOM_BELIEF_OK;
}

int dom_belief_store_remove_record(dom_belief_store *store,
                                   u64 record_id) {
    const int idx = store ? find_record_index(store->records, record_id) : -1;
    if (!store || record_id == 0ull) {
        return DOM_BELIEF_INVALID_ARGUMENT;
    }
    if (idx < 0) {
        return DOM_BELIEF_NOT_FOUND;
    }
    store->records.erase(store->records.begin() + (std::vector<dom_belief_record>::difference_type)idx);
    store->revision += 1u;
    return DOM_BELIEF_OK;
}

int dom_belief_store_clear(dom_belief_store *store) {
    if (!store) {
        return DOM_BELIEF_INVALID_ARGUMENT;
    }
    store->records.clear();
    store->revision += 1u;
    return DOM_BELIEF_OK;
}

int dom_belief_store_list_records(const dom_belief_store *store,
                                  dom_belief_record *out_records,
                                  u32 max_records,
                                  u32 *out_count) {
    if (!store || !out_count) {
        return DOM_BELIEF_INVALID_ARGUMENT;
    }
    *out_count = (u32)store->records.size();
    if (!out_records || max_records == 0u) {
        return DOM_BELIEF_OK;
    }
    {
        const u32 limit = (max_records < *out_count) ? max_records : *out_count;
        for (u32 i = 0u; i < limit; ++i) {
            out_records[i] = store->records[i];
        }
    }
    return DOM_BELIEF_OK;
}

int dom_belief_store_iterate(const dom_belief_store *store,
                             void (*fn)(const dom_belief_record *record, void *user),
                             void *user) {
    if (!store || !fn) {
        return DOM_BELIEF_INVALID_ARGUMENT;
    }
    for (size_t i = 0u; i < store->records.size(); ++i) {
        fn(&store->records[i], user);
    }
    return DOM_BELIEF_OK;
}

int dom_belief_store_get_revision(const dom_belief_store *store,
                                  u64 *out_revision) {
    if (!store || !out_revision) {
        return DOM_BELIEF_INVALID_ARGUMENT;
    }
    *out_revision = store->revision;
    return DOM_BELIEF_OK;
}
