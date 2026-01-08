/*
FILE: source/dominium/game/runtime/dom_universe_bundle.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/universe_bundle
RESPONSIBILITY: Portable universe bundle container (read/write + identity validation).
*/
#include "runtime/dom_universe_bundle.h"

#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include "dom_feature_epoch.h"
#include "dominium/core_tlv.h"

extern "C" {
#include "domino/io/container.h"
}

namespace {

struct BundleChunk {
    u16 version;
    bool present;
    std::vector<unsigned char> payload;

    BundleChunk() : version(1u), present(false), payload() {}
};

struct ForeignChunk {
    u32 type_id;
    u16 version;
    u16 flags;
    std::vector<unsigned char> payload;
};

struct BundleState {
    std::string universe_id;
    std::string instance_id;
    u64 content_graph_hash;
    u64 sim_flags_hash;
    u64 cosmo_graph_hash;
    u64 systems_hash;
    u64 bodies_hash;
    u64 frames_hash;
    u64 topology_hash;
    u64 orbits_hash;
    u64 surface_overrides_hash;
    u64 constructions_hash;
    u64 stations_hash;
    u64 routes_hash;
    u64 transfers_hash;
    u64 production_hash;
    u64 macro_economy_hash;
    u64 macro_events_hash;
    u32 ups;
    u64 tick_index;
    u32 feature_epoch;
    bool identity_set;

    BundleChunk cosmo;
    BundleChunk sysm;
    BundleChunk bods;
    BundleChunk fram;
    BundleChunk topb;
    BundleChunk orbt;
    BundleChunk sovr;
    BundleChunk cnst;
    BundleChunk stat;
    BundleChunk rout;
    BundleChunk tran;
    BundleChunk prod;
    BundleChunk meco;
    BundleChunk mevt;
    BundleChunk cele;
    BundleChunk vesl;
    BundleChunk surf;
    BundleChunk locl;
    BundleChunk rng;
    std::vector<ForeignChunk> foreign;

    BundleState()
        : universe_id(),
          instance_id(),
          content_graph_hash(0ull),
          sim_flags_hash(0ull),
          cosmo_graph_hash(0ull),
          systems_hash(0ull),
          bodies_hash(0ull),
          frames_hash(0ull),
          topology_hash(0ull),
          orbits_hash(0ull),
          surface_overrides_hash(0ull),
          constructions_hash(0ull),
          stations_hash(0ull),
          routes_hash(0ull),
          transfers_hash(0ull),
          production_hash(0ull),
          macro_economy_hash(0ull),
          macro_events_hash(0ull),
          ups(0u),
          tick_index(0ull),
          feature_epoch(0u),
          identity_set(false),
          cosmo(),
          sysm(),
          bods(),
          fram(),
          topb(),
          orbt(),
          sovr(),
          cnst(),
          stat(),
          rout(),
          tran(),
          prod(),
          meco(),
          mevt(),
          cele(),
          vesl(),
          surf(),
          locl(),
          rng(),
          foreign() {}
};

static BundleChunk *chunk_for_type(BundleState *state, u32 type_id) {
    if (!state) {
        return 0;
    }
    switch (type_id) {
        case DOM_UNIVERSE_CHUNK_COSM: return &state->cosmo;
        case DOM_UNIVERSE_CHUNK_SYSM: return &state->sysm;
        case DOM_UNIVERSE_CHUNK_BODS: return &state->bods;
        case DOM_UNIVERSE_CHUNK_FRAM: return &state->fram;
        case DOM_UNIVERSE_CHUNK_TOPB: return &state->topb;
        case DOM_UNIVERSE_CHUNK_ORBT: return &state->orbt;
        case DOM_UNIVERSE_CHUNK_SOVR: return &state->sovr;
        case DOM_UNIVERSE_CHUNK_CNST: return &state->cnst;
        case DOM_UNIVERSE_CHUNK_STAT: return &state->stat;
        case DOM_UNIVERSE_CHUNK_ROUT: return &state->rout;
        case DOM_UNIVERSE_CHUNK_TRAN: return &state->tran;
        case DOM_UNIVERSE_CHUNK_PROD: return &state->prod;
        case DOM_UNIVERSE_CHUNK_MECO: return &state->meco;
        case DOM_UNIVERSE_CHUNK_MEVT: return &state->mevt;
        case DOM_UNIVERSE_CHUNK_CELE: return &state->cele;
        case DOM_UNIVERSE_CHUNK_VESL: return &state->vesl;
        case DOM_UNIVERSE_CHUNK_SURF: return &state->surf;
        case DOM_UNIVERSE_CHUNK_LOCL: return &state->locl;
        case DOM_UNIVERSE_CHUNK_RNG:  return &state->rng;
        default: break;
    }
    return 0;
}

static const BundleChunk *chunk_for_type(const BundleState *state, u32 type_id) {
    return chunk_for_type(const_cast<BundleState *>(state), type_id);
}

static void bundle_reset(BundleState *state) {
    if (!state) {
        return;
    }
    state->universe_id.clear();
    state->instance_id.clear();
    state->content_graph_hash = 0ull;
    state->sim_flags_hash = 0ull;
    state->cosmo_graph_hash = 0ull;
    state->systems_hash = 0ull;
    state->bodies_hash = 0ull;
    state->frames_hash = 0ull;
    state->topology_hash = 0ull;
    state->orbits_hash = 0ull;
    state->surface_overrides_hash = 0ull;
    state->constructions_hash = 0ull;
    state->stations_hash = 0ull;
    state->routes_hash = 0ull;
    state->transfers_hash = 0ull;
    state->production_hash = 0ull;
    state->macro_economy_hash = 0ull;
    state->macro_events_hash = 0ull;
    state->ups = 0u;
    state->tick_index = 0ull;
    state->feature_epoch = 0u;
    state->identity_set = false;
    state->cosmo = BundleChunk();
    state->sysm = BundleChunk();
    state->bods = BundleChunk();
    state->fram = BundleChunk();
    state->topb = BundleChunk();
    state->orbt = BundleChunk();
    state->sovr = BundleChunk();
    state->cnst = BundleChunk();
    state->stat = BundleChunk();
    state->rout = BundleChunk();
    state->tran = BundleChunk();
    state->prod = BundleChunk();
    state->meco = BundleChunk();
    state->mevt = BundleChunk();
    state->cele = BundleChunk();
    state->vesl = BundleChunk();
    state->surf = BundleChunk();
    state->locl = BundleChunk();
    state->rng = BundleChunk();
    state->foreign.clear();
}

static int read_chunk_payload(dtlv_reader *reader,
                              const dtlv_dir_entry *entry,
                              std::vector<unsigned char> &out_payload) {
    unsigned char *bytes = 0;
    u32 size = 0u;
    if (dtlv_reader_read_chunk_alloc(reader, entry, &bytes, &size) != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    out_payload.assign(bytes, bytes + size);
    if (bytes) {
        std::free(bytes);
    }
    return DOM_UNIVERSE_BUNDLE_OK;
}

static u64 hash_bytes_fnv1a64(const std::vector<unsigned char> &bytes) {
    if (bytes.empty()) {
        return 0ull;
    }
    return dom::core_tlv::tlv_fnv1a64(&bytes[0], bytes.size());
}

static int parse_time_chunk(BundleState *state,
                            const unsigned char *payload,
                            u32 payload_len) {
    u32 offset = 0u;
    u32 tag = 0u;
    const unsigned char *pl = 0;
    u32 pl_len = 0u;
    int rc;

    bool have_universe = false;
    bool have_instance = false;
    bool have_content = false;
    bool have_flags = false;
    bool have_ups = false;
    bool have_tick = false;
    bool have_epoch = false;
    bool have_cosmo = false;
    bool have_systems = false;
    bool have_bodies = false;
    bool have_frames = false;
    bool have_topo = false;
    bool have_orbits = false;
    bool have_surface = false;
    bool have_constructions = false;
    bool have_stations = false;
    bool have_routes = false;
    bool have_transfers = false;
    bool have_production = false;
    bool have_macro_economy = false;
    bool have_macro_events = false;

    if (!state) {
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }

    while ((rc = dtlv_tlv_next(payload, payload_len, &offset, &tag, &pl, &pl_len)) == 0) {
        switch (tag) {
            case DOM_UNIVERSE_TLV_UNIVERSE_ID:
                if (!pl || pl_len == 0u) {
                    return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                }
                state->universe_id.assign((const char *)pl, pl_len);
                have_universe = true;
                break;
            case DOM_UNIVERSE_TLV_INSTANCE_ID:
                if (!pl || pl_len == 0u) {
                    return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                }
                state->instance_id.assign((const char *)pl, pl_len);
                have_instance = true;
                break;
            case DOM_UNIVERSE_TLV_CONTENT_HASH:
                if (!pl || pl_len != 8u) {
                    return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                }
                state->content_graph_hash = dtlv_le_read_u64(pl);
                have_content = true;
                break;
            case DOM_UNIVERSE_TLV_SIM_FLAGS_HASH:
                if (!pl || pl_len != 8u) {
                    return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                }
                state->sim_flags_hash = dtlv_le_read_u64(pl);
                have_flags = true;
                break;
            case DOM_UNIVERSE_TLV_COSMO_HASH:
                if (!pl || pl_len != 8u) {
                    return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                }
                state->cosmo_graph_hash = dtlv_le_read_u64(pl);
                have_cosmo = true;
                break;
            case DOM_UNIVERSE_TLV_SYSTEMS_HASH:
                if (!pl || pl_len != 8u) {
                    return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                }
                state->systems_hash = dtlv_le_read_u64(pl);
                have_systems = true;
                break;
            case DOM_UNIVERSE_TLV_BODIES_HASH:
                if (!pl || pl_len != 8u) {
                    return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                }
                state->bodies_hash = dtlv_le_read_u64(pl);
                have_bodies = true;
                break;
            case DOM_UNIVERSE_TLV_FRAMES_HASH:
                if (!pl || pl_len != 8u) {
                    return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                }
                state->frames_hash = dtlv_le_read_u64(pl);
                have_frames = true;
                break;
            case DOM_UNIVERSE_TLV_TOPOLOGY_HASH:
                if (!pl || pl_len != 8u) {
                    return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                }
                state->topology_hash = dtlv_le_read_u64(pl);
                have_topo = true;
                break;
            case DOM_UNIVERSE_TLV_ORBITS_HASH:
                if (!pl || pl_len != 8u) {
                    return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                }
                state->orbits_hash = dtlv_le_read_u64(pl);
                have_orbits = true;
                break;
            case DOM_UNIVERSE_TLV_SURFACE_HASH:
                if (!pl || pl_len != 8u) {
                    return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                }
                state->surface_overrides_hash = dtlv_le_read_u64(pl);
                have_surface = true;
                break;
            case DOM_UNIVERSE_TLV_CONSTRUCTIONS_HASH:
                if (!pl || pl_len != 8u) {
                    return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                }
                state->constructions_hash = dtlv_le_read_u64(pl);
                have_constructions = true;
                break;
            case DOM_UNIVERSE_TLV_STATIONS_HASH:
                if (!pl || pl_len != 8u) {
                    return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                }
                state->stations_hash = dtlv_le_read_u64(pl);
                have_stations = true;
                break;
            case DOM_UNIVERSE_TLV_ROUTES_HASH:
                if (!pl || pl_len != 8u) {
                    return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                }
                state->routes_hash = dtlv_le_read_u64(pl);
                have_routes = true;
                break;
            case DOM_UNIVERSE_TLV_TRANSFERS_HASH:
                if (!pl || pl_len != 8u) {
                    return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                }
                state->transfers_hash = dtlv_le_read_u64(pl);
                have_transfers = true;
                break;
            case DOM_UNIVERSE_TLV_PRODUCTION_HASH:
                if (!pl || pl_len != 8u) {
                    return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                }
                state->production_hash = dtlv_le_read_u64(pl);
                have_production = true;
                break;
            case DOM_UNIVERSE_TLV_MACRO_ECONOMY_HASH:
                if (!pl || pl_len != 8u) {
                    return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                }
                state->macro_economy_hash = dtlv_le_read_u64(pl);
                have_macro_economy = true;
                break;
            case DOM_UNIVERSE_TLV_MACRO_EVENTS_HASH:
                if (!pl || pl_len != 8u) {
                    return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                }
                state->macro_events_hash = dtlv_le_read_u64(pl);
                have_macro_events = true;
                break;
            case DOM_UNIVERSE_TLV_UPS:
                if (!pl || pl_len != 4u) {
                    return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                }
                state->ups = dtlv_le_read_u32(pl);
                have_ups = true;
                break;
            case DOM_UNIVERSE_TLV_TICK_INDEX:
                if (!pl || pl_len != 8u) {
                    return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                }
                state->tick_index = dtlv_le_read_u64(pl);
                have_tick = true;
                break;
            case DOM_UNIVERSE_TLV_FEATURE_EPOCH:
                if (!pl || pl_len != 4u) {
                    return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                }
                state->feature_epoch = dtlv_le_read_u32(pl);
                have_epoch = true;
                break;
            default:
                break;
        }
    }

    if (rc < 0) {
        return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
    }
    if (!have_universe || !have_instance || !have_content ||
        !have_flags || !have_cosmo || !have_ups || !have_tick) {
        return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
    }
    if (!have_epoch || !have_systems || !have_bodies || !have_frames ||
        !have_topo || !have_orbits || !have_surface || !have_constructions ||
        !have_stations || !have_routes || !have_transfers || !have_production ||
        !have_macro_economy || !have_macro_events) {
        return DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED;
    }
    if (state->ups == 0u) {
        return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
    }
    if (state->feature_epoch == 0u) {
        return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
    }
    if (!dom::dom_feature_epoch_supported(state->feature_epoch)) {
        return DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED;
    }

    state->identity_set = true;
    return DOM_UNIVERSE_BUNDLE_OK;
}

static int parse_foreign_chunk(BundleState *state,
                               const unsigned char *payload,
                               u32 payload_len) {
    u32 offset = 0u;
    u32 tag = 0u;
    const unsigned char *pl = 0;
    u32 pl_len = 0u;
    int rc;

    if (!state) {
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }

    while ((rc = dtlv_tlv_next(payload, payload_len, &offset, &tag, &pl, &pl_len)) == 0) {
        if (tag != 0x0001u) {
            continue;
        }
        if (!pl || pl_len < 16u) {
            return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
        }
        {
            ForeignChunk foreign;
            u64 size64;
            u32 size;
            foreign.type_id = dtlv_le_read_u32(pl + 0);
            foreign.version = dtlv_le_read_u16(pl + 4);
            foreign.flags = dtlv_le_read_u16(pl + 6);
            size64 = dtlv_le_read_u64(pl + 8);
            size = (size64 > 0xffffffffull) ? 0xffffffffu : (u32)size64;
            if (pl_len != (16u + size)) {
                return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
            }
            foreign.payload.assign(pl + 16, pl + 16 + size);
            state->foreign.push_back(foreign);
        }
    }

    if (rc < 0) {
        return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
    }
    return DOM_UNIVERSE_BUNDLE_OK;
}

static int identity_matches(const BundleState *state,
                            const dom_universe_bundle_identity *expected) {
    if (!state || !expected) {
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }
    if (!expected->universe_id || !expected->instance_id) {
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }
    if (expected->universe_id_len != state->universe_id.size()) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (expected->instance_id_len != state->instance_id.size()) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (std::memcmp(expected->universe_id,
                    state->universe_id.data(),
                    expected->universe_id_len) != 0) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (std::memcmp(expected->instance_id,
                    state->instance_id.data(),
                    expected->instance_id_len) != 0) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (expected->content_graph_hash != state->content_graph_hash ||
        expected->sim_flags_hash != state->sim_flags_hash ||
        expected->cosmo_graph_hash != state->cosmo_graph_hash ||
        expected->systems_hash != state->systems_hash ||
        expected->bodies_hash != state->bodies_hash ||
        expected->frames_hash != state->frames_hash ||
        expected->topology_hash != state->topology_hash ||
        expected->orbits_hash != state->orbits_hash ||
        expected->surface_overrides_hash != state->surface_overrides_hash ||
        expected->constructions_hash != state->constructions_hash ||
        expected->stations_hash != state->stations_hash ||
        expected->routes_hash != state->routes_hash ||
        expected->transfers_hash != state->transfers_hash ||
        expected->production_hash != state->production_hash ||
        expected->macro_economy_hash != state->macro_economy_hash ||
        expected->macro_events_hash != state->macro_events_hash ||
        expected->ups != state->ups ||
        expected->tick_index != state->tick_index) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (expected->feature_epoch != 0u &&
        dom::dom_feature_epoch_requires_migration(expected->feature_epoch,
                                                  state->feature_epoch)) {
        return DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED;
    }
    return DOM_UNIVERSE_BUNDLE_OK;
}

static int write_time_chunk(dtlv_writer *writer, const BundleState *state) {
    int rc;
    if (!writer || !state || !state->identity_set) {
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }
    rc = dtlv_writer_begin_chunk(writer, DOM_UNIVERSE_CHUNK_TIME, 1u, 0u);
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    rc = dtlv_writer_write_tlv(writer,
                               DOM_UNIVERSE_TLV_UNIVERSE_ID,
                               state->universe_id.data(),
                               (u32)state->universe_id.size());
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    rc = dtlv_writer_write_tlv(writer,
                               DOM_UNIVERSE_TLV_INSTANCE_ID,
                               state->instance_id.data(),
                               (u32)state->instance_id.size());
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    {
        unsigned char buf[8];
        dtlv_le_write_u64(buf, state->content_graph_hash);
        rc = dtlv_writer_write_tlv(writer,
                                   DOM_UNIVERSE_TLV_CONTENT_HASH,
                                   buf,
                                   8u);
    }
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    {
        unsigned char buf[8];
        dtlv_le_write_u64(buf, state->sim_flags_hash);
        rc = dtlv_writer_write_tlv(writer,
                                   DOM_UNIVERSE_TLV_SIM_FLAGS_HASH,
                                   buf,
                                   8u);
    }
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    {
        unsigned char buf[8];
        dtlv_le_write_u64(buf, state->cosmo_graph_hash);
        rc = dtlv_writer_write_tlv(writer,
                                   DOM_UNIVERSE_TLV_COSMO_HASH,
                                   buf,
                                   8u);
    }
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    {
        unsigned char buf[8];
        dtlv_le_write_u64(buf, state->systems_hash);
        rc = dtlv_writer_write_tlv(writer,
                                   DOM_UNIVERSE_TLV_SYSTEMS_HASH,
                                   buf,
                                   8u);
    }
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    {
        unsigned char buf[8];
        dtlv_le_write_u64(buf, state->bodies_hash);
        rc = dtlv_writer_write_tlv(writer,
                                   DOM_UNIVERSE_TLV_BODIES_HASH,
                                   buf,
                                   8u);
    }
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    {
        unsigned char buf[8];
        dtlv_le_write_u64(buf, state->frames_hash);
        rc = dtlv_writer_write_tlv(writer,
                                   DOM_UNIVERSE_TLV_FRAMES_HASH,
                                   buf,
                                   8u);
    }
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    {
        unsigned char buf[8];
        dtlv_le_write_u64(buf, state->topology_hash);
        rc = dtlv_writer_write_tlv(writer,
                                   DOM_UNIVERSE_TLV_TOPOLOGY_HASH,
                                   buf,
                                   8u);
    }
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    {
        unsigned char buf[8];
        dtlv_le_write_u64(buf, state->orbits_hash);
        rc = dtlv_writer_write_tlv(writer,
                                   DOM_UNIVERSE_TLV_ORBITS_HASH,
                                   buf,
                                   8u);
    }
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    {
        unsigned char buf[8];
        dtlv_le_write_u64(buf, state->surface_overrides_hash);
        rc = dtlv_writer_write_tlv(writer,
                                   DOM_UNIVERSE_TLV_SURFACE_HASH,
                                   buf,
                                   8u);
    }
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    {
        unsigned char buf[8];
        dtlv_le_write_u64(buf, state->constructions_hash);
        rc = dtlv_writer_write_tlv(writer,
                                   DOM_UNIVERSE_TLV_CONSTRUCTIONS_HASH,
                                   buf,
                                   8u);
    }
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    {
        unsigned char buf[8];
        dtlv_le_write_u64(buf, state->stations_hash);
        rc = dtlv_writer_write_tlv(writer,
                                   DOM_UNIVERSE_TLV_STATIONS_HASH,
                                   buf,
                                   8u);
    }
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    {
        unsigned char buf[8];
        dtlv_le_write_u64(buf, state->routes_hash);
        rc = dtlv_writer_write_tlv(writer,
                                   DOM_UNIVERSE_TLV_ROUTES_HASH,
                                   buf,
                                   8u);
    }
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    {
        unsigned char buf[8];
        dtlv_le_write_u64(buf, state->transfers_hash);
        rc = dtlv_writer_write_tlv(writer,
                                   DOM_UNIVERSE_TLV_TRANSFERS_HASH,
                                   buf,
                                   8u);
    }
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    {
        unsigned char buf[8];
        dtlv_le_write_u64(buf, state->production_hash);
        rc = dtlv_writer_write_tlv(writer,
                                   DOM_UNIVERSE_TLV_PRODUCTION_HASH,
                                   buf,
                                   8u);
    }
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    {
        unsigned char buf[8];
        dtlv_le_write_u64(buf, state->macro_economy_hash);
        rc = dtlv_writer_write_tlv(writer,
                                   DOM_UNIVERSE_TLV_MACRO_ECONOMY_HASH,
                                   buf,
                                   8u);
    }
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    {
        unsigned char buf[8];
        dtlv_le_write_u64(buf, state->macro_events_hash);
        rc = dtlv_writer_write_tlv(writer,
                                   DOM_UNIVERSE_TLV_MACRO_EVENTS_HASH,
                                   buf,
                                   8u);
    }
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    {
        unsigned char buf[4];
        dtlv_le_write_u32(buf, state->ups);
        rc = dtlv_writer_write_tlv(writer,
                                   DOM_UNIVERSE_TLV_UPS,
                                   buf,
                                   4u);
    }
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    {
        unsigned char buf[8];
        dtlv_le_write_u64(buf, state->tick_index);
        rc = dtlv_writer_write_tlv(writer,
                                   DOM_UNIVERSE_TLV_TICK_INDEX,
                                   buf,
                                   8u);
    }
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    {
        unsigned char buf[4];
        dtlv_le_write_u32(buf, state->feature_epoch);
        rc = dtlv_writer_write_tlv(writer,
                                   DOM_UNIVERSE_TLV_FEATURE_EPOCH,
                                   buf,
                                   4u);
    }
    if (rc != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    if (dtlv_writer_end_chunk(writer) != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    return DOM_UNIVERSE_BUNDLE_OK;
}

static int write_raw_chunk(dtlv_writer *writer, u32 type_id, const BundleChunk &chunk) {
    if (!writer) {
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }
    if (dtlv_writer_begin_chunk(writer, type_id, chunk.version, 0u) != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    if (!chunk.payload.empty()) {
        if (dtlv_writer_write(writer, &chunk.payload[0], (u32)chunk.payload.size()) != 0) {
            return DOM_UNIVERSE_BUNDLE_IO_ERROR;
        }
    }
    if (dtlv_writer_end_chunk(writer) != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    return DOM_UNIVERSE_BUNDLE_OK;
}

static int write_foreign_chunk(dtlv_writer *writer,
                               const std::vector<ForeignChunk> &foreign_list) {
    size_t i;
    if (!writer) {
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }
    if (dtlv_writer_begin_chunk(writer, DOM_UNIVERSE_CHUNK_FORN, 1u, 0u) != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    for (i = 0u; i < foreign_list.size(); ++i) {
        const ForeignChunk &f = foreign_list[i];
        std::vector<unsigned char> record;
        u64 payload_size = (u64)f.payload.size();
        if (payload_size > 0xffffffffull) {
            return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
        }
        record.resize(16u + (size_t)payload_size);
        dtlv_le_write_u32(&record[0], f.type_id);
        dtlv_le_write_u16(&record[4], f.version);
        dtlv_le_write_u16(&record[6], f.flags);
        dtlv_le_write_u64(&record[8], payload_size);
        if (payload_size > 0u) {
            std::memcpy(&record[16], &f.payload[0], (size_t)payload_size);
        }
        if (dtlv_writer_write_tlv(writer, 0x0001u, &record[0], (u32)record.size()) != 0) {
            return DOM_UNIVERSE_BUNDLE_IO_ERROR;
        }
    }
    if (dtlv_writer_end_chunk(writer) != 0) {
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }
    return DOM_UNIVERSE_BUNDLE_OK;
}

} // namespace

struct dom_universe_bundle {
    BundleState state;
};

dom_universe_bundle *dom_universe_bundle_create(void) {
    dom_universe_bundle *bundle = new dom_universe_bundle();
    return bundle;
}

void dom_universe_bundle_destroy(dom_universe_bundle *bundle) {
    if (!bundle) {
        return;
    }
    delete bundle;
}

int dom_universe_bundle_set_identity(dom_universe_bundle *bundle,
                                     const dom_universe_bundle_identity *id) {
    BundleState *state;
    if (!bundle || !id) {
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }
    if (!id->universe_id || !id->instance_id ||
        id->universe_id_len == 0u || id->instance_id_len == 0u ||
        id->ups == 0u || id->feature_epoch == 0u ||
        !dom::dom_feature_epoch_supported(id->feature_epoch)) {
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }
    state = &bundle->state;
    if (state->cosmo.present &&
        state->cosmo_graph_hash != id->cosmo_graph_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (state->sysm.present &&
        state->systems_hash != id->systems_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (state->bods.present &&
        state->bodies_hash != id->bodies_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (state->fram.present &&
        state->frames_hash != id->frames_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (state->topb.present &&
        state->topology_hash != id->topology_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (state->orbt.present &&
        state->orbits_hash != id->orbits_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (state->sovr.present &&
        state->surface_overrides_hash != id->surface_overrides_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (state->cnst.present &&
        state->constructions_hash != id->constructions_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (state->stat.present &&
        state->stations_hash != id->stations_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (state->rout.present &&
        state->routes_hash != id->routes_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (state->tran.present &&
        state->transfers_hash != id->transfers_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (state->prod.present &&
        state->production_hash != id->production_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (state->meco.present &&
        state->macro_economy_hash != id->macro_economy_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (state->mevt.present &&
        state->macro_events_hash != id->macro_events_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    state->universe_id.assign(id->universe_id, id->universe_id_len);
    state->instance_id.assign(id->instance_id, id->instance_id_len);
    state->content_graph_hash = id->content_graph_hash;
    state->sim_flags_hash = id->sim_flags_hash;
    state->cosmo_graph_hash = id->cosmo_graph_hash;
    state->systems_hash = id->systems_hash;
    state->bodies_hash = id->bodies_hash;
    state->frames_hash = id->frames_hash;
    state->topology_hash = id->topology_hash;
    state->orbits_hash = id->orbits_hash;
    state->surface_overrides_hash = id->surface_overrides_hash;
    state->constructions_hash = id->constructions_hash;
    state->stations_hash = id->stations_hash;
    state->routes_hash = id->routes_hash;
    state->transfers_hash = id->transfers_hash;
    state->production_hash = id->production_hash;
    state->macro_economy_hash = id->macro_economy_hash;
    state->macro_events_hash = id->macro_events_hash;
    state->ups = id->ups;
    state->tick_index = id->tick_index;
    state->feature_epoch = id->feature_epoch;
    state->identity_set = true;
    return DOM_UNIVERSE_BUNDLE_OK;
}

int dom_universe_bundle_get_identity(const dom_universe_bundle *bundle,
                                     dom_universe_bundle_identity *out_id) {
    const BundleState *state;
    if (!bundle || !out_id) {
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }
    state = &bundle->state;
    if (!state->identity_set) {
        return DOM_UNIVERSE_BUNDLE_ERR;
    }
    out_id->universe_id = state->universe_id.c_str();
    out_id->universe_id_len = (u32)state->universe_id.size();
    out_id->instance_id = state->instance_id.c_str();
    out_id->instance_id_len = (u32)state->instance_id.size();
    out_id->content_graph_hash = state->content_graph_hash;
    out_id->sim_flags_hash = state->sim_flags_hash;
    out_id->cosmo_graph_hash = state->cosmo_graph_hash;
    out_id->systems_hash = state->systems_hash;
    out_id->bodies_hash = state->bodies_hash;
    out_id->frames_hash = state->frames_hash;
    out_id->topology_hash = state->topology_hash;
    out_id->orbits_hash = state->orbits_hash;
    out_id->surface_overrides_hash = state->surface_overrides_hash;
    out_id->constructions_hash = state->constructions_hash;
    out_id->stations_hash = state->stations_hash;
    out_id->routes_hash = state->routes_hash;
    out_id->transfers_hash = state->transfers_hash;
    out_id->production_hash = state->production_hash;
    out_id->macro_economy_hash = state->macro_economy_hash;
    out_id->macro_events_hash = state->macro_events_hash;
    out_id->ups = state->ups;
    out_id->tick_index = state->tick_index;
    out_id->feature_epoch = state->feature_epoch;
    return DOM_UNIVERSE_BUNDLE_OK;
}

int dom_universe_bundle_set_chunk(dom_universe_bundle *bundle,
                                  u32 type_id,
                                  u16 version,
                                  const void *payload,
                                  u32 payload_size) {
    BundleChunk *chunk;
    if (!bundle) {
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }
    if (payload_size > 0u && !payload) {
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }
    if (type_id == DOM_UNIVERSE_CHUNK_TIME || type_id == DOM_UNIVERSE_CHUNK_FORN) {
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }
    chunk = chunk_for_type(&bundle->state, type_id);
    if (!chunk) {
        return DOM_UNIVERSE_BUNDLE_UNSUPPORTED_SCHEMA;
    }
    chunk->version = version;
    if (payload_size == 0u) {
        chunk->payload.clear();
    } else {
        chunk->payload.assign((const unsigned char *)payload,
                              (const unsigned char *)payload + payload_size);
    }
    chunk->present = true;
    if (type_id == DOM_UNIVERSE_CHUNK_COSM) {
        const u64 hash = hash_bytes_fnv1a64(chunk->payload);
        if (bundle->state.identity_set && bundle->state.cosmo_graph_hash != hash) {
            return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
        }
        bundle->state.cosmo_graph_hash = hash;
    } else if (type_id == DOM_UNIVERSE_CHUNK_SYSM) {
        const u64 hash = hash_bytes_fnv1a64(chunk->payload);
        if (bundle->state.identity_set && bundle->state.systems_hash != hash) {
            return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
        }
        bundle->state.systems_hash = hash;
    } else if (type_id == DOM_UNIVERSE_CHUNK_BODS) {
        const u64 hash = hash_bytes_fnv1a64(chunk->payload);
        if (bundle->state.identity_set && bundle->state.bodies_hash != hash) {
            return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
        }
        bundle->state.bodies_hash = hash;
    } else if (type_id == DOM_UNIVERSE_CHUNK_FRAM) {
        const u64 hash = hash_bytes_fnv1a64(chunk->payload);
        if (bundle->state.identity_set && bundle->state.frames_hash != hash) {
            return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
        }
        bundle->state.frames_hash = hash;
    } else if (type_id == DOM_UNIVERSE_CHUNK_TOPB) {
        const u64 hash = hash_bytes_fnv1a64(chunk->payload);
        if (bundle->state.identity_set && bundle->state.topology_hash != hash) {
            return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
        }
        bundle->state.topology_hash = hash;
    } else if (type_id == DOM_UNIVERSE_CHUNK_ORBT) {
        const u64 hash = hash_bytes_fnv1a64(chunk->payload);
        if (bundle->state.identity_set && bundle->state.orbits_hash != hash) {
            return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
        }
        bundle->state.orbits_hash = hash;
    } else if (type_id == DOM_UNIVERSE_CHUNK_SOVR) {
        const u64 hash = hash_bytes_fnv1a64(chunk->payload);
        if (bundle->state.identity_set && bundle->state.surface_overrides_hash != hash) {
            return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
        }
        bundle->state.surface_overrides_hash = hash;
    } else if (type_id == DOM_UNIVERSE_CHUNK_CNST) {
        const u64 hash = hash_bytes_fnv1a64(chunk->payload);
        if (bundle->state.identity_set && bundle->state.constructions_hash != hash) {
            return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
        }
        bundle->state.constructions_hash = hash;
    } else if (type_id == DOM_UNIVERSE_CHUNK_STAT) {
        const u64 hash = hash_bytes_fnv1a64(chunk->payload);
        if (bundle->state.identity_set && bundle->state.stations_hash != hash) {
            return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
        }
        bundle->state.stations_hash = hash;
    } else if (type_id == DOM_UNIVERSE_CHUNK_ROUT) {
        const u64 hash = hash_bytes_fnv1a64(chunk->payload);
        if (bundle->state.identity_set && bundle->state.routes_hash != hash) {
            return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
        }
        bundle->state.routes_hash = hash;
    } else if (type_id == DOM_UNIVERSE_CHUNK_TRAN) {
        const u64 hash = hash_bytes_fnv1a64(chunk->payload);
        if (bundle->state.identity_set && bundle->state.transfers_hash != hash) {
            return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
        }
        bundle->state.transfers_hash = hash;
    } else if (type_id == DOM_UNIVERSE_CHUNK_PROD) {
        const u64 hash = hash_bytes_fnv1a64(chunk->payload);
        if (bundle->state.identity_set && bundle->state.production_hash != hash) {
            return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
        }
        bundle->state.production_hash = hash;
    }
    return DOM_UNIVERSE_BUNDLE_OK;
}

int dom_universe_bundle_get_chunk(const dom_universe_bundle *bundle,
                                  u32 type_id,
                                  const unsigned char **out_payload,
                                  u32 *out_size,
                                  u16 *out_version) {
    const BundleChunk *chunk;
    if (!bundle || !out_payload || !out_size || !out_version) {
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }
    chunk = chunk_for_type(&bundle->state, type_id);
    if (!chunk || !chunk->present) {
        return DOM_UNIVERSE_BUNDLE_ERR;
    }
    *out_payload = chunk->payload.empty() ? 0 : &chunk->payload[0];
    *out_size = (u32)chunk->payload.size();
    *out_version = chunk->version;
    return DOM_UNIVERSE_BUNDLE_OK;
}

int dom_universe_bundle_clear_foreign(dom_universe_bundle *bundle) {
    if (!bundle) {
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }
    bundle->state.foreign.clear();
    return DOM_UNIVERSE_BUNDLE_OK;
}

int dom_universe_bundle_add_foreign(dom_universe_bundle *bundle,
                                    u32 type_id,
                                    u16 version,
                                    u16 flags,
                                    const void *payload,
                                    u32 payload_size) {
    ForeignChunk foreign;
    if (!bundle) {
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }
    if (payload_size > 0u && !payload) {
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }
    foreign.type_id = type_id;
    foreign.version = version;
    foreign.flags = flags;
    if (payload_size == 0u) {
        foreign.payload.clear();
    } else {
        foreign.payload.assign((const unsigned char *)payload,
                               (const unsigned char *)payload + payload_size);
    }
    bundle->state.foreign.push_back(foreign);
    return DOM_UNIVERSE_BUNDLE_OK;
}

int dom_universe_bundle_read_file(const char *path,
                                  const dom_universe_bundle_identity *expected,
                                  dom_universe_bundle *out_bundle) {
    dtlv_reader reader;
    u32 count;
    u32 i;
    bool have_time = false;
    bool have_cosm = false;
    bool have_sysm = false;
    bool have_bods = false;
    bool have_fram = false;
    bool have_topb = false;
    bool have_orbt = false;
    bool have_sovr = false;
    bool have_cnst = false;
    bool have_stat = false;
    bool have_rout = false;
    bool have_tran = false;
    bool have_prod = false;
    bool have_meco = false;
    bool have_mevt = false;
    bool have_cele = false;
    bool have_vesl = false;
    bool have_surf = false;
    bool have_locl = false;
    bool have_rng = false;
    bool have_forn = false;
    u64 cosmo_payload_hash = 0ull;
    bool cosmo_hash_set = false;
    u64 systems_payload_hash = 0ull;
    bool systems_hash_set = false;
    u64 bodies_payload_hash = 0ull;
    bool bodies_hash_set = false;
    u64 frames_payload_hash = 0ull;
    bool frames_hash_set = false;
    u64 topology_payload_hash = 0ull;
    bool topology_hash_set = false;
    u64 orbits_payload_hash = 0ull;
    bool orbits_hash_set = false;
    u64 surface_payload_hash = 0ull;
    bool surface_hash_set = false;
    u64 constructions_payload_hash = 0ull;
    bool constructions_hash_set = false;
    u64 stations_payload_hash = 0ull;
    bool stations_hash_set = false;
    u64 routes_payload_hash = 0ull;
    bool routes_hash_set = false;
    u64 transfers_payload_hash = 0ull;
    bool transfers_hash_set = false;
    u64 production_payload_hash = 0ull;
    bool production_hash_set = false;
    u64 macro_economy_payload_hash = 0ull;
    bool macro_economy_hash_set = false;
    u64 macro_events_payload_hash = 0ull;
    bool macro_events_hash_set = false;
    int rc;

    if (!path || !out_bundle) {
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }

    bundle_reset(&out_bundle->state);
    dtlv_reader_init(&reader);
    if (dtlv_reader_open_file(&reader, path) != 0) {
        dtlv_reader_dispose(&reader);
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }

    count = dtlv_reader_chunk_count(&reader);
    for (i = 0u; i < count; ++i) {
        const dtlv_dir_entry *entry = dtlv_reader_chunk_at(&reader, i);
        if (!entry) {
            continue;
        }
        switch (entry->type_id) {
            case DOM_UNIVERSE_CHUNK_TIME: {
                std::vector<unsigned char> payload;
                if (entry->version != 1u) {
                    rc = DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED;
                    goto cleanup;
                }
                rc = read_chunk_payload(&reader, entry, payload);
                if (rc != DOM_UNIVERSE_BUNDLE_OK) {
                    goto cleanup;
                }
                rc = parse_time_chunk(&out_bundle->state,
                                      payload.empty() ? 0 : &payload[0],
                                      (u32)payload.size());
                if (rc != DOM_UNIVERSE_BUNDLE_OK) {
                    goto cleanup;
                }
                have_time = true;
                break;
            }
            case DOM_UNIVERSE_CHUNK_COSM: {
                BundleChunk *chunk = chunk_for_type(&out_bundle->state, entry->type_id);
                if (!chunk) {
                    rc = DOM_UNIVERSE_BUNDLE_UNSUPPORTED_SCHEMA;
                    goto cleanup;
                }
                if (entry->version != 1u) {
                    rc = DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED;
                    goto cleanup;
                }
                rc = read_chunk_payload(&reader, entry, chunk->payload);
                if (rc != DOM_UNIVERSE_BUNDLE_OK) {
                    goto cleanup;
                }
                chunk->version = entry->version;
                chunk->present = true;
                cosmo_payload_hash = hash_bytes_fnv1a64(chunk->payload);
                cosmo_hash_set = true;
                if (out_bundle->state.identity_set &&
                    out_bundle->state.cosmo_graph_hash != cosmo_payload_hash) {
                    rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                    goto cleanup;
                }
                have_cosm = true;
                break;
            }
            case DOM_UNIVERSE_CHUNK_SYSM: {
                BundleChunk *chunk = chunk_for_type(&out_bundle->state, entry->type_id);
                if (!chunk) {
                    rc = DOM_UNIVERSE_BUNDLE_UNSUPPORTED_SCHEMA;
                    goto cleanup;
                }
                if (entry->version != 1u) {
                    rc = DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED;
                    goto cleanup;
                }
                rc = read_chunk_payload(&reader, entry, chunk->payload);
                if (rc != DOM_UNIVERSE_BUNDLE_OK) {
                    goto cleanup;
                }
                chunk->version = entry->version;
                chunk->present = true;
                systems_payload_hash = hash_bytes_fnv1a64(chunk->payload);
                systems_hash_set = true;
                if (out_bundle->state.identity_set &&
                    out_bundle->state.systems_hash != systems_payload_hash) {
                    rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                    goto cleanup;
                }
                have_sysm = true;
                break;
            }
            case DOM_UNIVERSE_CHUNK_BODS: {
                BundleChunk *chunk = chunk_for_type(&out_bundle->state, entry->type_id);
                if (!chunk) {
                    rc = DOM_UNIVERSE_BUNDLE_UNSUPPORTED_SCHEMA;
                    goto cleanup;
                }
                if (entry->version != 1u) {
                    rc = DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED;
                    goto cleanup;
                }
                rc = read_chunk_payload(&reader, entry, chunk->payload);
                if (rc != DOM_UNIVERSE_BUNDLE_OK) {
                    goto cleanup;
                }
                chunk->version = entry->version;
                chunk->present = true;
                bodies_payload_hash = hash_bytes_fnv1a64(chunk->payload);
                bodies_hash_set = true;
                if (out_bundle->state.identity_set &&
                    out_bundle->state.bodies_hash != bodies_payload_hash) {
                    rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                    goto cleanup;
                }
                have_bods = true;
                break;
            }
            case DOM_UNIVERSE_CHUNK_FRAM: {
                BundleChunk *chunk = chunk_for_type(&out_bundle->state, entry->type_id);
                if (!chunk) {
                    rc = DOM_UNIVERSE_BUNDLE_UNSUPPORTED_SCHEMA;
                    goto cleanup;
                }
                if (entry->version != 1u) {
                    rc = DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED;
                    goto cleanup;
                }
                rc = read_chunk_payload(&reader, entry, chunk->payload);
                if (rc != DOM_UNIVERSE_BUNDLE_OK) {
                    goto cleanup;
                }
                chunk->version = entry->version;
                chunk->present = true;
                frames_payload_hash = hash_bytes_fnv1a64(chunk->payload);
                frames_hash_set = true;
                if (out_bundle->state.identity_set &&
                    out_bundle->state.frames_hash != frames_payload_hash) {
                    rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                    goto cleanup;
                }
                have_fram = true;
                break;
            }
            case DOM_UNIVERSE_CHUNK_TOPB: {
                BundleChunk *chunk = chunk_for_type(&out_bundle->state, entry->type_id);
                if (!chunk) {
                    rc = DOM_UNIVERSE_BUNDLE_UNSUPPORTED_SCHEMA;
                    goto cleanup;
                }
                if (entry->version != 1u) {
                    rc = DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED;
                    goto cleanup;
                }
                rc = read_chunk_payload(&reader, entry, chunk->payload);
                if (rc != DOM_UNIVERSE_BUNDLE_OK) {
                    goto cleanup;
                }
                chunk->version = entry->version;
                chunk->present = true;
                topology_payload_hash = hash_bytes_fnv1a64(chunk->payload);
                topology_hash_set = true;
                if (out_bundle->state.identity_set &&
                    out_bundle->state.topology_hash != topology_payload_hash) {
                    rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                    goto cleanup;
                }
                have_topb = true;
                break;
            }
            case DOM_UNIVERSE_CHUNK_ORBT: {
                BundleChunk *chunk = chunk_for_type(&out_bundle->state, entry->type_id);
                if (!chunk) {
                    rc = DOM_UNIVERSE_BUNDLE_UNSUPPORTED_SCHEMA;
                    goto cleanup;
                }
                if (entry->version != 1u) {
                    rc = DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED;
                    goto cleanup;
                }
                rc = read_chunk_payload(&reader, entry, chunk->payload);
                if (rc != DOM_UNIVERSE_BUNDLE_OK) {
                    goto cleanup;
                }
                chunk->version = entry->version;
                chunk->present = true;
                orbits_payload_hash = hash_bytes_fnv1a64(chunk->payload);
                orbits_hash_set = true;
                if (out_bundle->state.identity_set &&
                    out_bundle->state.orbits_hash != orbits_payload_hash) {
                    rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                    goto cleanup;
                }
                have_orbt = true;
                break;
            }
            case DOM_UNIVERSE_CHUNK_SOVR: {
                BundleChunk *chunk = chunk_for_type(&out_bundle->state, entry->type_id);
                if (!chunk) {
                    rc = DOM_UNIVERSE_BUNDLE_UNSUPPORTED_SCHEMA;
                    goto cleanup;
                }
                if (entry->version != 1u) {
                    rc = DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED;
                    goto cleanup;
                }
                rc = read_chunk_payload(&reader, entry, chunk->payload);
                if (rc != DOM_UNIVERSE_BUNDLE_OK) {
                    goto cleanup;
                }
                chunk->version = entry->version;
                chunk->present = true;
                surface_payload_hash = hash_bytes_fnv1a64(chunk->payload);
                surface_hash_set = true;
                if (out_bundle->state.identity_set &&
                    out_bundle->state.surface_overrides_hash != surface_payload_hash) {
                    rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                    goto cleanup;
                }
                have_sovr = true;
                break;
            }
            case DOM_UNIVERSE_CHUNK_CNST: {
                BundleChunk *chunk = chunk_for_type(&out_bundle->state, entry->type_id);
                if (!chunk) {
                    rc = DOM_UNIVERSE_BUNDLE_UNSUPPORTED_SCHEMA;
                    goto cleanup;
                }
                if (entry->version != 1u) {
                    rc = DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED;
                    goto cleanup;
                }
                rc = read_chunk_payload(&reader, entry, chunk->payload);
                if (rc != DOM_UNIVERSE_BUNDLE_OK) {
                    goto cleanup;
                }
                chunk->version = entry->version;
                chunk->present = true;
                constructions_payload_hash = hash_bytes_fnv1a64(chunk->payload);
                constructions_hash_set = true;
                if (out_bundle->state.identity_set &&
                    out_bundle->state.constructions_hash != constructions_payload_hash) {
                    rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                    goto cleanup;
                }
                have_cnst = true;
                break;
            }
            case DOM_UNIVERSE_CHUNK_STAT: {
                BundleChunk *chunk = chunk_for_type(&out_bundle->state, entry->type_id);
                if (!chunk) {
                    rc = DOM_UNIVERSE_BUNDLE_UNSUPPORTED_SCHEMA;
                    goto cleanup;
                }
                if (entry->version != 1u) {
                    rc = DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED;
                    goto cleanup;
                }
                rc = read_chunk_payload(&reader, entry, chunk->payload);
                if (rc != DOM_UNIVERSE_BUNDLE_OK) {
                    goto cleanup;
                }
                chunk->version = entry->version;
                chunk->present = true;
                stations_payload_hash = hash_bytes_fnv1a64(chunk->payload);
                stations_hash_set = true;
                if (out_bundle->state.identity_set &&
                    out_bundle->state.stations_hash != stations_payload_hash) {
                    rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                    goto cleanup;
                }
                have_stat = true;
                break;
            }
            case DOM_UNIVERSE_CHUNK_ROUT: {
                BundleChunk *chunk = chunk_for_type(&out_bundle->state, entry->type_id);
                if (!chunk) {
                    rc = DOM_UNIVERSE_BUNDLE_UNSUPPORTED_SCHEMA;
                    goto cleanup;
                }
                if (entry->version != 1u) {
                    rc = DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED;
                    goto cleanup;
                }
                rc = read_chunk_payload(&reader, entry, chunk->payload);
                if (rc != DOM_UNIVERSE_BUNDLE_OK) {
                    goto cleanup;
                }
                chunk->version = entry->version;
                chunk->present = true;
                routes_payload_hash = hash_bytes_fnv1a64(chunk->payload);
                routes_hash_set = true;
                if (out_bundle->state.identity_set &&
                    out_bundle->state.routes_hash != routes_payload_hash) {
                    rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                    goto cleanup;
                }
                have_rout = true;
                break;
            }
            case DOM_UNIVERSE_CHUNK_TRAN: {
                BundleChunk *chunk = chunk_for_type(&out_bundle->state, entry->type_id);
                if (!chunk) {
                    rc = DOM_UNIVERSE_BUNDLE_UNSUPPORTED_SCHEMA;
                    goto cleanup;
                }
                if (entry->version != 1u) {
                    rc = DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED;
                    goto cleanup;
                }
                rc = read_chunk_payload(&reader, entry, chunk->payload);
                if (rc != DOM_UNIVERSE_BUNDLE_OK) {
                    goto cleanup;
                }
                chunk->version = entry->version;
                chunk->present = true;
                transfers_payload_hash = hash_bytes_fnv1a64(chunk->payload);
                transfers_hash_set = true;
                if (out_bundle->state.identity_set &&
                    out_bundle->state.transfers_hash != transfers_payload_hash) {
                    rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                    goto cleanup;
                }
                have_tran = true;
                break;
            }
            case DOM_UNIVERSE_CHUNK_PROD: {
                BundleChunk *chunk = chunk_for_type(&out_bundle->state, entry->type_id);
                if (!chunk) {
                    rc = DOM_UNIVERSE_BUNDLE_UNSUPPORTED_SCHEMA;
                    goto cleanup;
                }
                if (entry->version != 1u) {
                    rc = DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED;
                    goto cleanup;
                }
                rc = read_chunk_payload(&reader, entry, chunk->payload);
                if (rc != DOM_UNIVERSE_BUNDLE_OK) {
                    goto cleanup;
                }
                chunk->version = entry->version;
                chunk->present = true;
                production_payload_hash = hash_bytes_fnv1a64(chunk->payload);
                production_hash_set = true;
                if (out_bundle->state.identity_set &&
                    out_bundle->state.production_hash != production_payload_hash) {
                    rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                    goto cleanup;
                }
                have_prod = true;
                break;
            }
            case DOM_UNIVERSE_CHUNK_MECO: {
                BundleChunk *chunk = chunk_for_type(&out_bundle->state, entry->type_id);
                if (!chunk) {
                    rc = DOM_UNIVERSE_BUNDLE_UNSUPPORTED_SCHEMA;
                    goto cleanup;
                }
                if (entry->version != 1u) {
                    rc = DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED;
                    goto cleanup;
                }
                rc = read_chunk_payload(&reader, entry, chunk->payload);
                if (rc != DOM_UNIVERSE_BUNDLE_OK) {
                    goto cleanup;
                }
                chunk->version = entry->version;
                chunk->present = true;
                macro_economy_payload_hash = hash_bytes_fnv1a64(chunk->payload);
                macro_economy_hash_set = true;
                if (out_bundle->state.identity_set &&
                    out_bundle->state.macro_economy_hash != macro_economy_payload_hash) {
                    rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                    goto cleanup;
                }
                have_meco = true;
                break;
            }
            case DOM_UNIVERSE_CHUNK_MEVT: {
                BundleChunk *chunk = chunk_for_type(&out_bundle->state, entry->type_id);
                if (!chunk) {
                    rc = DOM_UNIVERSE_BUNDLE_UNSUPPORTED_SCHEMA;
                    goto cleanup;
                }
                if (entry->version != 1u) {
                    rc = DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED;
                    goto cleanup;
                }
                rc = read_chunk_payload(&reader, entry, chunk->payload);
                if (rc != DOM_UNIVERSE_BUNDLE_OK) {
                    goto cleanup;
                }
                chunk->version = entry->version;
                chunk->present = true;
                macro_events_payload_hash = hash_bytes_fnv1a64(chunk->payload);
                macro_events_hash_set = true;
                if (out_bundle->state.identity_set &&
                    out_bundle->state.macro_events_hash != macro_events_payload_hash) {
                    rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
                    goto cleanup;
                }
                have_mevt = true;
                break;
            }
            case DOM_UNIVERSE_CHUNK_CELE:
            case DOM_UNIVERSE_CHUNK_VESL:
            case DOM_UNIVERSE_CHUNK_SURF:
            case DOM_UNIVERSE_CHUNK_LOCL:
            case DOM_UNIVERSE_CHUNK_RNG: {
                BundleChunk *chunk = chunk_for_type(&out_bundle->state, entry->type_id);
                if (!chunk) {
                    rc = DOM_UNIVERSE_BUNDLE_UNSUPPORTED_SCHEMA;
                    goto cleanup;
                }
                if (entry->version != 1u) {
                    rc = DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED;
                    goto cleanup;
                }
                rc = read_chunk_payload(&reader, entry, chunk->payload);
                if (rc != DOM_UNIVERSE_BUNDLE_OK) {
                    goto cleanup;
                }
                chunk->version = entry->version;
                chunk->present = true;
                if (entry->type_id == DOM_UNIVERSE_CHUNK_CELE) have_cele = true;
                if (entry->type_id == DOM_UNIVERSE_CHUNK_VESL) have_vesl = true;
                if (entry->type_id == DOM_UNIVERSE_CHUNK_SURF) have_surf = true;
                if (entry->type_id == DOM_UNIVERSE_CHUNK_LOCL) have_locl = true;
                if (entry->type_id == DOM_UNIVERSE_CHUNK_RNG)  have_rng = true;
                break;
            }
            case DOM_UNIVERSE_CHUNK_FORN: {
                std::vector<unsigned char> payload;
                if (entry->version != 1u) {
                    rc = DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED;
                    goto cleanup;
                }
                rc = read_chunk_payload(&reader, entry, payload);
                if (rc != DOM_UNIVERSE_BUNDLE_OK) {
                    goto cleanup;
                }
                rc = parse_foreign_chunk(&out_bundle->state,
                                         payload.empty() ? 0 : &payload[0],
                                         (u32)payload.size());
                if (rc != DOM_UNIVERSE_BUNDLE_OK) {
                    goto cleanup;
                }
                have_forn = true;
                break;
            }
            default: {
                ForeignChunk foreign;
                std::vector<unsigned char> payload;
                rc = read_chunk_payload(&reader, entry, payload);
                if (rc != DOM_UNIVERSE_BUNDLE_OK) {
                    goto cleanup;
                }
                foreign.type_id = entry->type_id;
                foreign.version = entry->version;
                foreign.flags = entry->flags;
                foreign.payload = payload;
                out_bundle->state.foreign.push_back(foreign);
                break;
            }
        }
    }

    if (!have_time || !have_cosm || !have_cele || !have_vesl || !have_surf ||
        !have_locl || !have_rng || !have_forn ||
        !have_sysm || !have_bods || !have_fram || !have_topb || !have_orbt ||
        !have_sovr || !have_cnst || !have_stat || !have_rout || !have_tran || !have_prod ||
        !have_meco || !have_mevt) {
        rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
        goto cleanup;
    }
    if (out_bundle->state.identity_set &&
        cosmo_hash_set &&
        cosmo_payload_hash != out_bundle->state.cosmo_graph_hash) {
        rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
        goto cleanup;
    }
    if (out_bundle->state.identity_set &&
        systems_hash_set &&
        systems_payload_hash != out_bundle->state.systems_hash) {
        rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
        goto cleanup;
    }
    if (out_bundle->state.identity_set &&
        bodies_hash_set &&
        bodies_payload_hash != out_bundle->state.bodies_hash) {
        rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
        goto cleanup;
    }
    if (out_bundle->state.identity_set &&
        frames_hash_set &&
        frames_payload_hash != out_bundle->state.frames_hash) {
        rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
        goto cleanup;
    }
    if (out_bundle->state.identity_set &&
        topology_hash_set &&
        topology_payload_hash != out_bundle->state.topology_hash) {
        rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
        goto cleanup;
    }
    if (out_bundle->state.identity_set &&
        orbits_hash_set &&
        orbits_payload_hash != out_bundle->state.orbits_hash) {
        rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
        goto cleanup;
    }
    if (out_bundle->state.identity_set &&
        surface_hash_set &&
        surface_payload_hash != out_bundle->state.surface_overrides_hash) {
        rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
        goto cleanup;
    }
    if (out_bundle->state.identity_set &&
        constructions_hash_set &&
        constructions_payload_hash != out_bundle->state.constructions_hash) {
        rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
        goto cleanup;
    }
    if (out_bundle->state.identity_set &&
        stations_hash_set &&
        stations_payload_hash != out_bundle->state.stations_hash) {
        rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
        goto cleanup;
    }
    if (out_bundle->state.identity_set &&
        routes_hash_set &&
        routes_payload_hash != out_bundle->state.routes_hash) {
        rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
        goto cleanup;
    }
    if (out_bundle->state.identity_set &&
        transfers_hash_set &&
        transfers_payload_hash != out_bundle->state.transfers_hash) {
        rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
        goto cleanup;
    }
    if (out_bundle->state.identity_set &&
        production_hash_set &&
        production_payload_hash != out_bundle->state.production_hash) {
        rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
        goto cleanup;
    }
    if (out_bundle->state.identity_set &&
        macro_economy_hash_set &&
        macro_economy_payload_hash != out_bundle->state.macro_economy_hash) {
        rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
        goto cleanup;
    }
    if (out_bundle->state.identity_set &&
        macro_events_hash_set &&
        macro_events_payload_hash != out_bundle->state.macro_events_hash) {
        rc = DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
        goto cleanup;
    }

    if (expected) {
        rc = identity_matches(&out_bundle->state, expected);
        if (rc != DOM_UNIVERSE_BUNDLE_OK) {
            goto cleanup;
        }
    }

    rc = DOM_UNIVERSE_BUNDLE_OK;

cleanup:
    dtlv_reader_dispose(&reader);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        bundle_reset(&out_bundle->state);
    }
    return rc;
}

int dom_universe_bundle_write_file(const char *path,
                                   const dom_universe_bundle *bundle) {
    dtlv_writer writer;
    const BundleState *state;
    int rc;

    if (!path || !bundle) {
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }
    state = &bundle->state;
    if (!state->identity_set) {
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }
    if (hash_bytes_fnv1a64(state->cosmo.payload) != state->cosmo_graph_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (hash_bytes_fnv1a64(state->sysm.payload) != state->systems_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (hash_bytes_fnv1a64(state->bods.payload) != state->bodies_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (hash_bytes_fnv1a64(state->fram.payload) != state->frames_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (hash_bytes_fnv1a64(state->topb.payload) != state->topology_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (hash_bytes_fnv1a64(state->orbt.payload) != state->orbits_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (hash_bytes_fnv1a64(state->sovr.payload) != state->surface_overrides_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (hash_bytes_fnv1a64(state->cnst.payload) != state->constructions_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (hash_bytes_fnv1a64(state->stat.payload) != state->stations_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (hash_bytes_fnv1a64(state->rout.payload) != state->routes_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (hash_bytes_fnv1a64(state->tran.payload) != state->transfers_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (hash_bytes_fnv1a64(state->prod.payload) != state->production_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (hash_bytes_fnv1a64(state->meco.payload) != state->macro_economy_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }
    if (hash_bytes_fnv1a64(state->mevt.payload) != state->macro_events_hash) {
        return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
    }

    dtlv_writer_init(&writer);
    if (dtlv_writer_open_file(&writer, path) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }

    rc = write_time_chunk(&writer, state);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        goto cleanup;
    }
    rc = write_raw_chunk(&writer, DOM_UNIVERSE_CHUNK_COSM, state->cosmo);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        goto cleanup;
    }
    rc = write_raw_chunk(&writer, DOM_UNIVERSE_CHUNK_SYSM, state->sysm);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        goto cleanup;
    }
    rc = write_raw_chunk(&writer, DOM_UNIVERSE_CHUNK_BODS, state->bods);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        goto cleanup;
    }
    rc = write_raw_chunk(&writer, DOM_UNIVERSE_CHUNK_FRAM, state->fram);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        goto cleanup;
    }
    rc = write_raw_chunk(&writer, DOM_UNIVERSE_CHUNK_TOPB, state->topb);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        goto cleanup;
    }
    rc = write_raw_chunk(&writer, DOM_UNIVERSE_CHUNK_ORBT, state->orbt);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        goto cleanup;
    }
    rc = write_raw_chunk(&writer, DOM_UNIVERSE_CHUNK_SOVR, state->sovr);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        goto cleanup;
    }
    rc = write_raw_chunk(&writer, DOM_UNIVERSE_CHUNK_CNST, state->cnst);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        goto cleanup;
    }
    rc = write_raw_chunk(&writer, DOM_UNIVERSE_CHUNK_STAT, state->stat);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        goto cleanup;
    }
    rc = write_raw_chunk(&writer, DOM_UNIVERSE_CHUNK_ROUT, state->rout);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        goto cleanup;
    }
    rc = write_raw_chunk(&writer, DOM_UNIVERSE_CHUNK_TRAN, state->tran);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        goto cleanup;
    }
    rc = write_raw_chunk(&writer, DOM_UNIVERSE_CHUNK_PROD, state->prod);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        goto cleanup;
    }
    rc = write_raw_chunk(&writer, DOM_UNIVERSE_CHUNK_MECO, state->meco);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        goto cleanup;
    }
    rc = write_raw_chunk(&writer, DOM_UNIVERSE_CHUNK_MEVT, state->mevt);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        goto cleanup;
    }
    rc = write_raw_chunk(&writer, DOM_UNIVERSE_CHUNK_CELE, state->cele);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        goto cleanup;
    }
    rc = write_raw_chunk(&writer, DOM_UNIVERSE_CHUNK_VESL, state->vesl);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        goto cleanup;
    }
    rc = write_raw_chunk(&writer, DOM_UNIVERSE_CHUNK_SURF, state->surf);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        goto cleanup;
    }
    rc = write_raw_chunk(&writer, DOM_UNIVERSE_CHUNK_LOCL, state->locl);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        goto cleanup;
    }
    rc = write_raw_chunk(&writer, DOM_UNIVERSE_CHUNK_RNG, state->rng);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        goto cleanup;
    }
    rc = write_foreign_chunk(&writer, state->foreign);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        goto cleanup;
    }

    if (dtlv_writer_finalize(&writer) != 0) {
        rc = DOM_UNIVERSE_BUNDLE_IO_ERROR;
        goto cleanup;
    }
    rc = DOM_UNIVERSE_BUNDLE_OK;

cleanup:
    dtlv_writer_dispose(&writer);
    return rc;
}
