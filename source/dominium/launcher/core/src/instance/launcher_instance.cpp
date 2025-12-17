/*
FILE: source/dominium/launcher/core/src/instance/launcher_instance.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / instance
RESPONSIBILITY: Implements instance manifest (lockfile) TLV persistence + deterministic hashing.
*/

#include "launcher_instance.h"

#include "launcher_tlv.h"
#include "launcher_tlv_migrations.h"

namespace dom {
namespace launcher_core {

namespace {
enum {
    TAG_INSTANCE_ID = 2u,
    TAG_PIN_ENGINE_BUILD_ID = 3u,
    TAG_PIN_GAME_BUILD_ID = 4u,
    TAG_KNOWN_GOOD = 7u,
    TAG_CREATION_TIMESTAMP_US = 8u,
    TAG_LAST_VERIFIED_TIMESTAMP_US = 9u,
    TAG_PREVIOUS_MANIFEST_HASH64 = 10u,
    TAG_CONTENT_ENTRY = 11u,
    TAG_PROV_SOURCE_INSTANCE_ID = 12u,
    TAG_PROV_SOURCE_MANIFEST_HASH64 = 13u
};

enum {
    TAG_ENTRY_TYPE = 1u,
    TAG_ENTRY_ID = 2u,
    TAG_ENTRY_VERSION = 3u,
    TAG_ENTRY_HASH_BYTES = 4u,
    TAG_ENTRY_ENABLED = 5u,
    TAG_ENTRY_UPDATE_POLICY = 6u,
    TAG_ENTRY_EXPLICIT_ORDER_OVERRIDE = 7u
};

static void tlv_unknown_capture(std::vector<LauncherTlvUnknownRecord>& dst, const TlvRecord& rec) {
    LauncherTlvUnknownRecord u;
    u.tag = rec.tag;
    u.payload.clear();
    if (rec.len > 0u && rec.payload) {
        u.payload.assign(rec.payload, rec.payload + (size_t)rec.len);
    }
    dst.push_back(u);
}

static void tlv_unknown_emit(TlvWriter& w, const std::vector<LauncherTlvUnknownRecord>& src) {
    size_t i;
    for (i = 0u; i < src.size(); ++i) {
        if (!src[i].payload.empty()) {
            w.add_bytes(src[i].tag, &src[i].payload[0], (u32)src[i].payload.size());
        } else {
            w.add_bytes(src[i].tag, (const unsigned char*)0, 0u);
        }
    }
}

struct V1Pin {
    u32 kind;
    std::string id;
    std::string build_id;
    std::vector<unsigned char> hash_bytes;
    u32 order_index;
    V1Pin() : kind(0u), id(), build_id(), hash_bytes(), order_index(0u) {}
};

static void v1_sort_pins_by_order(std::vector<V1Pin>& pins) {
    /* Stable insertion sort (C++98) to preserve v1 explicit ordering deterministically. */
    size_t i;
    for (i = 1u; i < pins.size(); ++i) {
        V1Pin key = pins[i];
        size_t j = i;
        while (j > 0u && pins[j - 1u].order_index > key.order_index) {
            pins[j] = pins[j - 1u];
            --j;
        }
        pins[j] = key;
    }
}

} /* namespace */

LauncherTlvUnknownRecord::LauncherTlvUnknownRecord()
    : tag(0u), payload() {
}

LauncherContentEntry::LauncherContentEntry()
    : type((u32)LAUNCHER_CONTENT_UNKNOWN),
      id(),
      version(),
      hash_bytes(),
      enabled(1u),
      update_policy((u32)LAUNCHER_UPDATE_PROMPT),
      has_explicit_order_override(0u),
      explicit_order_override(0),
      unknown_fields() {
}

LauncherInstanceManifest::LauncherInstanceManifest()
    : schema_version(LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION),
      instance_id(),
      creation_timestamp_us(0ull),
      pinned_engine_build_id(),
      pinned_game_build_id(),
      content_entries(),
      known_good(0u),
      last_verified_timestamp_us(0ull),
      previous_manifest_hash64(0ull),
      provenance_source_instance_id(),
      provenance_source_manifest_hash64(0ull),
      unknown_fields() {
}

LauncherInstanceManifest launcher_instance_manifest_make_empty(const std::string& instance_id) {
    LauncherInstanceManifest m;
    m.instance_id = instance_id;
    m.creation_timestamp_us = 0ull;
    m.pinned_engine_build_id.clear();
    m.pinned_game_build_id.clear();
    m.content_entries.clear();
    m.known_good = 0u;
    m.last_verified_timestamp_us = 0ull;
    m.previous_manifest_hash64 = 0ull;
    m.provenance_source_instance_id.clear();
    m.provenance_source_manifest_hash64 = 0ull;
    m.unknown_fields.clear();
    return m;
}

LauncherInstanceManifest launcher_instance_manifest_make_null(void) {
    return launcher_instance_manifest_make_empty("null");
}

bool launcher_instance_manifest_to_tlv_bytes(const LauncherInstanceManifest& manifest,
                                             std::vector<unsigned char>& out_bytes) {
    TlvWriter w;
    size_t i;

    w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION);
    w.add_string(TAG_INSTANCE_ID, manifest.instance_id);
    w.add_u64(TAG_CREATION_TIMESTAMP_US, manifest.creation_timestamp_us);
    w.add_string(TAG_PIN_ENGINE_BUILD_ID, manifest.pinned_engine_build_id);
    w.add_string(TAG_PIN_GAME_BUILD_ID, manifest.pinned_game_build_id);
    w.add_u32(TAG_KNOWN_GOOD, manifest.known_good);
    w.add_u64(TAG_LAST_VERIFIED_TIMESTAMP_US, manifest.last_verified_timestamp_us);
    if (manifest.previous_manifest_hash64 != 0ull) {
        w.add_u64(TAG_PREVIOUS_MANIFEST_HASH64, manifest.previous_manifest_hash64);
    }
    if (!manifest.provenance_source_instance_id.empty()) {
        w.add_string(TAG_PROV_SOURCE_INSTANCE_ID, manifest.provenance_source_instance_id);
    }
    if (manifest.provenance_source_manifest_hash64 != 0ull) {
        w.add_u64(TAG_PROV_SOURCE_MANIFEST_HASH64, manifest.provenance_source_manifest_hash64);
    }

    for (i = 0u; i < manifest.content_entries.size(); ++i) {
        TlvWriter entry;
        entry.add_u32(TAG_ENTRY_TYPE, manifest.content_entries[i].type);
        entry.add_string(TAG_ENTRY_ID, manifest.content_entries[i].id);
        entry.add_string(TAG_ENTRY_VERSION, manifest.content_entries[i].version);
        entry.add_u32(TAG_ENTRY_ENABLED, manifest.content_entries[i].enabled ? 1u : 0u);
        entry.add_u32(TAG_ENTRY_UPDATE_POLICY, manifest.content_entries[i].update_policy);
        if (manifest.content_entries[i].has_explicit_order_override) {
            entry.add_i32(TAG_ENTRY_EXPLICIT_ORDER_OVERRIDE, manifest.content_entries[i].explicit_order_override);
        }
        if (!manifest.content_entries[i].hash_bytes.empty()) {
            entry.add_bytes(TAG_ENTRY_HASH_BYTES, &manifest.content_entries[i].hash_bytes[0],
                            (u32)manifest.content_entries[i].hash_bytes.size());
        } else {
            entry.add_bytes(TAG_ENTRY_HASH_BYTES, (const unsigned char*)0, 0u);
        }

        /* Round-trip preserve unknown entry fields. */
        tlv_unknown_emit(entry, manifest.content_entries[i].unknown_fields);

        w.add_container(TAG_CONTENT_ENTRY, entry.bytes());
    }

    /* Round-trip preserve unknown root fields. */
    tlv_unknown_emit(w, manifest.unknown_fields);

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
    if (!tlv_read_schema_version_or_default(data,
                                            size,
                                            version,
                                            launcher_tlv_schema_min_version(LAUNCHER_TLV_SCHEMA_INSTANCE_MANIFEST))) {
        return false;
    }
    if (!launcher_tlv_schema_accepts_version(LAUNCHER_TLV_SCHEMA_INSTANCE_MANIFEST, version)) {
        return false;
    }
    if (version != LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION) {
        return launcher_instance_manifest_migrate_tlv(version,
                                                      LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION,
                                                      data,
                                                      size,
                                                      out_manifest);
    }
    out_manifest.schema_version = LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION;

    while (r.next(rec)) {
        switch (rec.tag) {
        case LAUNCHER_TLV_TAG_SCHEMA_VERSION:
            break;
        case TAG_INSTANCE_ID:
            out_manifest.instance_id = tlv_read_string(rec.payload, rec.len);
            break;
        case TAG_CREATION_TIMESTAMP_US: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                out_manifest.creation_timestamp_us = v;
            }
            break;
        }
        case TAG_PIN_ENGINE_BUILD_ID:
            out_manifest.pinned_engine_build_id = tlv_read_string(rec.payload, rec.len);
            break;
        case TAG_PIN_GAME_BUILD_ID:
            out_manifest.pinned_game_build_id = tlv_read_string(rec.payload, rec.len);
            break;
        case TAG_KNOWN_GOOD: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                out_manifest.known_good = v;
            }
            break;
        }
        case TAG_LAST_VERIFIED_TIMESTAMP_US: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                out_manifest.last_verified_timestamp_us = v;
            }
            break;
        }
        case TAG_PREVIOUS_MANIFEST_HASH64: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                out_manifest.previous_manifest_hash64 = v;
            }
            break;
        }
        case TAG_PROV_SOURCE_INSTANCE_ID:
            out_manifest.provenance_source_instance_id = tlv_read_string(rec.payload, rec.len);
            break;
        case TAG_PROV_SOURCE_MANIFEST_HASH64: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                out_manifest.provenance_source_manifest_hash64 = v;
            }
            break;
        }
        case TAG_CONTENT_ENTRY: {
            LauncherContentEntry entry;
            TlvReader er(rec.payload, (size_t)rec.len);
            TlvRecord e;
            while (er.next(e)) {
                if (e.tag == TAG_ENTRY_TYPE) {
                    u32 v;
                    if (tlv_read_u32_le(e.payload, e.len, v)) {
                        entry.type = v;
                    }
                } else if (e.tag == TAG_ENTRY_ID) {
                    entry.id = tlv_read_string(e.payload, e.len);
                } else if (e.tag == TAG_ENTRY_VERSION) {
                    entry.version = tlv_read_string(e.payload, e.len);
                } else if (e.tag == TAG_ENTRY_HASH_BYTES) {
                    entry.hash_bytes.clear();
                    if (e.len > 0u && e.payload) {
                        entry.hash_bytes.assign(e.payload, e.payload + (size_t)e.len);
                    }
                } else if (e.tag == TAG_ENTRY_ENABLED) {
                    u32 v;
                    if (tlv_read_u32_le(e.payload, e.len, v)) {
                        entry.enabled = v ? 1u : 0u;
                    }
                } else if (e.tag == TAG_ENTRY_UPDATE_POLICY) {
                    u32 v;
                    if (tlv_read_u32_le(e.payload, e.len, v)) {
                        entry.update_policy = v;
                    }
                } else if (e.tag == TAG_ENTRY_EXPLICIT_ORDER_OVERRIDE) {
                    i32 v;
                    if (tlv_read_i32_le(e.payload, e.len, v)) {
                        entry.has_explicit_order_override = 1u;
                        entry.explicit_order_override = v;
                    }
                } else {
                    tlv_unknown_capture(entry.unknown_fields, e);
                }
            }
            out_manifest.content_entries.push_back(entry);
            break;
        }
        default:
            tlv_unknown_capture(out_manifest.unknown_fields, rec);
            break;
        }
    }

    return true;
}

u64 launcher_instance_manifest_hash64(const LauncherInstanceManifest& manifest) {
    std::vector<unsigned char> bytes;
    if (!launcher_instance_manifest_to_tlv_bytes(manifest, bytes)) {
        return 0ull;
    }
    return tlv_fnv1a64(bytes.empty() ? (const unsigned char*)0 : &bytes[0], bytes.size());
}

bool launcher_instance_manifest_migrate_tlv(u32 from_version,
                                            u32 to_version,
                                            const unsigned char* data,
                                            size_t size,
                                            LauncherInstanceManifest& out_manifest) {
    if (!data || size == 0u) {
        return false;
    }
    if (from_version == 1u && to_version == LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION) {
        TlvReader r(data, size);
        TlvRecord rec;
        LauncherInstanceManifest m;
        std::vector<V1Pin> pins;

        /* v1: optional update_policy_flags (ignored for now; future-defined). */
        while (r.next(rec)) {
            switch (rec.tag) {
            case LAUNCHER_TLV_TAG_SCHEMA_VERSION:
                break;
            case TAG_INSTANCE_ID:
                m.instance_id = tlv_read_string(rec.payload, rec.len);
                break;
            case TAG_PIN_ENGINE_BUILD_ID:
                m.pinned_engine_build_id = tlv_read_string(rec.payload, rec.len);
                break;
            case TAG_PIN_GAME_BUILD_ID:
                m.pinned_game_build_id = tlv_read_string(rec.payload, rec.len);
                break;
            case TAG_KNOWN_GOOD: {
                u32 v;
                if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                    m.known_good = v;
                }
                break;
            }
            case 5u: { /* v1 pinned-content entry */
                V1Pin pin;
                TlvReader er(rec.payload, (size_t)rec.len);
                TlvRecord e;
                while (er.next(e)) {
                    if (e.tag == 1u) { /* v1 kind */
                        u32 v;
                        if (tlv_read_u32_le(e.payload, e.len, v)) {
                            pin.kind = v;
                        }
                    } else if (e.tag == TAG_ENTRY_ID) {
                        pin.id = tlv_read_string(e.payload, e.len);
                    } else if (e.tag == 3u) { /* v1 build_id */
                        pin.build_id = tlv_read_string(e.payload, e.len);
                    } else if (e.tag == TAG_ENTRY_HASH_BYTES) {
                        pin.hash_bytes.clear();
                        if (e.len > 0u && e.payload) {
                            pin.hash_bytes.assign(e.payload, e.payload + (size_t)e.len);
                        }
                    } else if (e.tag == 5u) { /* v1 order */
                        u32 v;
                        if (tlv_read_u32_le(e.payload, e.len, v)) {
                            pin.order_index = v;
                        }
                    } else {
                        /* drop v1 unknown */
                    }
                }
                pins.push_back(pin);
                break;
            }
            default:
                /* drop v1 unknown */
                break;
            }
        }

        if (!pins.empty()) {
            v1_sort_pins_by_order(pins);
        }

        m.schema_version = LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION;
        m.creation_timestamp_us = 0ull;
        m.last_verified_timestamp_us = 0ull;
        m.previous_manifest_hash64 = 0ull;
        m.provenance_source_instance_id.clear();
        m.provenance_source_manifest_hash64 = 0ull;

        for (size_t i = 0u; i < pins.size(); ++i) {
            LauncherContentEntry ce;
            ce.id = pins[i].id;
            ce.version = pins[i].build_id;
            ce.hash_bytes = pins[i].hash_bytes;
            ce.enabled = 1u;
            ce.update_policy = (u32)LAUNCHER_UPDATE_PROMPT;
            switch (pins[i].kind) {
            case 1u: ce.type = (u32)LAUNCHER_CONTENT_ENGINE; break;
            case 2u: ce.type = (u32)LAUNCHER_CONTENT_GAME; break;
            case 3u: ce.type = (u32)LAUNCHER_CONTENT_PACK; break;
            case 4u: ce.type = (u32)LAUNCHER_CONTENT_MOD; break;
            default: ce.type = (u32)LAUNCHER_CONTENT_UNKNOWN; break;
            }
            m.content_entries.push_back(ce);
        }

        out_manifest = m;
        return true;
    }

    return false;
}

} /* namespace launcher_core */
} /* namespace dom */
