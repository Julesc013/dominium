/*
FILE: source/dominium/tools/universe_editor/ue_queries.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/universe_editor
RESPONSIBILITY: Implements bundle summaries and list renderers.
*/
#include "ue_queries.h"

#include <cstdio>
#include <cstring>
#include <sstream>

#include "ue_commands.h"

namespace dom {
namespace tools {
namespace {

static void append_json_escaped(std::string &out, const std::string &in) {
    size_t i;
    for (i = 0u; i < in.size(); ++i) {
        const unsigned char c = (unsigned char)in[i];
        switch (c) {
        case '\\': out += "\\\\"; break;
        case '"': out += "\\\""; break;
        case '\n': out += "\\n"; break;
        case '\r': out += "\\r"; break;
        case '\t': out += "\\t"; break;
        default:
            if (c < 0x20u) {
                char buf[8];
                std::snprintf(buf, sizeof(buf), "\\u%04x", (unsigned)c);
                out += buf;
            } else {
                out.push_back((char)c);
            }
            break;
        }
    }
}

static std::string u64_hex(u64 v) {
    static const char *hex = "0123456789abcdef";
    char buf[17];
    int i;
    for (i = 0; i < 16; ++i) {
        const unsigned shift = (unsigned)((15 - i) * 4u);
        const unsigned nib = (unsigned)((v >> shift) & 0xFu);
        buf[i] = hex[nib & 0xFu];
    }
    buf[16] = '\0';
    return std::string(buf);
}

} // namespace

bool ue_build_summary(dom_universe_bundle *bundle,
                      UeSummary &out,
                      std::string *err) {
    dom_universe_bundle_identity id;
    UeSummary summary;
    std::vector<UeSystemEntry> systems;
    std::vector<UeRouteEntry> routes;
    int rc;
    size_t i;

    if (!bundle) {
        if (err) *err = "bundle_null";
        return false;
    }
    rc = dom_universe_bundle_get_identity(bundle, &id);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        if (err) *err = "identity_missing";
        return false;
    }

    summary.universe_id = id.universe_id ? std::string(id.universe_id, id.universe_id_len) : std::string();
    summary.instance_id = id.instance_id ? std::string(id.instance_id, id.instance_id_len) : std::string();
    summary.tick_index = id.tick_index;
    summary.ups = id.ups;
    summary.feature_epoch = id.feature_epoch;
    summary.systems_count = 0u;
    summary.routes_count = 0u;
    summary.systems_parsed = ue_load_systems(bundle, systems, 0);
    summary.routes_parsed = ue_load_routes(bundle, routes, 0);
    if (summary.systems_parsed) {
        summary.systems_count = (u32)systems.size();
    }
    if (summary.routes_parsed) {
        summary.routes_count = (u32)routes.size();
    }

    {
        const u32 chunk_ids[] = {
            DOM_UNIVERSE_CHUNK_TIME,
            DOM_UNIVERSE_CHUNK_COSM,
            DOM_UNIVERSE_CHUNK_SYSM,
            DOM_UNIVERSE_CHUNK_BODS,
            DOM_UNIVERSE_CHUNK_FRAM,
            DOM_UNIVERSE_CHUNK_TOPB,
            DOM_UNIVERSE_CHUNK_ORBT,
            DOM_UNIVERSE_CHUNK_SOVR,
            DOM_UNIVERSE_CHUNK_MEDB,
            DOM_UNIVERSE_CHUNK_WEAT,
            DOM_UNIVERSE_CHUNK_AERP,
            DOM_UNIVERSE_CHUNK_AERS,
            DOM_UNIVERSE_CHUNK_CNST,
            DOM_UNIVERSE_CHUNK_STAT,
            DOM_UNIVERSE_CHUNK_ROUT,
            DOM_UNIVERSE_CHUNK_TRAN,
            DOM_UNIVERSE_CHUNK_PROD,
            DOM_UNIVERSE_CHUNK_MECO,
            DOM_UNIVERSE_CHUNK_MEVT,
            DOM_UNIVERSE_CHUNK_FACT,
            DOM_UNIVERSE_CHUNK_AISC,
            DOM_UNIVERSE_CHUNK_CELE,
            DOM_UNIVERSE_CHUNK_VESL,
            DOM_UNIVERSE_CHUNK_SURF,
            DOM_UNIVERSE_CHUNK_LOCL,
            DOM_UNIVERSE_CHUNK_RNG
        };
        const size_t chunk_count = sizeof(chunk_ids) / sizeof(chunk_ids[0]);
        summary.chunks.clear();
        for (i = 0u; i < chunk_count; ++i) {
            const unsigned char *payload = 0;
            u32 size = 0u;
            u16 version = 0u;
            UeChunkInfo info;
            rc = dom_universe_bundle_get_chunk(bundle, chunk_ids[i], &payload, &size, &version);
            info.type_id = chunk_ids[i];
            info.version = version;
            info.size = size;
            info.present = (rc == DOM_UNIVERSE_BUNDLE_OK);
            summary.chunks.push_back(info);
        }
    }

    out = summary;
    return true;
}

std::string ue_summary_json(const UeSummary &summary) {
    std::string out;
    size_t i;
    out.reserve(512u);
    out += "{";
    out += "\"universe_id\":\"";
    append_json_escaped(out, summary.universe_id);
    out += "\",";
    out += "\"instance_id\":\"";
    append_json_escaped(out, summary.instance_id);
    out += "\",";
    {
        char buf[64];
        std::snprintf(buf, sizeof(buf), "%llu", (unsigned long long)summary.tick_index);
        out += "\"tick_index\":";
        out += buf;
        out += ",";
        std::snprintf(buf, sizeof(buf), "%u", (unsigned)summary.ups);
        out += "\"ups\":";
        out += buf;
        out += ",";
        std::snprintf(buf, sizeof(buf), "%u", (unsigned)summary.feature_epoch);
        out += "\"feature_epoch\":";
        out += buf;
        out += ",";
        std::snprintf(buf, sizeof(buf), "%u", (unsigned)summary.systems_count);
        out += "\"systems_count\":";
        out += buf;
        out += ",";
        std::snprintf(buf, sizeof(buf), "%u", (unsigned)summary.routes_count);
        out += "\"routes_count\":";
        out += buf;
        out += ",";
        out += "\"systems_parsed\":";
        out += summary.systems_parsed ? "true" : "false";
        out += ",";
        out += "\"routes_parsed\":";
        out += summary.routes_parsed ? "true" : "false";
    }
    out += ",\"chunks\":[";
    for (i = 0u; i < summary.chunks.size(); ++i) {
        const UeChunkInfo &c = summary.chunks[i];
        char buf[64];
        if (i > 0u) out += ",";
        out += "{";
        std::snprintf(buf, sizeof(buf), "%u", (unsigned)c.type_id);
        out += "\"type_id\":";
        out += buf;
        out += ",";
        std::snprintf(buf, sizeof(buf), "%u", (unsigned)c.version);
        out += "\"version\":";
        out += buf;
        out += ",";
        std::snprintf(buf, sizeof(buf), "%u", (unsigned)c.size);
        out += "\"size\":";
        out += buf;
        out += ",";
        out += "\"present\":";
        out += c.present ? "true" : "false";
        out += "}";
    }
    out += "]";
    out += "}";
    return out;
}

bool ue_list_systems(dom_universe_bundle *bundle,
                     std::string &out,
                     std::string *err) {
    std::vector<UeSystemEntry> systems;
    size_t i;
    if (!ue_load_systems(bundle, systems, err)) {
        return false;
    }
    std::ostringstream ss;
    ss << "system_id,parent_id,string_id\n";
    for (i = 0u; i < systems.size(); ++i) {
        ss << u64_hex(systems[i].id) << ",";
        ss << u64_hex(systems[i].parent_id) << ",";
        ss << systems[i].string_id << "\n";
    }
    out = ss.str();
    return true;
}

bool ue_list_routes(dom_universe_bundle *bundle,
                    std::string &out,
                    std::string *err) {
    std::vector<UeRouteEntry> routes;
    size_t i;
    if (!ue_load_routes(bundle, routes, err)) {
        return false;
    }
    std::ostringstream ss;
    ss << "route_id,src_station_id,dst_station_id,duration_ticks,capacity_units\n";
    for (i = 0u; i < routes.size(); ++i) {
        ss << u64_hex(routes[i].id) << ",";
        ss << u64_hex(routes[i].src_station_id) << ",";
        ss << u64_hex(routes[i].dst_station_id) << ",";
        ss << routes[i].duration_ticks << ",";
        ss << routes[i].capacity_units << "\n";
    }
    out = ss.str();
    return true;
}

} // namespace tools
} // namespace dom
