/*
FILE: tests/contract/dominium_universe_bundle_tests.cpp
MODULE: Repository
LAYER / SUBSYSTEM: tests/contract
RESPONSIBILITY: Contract tests for universe bundle containers and migrations.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

extern "C" {
#include "domino/core/spacetime.h"
#include "domino/io/container.h"
}

#include "runtime/dom_universe_bundle.h"
#include "dom_schema_registry.h"
#include "dom_migration.h"

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg);
    return 1;
}

static void remove_if_exists(const char *path) {
    if (path && path[0]) {
        std::remove(path);
    }
}

static int make_temp_path(char *out_path, size_t cap) {
    char buf[L_tmpnam];
    if (!out_path || cap == 0u) {
        return 0;
    }
    if (!std::tmpnam(buf)) {
        return 0;
    }
    if (std::strlen(buf) + 1u > cap) {
        return 0;
    }
    std::strcpy(out_path, buf);
    return 1;
}

static int read_file_bytes(const char *path, std::vector<unsigned char> &out) {
    std::FILE *fh = 0;
    long size = 0;
    size_t read_size = 0u;

    if (!path) {
        return 1;
    }
    fh = std::fopen(path, "rb");
    if (!fh) {
        return 1;
    }
    if (std::fseek(fh, 0, SEEK_END) != 0) {
        std::fclose(fh);
        return 1;
    }
    size = std::ftell(fh);
    if (size < 0) {
        std::fclose(fh);
        return 1;
    }
    if (std::fseek(fh, 0, SEEK_SET) != 0) {
        std::fclose(fh);
        return 1;
    }
    out.resize((size_t)size);
    if (size > 0) {
        read_size = std::fread(&out[0], 1u, (size_t)size, fh);
    }
    std::fclose(fh);
    return (read_size == (size_t)size) ? 0 : 1;
}

static int hash_file(const char *path, u64 *out_hash) {
    std::vector<unsigned char> bytes;
    int rc;
    if (!out_hash) {
        return 1;
    }
    if (read_file_bytes(path, bytes) != 0) {
        return 1;
    }
    if (bytes.empty()) {
        return 1;
    }
    rc = dom_id_hash64((const char *)&bytes[0], (u32)bytes.size(), out_hash);
    return (rc == DOM_SPACETIME_OK) ? 0 : 1;
}

static int hash_payload(const std::vector<unsigned char> &bytes, u64 *out_hash) {
    int rc;
    if (!out_hash) {
        return 1;
    }
    if (bytes.empty()) {
        *out_hash = 0ull;
        return 0;
    }
    rc = dom_id_hash64((const char *)&bytes[0], (u32)bytes.size(), out_hash);
    return (rc == DOM_SPACETIME_OK) ? 0 : 1;
}

static int write_time_chunk(dtlv_writer *writer, const dom_universe_bundle_identity &id) {
    unsigned char buf[8];
    if (!writer || !id.universe_id || !id.instance_id) {
        return 1;
    }
    if (dtlv_writer_begin_chunk(writer, DOM_UNIVERSE_CHUNK_TIME, 1u, 0u) != 0) {
        return 1;
    }
    if (dtlv_writer_write_tlv(writer,
                              DOM_UNIVERSE_TLV_UNIVERSE_ID,
                              id.universe_id,
                              id.universe_id_len) != 0) {
        return 1;
    }
    if (dtlv_writer_write_tlv(writer,
                              DOM_UNIVERSE_TLV_INSTANCE_ID,
                              id.instance_id,
                              id.instance_id_len) != 0) {
        return 1;
    }
    dtlv_le_write_u64(buf, id.content_graph_hash);
    if (dtlv_writer_write_tlv(writer,
                              DOM_UNIVERSE_TLV_CONTENT_HASH,
                              buf,
                              8u) != 0) {
        return 1;
    }
    dtlv_le_write_u64(buf, id.sim_flags_hash);
    if (dtlv_writer_write_tlv(writer,
                              DOM_UNIVERSE_TLV_SIM_FLAGS_HASH,
                              buf,
                              8u) != 0) {
        return 1;
    }
    dtlv_le_write_u32(buf, id.ups);
    if (dtlv_writer_write_tlv(writer,
                              DOM_UNIVERSE_TLV_UPS,
                              buf,
                              4u) != 0) {
        return 1;
    }
    dtlv_le_write_u64(buf, id.tick_index);
    if (dtlv_writer_write_tlv(writer,
                              DOM_UNIVERSE_TLV_TICK_INDEX,
                              buf,
                              8u) != 0) {
        return 1;
    }
    dtlv_le_write_u32(buf, id.feature_epoch);
    if (dtlv_writer_write_tlv(writer,
                              DOM_UNIVERSE_TLV_FEATURE_EPOCH,
                              buf,
                              4u) != 0) {
        return 1;
    }
    dtlv_le_write_u64(buf, id.cosmo_graph_hash);
    if (dtlv_writer_write_tlv(writer,
                              DOM_UNIVERSE_TLV_COSMO_HASH,
                              buf,
                              8u) != 0) {
        return 1;
    }
    dtlv_le_write_u64(buf, id.systems_hash);
    if (dtlv_writer_write_tlv(writer,
                              DOM_UNIVERSE_TLV_SYSTEMS_HASH,
                              buf,
                              8u) != 0) {
        return 1;
    }
    dtlv_le_write_u64(buf, id.bodies_hash);
    if (dtlv_writer_write_tlv(writer,
                              DOM_UNIVERSE_TLV_BODIES_HASH,
                              buf,
                              8u) != 0) {
        return 1;
    }
    dtlv_le_write_u64(buf, id.frames_hash);
    if (dtlv_writer_write_tlv(writer,
                              DOM_UNIVERSE_TLV_FRAMES_HASH,
                              buf,
                              8u) != 0) {
        return 1;
    }
    dtlv_le_write_u64(buf, id.topology_hash);
    if (dtlv_writer_write_tlv(writer,
                              DOM_UNIVERSE_TLV_TOPOLOGY_HASH,
                              buf,
                              8u) != 0) {
        return 1;
    }
    dtlv_le_write_u64(buf, id.orbits_hash);
    if (dtlv_writer_write_tlv(writer,
                              DOM_UNIVERSE_TLV_ORBITS_HASH,
                              buf,
                              8u) != 0) {
        return 1;
    }
    dtlv_le_write_u64(buf, id.surface_overrides_hash);
    if (dtlv_writer_write_tlv(writer,
                              DOM_UNIVERSE_TLV_SURFACE_HASH,
                              buf,
                              8u) != 0) {
        return 1;
    }
    dtlv_le_write_u64(buf, id.constructions_hash);
    if (dtlv_writer_write_tlv(writer,
                              DOM_UNIVERSE_TLV_CONSTRUCTIONS_HASH,
                              buf,
                              8u) != 0) {
        return 1;
    }
    dtlv_le_write_u64(buf, id.stations_hash);
    if (dtlv_writer_write_tlv(writer,
                              DOM_UNIVERSE_TLV_STATIONS_HASH,
                              buf,
                              8u) != 0) {
        return 1;
    }
    dtlv_le_write_u64(buf, id.routes_hash);
    if (dtlv_writer_write_tlv(writer,
                              DOM_UNIVERSE_TLV_ROUTES_HASH,
                              buf,
                              8u) != 0) {
        return 1;
    }
    dtlv_le_write_u64(buf, id.transfers_hash);
    if (dtlv_writer_write_tlv(writer,
                              DOM_UNIVERSE_TLV_TRANSFERS_HASH,
                              buf,
                              8u) != 0) {
        return 1;
    }
    dtlv_le_write_u64(buf, id.production_hash);
    if (dtlv_writer_write_tlv(writer,
                              DOM_UNIVERSE_TLV_PRODUCTION_HASH,
                              buf,
                              8u) != 0) {
        return 1;
    }
    dtlv_le_write_u64(buf, id.macro_economy_hash);
    if (dtlv_writer_write_tlv(writer,
                              DOM_UNIVERSE_TLV_MACRO_ECONOMY_HASH,
                              buf,
                              8u) != 0) {
        return 1;
    }
    dtlv_le_write_u64(buf, id.macro_events_hash);
    if (dtlv_writer_write_tlv(writer,
                              DOM_UNIVERSE_TLV_MACRO_EVENTS_HASH,
                              buf,
                              8u) != 0) {
        return 1;
    }
    if (dtlv_writer_end_chunk(writer) != 0) {
        return 1;
    }
    return 0;
}

static int write_empty_chunk(dtlv_writer *writer, u32 type_id) {
    if (!writer) {
        return 1;
    }
    if (dtlv_writer_begin_chunk(writer, type_id, 1u, 0u) != 0) {
        return 1;
    }
    if (dtlv_writer_end_chunk(writer) != 0) {
        return 1;
    }
    return 0;
}

static int test_bundle_identity_timebase(void) {
    char path[L_tmpnam];
    dom_universe_bundle *bundle = 0;
    dom_universe_bundle *bundle_in = 0;
    dom_universe_bundle_identity id;
    dom_universe_bundle_identity got;

    if (!make_temp_path(path, sizeof(path))) {
        return fail("temp path allocation failed");
    }
    remove_if_exists(path);

    std::memset(&id, 0, sizeof(id));
    id.universe_id = "universe_alpha";
    id.universe_id_len = (u32)std::strlen(id.universe_id);
    id.instance_id = "instance_beta";
    id.instance_id_len = (u32)std::strlen(id.instance_id);
    id.content_graph_hash = 0x0102030405060708ull;
    id.sim_flags_hash = 0x090a0b0c0d0e0f10ull;
    id.ups = 60u;
    id.tick_index = 12345ull;
    id.feature_epoch = 1u;

    bundle = dom_universe_bundle_create();
    if (!bundle) {
        return fail("bundle_create failed");
    }
    if (dom_universe_bundle_set_identity(bundle, &id) != DOM_UNIVERSE_BUNDLE_OK) {
        dom_universe_bundle_destroy(bundle);
        return fail("bundle_set_identity failed");
    }
    if (dom_universe_bundle_write_file(path, bundle) != DOM_UNIVERSE_BUNDLE_OK) {
        dom_universe_bundle_destroy(bundle);
        return fail("bundle_write_file failed");
    }

    bundle_in = dom_universe_bundle_create();
    if (!bundle_in) {
        dom_universe_bundle_destroy(bundle);
        return fail("bundle_create read failed");
    }
    if (dom_universe_bundle_read_file(path, &id, bundle_in) != DOM_UNIVERSE_BUNDLE_OK) {
        dom_universe_bundle_destroy(bundle_in);
        dom_universe_bundle_destroy(bundle);
        return fail("bundle_read_file failed");
    }
    if (dom_universe_bundle_get_identity(bundle_in, &got) != DOM_UNIVERSE_BUNDLE_OK) {
        dom_universe_bundle_destroy(bundle_in);
        dom_universe_bundle_destroy(bundle);
        return fail("bundle_get_identity failed");
    }
    if (got.ups != id.ups || got.tick_index != id.tick_index) {
        dom_universe_bundle_destroy(bundle_in);
        dom_universe_bundle_destroy(bundle);
        return fail("timebase mismatch");
    }

    dom_universe_bundle_destroy(bundle_in);
    dom_universe_bundle_destroy(bundle);
    remove_if_exists(path);
    return 0;
}

static int test_bundle_unknown_preservation(void) {
    char path_in[L_tmpnam];
    char path_out[L_tmpnam];
    dom_universe_bundle *bundle = 0;
    dom_universe_bundle_identity id;
    dtlv_writer writer;
    dtlv_reader reader;
    const unsigned char unknown_payload[] = { 0x10u, 0x20u, 0x30u, 0x40u, 0x50u };
    const u32 unknown_type = DOM_U32_FOURCC('X','U','N','K');
    const u16 unknown_version = 7u;
    const u16 unknown_flags = 0u;
    int found = 0;

    if (!make_temp_path(path_in, sizeof(path_in)) ||
        !make_temp_path(path_out, sizeof(path_out))) {
        return fail("temp path allocation failed");
    }
    remove_if_exists(path_in);
    remove_if_exists(path_out);

    std::memset(&id, 0, sizeof(id));
    id.universe_id = "universe_gamma";
    id.universe_id_len = (u32)std::strlen(id.universe_id);
    id.instance_id = "instance_delta";
    id.instance_id_len = (u32)std::strlen(id.instance_id);
    id.content_graph_hash = 0x1112131415161718ull;
    id.sim_flags_hash = 0x2122232425262728ull;
    id.ups = 60u;
    id.tick_index = 9ull;
    id.feature_epoch = 1u;

    dtlv_writer_init(&writer);
    if (dtlv_writer_open_file(&writer, path_in) != 0) {
        dtlv_writer_dispose(&writer);
        return fail("dtlv_writer_open_file failed");
    }
    if (write_time_chunk(&writer, id) != 0 ||
        write_empty_chunk(&writer, DOM_UNIVERSE_CHUNK_COSM) != 0 ||
        write_empty_chunk(&writer, DOM_UNIVERSE_CHUNK_SYSM) != 0 ||
        write_empty_chunk(&writer, DOM_UNIVERSE_CHUNK_BODS) != 0 ||
        write_empty_chunk(&writer, DOM_UNIVERSE_CHUNK_FRAM) != 0 ||
        write_empty_chunk(&writer, DOM_UNIVERSE_CHUNK_TOPB) != 0 ||
        write_empty_chunk(&writer, DOM_UNIVERSE_CHUNK_ORBT) != 0 ||
        write_empty_chunk(&writer, DOM_UNIVERSE_CHUNK_SOVR) != 0 ||
        write_empty_chunk(&writer, DOM_UNIVERSE_CHUNK_CNST) != 0 ||
        write_empty_chunk(&writer, DOM_UNIVERSE_CHUNK_STAT) != 0 ||
        write_empty_chunk(&writer, DOM_UNIVERSE_CHUNK_ROUT) != 0 ||
        write_empty_chunk(&writer, DOM_UNIVERSE_CHUNK_TRAN) != 0 ||
        write_empty_chunk(&writer, DOM_UNIVERSE_CHUNK_PROD) != 0 ||
        write_empty_chunk(&writer, DOM_UNIVERSE_CHUNK_MECO) != 0 ||
        write_empty_chunk(&writer, DOM_UNIVERSE_CHUNK_MEVT) != 0 ||
        write_empty_chunk(&writer, DOM_UNIVERSE_CHUNK_CELE) != 0 ||
        write_empty_chunk(&writer, DOM_UNIVERSE_CHUNK_VESL) != 0 ||
        write_empty_chunk(&writer, DOM_UNIVERSE_CHUNK_SURF) != 0 ||
        write_empty_chunk(&writer, DOM_UNIVERSE_CHUNK_LOCL) != 0 ||
        write_empty_chunk(&writer, DOM_UNIVERSE_CHUNK_RNG) != 0) {
        dtlv_writer_dispose(&writer);
        return fail("failed to write required chunks");
    }
    if (dtlv_writer_begin_chunk(&writer, unknown_type, unknown_version, unknown_flags) != 0) {
        dtlv_writer_dispose(&writer);
        return fail("failed to write unknown chunk header");
    }
    if (dtlv_writer_write(&writer, unknown_payload, (u32)sizeof(unknown_payload)) != 0) {
        dtlv_writer_dispose(&writer);
        return fail("failed to write unknown chunk payload");
    }
    if (dtlv_writer_end_chunk(&writer) != 0) {
        dtlv_writer_dispose(&writer);
        return fail("failed to end unknown chunk");
    }
    if (write_empty_chunk(&writer, DOM_UNIVERSE_CHUNK_FORN) != 0) {
        dtlv_writer_dispose(&writer);
        return fail("failed to write foreign chunk");
    }
    if (dtlv_writer_finalize(&writer) != 0) {
        dtlv_writer_dispose(&writer);
        return fail("dtlv_writer_finalize failed");
    }
    dtlv_writer_dispose(&writer);

    bundle = dom_universe_bundle_create();
    if (!bundle) {
        return fail("bundle_create failed");
    }
    if (dom_universe_bundle_read_file(path_in, &id, bundle) != DOM_UNIVERSE_BUNDLE_OK) {
        dom_universe_bundle_destroy(bundle);
        return fail("bundle_read_file failed");
    }
    if (dom_universe_bundle_write_file(path_out, bundle) != DOM_UNIVERSE_BUNDLE_OK) {
        dom_universe_bundle_destroy(bundle);
        return fail("bundle_write_file failed");
    }

    dtlv_reader_init(&reader);
    if (dtlv_reader_open_file(&reader, path_out) != 0) {
        dtlv_reader_dispose(&reader);
        dom_universe_bundle_destroy(bundle);
        return fail("dtlv_reader_open_file failed");
    }
    {
        const dtlv_dir_entry *entry = dtlv_reader_find_first(&reader,
                                                             DOM_UNIVERSE_CHUNK_FORN,
                                                             1u);
        unsigned char *bytes = 0;
        u32 size = 0u;
        u32 offset = 0u;
        u32 tag = 0u;
        const unsigned char *pl = 0;
        u32 pl_len = 0u;
        int rc;

        if (!entry) {
            dtlv_reader_dispose(&reader);
            dom_universe_bundle_destroy(bundle);
            return fail("foreign chunk not found");
        }
        if (dtlv_reader_read_chunk_alloc(&reader, entry, &bytes, &size) != 0) {
            dtlv_reader_dispose(&reader);
            dom_universe_bundle_destroy(bundle);
            return fail("foreign chunk read failed");
        }
        while ((rc = dtlv_tlv_next(bytes, size, &offset, &tag, &pl, &pl_len)) == 0) {
            if (tag != 0x0001u || !pl || pl_len < 16u) {
                continue;
            }
            {
                u32 type_id = dtlv_le_read_u32(pl + 0);
                u16 version = dtlv_le_read_u16(pl + 4);
                u16 flags = dtlv_le_read_u16(pl + 6);
                u64 size64 = dtlv_le_read_u64(pl + 8);
                u32 payload_size = (size64 > 0xffffffffull) ? 0xffffffffu : (u32)size64;
                if (pl_len != 16u + payload_size) {
                    std::free(bytes);
                    dtlv_reader_dispose(&reader);
                    dom_universe_bundle_destroy(bundle);
                    return fail("foreign record size mismatch");
                }
                if (type_id == unknown_type) {
                    if (version != unknown_version || flags != unknown_flags) {
                        std::free(bytes);
                        dtlv_reader_dispose(&reader);
                        dom_universe_bundle_destroy(bundle);
                        return fail("foreign record metadata mismatch");
                    }
                    if (payload_size != (u32)sizeof(unknown_payload) ||
                        std::memcmp(pl + 16, unknown_payload, sizeof(unknown_payload)) != 0) {
                        std::free(bytes);
                        dtlv_reader_dispose(&reader);
                        dom_universe_bundle_destroy(bundle);
                        return fail("foreign payload mismatch");
                    }
                    found = 1;
                }
            }
        }
        std::free(bytes);
        if (rc < 0) {
            dtlv_reader_dispose(&reader);
            dom_universe_bundle_destroy(bundle);
            return fail("foreign chunk TLV parse failed");
        }
    }

    dtlv_reader_dispose(&reader);
    dom_universe_bundle_destroy(bundle);
    remove_if_exists(path_in);
    remove_if_exists(path_out);
    if (!found) {
        return fail("foreign record not preserved");
    }
    return 0;
}

static int test_bundle_hash_stable(void) {
    char path_a[L_tmpnam];
    char path_b[L_tmpnam];
    dom_universe_bundle *bundle = 0;
    dom_universe_bundle *bundle_in = 0;
    dom_universe_bundle_identity id;
    u64 hash_a = 0ull;
    u64 hash_b = 0ull;

    if (!make_temp_path(path_a, sizeof(path_a)) ||
        !make_temp_path(path_b, sizeof(path_b))) {
        return fail("temp path allocation failed");
    }
    remove_if_exists(path_a);
    remove_if_exists(path_b);

    std::memset(&id, 0, sizeof(id));
    id.universe_id = "universe_hash";
    id.universe_id_len = (u32)std::strlen(id.universe_id);
    id.instance_id = "instance_hash";
    id.instance_id_len = (u32)std::strlen(id.instance_id);
    id.content_graph_hash = 0x0000000000000001ull;
    id.sim_flags_hash = 0x0000000000000002ull;
    id.ups = 60u;
    id.tick_index = 0ull;
    id.feature_epoch = 1u;

    bundle = dom_universe_bundle_create();
    if (!bundle) {
        return fail("bundle_create failed");
    }
    if (dom_universe_bundle_set_identity(bundle, &id) != DOM_UNIVERSE_BUNDLE_OK) {
        dom_universe_bundle_destroy(bundle);
        return fail("bundle_set_identity failed");
    }
    if (dom_universe_bundle_write_file(path_a, bundle) != DOM_UNIVERSE_BUNDLE_OK) {
        dom_universe_bundle_destroy(bundle);
        return fail("bundle_write_file failed");
    }
    if (hash_file(path_a, &hash_a) != 0) {
        dom_universe_bundle_destroy(bundle);
        return fail("hash_file failed");
    }

    bundle_in = dom_universe_bundle_create();
    if (!bundle_in) {
        dom_universe_bundle_destroy(bundle);
        return fail("bundle_create read failed");
    }
    if (dom_universe_bundle_read_file(path_a, &id, bundle_in) != DOM_UNIVERSE_BUNDLE_OK) {
        dom_universe_bundle_destroy(bundle_in);
        dom_universe_bundle_destroy(bundle);
        return fail("bundle_read_file failed");
    }
    if (dom_universe_bundle_write_file(path_b, bundle_in) != DOM_UNIVERSE_BUNDLE_OK) {
        dom_universe_bundle_destroy(bundle_in);
        dom_universe_bundle_destroy(bundle);
        return fail("bundle_write_file repeat failed");
    }
    if (hash_file(path_b, &hash_b) != 0) {
        dom_universe_bundle_destroy(bundle_in);
        dom_universe_bundle_destroy(bundle);
        return fail("hash_file repeat failed");
    }

    dom_universe_bundle_destroy(bundle_in);
    dom_universe_bundle_destroy(bundle);
    remove_if_exists(path_a);
    remove_if_exists(path_b);

    if (hash_a != hash_b) {
        return fail("bundle hash mismatch");
    }
    return 0;
}

static int test_bundle_macro_roundtrip(void) {
    char path[L_tmpnam];
    dom_universe_bundle *bundle = 0;
    dom_universe_bundle *bundle_in = 0;
    dom_universe_bundle_identity id;
    std::vector<unsigned char> meco_payload;
    std::vector<unsigned char> mevt_payload;
    const unsigned char *payload = 0;
    u32 payload_size = 0u;
    u16 version = 0u;
    u64 meco_hash = 0ull;
    u64 mevt_hash = 0ull;

    if (!make_temp_path(path, sizeof(path))) {
        return fail("temp path allocation failed");
    }
    remove_if_exists(path);

    meco_payload.push_back(0x11u);
    meco_payload.push_back(0x22u);
    meco_payload.push_back(0x33u);
    mevt_payload.push_back(0x44u);
    mevt_payload.push_back(0x55u);

    if (hash_payload(meco_payload, &meco_hash) != 0 ||
        hash_payload(mevt_payload, &mevt_hash) != 0) {
        return fail("macro payload hash failed");
    }

    std::memset(&id, 0, sizeof(id));
    id.universe_id = "universe_macro";
    id.universe_id_len = (u32)std::strlen(id.universe_id);
    id.instance_id = "instance_macro";
    id.instance_id_len = (u32)std::strlen(id.instance_id);
    id.content_graph_hash = 0x0102030405060708ull;
    id.sim_flags_hash = 0x1112131415161718ull;
    id.macro_economy_hash = meco_hash;
    id.macro_events_hash = mevt_hash;
    id.ups = 60u;
    id.tick_index = 42ull;
    id.feature_epoch = 1u;

    bundle = dom_universe_bundle_create();
    if (!bundle) {
        return fail("bundle_create failed");
    }
    if (dom_universe_bundle_set_identity(bundle, &id) != DOM_UNIVERSE_BUNDLE_OK) {
        dom_universe_bundle_destroy(bundle);
        return fail("bundle_set_identity failed");
    }
    if (dom_universe_bundle_set_chunk(bundle,
                                      DOM_UNIVERSE_CHUNK_MECO,
                                      1u,
                                      meco_payload.empty() ? 0 : &meco_payload[0],
                                      (u32)meco_payload.size()) != DOM_UNIVERSE_BUNDLE_OK) {
        dom_universe_bundle_destroy(bundle);
        return fail("bundle_set_chunk MECO failed");
    }
    if (dom_universe_bundle_set_chunk(bundle,
                                      DOM_UNIVERSE_CHUNK_MEVT,
                                      1u,
                                      mevt_payload.empty() ? 0 : &mevt_payload[0],
                                      (u32)mevt_payload.size()) != DOM_UNIVERSE_BUNDLE_OK) {
        dom_universe_bundle_destroy(bundle);
        return fail("bundle_set_chunk MEVT failed");
    }
    if (dom_universe_bundle_write_file(path, bundle) != DOM_UNIVERSE_BUNDLE_OK) {
        dom_universe_bundle_destroy(bundle);
        return fail("bundle_write_file failed");
    }

    bundle_in = dom_universe_bundle_create();
    if (!bundle_in) {
        dom_universe_bundle_destroy(bundle);
        return fail("bundle_create read failed");
    }
    if (dom_universe_bundle_read_file(path, &id, bundle_in) != DOM_UNIVERSE_BUNDLE_OK) {
        dom_universe_bundle_destroy(bundle_in);
        dom_universe_bundle_destroy(bundle);
        return fail("bundle_read_file failed");
    }
    if (dom_universe_bundle_get_chunk(bundle_in,
                                      DOM_UNIVERSE_CHUNK_MECO,
                                      &payload,
                                      &payload_size,
                                      &version) != DOM_UNIVERSE_BUNDLE_OK) {
        dom_universe_bundle_destroy(bundle_in);
        dom_universe_bundle_destroy(bundle);
        return fail("bundle_get_chunk MECO failed");
    }
    if (version != 1u || payload_size != meco_payload.size() ||
        (payload_size > 0u && std::memcmp(payload, &meco_payload[0], payload_size) != 0)) {
        dom_universe_bundle_destroy(bundle_in);
        dom_universe_bundle_destroy(bundle);
        return fail("macro economy payload mismatch");
    }
    if (dom_universe_bundle_get_chunk(bundle_in,
                                      DOM_UNIVERSE_CHUNK_MEVT,
                                      &payload,
                                      &payload_size,
                                      &version) != DOM_UNIVERSE_BUNDLE_OK) {
        dom_universe_bundle_destroy(bundle_in);
        dom_universe_bundle_destroy(bundle);
        return fail("bundle_get_chunk MEVT failed");
    }
    if (version != 1u || payload_size != mevt_payload.size() ||
        (payload_size > 0u && std::memcmp(payload, &mevt_payload[0], payload_size) != 0)) {
        dom_universe_bundle_destroy(bundle_in);
        dom_universe_bundle_destroy(bundle);
        return fail("macro events payload mismatch");
    }

    dom_universe_bundle_destroy(bundle_in);
    dom_universe_bundle_destroy(bundle);
    remove_if_exists(path);
    return 0;
}

struct MigrationCounter {
    int calls;
};

static int mock_migration(u64 schema_id, u32 from_version, u32 to_version, void *user) {
    MigrationCounter *counter = (MigrationCounter *)user;
    (void)schema_id;
    (void)from_version;
    (void)to_version;
    if (counter) {
        counter->calls += 1;
    }
    return DOM_SCHEMA_REGISTRY_OK;
}

static int test_migration_path(void) {
    dom_schema_registry registry;
    dom_schema_desc desc;
    dom_migration_desc m1;
    dom_migration_desc m2;
    u32 path[8];
    u32 count = 0u;
    MigrationCounter counter;
    const u64 schema_id = 0x1234567890abcdefull;

    dom_schema_registry_init(&registry);

    desc.schema_id = schema_id;
    desc.current_version = 3u;
    desc.name = "test_schema";
    if (dom_schema_registry_register(&registry, &desc) != DOM_SCHEMA_REGISTRY_OK) {
        dom_schema_registry_dispose(&registry);
        return fail("schema register failed");
    }

    counter.calls = 0;
    m1.schema_id = schema_id;
    m1.from_version = 1u;
    m1.to_version = 2u;
    m1.fn = mock_migration;
    m1.user = &counter;
    if (dom_migration_register(&registry, &m1) != DOM_SCHEMA_REGISTRY_OK) {
        dom_schema_registry_dispose(&registry);
        return fail("migration register 1 failed");
    }
    m2.schema_id = schema_id;
    m2.from_version = 2u;
    m2.to_version = 3u;
    m2.fn = mock_migration;
    m2.user = &counter;
    if (dom_migration_register(&registry, &m2) != DOM_SCHEMA_REGISTRY_OK) {
        dom_schema_registry_dispose(&registry);
        return fail("migration register 2 failed");
    }

    if (dom_migration_find_path(&registry,
                                schema_id,
                                1u,
                                3u,
                                path,
                                (u32)(sizeof(path) / sizeof(path[0])),
                                &count) != DOM_SCHEMA_REGISTRY_OK) {
        dom_schema_registry_dispose(&registry);
        return fail("migration path find failed");
    }
    if (count != 3u || path[0] != 1u || path[1] != 2u || path[2] != 3u) {
        dom_schema_registry_dispose(&registry);
        return fail("migration path mismatch");
    }
    if (dom_migration_apply_chain(&registry,
                                  schema_id,
                                  1u,
                                  3u,
                                  0) != DOM_SCHEMA_REGISTRY_OK) {
        dom_schema_registry_dispose(&registry);
        return fail("migration apply failed");
    }
    if (counter.calls != 2) {
        dom_schema_registry_dispose(&registry);
        return fail("migration call count mismatch");
    }

    dom_schema_registry_dispose(&registry);
    return 0;
}

int main(void) {
    int rc = 0;
    if ((rc = test_bundle_identity_timebase()) != 0) return rc;
    if ((rc = test_bundle_unknown_preservation()) != 0) return rc;
    if ((rc = test_bundle_hash_stable()) != 0) return rc;
    if ((rc = test_bundle_macro_roundtrip()) != 0) return rc;
    if ((rc = test_migration_path()) != 0) return rc;
    std::printf("dominium universe bundle tests passed\n");
    return 0;
}
