/*
FILE: source/dominium/launcher/core/src/instance/launcher_instance_payload_refs.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / instance_payload_refs
RESPONSIBILITY: Implements payload_refs.tlv persistence (skip-unknown; deterministic).
*/

#include "launcher_instance_payload_refs.h"

#include "launcher_tlv.h"
#include "launcher_tlv_migrations.h"

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

LauncherPayloadRefEntry::LauncherPayloadRefEntry()
    : type((u32)LAUNCHER_CONTENT_UNKNOWN),
      id(),
      version(),
      hash_bytes(),
      size_bytes(0ull),
      store_algo(),
      unknown_fields() {
}

LauncherInstancePayloadRefs::LauncherInstancePayloadRefs()
    : schema_version(LAUNCHER_INSTANCE_PAYLOAD_REFS_TLV_VERSION),
      instance_id(),
      manifest_hash64(0ull),
      entries(),
      unknown_fields() {
}

bool launcher_instance_payload_refs_to_tlv_bytes(const LauncherInstancePayloadRefs& refs,
                                                 std::vector<unsigned char>& out_bytes) {
    TlvWriter w;
    size_t i;

    w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, LAUNCHER_INSTANCE_PAYLOAD_REFS_TLV_VERSION);
    w.add_string(LAUNCHER_PAYLOAD_REFS_TLV_TAG_INSTANCE_ID, refs.instance_id);
    w.add_u64(LAUNCHER_PAYLOAD_REFS_TLV_TAG_MANIFEST_HASH64, refs.manifest_hash64);

    for (i = 0u; i < refs.entries.size(); ++i) {
        const LauncherPayloadRefEntry& e = refs.entries[i];
        TlvWriter ew;
        ew.add_u32(LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_TYPE, e.type);
        ew.add_string(LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_ID, e.id);
        ew.add_string(LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_VERSION, e.version);
        if (!e.hash_bytes.empty()) {
            ew.add_bytes(LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_HASH_BYTES, &e.hash_bytes[0], (u32)e.hash_bytes.size());
        } else {
            ew.add_bytes(LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_HASH_BYTES, (const unsigned char*)0, 0u);
        }
        ew.add_u64(LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_SIZE_BYTES, e.size_bytes);
        if (!e.store_algo.empty()) {
            ew.add_string(LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_STORE_ALGO, e.store_algo);
        }
        tlv_unknown_emit(ew, e.unknown_fields);
        w.add_container(LAUNCHER_PAYLOAD_REFS_TLV_TAG_ENTRY, ew.bytes());
    }

    tlv_unknown_emit(w, refs.unknown_fields);
    out_bytes = w.bytes();
    return true;
}

bool launcher_instance_payload_refs_from_tlv_bytes(const unsigned char* data,
                                                   size_t size,
                                                   LauncherInstancePayloadRefs& out_refs) {
    TlvReader r(data, size);
    TlvRecord rec;
    u32 version = 0u;
    LauncherInstancePayloadRefs refs;

    if (!data || size == 0u) {
        return false;
    }
    if (!tlv_read_schema_version_or_default(data,
                                            size,
                                            version,
                                            launcher_tlv_schema_min_version(LAUNCHER_TLV_SCHEMA_INSTANCE_PAYLOAD_REFS))) {
        return false;
    }
    if (!launcher_tlv_schema_accepts_version(LAUNCHER_TLV_SCHEMA_INSTANCE_PAYLOAD_REFS, version)) {
        return false;
    }
    refs.schema_version = launcher_tlv_schema_current_version(LAUNCHER_TLV_SCHEMA_INSTANCE_PAYLOAD_REFS);

    while (r.next(rec)) {
        if (rec.tag == LAUNCHER_TLV_TAG_SCHEMA_VERSION) {
            continue;
        }
        switch (rec.tag) {
        case LAUNCHER_PAYLOAD_REFS_TLV_TAG_INSTANCE_ID:
            refs.instance_id = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_PAYLOAD_REFS_TLV_TAG_MANIFEST_HASH64: {
            u64 v;
            if (tlv_read_u64_le(rec.payload, rec.len, v)) {
                refs.manifest_hash64 = v;
            }
            break;
        }
        case LAUNCHER_PAYLOAD_REFS_TLV_TAG_ENTRY: {
            LauncherPayloadRefEntry e;
            TlvReader er(rec.payload, (size_t)rec.len);
            TlvRecord rr;
            while (er.next(rr)) {
                switch (rr.tag) {
                case LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_TYPE: {
                    u32 v;
                    if (tlv_read_u32_le(rr.payload, rr.len, v)) {
                        e.type = v;
                    }
                    break;
                }
                case LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_ID:
                    e.id = tlv_read_string(rr.payload, rr.len);
                    break;
                case LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_VERSION:
                    e.version = tlv_read_string(rr.payload, rr.len);
                    break;
                case LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_HASH_BYTES:
                    e.hash_bytes.clear();
                    if (rr.len > 0u && rr.payload) {
                        e.hash_bytes.assign(rr.payload, rr.payload + (size_t)rr.len);
                    }
                    break;
                case LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_SIZE_BYTES: {
                    u64 v;
                    if (tlv_read_u64_le(rr.payload, rr.len, v)) {
                        e.size_bytes = v;
                    }
                    break;
                }
                case LAUNCHER_PAYLOAD_REFS_ENTRY_TLV_TAG_STORE_ALGO:
                    e.store_algo = tlv_read_string(rr.payload, rr.len);
                    break;
                default:
                    tlv_unknown_capture(e.unknown_fields, rr);
                    break;
                }
            }
            refs.entries.push_back(e);
            break;
        }
        default:
            tlv_unknown_capture(refs.unknown_fields, rec);
            break;
        }
    }

    out_refs = refs;
    return true;
}

} /* namespace launcher_core */
} /* namespace dom */
