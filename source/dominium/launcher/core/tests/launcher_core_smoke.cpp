/*
FILE: source/dominium/launcher/core/tests/launcher_core_smoke.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / tests
RESPONSIBILITY: Smoke tests for launcher core foundation (null/headless).
NOTES: No OS/UI/renderer dependencies beyond standard C/C++ file IO.
*/

#include <cassert>
#include <cstdio>
#include <cstring>
#include <vector>

#include "launcher_core_api.h"

#include "launcher_audit.h"
#include "launcher_instance.h"
#include "launcher_profile.h"
#include "launcher_tlv.h"

static bool read_file_all(const char* path, std::vector<unsigned char>& out) {
    FILE* f;
    long sz;
    size_t got;

    if (!path) {
        return false;
    }
    f = std::fopen(path, "rb");
    if (!f) {
        return false;
    }
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
    out.resize((size_t)sz);
    got = 0u;
    if (sz > 0L) {
        got = std::fread(&out[0], 1u, (size_t)sz, f);
    }
    std::fclose(f);
    return got == (size_t)sz;
}

static void test_instance_creation() {
    dom::launcher_core::LauncherInstanceManifest m = dom::launcher_core::launcher_instance_manifest_make_empty("inst0");
    assert(m.instance_id == "inst0");
    assert(m.known_good == 0u);
}

static void test_manifest_roundtrip_and_hash() {
    dom::launcher_core::LauncherInstanceManifest m = dom::launcher_core::launcher_instance_manifest_make_empty("inst0");
    dom::launcher_core::LauncherPinnedContent pin;
    std::vector<unsigned char> bytes;
    dom::launcher_core::LauncherInstanceManifest m2;
    u64 h1, h2;

    pin.artifact.kind = (u32)dom::launcher_core::LAUNCHER_ARTIFACT_MOD;
    pin.artifact.id = "mod.example";
    pin.artifact.build_id = "1.2.3";
    pin.order_index = 2u;
    pin.artifact.hash_bytes.push_back(0xAAu);
    pin.artifact.hash_bytes.push_back(0xBBu);
    m.pinned_content.push_back(pin);

    assert(dom::launcher_core::launcher_instance_manifest_to_tlv_bytes(m, bytes));
    assert(!bytes.empty());
    assert(dom::launcher_core::launcher_instance_manifest_from_tlv_bytes(&bytes[0], bytes.size(), m2));
    assert(m2.instance_id == "inst0");
    assert(m2.pinned_content.size() == 1u);
    assert(m2.pinned_content[0].artifact.id == "mod.example");

    h1 = dom::launcher_core::launcher_instance_manifest_hash64(m);
    h2 = dom::launcher_core::launcher_instance_manifest_hash64(m);
    assert(h1 != 0ull);
    assert(h1 == h2);
}

static void test_skip_unknown_tlv() {
    dom::launcher_core::LauncherInstanceManifest m = dom::launcher_core::launcher_instance_manifest_make_empty("inst_unknown");
    std::vector<unsigned char> bytes;
    std::vector<unsigned char> mutated;
    dom::launcher_core::LauncherInstanceManifest out;

    assert(dom::launcher_core::launcher_instance_manifest_to_tlv_bytes(m, bytes));
    mutated = bytes;

    /* Append an unknown tag with a small payload; reader must skip it. */
    {
        dom::launcher_core::TlvWriter w;
        std::vector<unsigned char> extra;
        w.add_u32(9999u, 0x12345678u);
        extra = w.bytes();
        mutated.insert(mutated.end(), extra.begin(), extra.end());
    }

    assert(dom::launcher_core::launcher_instance_manifest_from_tlv_bytes(&mutated[0], mutated.size(), out));
    assert(out.instance_id == "inst_unknown");
}

static void test_audit_emission_null_mode() {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    launcher_core_desc_v1 desc;
    launcher_core* core;
    const char* out_path = "launcher_core_smoke_audit.tlv";
    std::vector<unsigned char> bytes;
    dom::launcher_core::LauncherAuditLog audit;

    std::memset(&desc, 0, sizeof(desc));
    desc.struct_size = (u32)sizeof(desc);
    desc.struct_version = LAUNCHER_CORE_DESC_VERSION;
    desc.services = services;
    desc.audit_output_path = out_path;
    desc.selected_profile_id = "null";
    desc.argv = 0;
    desc.argv_count = 0u;

    core = launcher_core_create(&desc);
    assert(core != 0);
    assert(launcher_core_load_null_profile(core) == 0);
    assert(launcher_core_create_empty_instance(core, "inst_smoke") == 0);
    assert(launcher_core_emit_audit(core, 0) == 0);
    launcher_core_destroy(core);

    assert(read_file_all(out_path, bytes));
    assert(!bytes.empty());
    assert(dom::launcher_core::launcher_audit_from_tlv_bytes(&bytes[0], bytes.size(), audit));
    assert(audit.run_id != 0ull);
    assert(audit.selected_profile_id == "null");
    assert(audit.exit_result == 0);

    (void)std::remove(out_path);
}

int main() {
    test_instance_creation();
    test_manifest_roundtrip_and_hash();
    test_skip_unknown_tlv();
    test_audit_emission_null_mode();
    std::printf("launcher_core_smoke: OK\n");
    return 0;
}

