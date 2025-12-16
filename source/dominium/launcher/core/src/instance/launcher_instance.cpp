/*
FILE: source/dominium/launcher/core/src/instance/launcher_instance.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / instance
RESPONSIBILITY: Implements instance manifest (lockfile) TLV persistence + deterministic hashing.
*/

#include "launcher_instance.h"

#include <algorithm>

#include "launcher_tlv.h"

namespace dom {
namespace launcher_core {

namespace {
enum {
    TAG_INSTANCE_ID = 2u,
    TAG_PIN_ENGINE_BUILD_ID = 3u,
    TAG_PIN_GAME_BUILD_ID = 4u,
    TAG_PINNED_CONTENT_ENTRY = 5u,
    TAG_UPDATE_POLICY_FLAGS = 6u,
    TAG_KNOWN_GOOD = 7u
};

enum {
    TAG_ENTRY_KIND = 1u,
    TAG_ENTRY_ID = 2u,
    TAG_ENTRY_BUILD_ID = 3u,
    TAG_ENTRY_HASH_BYTES = 4u,
    TAG_ENTRY_ORDER = 5u
};

static bool pinned_less(const LauncherPinnedContent& a, const LauncherPinnedContent& b) {
    if (a.order_index != b.order_index) return a.order_index < b.order_index;
    if (a.artifact.kind != b.artifact.kind) return a.artifact.kind < b.artifact.kind;
    if (a.artifact.id != b.artifact.id) return a.artifact.id < b.artifact.id;
    if (a.artifact.build_id != b.artifact.build_id) return a.artifact.build_id < b.artifact.build_id;
    if (a.artifact.hash_bytes != b.artifact.hash_bytes) return a.artifact.hash_bytes < b.artifact.hash_bytes;
    return false;
}
}

LauncherPinnedContent::LauncherPinnedContent()
    : artifact(), order_index(0u) {
}

LauncherInstanceManifest::LauncherInstanceManifest()
    : schema_version(LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION),
      instance_id(),
      pinned_engine_build_id(),
      pinned_game_build_id(),
      pinned_content(),
      update_policy_flags(0u),
      known_good(0u) {
}

LauncherInstanceManifest launcher_instance_manifest_make_empty(const std::string& instance_id) {
    LauncherInstanceManifest m;
    m.instance_id = instance_id;
    m.pinned_engine_build_id.clear();
    m.pinned_game_build_id.clear();
    m.pinned_content.clear();
    m.update_policy_flags = 0u;
    m.known_good = 0u;
    return m;
}

LauncherInstanceManifest launcher_instance_manifest_make_null(void) {
    return launcher_instance_manifest_make_empty("null");
}

bool launcher_instance_manifest_to_tlv_bytes(const LauncherInstanceManifest& manifest,
                                             std::vector<unsigned char>& out_bytes) {
    TlvWriter w;
    std::vector<LauncherPinnedContent> pins = manifest.pinned_content;
    size_t i;

    /* Canonicalize ordering deterministically by explicit order_index. */
    std::stable_sort(pins.begin(), pins.end(), pinned_less);

    w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION);
    w.add_string(TAG_INSTANCE_ID, manifest.instance_id);
    w.add_string(TAG_PIN_ENGINE_BUILD_ID, manifest.pinned_engine_build_id);
    w.add_string(TAG_PIN_GAME_BUILD_ID, manifest.pinned_game_build_id);
    w.add_u32(TAG_UPDATE_POLICY_FLAGS, manifest.update_policy_flags);
    w.add_u32(TAG_KNOWN_GOOD, manifest.known_good);

    for (i = 0u; i < pins.size(); ++i) {
        TlvWriter entry;
        entry.add_u32(TAG_ENTRY_KIND, pins[i].artifact.kind);
        entry.add_string(TAG_ENTRY_ID, pins[i].artifact.id);
        entry.add_string(TAG_ENTRY_BUILD_ID, pins[i].artifact.build_id);
        entry.add_u32(TAG_ENTRY_ORDER, pins[i].order_index);
        if (!pins[i].artifact.hash_bytes.empty()) {
            entry.add_bytes(TAG_ENTRY_HASH_BYTES, &pins[i].artifact.hash_bytes[0],
                            (u32)pins[i].artifact.hash_bytes.size());
        } else {
            entry.add_bytes(TAG_ENTRY_HASH_BYTES, (const unsigned char*)0, 0u);
        }
        w.add_container(TAG_PINNED_CONTENT_ENTRY, entry.bytes());
    }

    out_bytes = w.bytes();
    return true;
}

bool launcher_instance_manifest_from_tlv_bytes(const unsigned char* data,
                                               size_t size,
                                               LauncherInstanceManifest& out_manifest) {
    TlvReader r(data, size);
    TlvRecord rec;
    u32 version = 0u;

    out_manifest = LauncherInstanceManifest();
    if (!tlv_read_schema_version_or_default(data, size, version, LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION)) {
        return false;
    }
    out_manifest.schema_version = version;
    if (version != LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION) {
        return launcher_instance_manifest_migrate_tlv(version,
                                                      LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION,
                                                      data,
                                                      size,
                                                      out_manifest);
    }

    while (r.next(rec)) {
        switch (rec.tag) {
        case LAUNCHER_TLV_TAG_SCHEMA_VERSION:
            break;
        case TAG_INSTANCE_ID:
            out_manifest.instance_id = tlv_read_string(rec.payload, rec.len);
            break;
        case TAG_PIN_ENGINE_BUILD_ID:
            out_manifest.pinned_engine_build_id = tlv_read_string(rec.payload, rec.len);
            break;
        case TAG_PIN_GAME_BUILD_ID:
            out_manifest.pinned_game_build_id = tlv_read_string(rec.payload, rec.len);
            break;
        case TAG_UPDATE_POLICY_FLAGS: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                out_manifest.update_policy_flags = v;
            }
            break;
        }
        case TAG_KNOWN_GOOD: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                out_manifest.known_good = v;
            }
            break;
        }
        case TAG_PINNED_CONTENT_ENTRY: {
            LauncherPinnedContent pin;
            TlvReader er(rec.payload, (size_t)rec.len);
            TlvRecord e;
            while (er.next(e)) {
                if (e.tag == TAG_ENTRY_KIND) {
                    u32 v;
                    if (tlv_read_u32_le(e.payload, e.len, v)) {
                        pin.artifact.kind = v;
                    }
                } else if (e.tag == TAG_ENTRY_ID) {
                    pin.artifact.id = tlv_read_string(e.payload, e.len);
                } else if (e.tag == TAG_ENTRY_BUILD_ID) {
                    pin.artifact.build_id = tlv_read_string(e.payload, e.len);
                } else if (e.tag == TAG_ENTRY_HASH_BYTES) {
                    pin.artifact.hash_bytes.clear();
                    if (e.len > 0u && e.payload) {
                        pin.artifact.hash_bytes.assign(e.payload, e.payload + (size_t)e.len);
                    }
                } else if (e.tag == TAG_ENTRY_ORDER) {
                    u32 v;
                    if (tlv_read_u32_le(e.payload, e.len, v)) {
                        pin.order_index = v;
                    }
                } else {
                    /* skip unknown */
                }
            }
            out_manifest.pinned_content.push_back(pin);
            break;
        }
        default:
            /* skip unknown */
            break;
        }
    }

    /* Keep pinned_content as read order; canonical ordering is applied on write/hash. */
    return true;
}

u64 launcher_instance_manifest_hash64(const LauncherInstanceManifest& manifest) {
    std::vector<unsigned char> bytes;
    if (!launcher_instance_manifest_to_tlv_bytes(manifest, bytes)) {
        return 0ull;
    }
    return tlv_fnv1a64(bytes.empty() ? (const unsigned char*)0 : &bytes[0], bytes.size());
}

bool launcher_instance_manifest_migrate_tlv(u32 /*from_version*/,
                                            u32 /*to_version*/,
                                            const unsigned char* /*data*/,
                                            size_t /*size*/,
                                            LauncherInstanceManifest& /*out_manifest*/) {
    /* Defined but not implemented in foundation. */
    return false;
}

} /* namespace launcher_core */
} /* namespace dom */
