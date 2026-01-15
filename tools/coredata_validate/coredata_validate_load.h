/*
FILE: source/dominium/tools/coredata_validate/coredata_validate_load.h
MODULE: Dominium
PURPOSE: Coredata validator loaders (authoring + pack/manifest).
*/
#ifndef DOMINIUM_TOOLS_COREDATA_VALIDATE_LOAD_H
#define DOMINIUM_TOOLS_COREDATA_VALIDATE_LOAD_H

#include <string>
#include <vector>

#include "coredata_compile/coredata_load.h"

namespace dom {
namespace tools {

struct CoredataPackRecordView {
    u32 type_id;
    std::string id;
    u64 id_hash;
    std::vector<unsigned char> payload;
    u64 record_hash;

    CoredataPackRecordView();
};

struct CoredataPackView {
    bool has_pack_meta;
    u32 pack_schema_version;
    std::string pack_id;
    u32 pack_version_num;
    std::string pack_version_str;
    u64 content_hash;
    u64 pack_hash;
    std::vector<CoredataPackRecordView> records;

    CoredataPackView();
};

struct CoredataManifestRecordView {
    u32 type_id;
    u32 version;
    std::string id;
    u64 id_hash;
    u64 record_hash;

    CoredataManifestRecordView();
};

struct CoredataManifestView {
    bool present;
    u32 schema_version;
    std::string pack_id;
    u32 pack_version_num;
    std::string pack_version_str;
    u32 pack_schema_version;
    u64 content_hash;
    u64 pack_hash;
    std::vector<CoredataManifestRecordView> records;

    CoredataManifestView();
};

bool coredata_validate_load_authoring(const std::string &root,
                                      CoredataData &out,
                                      std::vector<CoredataError> &errors);

bool coredata_validate_load_pack(const std::string &path,
                                 CoredataPackView &out_pack,
                                 std::vector<CoredataError> &errors);

bool coredata_validate_load_manifest(const std::string &path,
                                     CoredataManifestView &out_manifest,
                                     std::vector<CoredataError> &errors);

} // namespace tools
} // namespace dom

#endif /* DOMINIUM_TOOLS_COREDATA_VALIDATE_LOAD_H */
