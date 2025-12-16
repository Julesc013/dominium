/*
FILE: source/dominium/launcher/core/src/instance/launcher_instance_known_good.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / instance_known_good
RESPONSIBILITY: Implements known_good.tlv persistence (skip-unknown; deterministic).
*/

#include "launcher_instance_known_good.h"

#include "launcher_tlv.h"

namespace dom {
namespace launcher_core {

namespace {

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

} /* namespace */

LauncherInstanceKnownGoodPointer::LauncherInstanceKnownGoodPointer()
    : schema_version(LAUNCHER_INSTANCE_KNOWN_GOOD_TLV_VERSION),
      instance_id(),
      previous_dir(),
      manifest_hash64(0ull),
      timestamp_us(0ull),
      unknown_fields() {
}

bool launcher_instance_known_good_to_tlv_bytes(const LauncherInstanceKnownGoodPointer& kg,
                                               std::vector<unsigned char>& out_bytes) {
    TlvWriter w;

    w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, LAUNCHER_INSTANCE_KNOWN_GOOD_TLV_VERSION);
    w.add_string(LAUNCHER_KNOWN_GOOD_TLV_TAG_INSTANCE_ID, kg.instance_id);
    w.add_string(LAUNCHER_KNOWN_GOOD_TLV_TAG_PREVIOUS_DIR, kg.previous_dir);
    w.add_u64(LAUNCHER_KNOWN_GOOD_TLV_TAG_MANIFEST_HASH64, kg.manifest_hash64);
    w.add_u64(LAUNCHER_KNOWN_GOOD_TLV_TAG_TIMESTAMP_US, kg.timestamp_us);
    tlv_unknown_emit(w, kg.unknown_fields);
    out_bytes = w.bytes();
    return true;
}

bool launcher_instance_known_good_from_tlv_bytes(const unsigned char* data,
                                                 size_t size,
                                                 LauncherInstanceKnownGoodPointer& out_kg) {
    TlvReader r(data, size);
    TlvRecord rec;
    u32 version = 0u;
    LauncherInstanceKnownGoodPointer kg;

    if (!data || size == 0u) {
        return false;
    }
    if (!tlv_read_schema_version_or_default(data, size, version, 1u)) {
        return false;
    }
    kg.schema_version = version;

    while (r.next(rec)) {
        if (rec.tag == LAUNCHER_TLV_TAG_SCHEMA_VERSION) {
            continue;
        }
        switch (rec.tag) {
        case LAUNCHER_KNOWN_GOOD_TLV_TAG_INSTANCE_ID:
            kg.instance_id = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_KNOWN_GOOD_TLV_TAG_PREVIOUS_DIR:
            kg.previous_dir = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_KNOWN_GOOD_TLV_TAG_MANIFEST_HASH64: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                kg.manifest_hash64 = v;
            }
            break;
        }
        case LAUNCHER_KNOWN_GOOD_TLV_TAG_TIMESTAMP_US: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                kg.timestamp_us = v;
            }
            break;
        }
        default:
            tlv_unknown_capture(kg.unknown_fields, rec);
            break;
        }
    }

    out_kg = kg;
    return true;
}

} /* namespace launcher_core */
} /* namespace dom */

