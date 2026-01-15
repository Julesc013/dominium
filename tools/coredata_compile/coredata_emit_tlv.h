/*
FILE: source/dominium/tools/coredata_compile/coredata_emit_tlv.h
MODULE: Dominium
PURPOSE: Coredata compiler TLV emission (deterministic pack bytes).
*/
#ifndef DOMINIUM_TOOLS_COREDATA_EMIT_TLV_H
#define DOMINIUM_TOOLS_COREDATA_EMIT_TLV_H

#include <string>
#include <vector>

#include "coredata_load.h"

namespace dom {
namespace tools {

struct CoredataRecord {
    u32 type_id;
    u16 version;
    std::string id;
    u64 id_hash;
    std::vector<unsigned char> payload;
    u64 record_hash;

    CoredataRecord();
};

struct CoredataPack {
    std::string pack_id;
    std::string pack_version_str;
    u32 pack_version_num;
    u32 pack_schema_version;
    u64 content_hash;
    u64 pack_hash;
    std::vector<CoredataRecord> records;
    std::vector<unsigned char> pack_bytes;

    CoredataPack();
};

struct CoredataEmitOptions {
    std::string pack_id;
    std::string pack_version_str;
    u32 pack_version_num;
    u32 pack_schema_version;

    CoredataEmitOptions();
};

bool coredata_emit_pack(const CoredataData &data,
                        const CoredataEmitOptions &opts,
                        CoredataPack &out_pack,
                        std::vector<CoredataError> &errors);

} // namespace tools
} // namespace dom

#endif /* DOMINIUM_TOOLS_COREDATA_EMIT_TLV_H */
