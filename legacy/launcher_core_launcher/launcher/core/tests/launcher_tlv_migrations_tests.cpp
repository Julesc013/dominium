/*
FILE: source/dominium/launcher/core/tests/launcher_tlv_migrations_tests.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / tests
RESPONSIBILITY: TLV schema version guards, migration registry, and skip-unknown forward compatibility tests.
*/

#include <cassert>
#include <vector>

#include "launcher_artifact_store.h"
#include "launcher_audit.h"
#include "launcher_instance.h"
#include "launcher_instance_config.h"
#include "launcher_instance_known_good.h"
#include "launcher_instance_launch_history.h"
#include "launcher_instance_payload_refs.h"
#include "launcher_pack_manifest.h"
#include "launcher_profile.h"
#include "launcher_tlv.h"
#include "launcher_tlv_migrations.h"

namespace {

static bool tlv_has_tag(const std::vector<unsigned char>& bytes, u32 tag) {
    dom::launcher_core::TlvReader r(bytes.empty() ? (const unsigned char*)0 : &bytes[0], bytes.size());
    dom::launcher_core::TlvRecord rec;
    while (r.next(rec)) {
        if (rec.tag == tag) {
            return true;
        }
    }
    return false;
}

static void test_manifest_v1_to_v2_migration_and_registry() {
    using namespace dom::launcher_core;
    TlvWriter root;
    TlvWriter pin_a;
    TlvWriter pin_b;
    std::vector<unsigned char> v1;
    std::vector<unsigned char> migrated;

    std::vector<unsigned char> hash_a(8u, 0x11u);
    std::vector<unsigned char> hash_b(8u, 0x22u);

    /* v1 pinned entry A (order=2) */
    pin_a.add_u32(1u, 4u); /* v1 kind: mod */
    pin_a.add_string(LAUNCHER_INSTANCE_ENTRY_TLV_TAG_ID, "mod.a"); /* tag 2 */
    pin_a.add_string(3u, "build_a"); /* v1 build_id */
    pin_a.add_bytes(LAUNCHER_INSTANCE_ENTRY_TLV_TAG_HASH_BYTES, &hash_a[0], (u32)hash_a.size());
    pin_a.add_u32(5u, 2u); /* v1 order */

    /* v1 pinned entry B (order=1) */
    pin_b.add_u32(1u, 4u); /* v1 kind: mod */
    pin_b.add_string(LAUNCHER_INSTANCE_ENTRY_TLV_TAG_ID, "mod.b"); /* tag 2 */
    pin_b.add_string(3u, "build_b"); /* v1 build_id */
    pin_b.add_bytes(LAUNCHER_INSTANCE_ENTRY_TLV_TAG_HASH_BYTES, &hash_b[0], (u32)hash_b.size());
    pin_b.add_u32(5u, 1u); /* v1 order */

    root.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, 1u);
    root.add_string(LAUNCHER_INSTANCE_TLV_TAG_INSTANCE_ID, "inst_v1");
    root.add_string(LAUNCHER_INSTANCE_TLV_TAG_PIN_ENGINE_BUILD_ID, "eng1");
    root.add_string(LAUNCHER_INSTANCE_TLV_TAG_PIN_GAME_BUILD_ID, "game1");
    root.add_u32(LAUNCHER_INSTANCE_TLV_TAG_KNOWN_GOOD, 1u);
    root.add_container(5u, pin_a.bytes()); /* v1 pinned-content entries */
    root.add_container(5u, pin_b.bytes());
    v1 = root.bytes();

    assert(launcher_tlv_schema_accepts_version(LAUNCHER_TLV_SCHEMA_INSTANCE_MANIFEST, 1u));
    assert(launcher_tlv_schema_accepts_version(LAUNCHER_TLV_SCHEMA_INSTANCE_MANIFEST, LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION));
    assert(!launcher_tlv_schema_accepts_version(LAUNCHER_TLV_SCHEMA_INSTANCE_MANIFEST, LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION + 1u));

    assert(launcher_tlv_schema_migrate_bytes(LAUNCHER_TLV_SCHEMA_INSTANCE_MANIFEST,
                                             1u,
                                             LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION,
                                             &v1[0],
                                             v1.size(),
                                             migrated));
    assert(tlv_has_tag(migrated, LAUNCHER_TLV_TAG_SCHEMA_VERSION));

    {
        LauncherInstanceManifest out;
        assert(launcher_instance_manifest_from_tlv_bytes(&v1[0], v1.size(), out));
        assert(out.schema_version == LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION);
        assert(out.instance_id == "inst_v1");
        assert(out.pinned_engine_build_id == "eng1");
        assert(out.pinned_game_build_id == "game1");
        assert(out.known_good == 1u);
        assert(out.content_entries.size() == 2u);
        /* v1 order sorting should place mod.b first. */
        assert(out.content_entries[0].id == "mod.b");
        assert(out.content_entries[0].version == "build_b");
        assert(out.content_entries[0].type == (u32)LAUNCHER_CONTENT_MOD);
        assert(out.content_entries[0].hash_bytes == hash_b);
        assert(out.content_entries[1].id == "mod.a");
        assert(out.content_entries[1].version == "build_a");
        assert(out.content_entries[1].type == (u32)LAUNCHER_CONTENT_MOD);
        assert(out.content_entries[1].hash_bytes == hash_a);
    }
}

static void test_skip_unknown_preserved_artifact_metadata() {
    using namespace dom::launcher_core;
    LauncherArtifactMetadata meta;
    std::vector<unsigned char> bytes;
    std::vector<unsigned char> mutated;
    std::vector<unsigned char> roundtrip;
    LauncherArtifactMetadata out;

    meta.hash_bytes.assign(32u, 0xABu);
    meta.size_bytes = 1234ull;
    meta.content_type = (u32)LAUNCHER_CONTENT_MOD;
    meta.timestamp_us = 42ull;
    meta.verification_status = (u32)LAUNCHER_ARTIFACT_VERIFY_VERIFIED;
    meta.source = "test";

    assert(launcher_artifact_metadata_to_tlv_bytes(meta, bytes));
    mutated = bytes;

    {
        TlvWriter extra;
        extra.add_u32(9999u, 0x12345678u);
        std::vector<unsigned char> x = extra.bytes();
        mutated.insert(mutated.end(), x.begin(), x.end());
    }

    assert(launcher_artifact_metadata_from_tlv_bytes(&mutated[0], mutated.size(), out));
    assert(launcher_artifact_metadata_to_tlv_bytes(out, roundtrip));
    assert(tlv_has_tag(roundtrip, 9999u));
}

static void test_version_refusal_when_impossible() {
    using namespace dom::launcher_core;
    std::vector<unsigned char> bad;
    {
        TlvWriter w;
        w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, 999u);
        w.add_string(2u, "x");
        bad = w.bytes();
    }

    {
        LauncherAuditLog a;
        assert(!launcher_audit_from_tlv_bytes(&bad[0], bad.size(), a));
    }
    {
        LauncherProfile p;
        assert(!launcher_profile_from_tlv_bytes(&bad[0], bad.size(), p));
    }
    {
        LauncherInstanceKnownGoodPointer kg;
        assert(!launcher_instance_known_good_from_tlv_bytes(&bad[0], bad.size(), kg));
    }
    {
        LauncherInstanceLaunchHistory h;
        assert(!launcher_instance_launch_history_from_tlv_bytes(&bad[0], bad.size(), h));
    }
    {
        LauncherInstancePayloadRefs r;
        assert(!launcher_instance_payload_refs_from_tlv_bytes(&bad[0], bad.size(), r));
    }
    {
        LauncherInstanceConfig cfg;
        assert(!launcher_instance_config_from_tlv_bytes(&bad[0], bad.size(), cfg));
    }
    {
        LauncherArtifactMetadata m;
        assert(!launcher_artifact_metadata_from_tlv_bytes(&bad[0], bad.size(), m));
    }
    {
        LauncherPackManifest pm;
        assert(!launcher_pack_manifest_from_tlv_bytes(&bad[0], bad.size(), pm));
    }
    {
        LauncherInstanceManifest im;
        assert(!launcher_instance_manifest_from_tlv_bytes(&bad[0], bad.size(), im));
    }
}

} /* namespace */

int main() {
    test_manifest_v1_to_v2_migration_and_registry();
    test_skip_unknown_preserved_artifact_metadata();
    test_version_refusal_when_impossible();
    return 0;
}

