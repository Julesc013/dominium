/*
FILE: source/dominium/tools/coredata_compile/coredata_manifest.cpp
MODULE: Dominium
PURPOSE: Coredata compiler manifest emission (deterministic record listing).
*/
#include "coredata_manifest.h"

#include <cstdio>

#include "dominium/core_tlv.h"

namespace dom {
namespace tools {

CoredataManifest::CoredataManifest()
    : bytes(),
      manifest_hash(0ull) {
}

namespace {

static void add_error(std::vector<CoredataError> &errors,
                      const char *code,
                      const std::string &message) {
    CoredataError e;
    e.path = "manifest";
    e.line = 0;
    e.code = code ? code : "error";
    e.message = message;
    errors.push_back(e);
}

} // namespace

bool coredata_emit_manifest(const CoredataPack &pack,
                            CoredataManifest &out_manifest,
                            std::vector<CoredataError> &errors) {
    dom::core_tlv::TlvWriter w;
    size_t i;

    errors.clear();
    out_manifest = CoredataManifest();

    if (pack.pack_id.empty()) {
        add_error(errors, "manifest_pack_id_missing", "pack_id");
        return false;
    }

    w.add_u32(CORE_DATA_MANIFEST_TAG_SCHEMA_VERSION, 1u);
    w.add_string(CORE_DATA_MANIFEST_TAG_PACK_ID, pack.pack_id);
    w.add_u32(CORE_DATA_MANIFEST_TAG_PACK_VERSION_NUM, pack.pack_version_num);
    if (!pack.pack_version_str.empty()) {
        w.add_string(CORE_DATA_MANIFEST_TAG_PACK_VERSION_STR, pack.pack_version_str);
    }
    w.add_u32(CORE_DATA_MANIFEST_TAG_PACK_SCHEMA_VERSION, pack.pack_schema_version);
    w.add_u64(CORE_DATA_MANIFEST_TAG_CONTENT_HASH, pack.content_hash);
    w.add_u64(CORE_DATA_MANIFEST_TAG_PACK_HASH, pack.pack_hash);

    for (i = 0u; i < pack.records.size(); ++i) {
        const CoredataRecord &r = pack.records[i];
        dom::core_tlv::TlvWriter inner;
        inner.add_u32(CORE_DATA_MANIFEST_REC_TAG_TYPE, r.type_id);
        inner.add_u32(CORE_DATA_MANIFEST_REC_TAG_VERSION, (u32)r.version);
        if (!r.id.empty()) {
            inner.add_string(CORE_DATA_MANIFEST_REC_TAG_ID, r.id);
            inner.add_u64(CORE_DATA_MANIFEST_REC_TAG_ID_HASH, r.id_hash);
        }
        inner.add_u64(CORE_DATA_MANIFEST_REC_TAG_RECORD_HASH, r.record_hash);
        w.add_container(CORE_DATA_MANIFEST_TAG_RECORD, inner.bytes());
    }

    out_manifest.bytes = w.bytes();
    out_manifest.manifest_hash = dom::core_tlv::tlv_fnv1a64(
        out_manifest.bytes.empty() ? 0 : &out_manifest.bytes[0],
        out_manifest.bytes.size());
    return errors.empty();
}

} // namespace tools
} // namespace dom
