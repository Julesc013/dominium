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
    u32 ups;
    u64 tick_index;
    u32 feature_epoch;
    bool identity_set;

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
          ups(0u),
          tick_index(0ull),
          feature_epoch(0u),
          identity_set(false),
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
    state->ups = 0u;
    state->tick_index = 0ull;
    state->feature_epoch = 0u;
    state->identity_set = false;
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
        !have_flags || !have_ups || !have_tick) {
        return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
    }
    if (!have_epoch) {
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
    state->universe_id.assign(id->universe_id, id->universe_id_len);
    state->instance_id.assign(id->instance_id, id->instance_id_len);
    state->content_graph_hash = id->content_graph_hash;
    state->sim_flags_hash = id->sim_flags_hash;
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
    bool have_cele = false;
    bool have_vesl = false;
    bool have_surf = false;
    bool have_locl = false;
    bool have_rng = false;
    bool have_forn = false;
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

    if (!have_time || !have_cele || !have_vesl || !have_surf ||
        !have_locl || !have_rng || !have_forn) {
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

    dtlv_writer_init(&writer);
    if (dtlv_writer_open_file(&writer, path) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }

    rc = write_time_chunk(&writer, state);
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
