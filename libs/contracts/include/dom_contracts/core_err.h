/*
FILE: include/dominium/core_err.h
MODULE: Dominium
PURPOSE: Stable, deterministic error model shared across launcher/setup kernels and frontends.
NOTES: Message IDs are append-only; never renumber.
*/
#ifndef DOMINIUM_CORE_ERR_H
#define DOMINIUM_CORE_ERR_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/*------------------------------------------------------------
 * Error domains (stable numeric IDs; append-only).
 *------------------------------------------------------------*/
typedef enum err_domain_e {
    ERRD_NONE = 0u,
    ERRD_COMMON = 1u,
    ERRD_TLV = 2u,
    ERRD_FS = 3u,
    ERRD_PROC = 4u,
    ERRD_CRYPTO = 5u,
    ERRD_ARCHIVE = 6u,
    ERRD_NET = 7u,
    ERRD_LAUNCHER = 8u,
    ERRD_SETUP = 9u,
    ERRD_PACKS = 10u,
    ERRD_ARTIFACT = 11u,
    ERRD_TXN = 12u
} err_domain;

/*------------------------------------------------------------
 * Error flags (bitset; stable).
 *------------------------------------------------------------*/
typedef enum err_flags_e {
    ERRF_NONE = 0u,
    ERRF_RETRYABLE = 1u << 0u,
    ERRF_USER_ACTIONABLE = 1u << 1u,
    ERRF_FATAL = 1u << 2u,
    ERRF_TRANSIENT = 1u << 3u,
    ERRF_INTEGRITY = 1u << 4u,
    ERRF_POLICY_REFUSAL = 1u << 5u,
    ERRF_NOT_SUPPORTED = 1u << 6u
} err_flags;

/*------------------------------------------------------------
 * Domain-specific codes (stable; append-only per domain).
 *------------------------------------------------------------*/
typedef enum err_common_code_e {
    ERRC_COMMON_OK = 0u,
    ERRC_COMMON_INVALID_ARGS = 1u,
    ERRC_COMMON_OUT_OF_MEMORY = 2u,
    ERRC_COMMON_NOT_FOUND = 3u,
    ERRC_COMMON_UNSUPPORTED = 4u,
    ERRC_COMMON_INTERNAL = 5u,
    ERRC_COMMON_BAD_STATE = 6u
} err_common_code;

typedef enum err_tlv_code_e {
    ERRC_TLV_PARSE_FAILED = 1u,
    ERRC_TLV_SCHEMA_VERSION = 2u,
    ERRC_TLV_MISSING_FIELD = 3u,
    ERRC_TLV_INTEGRITY = 4u
} err_tlv_code;

typedef enum err_fs_code_e {
    ERRC_FS_OPEN_FAILED = 1u,
    ERRC_FS_READ_FAILED = 2u,
    ERRC_FS_WRITE_FAILED = 3u,
    ERRC_FS_PATH_INVALID = 4u,
    ERRC_FS_NOT_FOUND = 5u,
    ERRC_FS_PERMISSION = 6u
} err_fs_code;

typedef enum err_proc_code_e {
    ERRC_PROC_SPAWN_FAILED = 1u,
    ERRC_PROC_WAIT_FAILED = 2u
} err_proc_code;

typedef enum err_crypto_code_e {
    ERRC_CRYPTO_HASH_MISMATCH = 1u,
    ERRC_CRYPTO_VERIFY_FAILED = 2u
} err_crypto_code;

typedef enum err_archive_code_e {
    ERRC_ARCHIVE_OPEN_FAILED = 1u,
    ERRC_ARCHIVE_EXTRACT_FAILED = 2u
} err_archive_code;

typedef enum err_net_code_e {
    ERRC_NET_CONNECT_FAILED = 1u,
    ERRC_NET_TIMEOUT = 2u,
    ERRC_NET_PROTOCOL = 3u
} err_net_code;

typedef enum err_launcher_code_e {
    ERRC_LAUNCHER_INSTANCE_INVALID = 1u,
    ERRC_LAUNCHER_INSTANCE_NOT_FOUND = 2u,
    ERRC_LAUNCHER_INSTANCE_EXISTS = 3u,
    ERRC_LAUNCHER_MANIFEST_INVALID = 4u,
    ERRC_LAUNCHER_MANIFEST_WRITE_FAILED = 5u,
    ERRC_LAUNCHER_PAYLOAD_HASH_MISMATCH = 6u,
    ERRC_LAUNCHER_PAYLOAD_MISSING = 7u,
    ERRC_LAUNCHER_STATE_ROOT_UNAVAILABLE = 8u,
    ERRC_LAUNCHER_EXPORT_FAILED = 9u,
    ERRC_LAUNCHER_IMPORT_FAILED = 10u,
    ERRC_LAUNCHER_HANDSHAKE_INVALID = 11u
} err_launcher_code;

typedef enum err_setup_code_e {
    ERRC_SETUP_INVALID_MANIFEST = 1u,
    ERRC_SETUP_UNSUPPORTED_PLATFORM = 2u,
    ERRC_SETUP_DEPENDENCY_CONFLICT = 3u,
    ERRC_SETUP_OFFLINE_REFUSED = 4u,
    ERRC_SETUP_INSTALL_FAILED = 5u,
    ERRC_SETUP_REPAIR_FAILED = 6u,
    ERRC_SETUP_UNINSTALL_FAILED = 7u,
    ERRC_SETUP_VERIFY_FAILED = 8u,
    ERRC_SETUP_PLAN_FAILED = 9u,
    ERRC_SETUP_APPLY_FAILED = 10u,
    ERRC_SETUP_RESOLVE_FAILED = 11u,
    ERRC_SETUP_MANIFEST_NOT_FOUND = 12u
} err_setup_code;

typedef enum err_packs_code_e {
    ERRC_PACKS_DEPENDENCY_MISSING = 1u,
    ERRC_PACKS_DEPENDENCY_CONFLICT = 2u,
    ERRC_PACKS_PACK_NOT_FOUND = 3u,
    ERRC_PACKS_PACK_INVALID = 4u,
    ERRC_PACKS_SIM_FLAGS_MISSING = 5u,
    ERRC_PACKS_OFFLINE_REFUSED = 6u
} err_packs_code;

typedef enum err_artifact_code_e {
    ERRC_ARTIFACT_METADATA_NOT_FOUND = 1u,
    ERRC_ARTIFACT_METADATA_INVALID = 2u,
    ERRC_ARTIFACT_PAYLOAD_MISSING = 3u,
    ERRC_ARTIFACT_PAYLOAD_HASH_MISMATCH = 4u,
    ERRC_ARTIFACT_CONTENT_TYPE_MISMATCH = 5u,
    ERRC_ARTIFACT_SIZE_MISMATCH = 6u
} err_artifact_code;

typedef enum err_txn_code_e {
    ERRC_TXN_PHASE_FAILED = 1u,
    ERRC_TXN_COMMIT_FAILED = 2u,
    ERRC_TXN_ROLLBACK_FAILED = 3u,
    ERRC_TXN_CANCELLED = 4u
} err_txn_code;

/*------------------------------------------------------------
 * Message ID catalog (append-only; stable numeric IDs).
 *------------------------------------------------------------*/
typedef enum err_msg_id_e {
    ERRMSG_NONE = 0u,

    /* Common */
    ERRMSG_COMMON_INVALID_ARGS = 1u,
    ERRMSG_COMMON_OUT_OF_MEMORY = 2u,
    ERRMSG_COMMON_NOT_FOUND = 3u,
    ERRMSG_COMMON_UNSUPPORTED = 4u,
    ERRMSG_COMMON_INTERNAL = 5u,
    ERRMSG_COMMON_BAD_STATE = 6u,

    /* TLV */
    ERRMSG_TLV_PARSE_FAILED = 10u,
    ERRMSG_TLV_SCHEMA_VERSION = 11u,
    ERRMSG_TLV_MISSING_FIELD = 12u,
    ERRMSG_TLV_INTEGRITY = 13u,

    /* FS */
    ERRMSG_FS_OPEN_FAILED = 20u,
    ERRMSG_FS_READ_FAILED = 21u,
    ERRMSG_FS_WRITE_FAILED = 22u,
    ERRMSG_FS_PATH_INVALID = 23u,
    ERRMSG_FS_NOT_FOUND = 24u,
    ERRMSG_FS_PERMISSION = 25u,

    /* Process */
    ERRMSG_PROC_SPAWN_FAILED = 30u,
    ERRMSG_PROC_WAIT_FAILED = 31u,

    /* Crypto */
    ERRMSG_CRYPTO_HASH_MISMATCH = 40u,
    ERRMSG_CRYPTO_VERIFY_FAILED = 41u,

    /* Archive */
    ERRMSG_ARCHIVE_OPEN_FAILED = 50u,
    ERRMSG_ARCHIVE_EXTRACT_FAILED = 51u,

    /* Net */
    ERRMSG_NET_CONNECT_FAILED = 60u,
    ERRMSG_NET_TIMEOUT = 61u,
    ERRMSG_NET_PROTOCOL = 62u,

    /* Launcher */
    ERRMSG_LAUNCHER_INSTANCE_ID_INVALID = 100u,
    ERRMSG_LAUNCHER_INSTANCE_NOT_FOUND = 101u,
    ERRMSG_LAUNCHER_INSTANCE_EXISTS = 102u,
    ERRMSG_LAUNCHER_INSTANCE_MANIFEST_INVALID = 103u,
    ERRMSG_LAUNCHER_INSTANCE_MANIFEST_WRITE_FAILED = 104u,
    ERRMSG_LAUNCHER_INSTANCE_PAYLOAD_HASH_MISMATCH = 105u,
    ERRMSG_LAUNCHER_INSTANCE_PAYLOAD_MISSING = 106u,
    ERRMSG_LAUNCHER_STATE_ROOT_UNAVAILABLE = 107u,
    ERRMSG_LAUNCHER_INSTANCE_EXPORT_FAILED = 108u,
    ERRMSG_LAUNCHER_INSTANCE_IMPORT_FAILED = 109u,
    ERRMSG_LAUNCHER_HANDSHAKE_INVALID = 110u,

    /* Packs */
    ERRMSG_PACKS_DEPENDENCY_MISSING = 120u,
    ERRMSG_PACKS_DEPENDENCY_CONFLICT = 121u,
    ERRMSG_PACKS_PACK_NOT_FOUND = 122u,
    ERRMSG_PACKS_PACK_INVALID = 123u,
    ERRMSG_PACKS_SIM_FLAGS_MISSING = 124u,
    ERRMSG_PACKS_OFFLINE_REFUSED = 125u,

    /* Artifact */
    ERRMSG_ARTIFACT_METADATA_NOT_FOUND = 130u,
    ERRMSG_ARTIFACT_METADATA_INVALID = 131u,
    ERRMSG_ARTIFACT_PAYLOAD_MISSING = 132u,
    ERRMSG_ARTIFACT_PAYLOAD_HASH_MISMATCH = 133u,
    ERRMSG_ARTIFACT_CONTENT_TYPE_MISMATCH = 134u,
    ERRMSG_ARTIFACT_SIZE_MISMATCH = 135u,

    /* Transactions */
    ERRMSG_TXN_PHASE_FAILED = 140u,
    ERRMSG_TXN_COMMIT_FAILED = 141u,
    ERRMSG_TXN_ROLLBACK_FAILED = 142u,
    ERRMSG_TXN_CANCELLED = 143u,

    /* Setup */
    ERRMSG_SETUP_INVALID_MANIFEST = 200u,
    ERRMSG_SETUP_UNSUPPORTED_PLATFORM = 201u,
    ERRMSG_SETUP_DEPENDENCY_CONFLICT = 202u,
    ERRMSG_SETUP_OFFLINE_REFUSED = 203u,
    ERRMSG_SETUP_INSTALL_FAILED = 204u,
    ERRMSG_SETUP_REPAIR_FAILED = 205u,
    ERRMSG_SETUP_UNINSTALL_FAILED = 206u,
    ERRMSG_SETUP_VERIFY_FAILED = 207u,
    ERRMSG_SETUP_PLAN_FAILED = 208u,
    ERRMSG_SETUP_APPLY_FAILED = 209u,
    ERRMSG_SETUP_RESOLVE_FAILED = 210u,
    ERRMSG_SETUP_MANIFEST_NOT_FOUND = 211u
} err_msg_id;

/*------------------------------------------------------------
 * Detail keys + types (stable; append-only).
 *------------------------------------------------------------*/
typedef enum err_detail_key_e {
    ERR_DETAIL_KEY_NONE = 0u,
    ERR_DETAIL_KEY_INSTANCE_ID = 1u,
    ERR_DETAIL_KEY_PROFILE_ID = 2u,
    ERR_DETAIL_KEY_PACK_ID = 3u,
    ERR_DETAIL_KEY_PACK_VERSION = 4u,
    ERR_DETAIL_KEY_ARTIFACT_HASH = 5u,
    ERR_DETAIL_KEY_EXPECTED_HASH64 = 6u,
    ERR_DETAIL_KEY_ACTUAL_HASH64 = 7u,
    ERR_DETAIL_KEY_PATH_HASH64 = 8u,
    ERR_DETAIL_KEY_STATE_ROOT_HASH64 = 9u,
    ERR_DETAIL_KEY_MANIFEST_HASH64 = 10u,
    ERR_DETAIL_KEY_COMPONENT_ID = 11u,
    ERR_DETAIL_KEY_OPERATION = 12u,
    ERR_DETAIL_KEY_PLATFORM_ID = 13u,
    ERR_DETAIL_KEY_STAGE = 14u,
    ERR_DETAIL_KEY_TXN_STEP = 15u,
    ERR_DETAIL_KEY_OFFLINE_MODE = 16u,
    ERR_DETAIL_KEY_STATUS_CODE = 17u,
    ERR_DETAIL_KEY_SCHEMA_VERSION = 18u,
    ERR_DETAIL_KEY_REQUIRED_FIELD = 19u,
    ERR_DETAIL_KEY_EXPORT_ROOT_HASH64 = 20u,
    ERR_DETAIL_KEY_IMPORT_ROOT_HASH64 = 21u,
    ERR_DETAIL_KEY_CONTENT_TYPE = 22u,
    ERR_DETAIL_KEY_SAFE_MODE = 23u,
    ERR_DETAIL_KEY_SUBCODE = 24u
} err_detail_key;

typedef enum err_detail_type_e {
    ERR_DETAIL_TYPE_NONE = 0u,
    ERR_DETAIL_TYPE_U32 = 1u,
    ERR_DETAIL_TYPE_U64 = 2u,
    ERR_DETAIL_TYPE_MSG_ID = 3u,
    ERR_DETAIL_TYPE_HASH64 = 4u,
    ERR_DETAIL_TYPE_PATH_HASH64 = 5u
} err_detail_type;

typedef struct err_detail_t {
    u32 key_id;
    u32 type;
    union {
        u32 u32_value;
        u64 u64_value;
        u32 msg_id;
        u64 hash64;
    } v;
} err_detail;

enum { ERR_DETAIL_MAX = 8u };

/*------------------------------------------------------------
 * err_t: stable POD error record (no allocation).
 *------------------------------------------------------------*/
typedef struct err_t {
    u16 domain;      /* err_domain */
    u16 code;        /* domain-specific code */
    u32 flags;       /* err_flags bitset */
    u32 msg_id;      /* err_msg_id */
    u32 detail_count;
    err_detail details[ERR_DETAIL_MAX];
} err_t;

/*------------------------------------------------------------
 * Helpers (C89 compatible; no allocation).
 *------------------------------------------------------------*/
err_t err_ok(void);
err_t err_make(u16 domain, u16 code, u32 flags, u32 msg_id);
err_t err_refuse(u16 domain, u16 code, u32 msg_id);
int err_is_ok(const err_t* err);
void err_clear(err_t* err);

int err_add_detail_u32(err_t* err, u32 key_id, u32 value);
int err_add_detail_u64(err_t* err, u32 key_id, u64 value);
int err_add_detail_msg_id(err_t* err, u32 key_id, u32 msg_id);
int err_add_detail_hash64(err_t* err, u32 key_id, u64 hash64);

void err_sort_details_by_key(err_t* err);

const char* err_domain_token(u16 domain);
const char* err_msg_id_token(u32 msg_id);
const char* err_detail_key_token(u32 key_id);
const char* err_to_string_id(const err_t* err);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_CORE_ERR_H */
