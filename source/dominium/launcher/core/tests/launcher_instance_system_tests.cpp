/*
FILE: source/dominium/launcher/core/tests/launcher_instance_system_tests.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / tests
RESPONSIBILITY: Instance system tests (isolated roots, manifest reproducibility, cloning/templates, import/export, deterministic hashing).
NOTES: Runs under null services; no UI/gfx dependencies.
*/

#include <cassert>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "launcher_audit.h"
#include "launcher_core_api.h"
#include "launcher_instance.h"
#include "launcher_instance_ops.h"
#include "launcher_tlv.h"

namespace {

static void u64_to_hex16(u64 v, char out_hex[17]) {
    static const char* hex = "0123456789abcdef";
    int i;
    for (i = 0; i < 16; ++i) {
        unsigned shift = (unsigned)((15 - i) * 4);
        unsigned nib = (unsigned)((v >> shift) & (u64)0xFu);
        out_hex[i] = hex[nib & 0xFu];
    }
    out_hex[16] = '\0';
}

static std::string normalize_seps(const std::string& in) {
    std::string out = in;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        if (out[i] == '\\') out[i] = '/';
    }
    return out;
}

static bool is_sep(char c) {
    return c == '/' || c == '\\';
}

static std::string path_join(const std::string& a, const std::string& b) {
    std::string aa = normalize_seps(a);
    std::string bb = normalize_seps(b);
    if (aa.empty()) return bb;
    if (bb.empty()) return aa;
    if (is_sep(aa[aa.size() - 1u])) return aa + bb;
    return aa + "/" + bb;
}

static bool file_exists(const std::string& path) {
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) return false;
    std::fclose(f);
    return true;
}

static bool write_file_all(const std::string& path, const std::vector<unsigned char>& bytes) {
    FILE* f = std::fopen(path.c_str(), "wb");
    size_t wrote = 0u;
    if (!f) return false;
    if (!bytes.empty()) {
        wrote = std::fwrite(&bytes[0], 1u, bytes.size(), f);
    }
    std::fclose(f);
    return wrote == bytes.size();
}

static bool read_file_all(const std::string& path, std::vector<unsigned char>& out_bytes) {
    FILE* f;
    long sz;
    size_t got;
    out_bytes.clear();
    f = std::fopen(path.c_str(), "rb");
    if (!f) return false;
    if (std::fseek(f, 0L, SEEK_END) != 0) {
        std::fclose(f);
        return false;
    }
    sz = std::ftell(f);
    if (sz < 0L) {
        std::fclose(f);
        return false;
    }
    if (std::fseek(f, 0L, SEEK_SET) != 0) {
        std::fclose(f);
        return false;
    }
    out_bytes.resize((size_t)sz);
    got = 0u;
    if (sz > 0L) {
        got = std::fread(&out_bytes[0], 1u, (size_t)sz, f);
    }
    std::fclose(f);
    return got == (size_t)sz;
}

#if defined(_WIN32) || defined(_WIN64)
extern "C" int _rmdir(const char* path);
#else
extern "C" int rmdir(const char* path);
#endif

static void remove_file_best_effort(const std::string& path) {
    (void)std::remove(path.c_str());
}

static void rmdir_best_effort(const std::string& path) {
#if defined(_WIN32) || defined(_WIN64)
    (void)_rmdir(path.c_str());
#else
    (void)rmdir(path.c_str());
#endif
}

static std::string bytes_to_hex_lower(const std::vector<unsigned char>& bytes) {
    static const char* hex = "0123456789abcdef";
    std::string out;
    size_t i;
    out.reserve(bytes.size() * 2u);
    for (i = 0u; i < bytes.size(); ++i) {
        unsigned v = (unsigned)bytes[i];
        out.push_back(hex[(v >> 4u) & 0xFu]);
        out.push_back(hex[v & 0xFu]);
    }
    return out;
}

static std::string make_temp_root(const launcher_services_api_v1* services, const char* prefix) {
    void* iface = 0;
    const launcher_time_api_v1* time = 0;
    char hex[17];
    u64 stamp = 0ull;
    if (services && services->query_interface && services->query_interface(LAUNCHER_IID_TIME_V1, &iface) == 0) {
        time = (const launcher_time_api_v1*)iface;
    }
    if (time && time->now_us) {
        stamp = time->now_us();
    }
    u64_to_hex16(stamp, hex);
    return std::string(prefix) + "_" + std::string(hex);
}

static bool audit_find_kv_hex16(const dom::launcher_core::LauncherAuditLog& audit,
                                const std::string& key,
                                std::string& out_hex16) {
    const std::string needle = key + "=0x";
    size_t i;
    for (i = 0u; i < audit.reasons.size(); ++i) {
        const std::string& s = audit.reasons[i];
        size_t pos = s.find(needle);
        if (pos == std::string::npos) continue;
        pos += needle.size();
        if (pos + 16u > s.size()) continue;
        out_hex16 = s.substr(pos, 16u);
        return true;
    }
    return false;
}

static void rm_instance_tree_at(const std::string& instance_root,
                                bool remove_manifest,
                                const std::vector<std::string>& content_payload_hexes,
                                const std::vector<std::string>& mods_payload_hexes,
                                const std::vector<std::string>& previous_subdirs) {
    size_t i;
    std::string manifest_path = path_join(instance_root, "manifest.tlv");
    std::string config_root = path_join(instance_root, "config");
    std::string config_path = path_join(config_root, "config.tlv");
    std::string saves_root = path_join(instance_root, "saves");
    std::string mods_root = path_join(instance_root, "mods");
    std::string content_root = path_join(instance_root, "content");
    std::string cache_root = path_join(instance_root, "cache");
    std::string logs_root = path_join(instance_root, "logs");
    std::string staging_root = path_join(instance_root, "staging");
    std::string staging_manifest = path_join(staging_root, "manifest.tlv");
    std::string previous_root = path_join(instance_root, "previous");

    if (remove_manifest) {
        remove_file_best_effort(manifest_path);
    }
    remove_file_best_effort(staging_manifest);
    remove_file_best_effort(config_path);

    for (i = 0u; i < content_payload_hexes.size(); ++i) {
        remove_file_best_effort(path_join(content_root, content_payload_hexes[i] + ".bin"));
    }
    for (i = 0u; i < mods_payload_hexes.size(); ++i) {
        remove_file_best_effort(path_join(mods_root, mods_payload_hexes[i] + ".bin"));
    }

    for (i = 0u; i < previous_subdirs.size(); ++i) {
        std::string sub = path_join(previous_root, previous_subdirs[i]);
        rm_instance_tree_at(sub, true, content_payload_hexes, mods_payload_hexes, std::vector<std::string>());
        rmdir_best_effort(sub);
    }

    rmdir_best_effort(staging_root);
    rmdir_best_effort(logs_root);
    rmdir_best_effort(cache_root);
    rmdir_best_effort(content_root);
    rmdir_best_effort(mods_root);
    rmdir_best_effort(saves_root);
    rmdir_best_effort(config_root);
    rmdir_best_effort(previous_root);
    rmdir_best_effort(instance_root);
}

static void rm_state_root_best_effort(const std::string& state_root) {
    std::string instances_root = path_join(state_root, "instances");
    rmdir_best_effort(instances_root);
    rmdir_best_effort(state_root);
}

static void test_manifest_roundtrip_and_hash() {
    dom::launcher_core::LauncherInstanceManifest m = dom::launcher_core::launcher_instance_manifest_make_empty("inst0");
    dom::launcher_core::LauncherContentEntry a;
    dom::launcher_core::LauncherContentEntry b;
    std::vector<unsigned char> bytes;
    dom::launcher_core::LauncherInstanceManifest out;

    m.creation_timestamp_us = 123ull;
    m.pinned_engine_build_id = "engine.1";
    m.pinned_game_build_id = "game.2";
    m.known_good = 1u;
    m.last_verified_timestamp_us = 456ull;

    a.type = (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK;
    a.id = "pack.a";
    a.version = "1.0.0";
    a.enabled = 1u;
    a.update_policy = (u32)dom::launcher_core::LAUNCHER_UPDATE_PROMPT;
    a.hash_bytes.assign(8u, 0x11u);

    b.type = (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD;
    b.id = "mod.b";
    b.version = "2.0.0";
    b.enabled = 0u;
    b.update_policy = (u32)dom::launcher_core::LAUNCHER_UPDATE_NEVER;
    b.hash_bytes.assign(8u, 0x22u);

    m.content_entries.push_back(a);
    m.content_entries.push_back(b);

    assert(dom::launcher_core::launcher_instance_manifest_to_tlv_bytes(m, bytes));
    assert(!bytes.empty());
    assert(dom::launcher_core::launcher_instance_manifest_from_tlv_bytes(&bytes[0], bytes.size(), out));
    assert(out.instance_id == "inst0");
    assert(out.creation_timestamp_us == 123ull);
    assert(out.pinned_engine_build_id == "engine.1");
    assert(out.pinned_game_build_id == "game.2");
    assert(out.known_good == 1u);
    assert(out.last_verified_timestamp_us == 456ull);
    assert(out.content_entries.size() == 2u);
    assert(out.content_entries[0].id == "pack.a");
    assert(out.content_entries[1].id == "mod.b");

    {
        u64 h1 = dom::launcher_core::launcher_instance_manifest_hash64(m);
        u64 h2 = dom::launcher_core::launcher_instance_manifest_hash64(m);
        assert(h1 != 0ull);
        assert(h1 == h2);
    }
}

static void test_hash_order_sensitivity() {
    dom::launcher_core::LauncherInstanceManifest m1 = dom::launcher_core::launcher_instance_manifest_make_empty("inst_order");
    dom::launcher_core::LauncherInstanceManifest m2 = dom::launcher_core::launcher_instance_manifest_make_empty("inst_order");
    dom::launcher_core::LauncherContentEntry a;
    dom::launcher_core::LauncherContentEntry b;
    u64 h1, h2;

    a.type = (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK;
    a.id = "a";
    a.version = "1";
    a.hash_bytes.assign(8u, 0x01u);

    b.type = (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK;
    b.id = "b";
    b.version = "1";
    b.hash_bytes.assign(8u, 0x02u);

    m1.content_entries.push_back(a);
    m1.content_entries.push_back(b);

    m2.content_entries.push_back(b);
    m2.content_entries.push_back(a);

    h1 = dom::launcher_core::launcher_instance_manifest_hash64(m1);
    h2 = dom::launcher_core::launcher_instance_manifest_hash64(m2);
    assert(h1 != 0ull);
    assert(h2 != 0ull);
    assert(h1 != h2);
}

static void test_skip_unknown_preserved() {
    /* Root unknown record preserved on round-trip. */
    dom::launcher_core::LauncherInstanceManifest m = dom::launcher_core::launcher_instance_manifest_make_empty("inst_unknown");
    std::vector<unsigned char> bytes;
    std::vector<unsigned char> mutated;
    std::vector<unsigned char> roundtrip;
    dom::launcher_core::LauncherInstanceManifest out;

    assert(dom::launcher_core::launcher_instance_manifest_to_tlv_bytes(m, bytes));
    mutated = bytes;

    {
        dom::launcher_core::TlvWriter w;
        std::vector<unsigned char> extra;
        w.add_u32(9999u, 0x12345678u);
        extra = w.bytes();
        mutated.insert(mutated.end(), extra.begin(), extra.end());
    }

    assert(dom::launcher_core::launcher_instance_manifest_from_tlv_bytes(&mutated[0], mutated.size(), out));
    assert(out.instance_id == "inst_unknown");
    assert(dom::launcher_core::launcher_instance_manifest_to_tlv_bytes(out, roundtrip));

    {
        bool found = false;
        dom::launcher_core::TlvReader r(&roundtrip[0], roundtrip.size());
        dom::launcher_core::TlvRecord rec;
        while (r.next(rec)) {
            if (rec.tag == 9999u) {
                found = true;
                break;
            }
        }
        assert(found);
    }

    /* Unknown record inside a content entry is preserved. */
    {
        dom::launcher_core::TlvWriter entry;
        dom::launcher_core::TlvWriter root;
        std::vector<unsigned char> b2;
        dom::launcher_core::LauncherInstanceManifest parsed;
        std::vector<unsigned char> rt;
        bool found = false;

        entry.add_u32(dom::launcher_core::LAUNCHER_INSTANCE_ENTRY_TLV_TAG_TYPE, (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD);
        entry.add_string(dom::launcher_core::LAUNCHER_INSTANCE_ENTRY_TLV_TAG_ID, "mod.x");
        entry.add_string(dom::launcher_core::LAUNCHER_INSTANCE_ENTRY_TLV_TAG_VERSION, "1");
        entry.add_bytes(dom::launcher_core::LAUNCHER_INSTANCE_ENTRY_TLV_TAG_HASH_BYTES, (const unsigned char*)0, 0u);
        entry.add_u32(dom::launcher_core::LAUNCHER_INSTANCE_ENTRY_TLV_TAG_ENABLED, 1u);
        entry.add_u32(dom::launcher_core::LAUNCHER_INSTANCE_ENTRY_TLV_TAG_UPDATE_POLICY, (u32)dom::launcher_core::LAUNCHER_UPDATE_PROMPT);
        entry.add_u32(8888u, 0xAABBCCDDu); /* unknown */

        root.add_u32(dom::launcher_core::LAUNCHER_TLV_TAG_SCHEMA_VERSION, dom::launcher_core::LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION);
        root.add_string(dom::launcher_core::LAUNCHER_INSTANCE_TLV_TAG_INSTANCE_ID, "inst_entry_unknown");
        root.add_u64(dom::launcher_core::LAUNCHER_INSTANCE_TLV_TAG_CREATION_TIMESTAMP_US, 1ull);
        root.add_container(dom::launcher_core::LAUNCHER_INSTANCE_TLV_TAG_CONTENT_ENTRY, entry.bytes());
        b2 = root.bytes();

        assert(dom::launcher_core::launcher_instance_manifest_from_tlv_bytes(&b2[0], b2.size(), parsed));
        assert(parsed.content_entries.size() == 1u);
        assert(!parsed.content_entries[0].unknown_fields.empty());
        assert(parsed.content_entries[0].unknown_fields[0].tag == 8888u);

        assert(dom::launcher_core::launcher_instance_manifest_to_tlv_bytes(parsed, rt));
        {
            dom::launcher_core::TlvReader rr(&rt[0], rt.size());
            dom::launcher_core::TlvRecord rec;
            while (rr.next(rec)) {
                if (rec.tag == dom::launcher_core::LAUNCHER_INSTANCE_TLV_TAG_CONTENT_ENTRY) {
                    dom::launcher_core::TlvReader er(rec.payload, (size_t)rec.len);
                    dom::launcher_core::TlvRecord e;
                    while (er.next(e)) {
                        if (e.tag == 8888u) {
                            found = true;
                            break;
                        }
                    }
                }
            }
        }
        assert(found);
    }
}

static void test_instance_create_delete_clone_template_import_export() {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    dom::launcher_core::LauncherAuditLog audit;
    dom::launcher_core::LauncherInstanceManifest created;
    dom::launcher_core::LauncherInstanceManifest loaded;

    const std::string state_root = make_temp_root(services, "launcher_instance_tests_state");
    std::string payload_hex;

    /* Create */
    {
        dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty("inst_create");
        desired.pinned_engine_build_id = "engine.pin";
        desired.pinned_game_build_id = "game.pin";
        assert(dom::launcher_core::launcher_instance_create_instance(services, desired, state_root, created, &audit));
        assert(dom::launcher_core::launcher_instance_load_manifest(services, "inst_create", state_root, loaded));
        assert(loaded.instance_id == "inst_create");
        assert(file_exists(path_join(path_join(state_root, "instances/inst_create"), "manifest.tlv")));
        assert(file_exists(path_join(path_join(state_root, "instances/inst_create/config"), "config.tlv")));
    }

    /* Clone + template */
    {
        dom::launcher_core::LauncherAuditLog a2;
        dom::launcher_core::LauncherInstanceManifest src = loaded;
        dom::launcher_core::LauncherInstancePaths src_paths = dom::launcher_core::launcher_instance_paths_make(state_root, "inst_create");

        /* Write a non-empty TLV config so clone/template can validate byte-for-byte copy. */
        {
            dom::launcher_core::TlvWriter w;
            std::vector<unsigned char> cfg;
            w.add_u32(dom::launcher_core::LAUNCHER_TLV_TAG_SCHEMA_VERSION, 1u);
            w.add_u32(777u, 0xDEADBEEFu);
            cfg = w.bytes();
            assert(write_file_all(src_paths.config_file_path, cfg));
        }

        {
            dom::launcher_core::LauncherInstanceManifest clone_m;
            assert(dom::launcher_core::launcher_instance_clone_instance(services, "inst_create", "inst_clone", state_root, clone_m, &a2));
            assert(dom::launcher_core::launcher_instance_load_manifest(services, "inst_clone", state_root, loaded));
            assert(loaded.instance_id == "inst_clone");
            assert(loaded.provenance_source_instance_id == "inst_create");
            assert(loaded.pinned_engine_build_id == src.pinned_engine_build_id);

            /* Config copied */
            {
                std::vector<unsigned char> a_bytes;
                std::vector<unsigned char> b_bytes;
                dom::launcher_core::LauncherInstancePaths clone_paths = dom::launcher_core::launcher_instance_paths_make(state_root, "inst_clone");
                assert(read_file_all(src_paths.config_file_path, a_bytes));
                assert(read_file_all(clone_paths.config_file_path, b_bytes));
                assert(a_bytes == b_bytes);
            }
        }

        {
            dom::launcher_core::LauncherInstanceManifest tmpl_m;
            assert(dom::launcher_core::launcher_instance_template_instance(services, "inst_create", "inst_tmpl", state_root, tmpl_m, &a2));
            assert(dom::launcher_core::launcher_instance_load_manifest(services, "inst_tmpl", state_root, loaded));
            assert(loaded.instance_id == "inst_tmpl");
            assert(loaded.provenance_source_instance_id == "inst_create");
            assert(loaded.pinned_engine_build_id.empty());
            assert(loaded.pinned_game_build_id.empty());

            /* Config copied */
            {
                std::vector<unsigned char> a_bytes;
                std::vector<unsigned char> b_bytes;
                dom::launcher_core::LauncherInstancePaths tmpl_paths = dom::launcher_core::launcher_instance_paths_make(state_root, "inst_tmpl");
                assert(read_file_all(src_paths.config_file_path, a_bytes));
                assert(read_file_all(tmpl_paths.config_file_path, b_bytes));
                assert(a_bytes == b_bytes);
            }
        }
    }

    /* Export/import (full bundle + integrity) */
    {
        dom::launcher_core::LauncherAuditLog a3;
        dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty("inst_export_src");
        std::vector<unsigned char> payload;
        std::vector<unsigned char> hb;
        unsigned char le[8];
        dom::launcher_core::LauncherContentEntry ent;
        dom::launcher_core::LauncherInstanceManifest exp_created;
        dom::launcher_core::LauncherInstanceManifest imp_created;

        payload.push_back(0x10u);
        payload.push_back(0x20u);
        payload.push_back(0x30u);

        {
            u64 fnv = dom::launcher_core::tlv_fnv1a64(&payload[0], payload.size());
            dom::launcher_core::tlv_write_u64_le(le, fnv);
            hb.assign(le, le + 8u);
        }

        ent.type = (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK;
        ent.id = "pack.payload";
        ent.version = "1";
        ent.enabled = 1u;
        ent.update_policy = (u32)dom::launcher_core::LAUNCHER_UPDATE_PROMPT;
        ent.hash_bytes = hb;
        desired.content_entries.push_back(ent);

        assert(dom::launcher_core::launcher_instance_create_instance(services, desired, state_root, exp_created, &a3));

        /* Create payload file in instance root for export. */
        {
            dom::launcher_core::LauncherInstancePaths p = dom::launcher_core::launcher_instance_paths_make(state_root, "inst_export_src");
            payload_hex = bytes_to_hex_lower(hb);
            assert(write_file_all(path_join(p.content_root, payload_hex + ".bin"), payload));
        }

        {
            const std::string bundle_root = path_join(state_root, "bundle_full");
            assert(dom::launcher_core::launcher_instance_export_instance(services, "inst_export_src", bundle_root, state_root,
                                                                        (u32)dom::launcher_core::LAUNCHER_INSTANCE_EXPORT_FULL_BUNDLE, &a3));

            /* Import (safe_mode=0) */
            assert(dom::launcher_core::launcher_instance_import_instance(services, bundle_root, "inst_import_ok", state_root,
                                                                        (u32)dom::launcher_core::LAUNCHER_INSTANCE_IMPORT_FULL_BUNDLE, 0u,
                                                                        imp_created, &a3));
            assert(dom::launcher_core::launcher_instance_load_manifest(services, "inst_import_ok", state_root, loaded));
            assert(loaded.instance_id == "inst_import_ok");
            assert(loaded.provenance_source_instance_id == "inst_export_src");

            /* Payload copied into imported instance root */
            {
                dom::launcher_core::LauncherInstancePaths ip = dom::launcher_core::launcher_instance_paths_make(state_root, "inst_import_ok");
                std::string hex = bytes_to_hex_lower(hb);
                std::vector<unsigned char> got;
                assert(read_file_all(path_join(ip.content_root, hex + ".bin"), got));
                assert(got == payload);
            }

            /* Corrupt payload and ensure import refuses unless safe_mode=1. */
            {
                std::string payload_path = path_join(path_join(bundle_root, "payloads"), payload_hex + ".bin");
                std::vector<unsigned char> corrupt;
                assert(read_file_all(payload_path, corrupt));
                assert(!corrupt.empty());
                corrupt[0] ^= 0xFFu;
                assert(write_file_all(payload_path, corrupt));
            }
            {
                dom::launcher_core::LauncherInstanceManifest tmp;
                bool ok = dom::launcher_core::launcher_instance_import_instance(services, bundle_root, "inst_import_fail", state_root,
                                                                               (u32)dom::launcher_core::LAUNCHER_INSTANCE_IMPORT_FULL_BUNDLE, 0u,
                                                                               tmp, &a3);
                assert(!ok);
            }
            {
                dom::launcher_core::LauncherInstanceManifest tmp;
                bool ok = dom::launcher_core::launcher_instance_import_instance(services, bundle_root, "inst_import_safe", state_root,
                                                                               (u32)dom::launcher_core::LAUNCHER_INSTANCE_IMPORT_FULL_BUNDLE, 1u,
                                                                               tmp, &a3);
                assert(ok);
            }

            /* Cleanup bundle */
            {
                remove_file_best_effort(path_join(bundle_root, "manifest.tlv"));
                remove_file_best_effort(path_join(path_join(bundle_root, "config"), "config.tlv"));
                remove_file_best_effort(path_join(path_join(bundle_root, "payloads"), payload_hex + ".bin"));
                rmdir_best_effort(path_join(bundle_root, "payloads"));
                rmdir_best_effort(path_join(bundle_root, "config"));
                rmdir_best_effort(bundle_root);
            }
        }
    }

    /* Delete created instance; parse stamp from audit to clean previous/deleted_<stamp>. */
    {
        dom::launcher_core::LauncherAuditLog del_audit;
        std::string stamp_hex;
        assert(dom::launcher_core::launcher_instance_delete_instance(services, "inst_create", state_root, &del_audit));
        assert(audit_find_kv_hex16(del_audit, "stamp_us", stamp_hex));

        /* Cleanup instances */
        {
            std::vector<std::string> none;
            std::vector<std::string> prev;
            prev.push_back(std::string("deleted_") + stamp_hex);
            rm_instance_tree_at(path_join(path_join(state_root, "instances"), "inst_create"), false, none, none, prev);
        }
    }

    /* Cleanup remaining live instances created in this test. */
    {
        std::vector<std::string> none;
        rm_instance_tree_at(path_join(path_join(state_root, "instances"), "inst_clone"), true, none, none, std::vector<std::string>());
        rm_instance_tree_at(path_join(path_join(state_root, "instances"), "inst_tmpl"), true, none, none, std::vector<std::string>());
        {
            std::vector<std::string> payloads;
            if (!payload_hex.empty()) {
                payloads.push_back(payload_hex);
            }
            rm_instance_tree_at(path_join(path_join(state_root, "instances"), "inst_export_src"), true, payloads, std::vector<std::string>(), std::vector<std::string>());
            rm_instance_tree_at(path_join(path_join(state_root, "instances"), "inst_import_ok"), true, payloads, std::vector<std::string>(), std::vector<std::string>());
            rm_instance_tree_at(path_join(path_join(state_root, "instances"), "inst_import_safe"), true, payloads, std::vector<std::string>(), std::vector<std::string>());
        }
    }

    rm_state_root_best_effort(state_root);
}

} /* namespace */

int main() {
    test_manifest_roundtrip_and_hash();
    test_hash_order_sensitivity();
    test_skip_unknown_preserved();
    test_instance_create_delete_clone_template_import_export();
    std::printf("launcher_instance_system_tests: OK\n");
    return 0;
}
