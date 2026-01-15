/*
FILE: source/dominium/game/runtime/dom_transfer_scheduler.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/transfer_scheduler
RESPONSIBILITY: Deterministic transfer scheduling and arrival updates.
*/
#include "runtime/dom_transfer_scheduler.h"

#include <algorithm>
#include <vector>
#include <climits>

namespace {

struct TransferRecord {
    dom_transfer_id transfer_id;
    dom_route_id route_id;
    u64 start_tick;
    u64 arrival_tick;
    u32 entry_count;
    u64 total_units;
    std::vector<dom_transfer_entry> entries;
};

static bool entry_less(const dom_transfer_entry &a, const dom_transfer_entry &b) {
    return a.resource_id < b.resource_id;
}

static bool transfer_less(const TransferRecord &a, const TransferRecord &b) {
    if (a.arrival_tick != b.arrival_tick) {
        return a.arrival_tick < b.arrival_tick;
    }
    return a.transfer_id < b.transfer_id;
}

static int normalize_entries(const dom_transfer_entry *entries,
                             u32 entry_count,
                             std::vector<dom_transfer_entry> &out,
                             u64 *out_total_units) {
    if (!entries || entry_count == 0u || !out_total_units) {
        return DOM_TRANSFER_INVALID_ARGUMENT;
    }
    out.clear();
    out.reserve(entry_count);
    for (u32 i = 0u; i < entry_count; ++i) {
        if (entries[i].resource_id == 0ull || entries[i].quantity <= 0) {
            return DOM_TRANSFER_INVALID_DATA;
        }
        out.push_back(entries[i]);
    }
    std::sort(out.begin(), out.end(), entry_less);

    *out_total_units = 0ull;
    {
        std::vector<dom_transfer_entry> merged;
        merged.reserve(out.size());
        for (size_t i = 0u; i < out.size(); ++i) {
            const dom_transfer_entry &entry = out[i];
            if (!merged.empty() && merged.back().resource_id == entry.resource_id) {
                if (entry.quantity > 0 &&
                    merged.back().quantity > (LLONG_MAX - entry.quantity)) {
                    return DOM_TRANSFER_OVERFLOW;
                }
                merged.back().quantity += entry.quantity;
            } else {
                merged.push_back(entry);
            }
        }
        out.swap(merged);
    }

    for (size_t i = 0u; i < out.size(); ++i) {
        const i64 qty = out[i].quantity;
        if (qty <= 0) {
            return DOM_TRANSFER_INVALID_DATA;
        }
        if (*out_total_units > (ULLONG_MAX - (u64)qty)) {
            return DOM_TRANSFER_OVERFLOW;
        }
        *out_total_units += (u64)qty;
    }
    return DOM_TRANSFER_OK;
}

} // namespace

struct dom_transfer_scheduler {
    std::vector<TransferRecord> transfers;
    dom_transfer_id next_id;
};

dom_transfer_scheduler *dom_transfer_scheduler_create(void) {
    dom_transfer_scheduler *sched = new dom_transfer_scheduler();
    if (!sched) {
        return 0;
    }
    (void)dom_transfer_scheduler_init(sched);
    return sched;
}

void dom_transfer_scheduler_destroy(dom_transfer_scheduler *sched) {
    if (!sched) {
        return;
    }
    delete sched;
}

int dom_transfer_scheduler_init(dom_transfer_scheduler *sched) {
    if (!sched) {
        return DOM_TRANSFER_INVALID_ARGUMENT;
    }
    sched->transfers.clear();
    sched->next_id = 1ull;
    return DOM_TRANSFER_OK;
}

int dom_transfer_schedule(dom_transfer_scheduler *sched,
                          const dom_route_graph *routes,
                          dom_station_registry *stations,
                          dom_route_id route_id,
                          const dom_transfer_entry *entries,
                          u32 entry_count,
                          u64 current_tick,
                          dom_transfer_id *out_id) {
    dom_route_info route;
    TransferRecord record;
    std::vector<dom_transfer_entry> normalized;
    u64 total_units = 0ull;
    u64 arrival_tick = 0ull;
    int rc;

    if (!sched || !routes || !stations || route_id == 0ull) {
        return DOM_TRANSFER_INVALID_ARGUMENT;
    }

    rc = dom_route_graph_get(routes, route_id, &route);
    if (rc != DOM_ROUTE_GRAPH_OK) {
        return DOM_TRANSFER_NOT_FOUND;
    }

    rc = normalize_entries(entries, entry_count, normalized, &total_units);
    if (rc != DOM_TRANSFER_OK) {
        return rc;
    }
    if (total_units > route.capacity_units) {
        return DOM_TRANSFER_CAPACITY_EXCEEDED;
    }

    for (size_t i = 0u; i < normalized.size(); ++i) {
        i64 have = 0;
        rc = dom_station_inventory_get(stations,
                                       route.src_station_id,
                                       normalized[i].resource_id,
                                       &have);
        if (rc != DOM_STATION_REGISTRY_OK || have < normalized[i].quantity) {
            return DOM_TRANSFER_INSUFFICIENT;
        }
    }
    for (size_t i = 0u; i < normalized.size(); ++i) {
        rc = dom_station_inventory_remove(stations,
                                          route.src_station_id,
                                          normalized[i].resource_id,
                                          normalized[i].quantity);
        if (rc != DOM_STATION_REGISTRY_OK) {
            return DOM_TRANSFER_ERR;
        }
    }

    if (sched->next_id == 0ull) {
        sched->next_id = 1ull;
    }
    record.transfer_id = sched->next_id++;
    record.route_id = route.route_id;
    record.start_tick = current_tick;
    arrival_tick = current_tick + route.duration_ticks;
    if (arrival_tick < current_tick) {
        return DOM_TRANSFER_OVERFLOW;
    }
    record.arrival_tick = arrival_tick;
    record.entries = normalized;
    record.entry_count = (u32)normalized.size();
    record.total_units = total_units;

    {
        size_t i = 0u;
        while (i < sched->transfers.size() && transfer_less(sched->transfers[i], record)) {
            ++i;
        }
        sched->transfers.insert(sched->transfers.begin() +
                                (std::vector<TransferRecord>::difference_type)i,
                                record);
    }

    if (out_id) {
        *out_id = record.transfer_id;
    }
    return DOM_TRANSFER_OK;
}

int dom_transfer_add_loaded(dom_transfer_scheduler *sched,
                            const dom_route_graph *routes,
                            dom_route_id route_id,
                            dom_transfer_id transfer_id,
                            u64 start_tick,
                            u64 arrival_tick,
                            const dom_transfer_entry *entries,
                            u32 entry_count,
                            u64 total_units) {
    dom_route_info route;
    TransferRecord record;
    std::vector<dom_transfer_entry> normalized;
    u64 computed_units = 0ull;
    int rc;

    if (!sched || !routes || route_id == 0ull || transfer_id == 0ull) {
        return DOM_TRANSFER_INVALID_ARGUMENT;
    }
    if (arrival_tick < start_tick) {
        return DOM_TRANSFER_INVALID_DATA;
    }
    for (size_t i = 0u; i < sched->transfers.size(); ++i) {
        if (sched->transfers[i].transfer_id == transfer_id) {
            return DOM_TRANSFER_INVALID_DATA;
        }
    }

    rc = dom_route_graph_get(routes, route_id, &route);
    if (rc != DOM_ROUTE_GRAPH_OK) {
        return DOM_TRANSFER_NOT_FOUND;
    }
    rc = normalize_entries(entries, entry_count, normalized, &computed_units);
    if (rc != DOM_TRANSFER_OK) {
        return rc;
    }
    if (total_units != 0ull && total_units != computed_units) {
        return DOM_TRANSFER_INVALID_DATA;
    }
    if (computed_units > route.capacity_units) {
        return DOM_TRANSFER_CAPACITY_EXCEEDED;
    }

    record.transfer_id = transfer_id;
    record.route_id = route_id;
    record.start_tick = start_tick;
    record.arrival_tick = arrival_tick;
    record.entries = normalized;
    record.entry_count = (u32)normalized.size();
    record.total_units = computed_units;

    {
        size_t i = 0u;
        while (i < sched->transfers.size() && transfer_less(sched->transfers[i], record)) {
            ++i;
        }
        sched->transfers.insert(sched->transfers.begin() +
                                (std::vector<TransferRecord>::difference_type)i,
                                record);
    }
    if (transfer_id >= sched->next_id) {
        sched->next_id = transfer_id + 1ull;
    }
    return DOM_TRANSFER_OK;
}

int dom_transfer_update(dom_transfer_scheduler *sched,
                        const dom_route_graph *routes,
                        dom_station_registry *stations,
                        u64 current_tick) {
    size_t i = 0u;
    if (!sched || !routes || !stations) {
        return DOM_TRANSFER_INVALID_ARGUMENT;
    }
    while (i < sched->transfers.size()) {
        TransferRecord &rec = sched->transfers[i];
        if (rec.arrival_tick > current_tick) {
            ++i;
            continue;
        }
        dom_route_info route;
        if (dom_route_graph_get(routes, rec.route_id, &route) != DOM_ROUTE_GRAPH_OK) {
            return DOM_TRANSFER_ERR;
        }
        for (size_t j = 0u; j < rec.entries.size(); ++j) {
            const dom_transfer_entry &entry = rec.entries[j];
            if (dom_station_inventory_add(stations,
                                          route.dst_station_id,
                                          entry.resource_id,
                                          entry.quantity) != DOM_STATION_REGISTRY_OK) {
                return DOM_TRANSFER_ERR;
            }
        }
        sched->transfers.erase(sched->transfers.begin() +
                               (std::vector<TransferRecord>::difference_type)i);
    }
    return DOM_TRANSFER_OK;
}

int dom_transfer_list(const dom_transfer_scheduler *sched,
                      dom_transfer_info *out_list,
                      u32 max_entries,
                      u32 *out_count) {
    u32 count;
    if (!sched || !out_count) {
        return DOM_TRANSFER_INVALID_ARGUMENT;
    }
    count = (u32)sched->transfers.size();
    if (out_list && max_entries > 0u) {
        const u32 limit = (count < max_entries) ? count : max_entries;
        for (u32 i = 0u; i < limit; ++i) {
            const TransferRecord &rec = sched->transfers[i];
            out_list[i].transfer_id = rec.transfer_id;
            out_list[i].route_id = rec.route_id;
            out_list[i].start_tick = rec.start_tick;
            out_list[i].arrival_tick = rec.arrival_tick;
            out_list[i].entry_count = rec.entry_count;
            out_list[i].total_units = rec.total_units;
        }
    }
    *out_count = count;
    return DOM_TRANSFER_OK;
}

int dom_transfer_get_entries(const dom_transfer_scheduler *sched,
                             dom_transfer_id transfer_id,
                             dom_transfer_entry *out_entries,
                             u32 max_entries,
                             u32 *out_count) {
    if (!sched || !out_count || transfer_id == 0ull) {
        return DOM_TRANSFER_INVALID_ARGUMENT;
    }
    for (size_t i = 0u; i < sched->transfers.size(); ++i) {
        if (sched->transfers[i].transfer_id == transfer_id) {
            const TransferRecord &rec = sched->transfers[i];
            const u32 count = (u32)rec.entries.size();
            if (out_entries && max_entries > 0u) {
                const u32 limit = (count < max_entries) ? count : max_entries;
                for (u32 j = 0u; j < limit; ++j) {
                    out_entries[j] = rec.entries[j];
                }
            }
            *out_count = count;
            return DOM_TRANSFER_OK;
        }
    }
    return DOM_TRANSFER_NOT_FOUND;
}

u32 dom_transfer_count(const dom_transfer_scheduler *sched) {
    if (!sched) {
        return 0u;
    }
    return (u32)sched->transfers.size();
}
