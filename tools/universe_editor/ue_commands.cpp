/*
FILE: source/dominium/tools/universe_editor/ue_commands.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/universe_editor
RESPONSIBILITY: Implements deterministic edits for systems/routes chunks.
*/
#include "ue_commands.h"

#include <algorithm>
#include <cstring>
#include <vector>

extern "C" {
#include "domino/core/spacetime.h"
}

#include "dominium/core_tlv.h"

namespace dom {
namespace tools {
namespace {

static bool read_u32(const unsigned char *data, size_t size, size_t &offset, u32 &out) {
    if (!data || offset + 4u > size) {
        return false;
    }
    std::memcpy(&out, data + offset, 4u);
    offset += 4u;
    return true;
}

static bool read_u64(const unsigned char *data, size_t size, size_t &offset, u64 &out) {
    if (!data || offset + 8u > size) {
        return false;
    }
    std::memcpy(&out, data + offset, 8u);
    offset += 8u;
    return true;
}

static void write_u32(std::vector<unsigned char> &out, u32 v) {
    size_t base = out.size();
    out.resize(base + 4u);
    std::memcpy(&out[base], &v, 4u);
}

static void write_u64(std::vector<unsigned char> &out, u64 v) {
    size_t base = out.size();
    out.resize(base + 8u);
    std::memcpy(&out[base], &v, 8u);
}

static u64 hash_payload(const std::vector<unsigned char> &payload) {
    if (payload.empty()) {
        return 0ull;
    }
    return dom::core_tlv::tlv_fnv1a64(&payload[0], payload.size());
}

static bool load_chunk(dom_universe_bundle *bundle,
                       u32 type_id,
                       std::vector<unsigned char> &out,
                       std::string *err) {
    const unsigned char *payload = 0;
    u32 size = 0u;
    u16 version = 0u;
    int rc = dom_universe_bundle_get_chunk(bundle, type_id, &payload, &size, &version);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        if (err) *err = "chunk_missing_or_invalid";
        return false;
    }
    out.assign(payload, payload + size);
    return true;
}

static bool update_identity_hash(dom_universe_bundle *bundle,
                                 u32 type_id,
                                 u64 new_hash,
                                 std::string *err) {
    dom_universe_bundle_identity id;
    int rc = dom_universe_bundle_get_identity(bundle, &id);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        if (err) *err = "identity_missing";
        return false;
    }
    std::string universe_id = id.universe_id ? std::string(id.universe_id, id.universe_id_len) : std::string();
    std::string instance_id = id.instance_id ? std::string(id.instance_id, id.instance_id_len) : std::string();
    id.universe_id = universe_id.c_str();
    id.universe_id_len = (u32)universe_id.size();
    id.instance_id = instance_id.c_str();
    id.instance_id_len = (u32)instance_id.size();

    switch (type_id) {
    case DOM_UNIVERSE_CHUNK_SYSM:
        id.systems_hash = new_hash;
        break;
    case DOM_UNIVERSE_CHUNK_ROUT:
        id.routes_hash = new_hash;
        break;
    default:
        break;
    }

    rc = dom_universe_bundle_set_identity(bundle, &id);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        if (err) *err = "identity_update_failed";
        return false;
    }
    return true;
}

struct SystemEntryLess {
    bool operator()(const UeSystemEntry &a, const UeSystemEntry &b) const {
        return a.id < b.id;
    }
};

struct RouteEntryLess {
    bool operator()(const UeRouteEntry &a, const UeRouteEntry &b) const {
        return a.id < b.id;
    }
};

static void sort_systems(std::vector<UeSystemEntry> &systems) {
    std::sort(systems.begin(), systems.end(), SystemEntryLess());
}

static void sort_routes(std::vector<UeRouteEntry> &routes) {
    std::sort(routes.begin(), routes.end(), RouteEntryLess());
}

static bool parse_systems_payload(const std::vector<unsigned char> &payload,
                                  std::vector<UeSystemEntry> &out,
                                  std::string *err) {
    size_t offset = 0u;
    u32 count = 0u;
    u32 i;
    out.clear();
    if (payload.empty()) {
        return true;
    }
    if (!read_u32(&payload[0], payload.size(), offset, count)) {
        if (err) *err = "systems_payload_short";
        return false;
    }
    for (i = 0u; i < count; ++i) {
        UeSystemEntry entry;
        u32 name_len = 0u;
        if (!read_u64(&payload[0], payload.size(), offset, entry.id)) {
            if (err) *err = "systems_payload_short_id";
            return false;
        }
        if (!read_u64(&payload[0], payload.size(), offset, entry.parent_id)) {
            if (err) *err = "systems_payload_short_parent";
            return false;
        }
        if (!read_u32(&payload[0], payload.size(), offset, name_len)) {
            if (err) *err = "systems_payload_short_name_len";
            return false;
        }
        if (offset + name_len > payload.size()) {
            if (err) *err = "systems_payload_name_overflow";
            return false;
        }
        entry.string_id.assign((const char *)&payload[offset], name_len);
        offset += name_len;
        out.push_back(entry);
    }
    return true;
}

static std::vector<unsigned char> serialize_systems_payload(const std::vector<UeSystemEntry> &systems) {
    std::vector<unsigned char> out;
    size_t i;
    write_u32(out, (u32)systems.size());
    for (i = 0u; i < systems.size(); ++i) {
        const UeSystemEntry &entry = systems[i];
        write_u64(out, entry.id);
        write_u64(out, entry.parent_id);
        write_u32(out, (u32)entry.string_id.size());
        if (!entry.string_id.empty()) {
            const size_t base = out.size();
            out.resize(base + entry.string_id.size());
            std::memcpy(&out[base], entry.string_id.data(), entry.string_id.size());
        }
    }
    return out;
}

static bool parse_routes_payload(const std::vector<unsigned char> &payload,
                                 std::vector<UeRouteEntry> &out,
                                 std::string *err) {
    size_t offset = 0u;
    u32 count = 0u;
    u32 i;
    out.clear();
    if (payload.empty()) {
        return true;
    }
    if (!read_u32(&payload[0], payload.size(), offset, count)) {
        if (err) *err = "routes_payload_short";
        return false;
    }
    for (i = 0u; i < count; ++i) {
        UeRouteEntry entry;
        if (!read_u64(&payload[0], payload.size(), offset, entry.id) ||
            !read_u64(&payload[0], payload.size(), offset, entry.src_station_id) ||
            !read_u64(&payload[0], payload.size(), offset, entry.dst_station_id) ||
            !read_u64(&payload[0], payload.size(), offset, entry.duration_ticks) ||
            !read_u64(&payload[0], payload.size(), offset, entry.capacity_units)) {
            if (err) *err = "routes_payload_short";
            return false;
        }
        out.push_back(entry);
    }
    return true;
}

static std::vector<unsigned char> serialize_routes_payload(const std::vector<UeRouteEntry> &routes) {
    std::vector<unsigned char> out;
    size_t i;
    write_u32(out, (u32)routes.size());
    for (i = 0u; i < routes.size(); ++i) {
        const UeRouteEntry &entry = routes[i];
        write_u64(out, entry.id);
        write_u64(out, entry.src_station_id);
        write_u64(out, entry.dst_station_id);
        write_u64(out, entry.duration_ticks);
        write_u64(out, entry.capacity_units);
    }
    return out;
}

} // namespace

bool ue_load_systems(dom_universe_bundle *bundle,
                     std::vector<UeSystemEntry> &out,
                     std::string *err) {
    std::vector<unsigned char> payload;
    if (!bundle) {
        if (err) *err = "bundle_null";
        return false;
    }
    if (!load_chunk(bundle, DOM_UNIVERSE_CHUNK_SYSM, payload, err)) {
        return false;
    }
    return parse_systems_payload(payload, out, err);
}

bool ue_store_systems(dom_universe_bundle *bundle,
                      const std::vector<UeSystemEntry> &systems,
                      std::string *err) {
    std::vector<UeSystemEntry> sorted = systems;
    std::vector<unsigned char> payload;
    int rc;
    if (!bundle) {
        if (err) *err = "bundle_null";
        return false;
    }
    sort_systems(sorted);
    payload = serialize_systems_payload(sorted);
    rc = dom_universe_bundle_set_chunk(bundle,
                                       DOM_UNIVERSE_CHUNK_SYSM,
                                       1u,
                                       payload.empty() ? 0 : &payload[0],
                                       (u32)payload.size());
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        if (err) *err = "systems_chunk_write_failed";
        return false;
    }
    return update_identity_hash(bundle, DOM_UNIVERSE_CHUNK_SYSM, hash_payload(payload), err);
}

bool ue_add_system(dom_universe_bundle *bundle,
                   const std::string &string_id,
                   u64 parent_id,
                   std::string *err) {
    std::vector<UeSystemEntry> systems;
    UeSystemEntry entry;
    u64 hash = 0ull;
    if (string_id.empty()) {
        if (err) *err = "system_id_empty";
        return false;
    }
    if (dom_id_hash64(string_id.c_str(), (u32)string_id.size(), &hash) != DOM_SPACETIME_OK) {
        if (err) *err = "system_id_hash_failed";
        return false;
    }
    if (hash == 0ull) {
        if (err) *err = "system_id_hash_zero";
        return false;
    }
    if (!ue_load_systems(bundle, systems, err)) {
        return false;
    }
    {
        size_t i;
        for (i = 0u; i < systems.size(); ++i) {
            if (systems[i].id == hash) {
                if (err) *err = "system_id_duplicate";
                return false;
            }
        }
    }
    entry.id = hash;
    entry.parent_id = parent_id;
    entry.string_id = string_id;
    systems.push_back(entry);
    return ue_store_systems(bundle, systems, err);
}

bool ue_remove_system(dom_universe_bundle *bundle,
                      u64 system_id,
                      std::string *err) {
    std::vector<UeSystemEntry> systems;
    size_t i;
    bool removed = false;
    if (system_id == 0ull) {
        if (err) *err = "system_id_zero";
        return false;
    }
    if (!ue_load_systems(bundle, systems, err)) {
        return false;
    }
    for (i = 0u; i < systems.size(); ++i) {
        if (systems[i].id == system_id) {
            systems.erase(systems.begin() + (std::vector<UeSystemEntry>::difference_type)i);
            removed = true;
            break;
        }
    }
    if (!removed) {
        if (err) *err = "system_id_not_found";
        return false;
    }
    return ue_store_systems(bundle, systems, err);
}

bool ue_load_routes(dom_universe_bundle *bundle,
                    std::vector<UeRouteEntry> &out,
                    std::string *err) {
    std::vector<unsigned char> payload;
    if (!bundle) {
        if (err) *err = "bundle_null";
        return false;
    }
    if (!load_chunk(bundle, DOM_UNIVERSE_CHUNK_ROUT, payload, err)) {
        return false;
    }
    return parse_routes_payload(payload, out, err);
}

bool ue_store_routes(dom_universe_bundle *bundle,
                     const std::vector<UeRouteEntry> &routes,
                     std::string *err) {
    std::vector<UeRouteEntry> sorted = routes;
    std::vector<unsigned char> payload;
    int rc;
    if (!bundle) {
        if (err) *err = "bundle_null";
        return false;
    }
    sort_routes(sorted);
    payload = serialize_routes_payload(sorted);
    rc = dom_universe_bundle_set_chunk(bundle,
                                       DOM_UNIVERSE_CHUNK_ROUT,
                                       1u,
                                       payload.empty() ? 0 : &payload[0],
                                       (u32)payload.size());
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        if (err) *err = "routes_chunk_write_failed";
        return false;
    }
    return update_identity_hash(bundle, DOM_UNIVERSE_CHUNK_ROUT, hash_payload(payload), err);
}

bool ue_upsert_route(dom_universe_bundle *bundle,
                     const UeRouteEntry &route,
                     std::string *err) {
    std::vector<UeRouteEntry> routes;
    size_t i;
    bool updated = false;
    if (route.id == 0ull || route.src_station_id == 0ull || route.dst_station_id == 0ull ||
        route.duration_ticks == 0ull || route.capacity_units == 0ull) {
        if (err) *err = "route_invalid_fields";
        return false;
    }
    if (!ue_load_routes(bundle, routes, err)) {
        return false;
    }
    for (i = 0u; i < routes.size(); ++i) {
        if (routes[i].id == route.id) {
            routes[i] = route;
            updated = true;
            break;
        }
    }
    if (!updated) {
        routes.push_back(route);
    }
    return ue_store_routes(bundle, routes, err);
}

bool ue_remove_route(dom_universe_bundle *bundle,
                     u64 route_id,
                     std::string *err) {
    std::vector<UeRouteEntry> routes;
    size_t i;
    bool removed = false;
    if (route_id == 0ull) {
        if (err) *err = "route_id_zero";
        return false;
    }
    if (!ue_load_routes(bundle, routes, err)) {
        return false;
    }
    for (i = 0u; i < routes.size(); ++i) {
        if (routes[i].id == route_id) {
            routes.erase(routes.begin() + (std::vector<UeRouteEntry>::difference_type)i);
            removed = true;
            break;
        }
    }
    if (!removed) {
        if (err) *err = "route_id_not_found";
        return false;
    }
    return ue_store_routes(bundle, routes, err);
}

} // namespace tools
} // namespace dom
