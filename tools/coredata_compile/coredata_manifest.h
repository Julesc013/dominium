/*
FILE: source/dominium/tools/coredata_compile/coredata_manifest.h
MODULE: Dominium
PURPOSE: Coredata compiler manifest emission (deterministic record listing).
*/
#ifndef DOMINIUM_TOOLS_COREDATA_MANIFEST_H
#define DOMINIUM_TOOLS_COREDATA_MANIFEST_H

#include <vector>

#include "coredata_emit_tlv.h"

namespace dom {
namespace tools {

enum {
    CORE_DATA_MANIFEST_TAG_SCHEMA_VERSION = 1u,
    CORE_DATA_MANIFEST_TAG_PACK_ID = 2u,
    CORE_DATA_MANIFEST_TAG_PACK_VERSION_NUM = 3u,
    CORE_DATA_MANIFEST_TAG_PACK_VERSION_STR = 4u,
    CORE_DATA_MANIFEST_TAG_PACK_SCHEMA_VERSION = 5u,
    CORE_DATA_MANIFEST_TAG_CONTENT_HASH = 6u,
    CORE_DATA_MANIFEST_TAG_PACK_HASH = 7u,
    CORE_DATA_MANIFEST_TAG_RECORD = 8u
};

enum {
    CORE_DATA_MANIFEST_REC_TAG_TYPE = 1u,
    CORE_DATA_MANIFEST_REC_TAG_VERSION = 2u,
    CORE_DATA_MANIFEST_REC_TAG_ID = 3u,
    CORE_DATA_MANIFEST_REC_TAG_ID_HASH = 4u,
    CORE_DATA_MANIFEST_REC_TAG_RECORD_HASH = 5u
};

struct CoredataManifest {
    std::vector<unsigned char> bytes;
    u64 manifest_hash;

    CoredataManifest();
};

bool coredata_emit_manifest(const CoredataPack &pack,
                            CoredataManifest &out_manifest,
                            std::vector<CoredataError> &errors);

} // namespace tools
} // namespace dom

#endif /* DOMINIUM_TOOLS_COREDATA_MANIFEST_H */
