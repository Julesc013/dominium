/*
FILE: include/dominium/core_tlv_schema.h
MODULE: Dominium
PURPOSE: Central TLV schema registry with version governance and migration hooks.
NOTES: Schema IDs are append-only; validators must be deterministic and skip-unknown safe.
*/
#ifndef DOMINIUM_CORE_TLV_SCHEMA_H
#define DOMINIUM_CORE_TLV_SCHEMA_H

#include "domino/abi.h"
#include "domino/core/types.h"
#include "dominium/core_err.h"

#ifdef __cplusplus
extern "C" {
#endif

/*------------------------------------------------------------
 * Limits (fixed; append-only if changed).
 *------------------------------------------------------------*/
#define CORE_TLV_SCHEMA_MAX_ENTRIES 64u

/*------------------------------------------------------------
 * Schema IDs (stable numeric IDs; append-only).
 *------------------------------------------------------------*/
typedef enum core_tlv_schema_id_e {
    CORE_TLV_SCHEMA_UNKNOWN = 0u,
    CORE_TLV_SCHEMA_LAUNCHER_INSTANCE_MANIFEST = 1u,
    CORE_TLV_SCHEMA_LAUNCHER_PACK_MANIFEST = 2u,
    CORE_TLV_SCHEMA_LAUNCHER_AUDIT_LOG = 3u,
    CORE_TLV_SCHEMA_LAUNCHER_HANDSHAKE = 4u,
    CORE_TLV_SCHEMA_LAUNCHER_SELECTION_SUMMARY = 5u,
    CORE_TLV_SCHEMA_SETUP_INSTALLED_STATE = 6u,
    CORE_TLV_SCHEMA_CORE_JOB_DEF = 7u,
    CORE_TLV_SCHEMA_CORE_JOB_STATE = 8u,
    CORE_TLV_SCHEMA_LAUNCHER_TOOLS_REGISTRY = 9u,
    CORE_TLV_SCHEMA_LAUNCHER_CAPS_SNAPSHOT = 10u,
    CORE_TLV_SCHEMA_DIAG_BUNDLE_INDEX = 11u,
    CORE_TLV_SCHEMA_DIAG_BUNDLE_META = 12u
} core_tlv_schema_id;

/*------------------------------------------------------------
 * Registry entry.
 *------------------------------------------------------------*/
typedef err_t (*core_tlv_schema_validate_fn)(const unsigned char* data,
                                             u32 size,
                                             u32* out_version);

typedef dom_abi_result (*core_tlv_schema_write_fn)(void* user,
                                                   const void* data,
                                                   u32 len);

typedef struct core_tlv_schema_sink_t {
    void* user;
    core_tlv_schema_write_fn write;
} core_tlv_schema_sink;

typedef err_t (*core_tlv_schema_migrate_fn)(u32 from_version,
                                            u32 to_version,
                                            const unsigned char* data,
                                            u32 size,
                                            const core_tlv_schema_sink* sink);

typedef struct core_tlv_schema_entry_t {
    u32 schema_id;
    const char* name;
    u32 current_version;
    u32 min_version;
    u32 max_version;
    core_tlv_schema_validate_fn validate;
    core_tlv_schema_migrate_fn migrate;
} core_tlv_schema_entry;

typedef enum core_tlv_schema_result_e {
    CORE_TLV_SCHEMA_OK = 0,
    CORE_TLV_SCHEMA_ERR_NULL = -1,
    CORE_TLV_SCHEMA_ERR_FULL = -2,
    CORE_TLV_SCHEMA_ERR_CONFLICT = -3
} core_tlv_schema_result;

/*------------------------------------------------------------
 * Registry management.
 *------------------------------------------------------------*/
void core_tlv_schema_reset_registry(void);
core_tlv_schema_result core_tlv_schema_register(const core_tlv_schema_entry* entry);

u32 core_tlv_schema_count(void);
const core_tlv_schema_entry* core_tlv_schema_at(u32 index);
const core_tlv_schema_entry* core_tlv_schema_find(u32 schema_id);

/*------------------------------------------------------------
 * Version checks + migrations.
 *------------------------------------------------------------*/
int core_tlv_schema_accepts_version(const core_tlv_schema_entry* entry, u32 version);

err_t core_tlv_schema_validate_entry(const core_tlv_schema_entry* entry,
                                     const unsigned char* data,
                                     u32 size,
                                     u32* out_version);

err_t core_tlv_schema_validate(u32 schema_id,
                               const unsigned char* data,
                               u32 size,
                               u32* out_version);

err_t core_tlv_schema_migrate(u32 schema_id,
                              u32 from_version,
                              u32 to_version,
                              const unsigned char* data,
                              u32 size,
                              const core_tlv_schema_sink* sink);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_CORE_TLV_SCHEMA_H */
