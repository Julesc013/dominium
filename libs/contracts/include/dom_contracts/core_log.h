/*
FILE: include/dominium/core_log.h
MODULE: Dominium
PURPOSE: Structured, deterministic event logging (POD events + TLV encoding).
NOTES: No free-form strings in kernel logs; paths must be redacted or safe relative.
*/
#ifndef DOMINIUM_CORE_LOG_H
#define DOMINIUM_CORE_LOG_H

#include "domino/abi.h"
#include "domino/core/types.h"
#include "dom_contracts/core_err.h"

#ifdef __cplusplus
extern "C" {
#endif

/*------------------------------------------------------------
 * Limits (fixed; append-only if changed).
 *------------------------------------------------------------*/
#define CORE_LOG_MAX_FIELDS 8u
#define CORE_LOG_MAX_PATH   96u

/*------------------------------------------------------------
 * Domain alignment (mirrors err_domain values).
 *------------------------------------------------------------*/
#define CORE_LOG_DOMAIN_NONE     ((u16)ERRD_NONE)
#define CORE_LOG_DOMAIN_COMMON   ((u16)ERRD_COMMON)
#define CORE_LOG_DOMAIN_TLV      ((u16)ERRD_TLV)
#define CORE_LOG_DOMAIN_FS       ((u16)ERRD_FS)
#define CORE_LOG_DOMAIN_PROC     ((u16)ERRD_PROC)
#define CORE_LOG_DOMAIN_CRYPTO   ((u16)ERRD_CRYPTO)
#define CORE_LOG_DOMAIN_ARCHIVE  ((u16)ERRD_ARCHIVE)
#define CORE_LOG_DOMAIN_NET      ((u16)ERRD_NET)
#define CORE_LOG_DOMAIN_LAUNCHER ((u16)ERRD_LAUNCHER)
#define CORE_LOG_DOMAIN_SETUP    ((u16)ERRD_SETUP)
#define CORE_LOG_DOMAIN_PACKS    ((u16)ERRD_PACKS)
#define CORE_LOG_DOMAIN_ARTIFACT ((u16)ERRD_ARTIFACT)
#define CORE_LOG_DOMAIN_TXN      ((u16)ERRD_TXN)

/*------------------------------------------------------------
 * Severity + flags (stable).
 *------------------------------------------------------------*/
typedef enum core_log_severity_e {
    CORE_LOG_SEV_DEBUG = 1u,
    CORE_LOG_SEV_INFO = 2u,
    CORE_LOG_SEV_WARN = 3u,
    CORE_LOG_SEV_ERROR = 4u
} core_log_severity;

typedef enum core_log_event_flags_e {
    CORE_LOG_EVT_FLAG_NONE = 0u,
    CORE_LOG_EVT_FLAG_REDACTED = 1u << 0u,
    CORE_LOG_EVT_FLAG_HAS_PATH = 1u << 1u,
    CORE_LOG_EVT_FLAG_HAS_HASH = 1u << 2u,
    CORE_LOG_EVT_FLAG_TRUNCATED = 1u << 3u
} core_log_event_flags;

typedef enum core_log_field_flags_e {
    CORE_LOG_FIELD_FLAG_NONE = 0u,
    CORE_LOG_FIELD_FLAG_REDACTED = 1u << 0u
} core_log_field_flags;

/*------------------------------------------------------------
 * Field types (stable; append-only).
 *------------------------------------------------------------*/
typedef enum core_log_field_type_e {
    CORE_LOG_FIELD_U32 = 1u,
    CORE_LOG_FIELD_U64 = 2u,
    CORE_LOG_FIELD_BOOL = 3u,
    CORE_LOG_FIELD_MSG_ID = 4u,
    CORE_LOG_FIELD_HASH64 = 5u,
    CORE_LOG_FIELD_PATH_REL = 6u,
    CORE_LOG_FIELD_PATH_REDACTED = 7u
} core_log_field_type;

/*------------------------------------------------------------
 * Field keys (stable; append-only).
 *------------------------------------------------------------*/
typedef enum core_log_field_key_e {
    CORE_LOG_KEY_NONE = 0u,
    CORE_LOG_KEY_OPERATION_ID = 1u,
    CORE_LOG_KEY_RUN_ID = 2u,
    CORE_LOG_KEY_INSTANCE_ID_HASH = 3u,
    CORE_LOG_KEY_PACK_ID_HASH = 4u,
    CORE_LOG_KEY_ARTIFACT_HASH = 5u,
    CORE_LOG_KEY_MANIFEST_HASH64 = 6u,
    CORE_LOG_KEY_STATUS_CODE = 7u,
    CORE_LOG_KEY_ERR_DOMAIN = 8u,
    CORE_LOG_KEY_ERR_CODE = 9u,
    CORE_LOG_KEY_ERR_FLAGS = 10u,
    CORE_LOG_KEY_ERR_MSG_ID = 11u,
    CORE_LOG_KEY_REFUSAL_CODE = 12u,
    CORE_LOG_KEY_PATH = 13u,
    CORE_LOG_KEY_JOB_ID = 14u,
    CORE_LOG_KEY_JOB_TYPE = 15u,
    CORE_LOG_KEY_JOB_STEP_ID = 16u,
    CORE_LOG_KEY_JOB_OUTCOME = 17u
} core_log_field_key;

/*------------------------------------------------------------
 * Operation IDs (stable; append-only).
 *------------------------------------------------------------*/
typedef enum core_log_operation_id_e {
    CORE_LOG_OP_NONE = 0u,
    CORE_LOG_OP_LAUNCHER_INSTANCE_CREATE = 1u,
    CORE_LOG_OP_LAUNCHER_INSTANCE_DELETE = 2u,
    CORE_LOG_OP_LAUNCHER_INSTANCE_CLONE = 3u,
    CORE_LOG_OP_LAUNCHER_INSTANCE_IMPORT = 4u,
    CORE_LOG_OP_LAUNCHER_INSTANCE_EXPORT = 5u,
    CORE_LOG_OP_LAUNCHER_PACK_RESOLVE = 6u,
    CORE_LOG_OP_LAUNCHER_ARTIFACT_VERIFY = 7u,
    CORE_LOG_OP_LAUNCHER_TXN_STAGE = 8u,
    CORE_LOG_OP_LAUNCHER_TXN_COMMIT = 9u,
    CORE_LOG_OP_LAUNCHER_TXN_ROLLBACK = 10u,
    CORE_LOG_OP_LAUNCHER_HANDSHAKE_VALIDATE = 11u,
    CORE_LOG_OP_LAUNCHER_LAUNCH_PREPARE = 12u,
    CORE_LOG_OP_LAUNCHER_INSTANCE_MARK_KNOWN_GOOD = 13u,
    CORE_LOG_OP_LAUNCHER_INSTANCE_MARK_BROKEN = 14u,
    CORE_LOG_OP_LAUNCHER_INSTANCE_TEMPLATE = 15u,
    CORE_LOG_OP_LAUNCHER_SIM_SAFETY_VALIDATE = 16u,
    CORE_LOG_OP_LAUNCHER_LAUNCH_EXECUTE = 17u,
    CORE_LOG_OP_LAUNCHER_JOB = 18u,
    CORE_LOG_OP_SETUP_PARSE_MANIFEST = 100u,
    CORE_LOG_OP_SETUP_PARSE_REQUEST = 101u,
    CORE_LOG_OP_SETUP_SPLAT_SELECT = 102u,
    CORE_LOG_OP_SETUP_WRITE_STATE = 103u,
    CORE_LOG_OP_SETUP_JOB = 104u
} core_log_operation_id;

/*------------------------------------------------------------
 * Event codes (stable; append-only).
 *------------------------------------------------------------*/
typedef enum core_log_event_code_e {
    CORE_LOG_EVT_OP_BEGIN = 1u,
    CORE_LOG_EVT_OP_OK = 2u,
    CORE_LOG_EVT_OP_FAIL = 3u,
    CORE_LOG_EVT_OP_REFUSED = 4u,
    CORE_LOG_EVT_STATE = 5u
} core_log_event_code;

/*------------------------------------------------------------
 * Scope routing.
 *------------------------------------------------------------*/
typedef enum core_log_scope_kind_e {
    CORE_LOG_SCOPE_GLOBAL = 0u,
    CORE_LOG_SCOPE_INSTANCE = 1u,
    CORE_LOG_SCOPE_RUN = 2u
} core_log_scope_kind;

typedef struct core_log_scope_t {
    u32 kind;               /* core_log_scope_kind */
    const char* instance_id;/* optional; scope-specific */
    u64 run_id;             /* optional; scope-specific */
    const char* state_root; /* optional; overrides default state root for routing */
} core_log_scope;

/*------------------------------------------------------------
 * Event + field POD.
 *------------------------------------------------------------*/
typedef struct core_log_field_t {
    u32 key_id;
    u8  type;
    u8  flags;
    u16 reserved;
    union {
        u32 u32_value;
        u64 u64_value;
        char path[CORE_LOG_MAX_PATH];
    } v;
} core_log_field;

typedef struct core_log_event_t {
    u16 domain;       /* core_log_domain */
    u16 code;         /* core_log_event_code or domain-specific */
    u8  severity;     /* core_log_severity */
    u8  flags;        /* core_log_event_flags */
    u16 reserved;
    u32 msg_id;       /* optional; may reuse err_msg_id */
    u64 t_mono;       /* monotonic timestamp (0 if unknown) */
    u32 field_count;
    core_log_field fields[CORE_LOG_MAX_FIELDS];
} core_log_event;

/*------------------------------------------------------------
 * Log sink interface (C ABI).
 *------------------------------------------------------------*/
#define CORE_LOG_SINK_ABI_VERSION 1u
typedef struct core_log_sink_v1 {
    DOM_ABI_HEADER;
    void* user;
    dom_abi_result (*emit_event)(void* user, const core_log_scope* scope, const core_log_event* ev);
} core_log_sink_v1;

/*------------------------------------------------------------
 * Helpers.
 *------------------------------------------------------------*/
void core_log_event_clear(core_log_event* ev);
dom_abi_result core_log_event_add_u32(core_log_event* ev, u32 key_id, u32 value);
dom_abi_result core_log_event_add_u64(core_log_event* ev, u32 key_id, u64 value);
dom_abi_result core_log_event_add_bool(core_log_event* ev, u32 key_id, u32 value);
dom_abi_result core_log_event_add_msg_id(core_log_event* ev, u32 key_id, u32 msg_id);
dom_abi_result core_log_event_add_hash64(core_log_event* ev, u32 key_id, u64 hash64);
dom_abi_result core_log_event_add_path_rel(core_log_event* ev, u32 key_id, const char* rel_path);
dom_abi_result core_log_event_add_path_redacted(core_log_event* ev, u32 key_id);

/* Path helpers: returns 1 on success; 0 if not under root. */
int core_log_path_make_relative(const char* root, const char* path, char* out_rel, u32 out_cap, u32 case_insensitive);

/*------------------------------------------------------------
 * TLV encoding (deterministic; canonical order).
 *------------------------------------------------------------*/
typedef dom_abi_result (*core_log_write_fn)(void* user, const void* data, u32 len);

typedef struct core_log_write_sink_t {
    void* user;
    core_log_write_fn write;
} core_log_write_sink;

dom_abi_result core_log_event_write_tlv(const core_log_event* ev, const core_log_write_sink* sink);
dom_abi_result core_log_event_read_tlv(const unsigned char* data, u32 size, core_log_event* out_ev, u32* out_used);
u32 core_log_event_encoded_size(const core_log_event* ev);

/* Stable hash helper for identifiers. */
u64 core_log_hash64(const void* data, u32 len);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_CORE_LOG_H */
