/*
FILE: include/dominium/core_caps.h
MODULE: Dominium
PURPOSE: Typed capability catalog (stable keys + values + deterministic helpers).
NOTES: Key IDs are append-only and never renumbered.
*/
#ifndef DOMINIUM_CORE_CAPS_H
#define DOMINIUM_CORE_CAPS_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/*------------------------------------------------------------
 * Limits (fixed; append-only if changed).
 *------------------------------------------------------------*/
#define CORE_CAPS_MAX_ENTRIES 64u

/*------------------------------------------------------------
 * Capability types (stable; append-only).
 *------------------------------------------------------------*/
typedef enum core_cap_type_e {
    CORE_CAP_BOOL = 1u,
    CORE_CAP_I32 = 2u,
    CORE_CAP_U32 = 3u,
    CORE_CAP_I64 = 4u,
    CORE_CAP_U64 = 5u,
    CORE_CAP_STRING_ID = 6u,
    CORE_CAP_RANGE_U32 = 7u,
    CORE_CAP_ENUM_ID = 8u
} core_cap_type;

typedef struct core_cap_range_u32_t {
    u32 min_value;
    u32 max_value;
} core_cap_range_u32;

typedef union core_cap_value_u {
    u32 bool_value;
    i32 i32_value;
    u32 u32_value;
    i64 i64_value;
    u64 u64_value;
    u32 string_id;
    u32 enum_id;
    core_cap_range_u32 range_u32;
} core_cap_value;

typedef struct core_cap_entry_t {
    u32 key_id;
    u8 type;
    u8 reserved;
    u16 reserved2;
    core_cap_value v;
} core_cap_entry;

typedef struct core_caps_t {
    u32 count;
    core_cap_entry entries[CORE_CAPS_MAX_ENTRIES];
} core_caps;

/*------------------------------------------------------------
 * Capability keys (stable numeric IDs; append-only).
 *------------------------------------------------------------*/
typedef enum core_cap_key_e {
    CORE_CAP_KEY_NONE = 0u,
    CORE_CAP_KEY_SUPPORTS_GUI_NATIVE_WIDGETS = 1u,
    CORE_CAP_KEY_SUPPORTS_GUI_DGFX = 2u,
    CORE_CAP_KEY_SUPPORTS_TUI = 3u,
    CORE_CAP_KEY_SUPPORTS_CLI = 4u,
    CORE_CAP_KEY_SUPPORTS_TLS = 5u,
    CORE_CAP_KEY_SUPPORTS_KEYCHAIN = 6u,
    CORE_CAP_KEY_SUPPORTS_STDOUT_CAPTURE = 7u,
    CORE_CAP_KEY_SUPPORTS_FILE_PICKER = 8u,
    CORE_CAP_KEY_SUPPORTS_OPEN_FOLDER = 9u,
    CORE_CAP_KEY_FS_PERMISSIONS_MODEL = 10u,
    CORE_CAP_KEY_OS_FAMILY = 11u,
    CORE_CAP_KEY_OS_VERSION_MAJOR = 12u,
    CORE_CAP_KEY_OS_VERSION_MINOR = 13u,
    CORE_CAP_KEY_CPU_ARCH = 14u,
    CORE_CAP_KEY_OS_IS_WIN32 = 15u,
    CORE_CAP_KEY_OS_IS_UNIX = 16u,
    CORE_CAP_KEY_OS_IS_APPLE = 17u,
    CORE_CAP_KEY_DETERMINISM_GRADE = 18u,
    CORE_CAP_KEY_PERF_CLASS = 19u,
    CORE_CAP_KEY_BACKEND_PRIORITY = 20u,
    CORE_CAP_KEY_SUBSYSTEM_ID = 21u
} core_cap_key;

/*------------------------------------------------------------
 * Common enum values (stable).
 *------------------------------------------------------------*/
typedef enum core_cap_os_family_e {
    CORE_CAP_OS_UNKNOWN = 0u,
    CORE_CAP_OS_WIN32 = 1u,
    CORE_CAP_OS_UNIX = 2u,
    CORE_CAP_OS_APPLE = 3u
} core_cap_os_family;

typedef enum core_cap_arch_e {
    CORE_CAP_ARCH_UNKNOWN = 0u,
    CORE_CAP_ARCH_X86_32 = 1u,
    CORE_CAP_ARCH_X86_64 = 2u,
    CORE_CAP_ARCH_ARM_32 = 3u,
    CORE_CAP_ARCH_ARM_64 = 4u
} core_cap_arch;

typedef enum core_cap_fs_perm_model_e {
    CORE_CAP_FS_PERM_UNKNOWN = 0u,
    CORE_CAP_FS_PERM_USER = 1u,
    CORE_CAP_FS_PERM_SYSTEM = 2u,
    CORE_CAP_FS_PERM_MIXED = 3u
} core_cap_fs_perm_model;

typedef enum core_cap_det_grade_e {
    CORE_CAP_DET_D0_BIT_EXACT = 0u,
    CORE_CAP_DET_D1_TICK_EXACT = 1u,
    CORE_CAP_DET_D2_BEST_EFFORT = 2u
} core_cap_det_grade;

typedef enum core_cap_perf_class_e {
    CORE_CAP_PERF_BASELINE = 0u,
    CORE_CAP_PERF_COMPAT = 1u,
    CORE_CAP_PERF_PERF = 2u
} core_cap_perf_class;

/*------------------------------------------------------------
 * Result codes.
 *------------------------------------------------------------*/
typedef enum core_caps_result_e {
    CORE_CAPS_OK = 0,
    CORE_CAPS_ERR_NULL = -1,
    CORE_CAPS_ERR_FULL = -2,
    CORE_CAPS_ERR_BAD_TYPE = -3
} core_caps_result;

/*------------------------------------------------------------
 * Helpers (C89 compatible; no allocation).
 *------------------------------------------------------------*/
void core_caps_clear(core_caps* caps);
core_caps_result core_caps_set_bool(core_caps* caps, u32 key_id, u32 value);
core_caps_result core_caps_set_i32(core_caps* caps, u32 key_id, i32 value);
core_caps_result core_caps_set_u32(core_caps* caps, u32 key_id, u32 value);
core_caps_result core_caps_set_i64(core_caps* caps, u32 key_id, i64 value);
core_caps_result core_caps_set_u64(core_caps* caps, u32 key_id, u64 value);
core_caps_result core_caps_set_enum(core_caps* caps, u32 key_id, u32 value);
core_caps_result core_caps_set_string_id(core_caps* caps, u32 key_id, u32 value);
core_caps_result core_caps_set_range_u32(core_caps* caps, u32 key_id, u32 min_v, u32 max_v);

int core_caps_get_bool(const core_caps* caps, u32 key_id, u32* out_value);
int core_caps_get_i32(const core_caps* caps, u32 key_id, i32* out_value);
int core_caps_get_u32(const core_caps* caps, u32 key_id, u32* out_value);
int core_caps_get_i64(const core_caps* caps, u32 key_id, i64* out_value);
int core_caps_get_u64(const core_caps* caps, u32 key_id, u64* out_value);
int core_caps_get_enum(const core_caps* caps, u32 key_id, u32* out_value);
int core_caps_get_string_id(const core_caps* caps, u32 key_id, u32* out_value);
int core_caps_get_range_u32(const core_caps* caps, u32 key_id, u32* out_min, u32* out_max);

int core_caps_merge(core_caps* dst, const core_caps* src);
int core_caps_compare(const core_caps* a, const core_caps* b);

const char* core_caps_key_token(u32 key_id);
const char* core_caps_type_token(u32 type_id);
const char* core_caps_enum_token(u32 key_id, u32 enum_value);

/*------------------------------------------------------------
 * TLV encoding (deterministic; canonical order).
 *------------------------------------------------------------*/
typedef dom_abi_result (*core_caps_write_fn)(void* user, const void* data, u32 len);

typedef struct core_caps_write_sink_t {
    void* user;
    core_caps_write_fn write;
} core_caps_write_sink;

dom_abi_result core_caps_write_tlv(const core_caps* caps, const core_caps_write_sink* sink);
dom_abi_result core_caps_read_tlv(const unsigned char* data, u32 size, core_caps* out_caps, u32* out_used);
u32 core_caps_encoded_size(const core_caps* caps);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_CORE_CAPS_H */
