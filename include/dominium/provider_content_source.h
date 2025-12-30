/*
FILE: include/dominium/provider_content_source.h
MODULE: Dominium
PURPOSE: Content source provider ABI (artifact resolution/acquisition).
*/
#ifndef DOMINIUM_PROVIDER_CONTENT_SOURCE_H
#define DOMINIUM_PROVIDER_CONTENT_SOURCE_H

#include "domino/abi.h"
#include "domino/core/types.h"
#include "dominium/core_err.h"
#include "dominium/provider_base.h"

#ifdef __cplusplus
extern "C" {
#endif

#define PROVIDER_IID_CONTENT_SOURCE_V1 ((dom_iid)0x50435331u) /* 'PCS1' */

#define PROVIDER_CONTENT_PATH_MAX 512u
#define PROVIDER_CONTENT_HASH_MAX 32u
#define PROVIDER_CONTENT_SOURCES_MAX 8u

typedef enum provider_content_request_flags_e {
    PROVIDER_CONTENT_REQ_NONE = 0u,
    PROVIDER_CONTENT_REQ_ALLOW_IMPORT = 1u << 0u,
    PROVIDER_CONTENT_REQ_OFFLINE_OK = 1u << 1u
} provider_content_request_flags;

typedef struct provider_content_request_v1 {
    u32 struct_size;
    u32 struct_version;
    u32 content_type;
    const char* content_id;
    const char* content_version;
    const unsigned char* hash_bytes;
    u32 hash_len;
    const char* state_root;
    const char* import_root;
    u32 flags;
} provider_content_request_v1;

typedef struct provider_content_artifact_ref_v1 {
    u32 struct_size;
    u32 struct_version;
    u32 content_type;
    u32 hash_len;
    unsigned char hash_bytes[PROVIDER_CONTENT_HASH_MAX];
    u64 size_bytes;
    u32 has_payload_path;
    u32 has_metadata_path;
    char payload_path[PROVIDER_CONTENT_PATH_MAX];
    char metadata_path[PROVIDER_CONTENT_PATH_MAX];
} provider_content_artifact_ref_v1;

typedef struct provider_content_source_entry_v1 {
    char source_id[64];
    char label[64];
} provider_content_source_entry_v1;

typedef struct provider_content_source_list_v1 {
    u32 count;
    provider_content_source_entry_v1 entries[PROVIDER_CONTENT_SOURCES_MAX];
} provider_content_source_list_v1;

typedef struct provider_content_source_v1 {
    DOM_ABI_HEADER;
    dom_query_interface_fn query_interface;
    const char* (*provider_id)(void);

    dom_abi_result (*enumerate_sources)(provider_content_source_list_v1* out_sources,
                                        err_t* out_err);
    dom_abi_result (*resolve_artifact)(const provider_content_request_v1* req,
                                       provider_content_artifact_ref_v1* out_ref,
                                       err_t* out_err);
    dom_abi_result (*acquire_artifact)(const provider_content_request_v1* req,
                                       const char* staging_path,
                                       err_t* out_err);
} provider_content_source_v1;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_PROVIDER_CONTENT_SOURCE_H */
