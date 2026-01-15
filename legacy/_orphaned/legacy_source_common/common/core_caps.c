/*
FILE: source/dominium/common/core_caps.c
MODULE: Dominium
PURPOSE: Implements typed capability catalog helpers and deterministic TLV encoding.
*/
#include "dominium/core_caps.h"

#include <string.h>

enum {
    CORE_CAPS_TLV_VERSION = 1u
};

enum {
    CORE_CAPS_TLV_TAG_SCHEMA_VERSION = 1u,
    CORE_CAPS_TLV_TAG_ENTRY = 2u
};

enum {
    CORE_CAPS_ENTRY_TAG_KEY_ID = 1u,
    CORE_CAPS_ENTRY_TAG_TYPE = 2u,
    CORE_CAPS_ENTRY_TAG_VALUE_U32 = 3u,
    CORE_CAPS_ENTRY_TAG_VALUE_I32 = 4u,
    CORE_CAPS_ENTRY_TAG_VALUE_U64 = 5u,
    CORE_CAPS_ENTRY_TAG_VALUE_I64 = 6u,
    CORE_CAPS_ENTRY_TAG_RANGE_U32_MIN = 7u,
    CORE_CAPS_ENTRY_TAG_RANGE_U32_MAX = 8u
};

static void caps_write_u32_le(unsigned char out[4], u32 v) {
    out[0] = (unsigned char)(v & 0xFFu);
    out[1] = (unsigned char)((v >> 8u) & 0xFFu);
    out[2] = (unsigned char)((v >> 16u) & 0xFFu);
    out[3] = (unsigned char)((v >> 24u) & 0xFFu);
}

static void caps_write_u64_le(unsigned char out[8], u64 v) {
    out[0] = (unsigned char)(v & 0xFFu);
    out[1] = (unsigned char)((v >> 8u) & 0xFFu);
    out[2] = (unsigned char)((v >> 16u) & 0xFFu);
    out[3] = (unsigned char)((v >> 24u) & 0xFFu);
    out[4] = (unsigned char)((v >> 32u) & 0xFFu);
    out[5] = (unsigned char)((v >> 40u) & 0xFFu);
    out[6] = (unsigned char)((v >> 48u) & 0xFFu);
    out[7] = (unsigned char)((v >> 56u) & 0xFFu);
}

static int caps_read_u32_le(const unsigned char* data, u32 len, u32* out_v) {
    if (!data || len != 4u || !out_v) {
        return 0;
    }
    *out_v = (u32)data[0] |
             ((u32)data[1] << 8u) |
             ((u32)data[2] << 16u) |
             ((u32)data[3] << 24u);
    return 1;
}

static int caps_read_i32_le(const unsigned char* data, u32 len, i32* out_v) {
    u32 v;
    if (!caps_read_u32_le(data, len, &v) || !out_v) {
        return 0;
    }
    *out_v = (i32)v;
    return 1;
}

static int caps_read_u64_le(const unsigned char* data, u32 len, u64* out_v) {
    if (!data || len != 8u || !out_v) {
        return 0;
    }
    *out_v = (u64)data[0] |
             ((u64)data[1] << 8u) |
             ((u64)data[2] << 16u) |
             ((u64)data[3] << 24u) |
             ((u64)data[4] << 32u) |
             ((u64)data[5] << 40u) |
             ((u64)data[6] << 48u) |
             ((u64)data[7] << 56u);
    return 1;
}

static int caps_read_i64_le(const unsigned char* data, u32 len, i64* out_v) {
    u64 v;
    if (!caps_read_u64_le(data, len, &v) || !out_v) {
        return 0;
    }
    *out_v = (i64)v;
    return 1;
}

static int caps_key_cmp(u32 a, u32 b) {
    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
}

static int caps_value_cmp(u8 type, const core_cap_value* a, const core_cap_value* b) {
    if (!a || !b) {
        return 0;
    }
    switch (type) {
    case CORE_CAP_BOOL:
    case CORE_CAP_U32:
    case CORE_CAP_ENUM_ID:
    case CORE_CAP_STRING_ID:
        if (a->u32_value < b->u32_value) return -1;
        if (a->u32_value > b->u32_value) return 1;
        return 0;
    case CORE_CAP_I32:
        if (a->i32_value < b->i32_value) return -1;
        if (a->i32_value > b->i32_value) return 1;
        return 0;
    case CORE_CAP_U64:
        if (a->u64_value < b->u64_value) return -1;
        if (a->u64_value > b->u64_value) return 1;
        return 0;
    case CORE_CAP_I64:
        if (a->i64_value < b->i64_value) return -1;
        if (a->i64_value > b->i64_value) return 1;
        return 0;
    case CORE_CAP_RANGE_U32:
        if (a->range_u32.min_value < b->range_u32.min_value) return -1;
        if (a->range_u32.min_value > b->range_u32.min_value) return 1;
        if (a->range_u32.max_value < b->range_u32.max_value) return -1;
        if (a->range_u32.max_value > b->range_u32.max_value) return 1;
        return 0;
    default:
        break;
    }
    return 0;
}

static int caps_entry_cmp(const core_cap_entry* a, const core_cap_entry* b) {
    int kc;
    if (!a || !b) return 0;
    kc = caps_key_cmp(a->key_id, b->key_id);
    if (kc != 0) return kc;
    if (a->type < b->type) return -1;
    if (a->type > b->type) return 1;
    return caps_value_cmp(a->type, &a->v, &b->v);
}

static int caps_find_index(const core_caps* caps, u32 key_id, u32* out_idx) {
    u32 i;
    if (!caps || !out_idx) {
        return 0;
    }
    for (i = 0u; i < caps->count; ++i) {
        if (caps->entries[i].key_id == key_id) {
            *out_idx = i;
            return 1;
        }
        if (caps->entries[i].key_id > key_id) {
            break;
        }
    }
    return 0;
}

static core_caps_result caps_insert_entry(core_caps* caps, const core_cap_entry* entry) {
    u32 i;
    u32 pos;
    if (!caps || !entry) {
        return CORE_CAPS_ERR_NULL;
    }
    if (caps->count >= CORE_CAPS_MAX_ENTRIES) {
        return CORE_CAPS_ERR_FULL;
    }
    pos = caps->count;
    for (i = 0u; i < caps->count; ++i) {
        if (caps->entries[i].key_id > entry->key_id) {
            pos = i;
            break;
        }
    }
    for (i = caps->count; i > pos; --i) {
        caps->entries[i] = caps->entries[i - 1u];
    }
    caps->entries[pos] = *entry;
    caps->count += 1u;
    return CORE_CAPS_OK;
}

void core_caps_clear(core_caps* caps) {
    if (!caps) {
        return;
    }
    caps->count = 0u;
    memset(caps->entries, 0, sizeof(caps->entries));
}

static core_caps_result caps_set_entry(core_caps* caps, u32 key_id, u8 type, const core_cap_value* v) {
    u32 idx;
    core_cap_entry e;
    if (!caps || !v) {
        return CORE_CAPS_ERR_NULL;
    }
    if (caps_find_index(caps, key_id, &idx)) {
        caps->entries[idx].type = type;
        caps->entries[idx].v = *v;
        return CORE_CAPS_OK;
    }
    memset(&e, 0, sizeof(e));
    e.key_id = key_id;
    e.type = type;
    e.v = *v;
    return caps_insert_entry(caps, &e);
}

core_caps_result core_caps_set_bool(core_caps* caps, u32 key_id, u32 value) {
    core_cap_value v;
    v.bool_value = value ? 1u : 0u;
    return caps_set_entry(caps, key_id, (u8)CORE_CAP_BOOL, &v);
}

core_caps_result core_caps_set_i32(core_caps* caps, u32 key_id, i32 value) {
    core_cap_value v;
    v.i32_value = value;
    return caps_set_entry(caps, key_id, (u8)CORE_CAP_I32, &v);
}

core_caps_result core_caps_set_u32(core_caps* caps, u32 key_id, u32 value) {
    core_cap_value v;
    v.u32_value = value;
    return caps_set_entry(caps, key_id, (u8)CORE_CAP_U32, &v);
}

core_caps_result core_caps_set_i64(core_caps* caps, u32 key_id, i64 value) {
    core_cap_value v;
    v.i64_value = value;
    return caps_set_entry(caps, key_id, (u8)CORE_CAP_I64, &v);
}

core_caps_result core_caps_set_u64(core_caps* caps, u32 key_id, u64 value) {
    core_cap_value v;
    v.u64_value = value;
    return caps_set_entry(caps, key_id, (u8)CORE_CAP_U64, &v);
}

core_caps_result core_caps_set_enum(core_caps* caps, u32 key_id, u32 value) {
    core_cap_value v;
    v.enum_id = value;
    return caps_set_entry(caps, key_id, (u8)CORE_CAP_ENUM_ID, &v);
}

core_caps_result core_caps_set_string_id(core_caps* caps, u32 key_id, u32 value) {
    core_cap_value v;
    v.string_id = value;
    return caps_set_entry(caps, key_id, (u8)CORE_CAP_STRING_ID, &v);
}

core_caps_result core_caps_set_range_u32(core_caps* caps, u32 key_id, u32 min_v, u32 max_v) {
    core_cap_value v;
    v.range_u32.min_value = min_v;
    v.range_u32.max_value = max_v;
    return caps_set_entry(caps, key_id, (u8)CORE_CAP_RANGE_U32, &v);
}

static int caps_get_entry(const core_caps* caps, u32 key_id, u8 expected_type, core_cap_value* out_v) {
    u32 idx;
    if (!caps || !out_v) {
        return 0;
    }
    if (!caps_find_index(caps, key_id, &idx)) {
        return 0;
    }
    if (caps->entries[idx].type != expected_type) {
        return 0;
    }
    *out_v = caps->entries[idx].v;
    return 1;
}

int core_caps_get_bool(const core_caps* caps, u32 key_id, u32* out_value) {
    core_cap_value v;
    if (!out_value) return 0;
    if (!caps_get_entry(caps, key_id, (u8)CORE_CAP_BOOL, &v)) return 0;
    *out_value = v.bool_value;
    return 1;
}

int core_caps_get_i32(const core_caps* caps, u32 key_id, i32* out_value) {
    core_cap_value v;
    if (!out_value) return 0;
    if (!caps_get_entry(caps, key_id, (u8)CORE_CAP_I32, &v)) return 0;
    *out_value = v.i32_value;
    return 1;
}

int core_caps_get_u32(const core_caps* caps, u32 key_id, u32* out_value) {
    core_cap_value v;
    if (!out_value) return 0;
    if (!caps_get_entry(caps, key_id, (u8)CORE_CAP_U32, &v)) return 0;
    *out_value = v.u32_value;
    return 1;
}

int core_caps_get_i64(const core_caps* caps, u32 key_id, i64* out_value) {
    core_cap_value v;
    if (!out_value) return 0;
    if (!caps_get_entry(caps, key_id, (u8)CORE_CAP_I64, &v)) return 0;
    *out_value = v.i64_value;
    return 1;
}

int core_caps_get_u64(const core_caps* caps, u32 key_id, u64* out_value) {
    core_cap_value v;
    if (!out_value) return 0;
    if (!caps_get_entry(caps, key_id, (u8)CORE_CAP_U64, &v)) return 0;
    *out_value = v.u64_value;
    return 1;
}

int core_caps_get_enum(const core_caps* caps, u32 key_id, u32* out_value) {
    core_cap_value v;
    if (!out_value) return 0;
    if (!caps_get_entry(caps, key_id, (u8)CORE_CAP_ENUM_ID, &v)) return 0;
    *out_value = v.enum_id;
    return 1;
}

int core_caps_get_string_id(const core_caps* caps, u32 key_id, u32* out_value) {
    core_cap_value v;
    if (!out_value) return 0;
    if (!caps_get_entry(caps, key_id, (u8)CORE_CAP_STRING_ID, &v)) return 0;
    *out_value = v.string_id;
    return 1;
}

int core_caps_get_range_u32(const core_caps* caps, u32 key_id, u32* out_min, u32* out_max) {
    core_cap_value v;
    if (!out_min || !out_max) return 0;
    if (!caps_get_entry(caps, key_id, (u8)CORE_CAP_RANGE_U32, &v)) return 0;
    *out_min = v.range_u32.min_value;
    *out_max = v.range_u32.max_value;
    return 1;
}

int core_caps_merge(core_caps* dst, const core_caps* src) {
    u32 i;
    if (!dst || !src) {
        return 0;
    }
    for (i = 0u; i < src->count; ++i) {
        const core_cap_entry* e = &src->entries[i];
        if (!e) continue;
        switch (e->type) {
        case CORE_CAP_BOOL:
            if (core_caps_set_bool(dst, e->key_id, e->v.bool_value) != CORE_CAPS_OK) return 0;
            break;
        case CORE_CAP_I32:
            if (core_caps_set_i32(dst, e->key_id, e->v.i32_value) != CORE_CAPS_OK) return 0;
            break;
        case CORE_CAP_U32:
            if (core_caps_set_u32(dst, e->key_id, e->v.u32_value) != CORE_CAPS_OK) return 0;
            break;
        case CORE_CAP_I64:
            if (core_caps_set_i64(dst, e->key_id, e->v.i64_value) != CORE_CAPS_OK) return 0;
            break;
        case CORE_CAP_U64:
            if (core_caps_set_u64(dst, e->key_id, e->v.u64_value) != CORE_CAPS_OK) return 0;
            break;
        case CORE_CAP_ENUM_ID:
            if (core_caps_set_enum(dst, e->key_id, e->v.enum_id) != CORE_CAPS_OK) return 0;
            break;
        case CORE_CAP_STRING_ID:
            if (core_caps_set_string_id(dst, e->key_id, e->v.string_id) != CORE_CAPS_OK) return 0;
            break;
        case CORE_CAP_RANGE_U32:
            if (core_caps_set_range_u32(dst, e->key_id, e->v.range_u32.min_value, e->v.range_u32.max_value) != CORE_CAPS_OK) return 0;
            break;
        default:
            return 0;
        }
    }
    return 1;
}

int core_caps_compare(const core_caps* a, const core_caps* b) {
    u32 i;
    if (!a || !b) {
        return 0;
    }
    if (a->count < b->count) return -1;
    if (a->count > b->count) return 1;
    for (i = 0u; i < a->count; ++i) {
        int c = caps_entry_cmp(&a->entries[i], &b->entries[i]);
        if (c != 0) return c;
    }
    return 0;
}

const char* core_caps_key_token(u32 key_id) {
    switch (key_id) {
    case CORE_CAP_KEY_SUPPORTS_GUI_NATIVE_WIDGETS: return "supports_gui_native_widgets";
    case CORE_CAP_KEY_SUPPORTS_GUI_DGFX: return "supports_gui_dgfx";
    case CORE_CAP_KEY_SUPPORTS_TUI: return "supports_tui";
    case CORE_CAP_KEY_SUPPORTS_CLI: return "supports_cli";
    case CORE_CAP_KEY_SUPPORTS_TLS: return "supports_tls";
    case CORE_CAP_KEY_SUPPORTS_KEYCHAIN: return "supports_keychain";
    case CORE_CAP_KEY_SUPPORTS_STDOUT_CAPTURE: return "supports_stdout_capture";
    case CORE_CAP_KEY_SUPPORTS_FILE_PICKER: return "supports_file_picker";
    case CORE_CAP_KEY_SUPPORTS_OPEN_FOLDER: return "supports_open_folder";
    case CORE_CAP_KEY_FS_PERMISSIONS_MODEL: return "fs_permissions_model";
    case CORE_CAP_KEY_OS_FAMILY: return "os_family";
    case CORE_CAP_KEY_OS_VERSION_MAJOR: return "os_version_major";
    case CORE_CAP_KEY_OS_VERSION_MINOR: return "os_version_minor";
    case CORE_CAP_KEY_CPU_ARCH: return "arch";
    case CORE_CAP_KEY_OS_IS_WIN32: return "os_is_win32";
    case CORE_CAP_KEY_OS_IS_UNIX: return "os_is_unix";
    case CORE_CAP_KEY_OS_IS_APPLE: return "os_is_apple";
    case CORE_CAP_KEY_DETERMINISM_GRADE: return "determinism_grade";
    case CORE_CAP_KEY_PERF_CLASS: return "perf_class";
    case CORE_CAP_KEY_BACKEND_PRIORITY: return "backend_priority";
    case CORE_CAP_KEY_SUBSYSTEM_ID: return "subsystem_id";
    case CORE_CAP_KEY_SETUP_TARGET_OK: return "setup_target_ok";
    case CORE_CAP_KEY_SETUP_SCOPE_OK: return "setup_scope_ok";
    case CORE_CAP_KEY_SETUP_UI_OK: return "setup_ui_ok";
    case CORE_CAP_KEY_SETUP_OWNERSHIP_OK: return "setup_ownership_ok";
    case CORE_CAP_KEY_SETUP_MANIFEST_ALLOWLIST_OK: return "setup_manifest_allowlist_ok";
    case CORE_CAP_KEY_SETUP_REQUIRED_CAPS_OK: return "setup_required_caps_ok";
    case CORE_CAP_KEY_SETUP_PROHIBITED_CAPS_OK: return "setup_prohibited_caps_ok";
    case CORE_CAP_KEY_SETUP_MANIFEST_TARGET_OK: return "setup_manifest_target_ok";
    case CORE_CAP_KEY_SUPPORTS_NETWORK: return "supports_network";
    case CORE_CAP_KEY_SUPPORTS_OFFLINE: return "supports_offline";
    case CORE_CAP_KEY_SUPPORTS_TRUST: return "supports_trust";
    default: break;
    }
    return "unknown";
}

const char* core_caps_type_token(u32 type_id) {
    switch (type_id) {
    case CORE_CAP_BOOL: return "bool";
    case CORE_CAP_I32: return "i32";
    case CORE_CAP_U32: return "u32";
    case CORE_CAP_I64: return "i64";
    case CORE_CAP_U64: return "u64";
    case CORE_CAP_STRING_ID: return "string_id";
    case CORE_CAP_RANGE_U32: return "range_u32";
    case CORE_CAP_ENUM_ID: return "enum_id";
    default: break;
    }
    return "unknown";
}

const char* core_caps_enum_token(u32 key_id, u32 enum_value) {
    switch (key_id) {
    case CORE_CAP_KEY_OS_FAMILY:
        switch (enum_value) {
        case CORE_CAP_OS_WIN32: return "win32";
        case CORE_CAP_OS_UNIX: return "unix";
        case CORE_CAP_OS_APPLE: return "apple";
        default: break;
        }
        return "unknown";
    case CORE_CAP_KEY_CPU_ARCH:
        switch (enum_value) {
        case CORE_CAP_ARCH_X86_32: return "x86_32";
        case CORE_CAP_ARCH_X86_64: return "x86_64";
        case CORE_CAP_ARCH_ARM_32: return "arm_32";
        case CORE_CAP_ARCH_ARM_64: return "arm_64";
        default: break;
        }
        return "unknown";
    case CORE_CAP_KEY_FS_PERMISSIONS_MODEL:
        switch (enum_value) {
        case CORE_CAP_FS_PERM_USER: return "user";
        case CORE_CAP_FS_PERM_SYSTEM: return "system";
        case CORE_CAP_FS_PERM_MIXED: return "mixed";
        default: break;
        }
        return "unknown";
    case CORE_CAP_KEY_DETERMINISM_GRADE:
        switch (enum_value) {
        case CORE_CAP_DET_D0_BIT_EXACT: return "D0";
        case CORE_CAP_DET_D1_TICK_EXACT: return "D1";
        case CORE_CAP_DET_D2_BEST_EFFORT: return "D2";
        default: break;
        }
        return "D2";
    case CORE_CAP_KEY_PERF_CLASS:
        switch (enum_value) {
        case CORE_CAP_PERF_BASELINE: return "baseline";
        case CORE_CAP_PERF_COMPAT: return "compat";
        case CORE_CAP_PERF_PERF: return "perf";
        default: break;
        }
        return "baseline";
    default:
        break;
    }
    return "unknown";
}

static dom_abi_result caps_sink_write(const core_caps_write_sink* sink,
                                      const unsigned char* data,
                                      u32 len) {
    if (!sink || !sink->write) {
        return (dom_abi_result)-1;
    }
    return sink->write(sink->user, data, len);
}

static dom_abi_result caps_write_record(const core_caps_write_sink* sink,
                                        u32 tag,
                                        const unsigned char* payload,
                                        u32 len) {
    unsigned char hdr[8];
    if (!sink) {
        return (dom_abi_result)-1;
    }
    caps_write_u32_le(hdr, tag);
    caps_write_u32_le(hdr + 4, len);
    if (caps_sink_write(sink, hdr, 8u) != 0) {
        return (dom_abi_result)-1;
    }
    if (len > 0u && payload) {
        if (caps_sink_write(sink, payload, len) != 0) {
            return (dom_abi_result)-1;
        }
    }
    return 0;
}

static u32 caps_entry_payload_size(const core_cap_entry* e) {
    u32 size = 0u;
    if (!e) return 0u;
    size += 8u + 4u; /* key_id */
    size += 8u + 4u; /* type */
    switch (e->type) {
    case CORE_CAP_BOOL:
    case CORE_CAP_U32:
    case CORE_CAP_ENUM_ID:
    case CORE_CAP_STRING_ID:
        size += 8u + 4u;
        break;
    case CORE_CAP_I32:
        size += 8u + 4u;
        break;
    case CORE_CAP_U64:
        size += 8u + 8u;
        break;
    case CORE_CAP_I64:
        size += 8u + 8u;
        break;
    case CORE_CAP_RANGE_U32:
        size += 8u + 4u;
        size += 8u + 4u;
        break;
    default:
        break;
    }
    return size;
}

u32 core_caps_encoded_size(const core_caps* caps) {
    u32 size = 0u;
    u32 i;
    if (!caps) return 0u;
    size += 8u + 4u; /* schema version */
    for (i = 0u; i < caps->count; ++i) {
        size += 8u; /* entry header */
        size += caps_entry_payload_size(&caps->entries[i]);
    }
    return size;
}

static dom_abi_result caps_write_entry(const core_caps_write_sink* sink,
                                       const core_cap_entry* e) {
    unsigned char buf[96];
    u32 off = 0u;
    unsigned char tmp[8];
    u32 len = 0u;
    if (!sink || !e) {
        return (dom_abi_result)-1;
    }
    len = caps_entry_payload_size(e);
    if (len > (u32)sizeof(buf)) {
        return (dom_abi_result)-1;
    }

    caps_write_u32_le(tmp, CORE_CAPS_ENTRY_TAG_KEY_ID);
    memcpy(buf + off, tmp, 4u);
    off += 4u;
    caps_write_u32_le(tmp, 4u);
    memcpy(buf + off, tmp, 4u);
    off += 4u;
    caps_write_u32_le(tmp, e->key_id);
    memcpy(buf + off, tmp, 4u);
    off += 4u;

    caps_write_u32_le(tmp, CORE_CAPS_ENTRY_TAG_TYPE);
    memcpy(buf + off, tmp, 4u);
    off += 4u;
    caps_write_u32_le(tmp, 4u);
    memcpy(buf + off, tmp, 4u);
    off += 4u;
    caps_write_u32_le(tmp, (u32)e->type);
    memcpy(buf + off, tmp, 4u);
    off += 4u;

    switch (e->type) {
    case CORE_CAP_BOOL:
    case CORE_CAP_U32:
    case CORE_CAP_ENUM_ID:
    case CORE_CAP_STRING_ID:
        caps_write_u32_le(tmp, CORE_CAPS_ENTRY_TAG_VALUE_U32);
        memcpy(buf + off, tmp, 4u);
        off += 4u;
        caps_write_u32_le(tmp, 4u);
        memcpy(buf + off, tmp, 4u);
        off += 4u;
        caps_write_u32_le(tmp, e->v.u32_value);
        memcpy(buf + off, tmp, 4u);
        off += 4u;
        break;
    case CORE_CAP_I32:
        caps_write_u32_le(tmp, CORE_CAPS_ENTRY_TAG_VALUE_I32);
        memcpy(buf + off, tmp, 4u);
        off += 4u;
        caps_write_u32_le(tmp, 4u);
        memcpy(buf + off, tmp, 4u);
        off += 4u;
        caps_write_u32_le(tmp, (u32)e->v.i32_value);
        memcpy(buf + off, tmp, 4u);
        off += 4u;
        break;
    case CORE_CAP_U64:
        caps_write_u32_le(tmp, CORE_CAPS_ENTRY_TAG_VALUE_U64);
        memcpy(buf + off, tmp, 4u);
        off += 4u;
        caps_write_u32_le(tmp, 8u);
        memcpy(buf + off, tmp, 4u);
        off += 4u;
        caps_write_u64_le(tmp, e->v.u64_value);
        memcpy(buf + off, tmp, 8u);
        off += 8u;
        break;
    case CORE_CAP_I64:
        caps_write_u32_le(tmp, CORE_CAPS_ENTRY_TAG_VALUE_I64);
        memcpy(buf + off, tmp, 4u);
        off += 4u;
        caps_write_u32_le(tmp, 8u);
        memcpy(buf + off, tmp, 4u);
        off += 4u;
        caps_write_u64_le(tmp, (u64)e->v.i64_value);
        memcpy(buf + off, tmp, 8u);
        off += 8u;
        break;
    case CORE_CAP_RANGE_U32:
        caps_write_u32_le(tmp, CORE_CAPS_ENTRY_TAG_RANGE_U32_MIN);
        memcpy(buf + off, tmp, 4u);
        off += 4u;
        caps_write_u32_le(tmp, 4u);
        memcpy(buf + off, tmp, 4u);
        off += 4u;
        caps_write_u32_le(tmp, e->v.range_u32.min_value);
        memcpy(buf + off, tmp, 4u);
        off += 4u;

        caps_write_u32_le(tmp, CORE_CAPS_ENTRY_TAG_RANGE_U32_MAX);
        memcpy(buf + off, tmp, 4u);
        off += 4u;
        caps_write_u32_le(tmp, 4u);
        memcpy(buf + off, tmp, 4u);
        off += 4u;
        caps_write_u32_le(tmp, e->v.range_u32.max_value);
        memcpy(buf + off, tmp, 4u);
        off += 4u;
        break;
    default:
        break;
    }

    return caps_write_record(sink, CORE_CAPS_TLV_TAG_ENTRY, buf, off);
}

dom_abi_result core_caps_write_tlv(const core_caps* caps, const core_caps_write_sink* sink) {
    unsigned char tmp[4];
    u32 i;
    if (!caps || !sink || !sink->write) {
        return (dom_abi_result)-1;
    }
    caps_write_u32_le(tmp, CORE_CAPS_TLV_VERSION);
    if (caps_write_record(sink, CORE_CAPS_TLV_TAG_SCHEMA_VERSION, tmp, 4u) != 0) {
        return (dom_abi_result)-1;
    }
    for (i = 0u; i < caps->count; ++i) {
        if (caps_write_entry(sink, &caps->entries[i]) != 0) {
            return (dom_abi_result)-1;
        }
    }
    return 0;
}

dom_abi_result core_caps_read_tlv(const unsigned char* data, u32 size, core_caps* out_caps, u32* out_used) {
    u32 off = 0u;
    u32 schema_version = 0u;
    int saw_version = 0;
    if (!data || !out_caps) {
        return (dom_abi_result)-1;
    }
    core_caps_clear(out_caps);
    while (off + 8u <= size) {
        u32 tag = 0u;
        u32 len = 0u;
        if (!caps_read_u32_le(data + off, 4u, &tag) ||
            !caps_read_u32_le(data + off + 4u, 4u, &len)) {
            return (dom_abi_result)-1;
        }
        off += 8u;
        if (off + len > size) {
            return (dom_abi_result)-1;
        }
        if (tag == CORE_CAPS_TLV_TAG_SCHEMA_VERSION) {
            if (len == 4u && caps_read_u32_le(data + off, len, &schema_version)) {
                saw_version = 1;
            }
        } else if (tag == CORE_CAPS_TLV_TAG_ENTRY) {
            u32 entry_off = 0u;
            core_cap_entry e;
            int have_key = 0;
            int have_type = 0;
            memset(&e, 0, sizeof(e));
            while (entry_off + 8u <= len) {
                u32 etag = 0u;
                u32 elen = 0u;
                if (!caps_read_u32_le(data + off + entry_off, 4u, &etag) ||
                    !caps_read_u32_le(data + off + entry_off + 4u, 4u, &elen)) {
                    return (dom_abi_result)-1;
                }
                entry_off += 8u;
                if (entry_off + elen > len) {
                    return (dom_abi_result)-1;
                }
                switch (etag) {
                case CORE_CAPS_ENTRY_TAG_KEY_ID:
                    if (caps_read_u32_le(data + off + entry_off, elen, &e.key_id)) {
                        have_key = 1;
                    }
                    break;
                case CORE_CAPS_ENTRY_TAG_TYPE: {
                    u32 v;
                    if (caps_read_u32_le(data + off + entry_off, elen, &v)) {
                        e.type = (u8)v;
                        have_type = 1;
                    }
                    break;
                }
                case CORE_CAPS_ENTRY_TAG_VALUE_U32: {
                    u32 v;
                    if (caps_read_u32_le(data + off + entry_off, elen, &v)) {
                        e.v.u32_value = v;
                    }
                    break;
                }
                case CORE_CAPS_ENTRY_TAG_VALUE_I32: {
                    i32 v;
                    if (caps_read_i32_le(data + off + entry_off, elen, &v)) {
                        e.v.i32_value = v;
                    }
                    break;
                }
                case CORE_CAPS_ENTRY_TAG_VALUE_U64: {
                    u64 v;
                    if (caps_read_u64_le(data + off + entry_off, elen, &v)) {
                        e.v.u64_value = v;
                    }
                    break;
                }
                case CORE_CAPS_ENTRY_TAG_VALUE_I64: {
                    i64 v;
                    if (caps_read_i64_le(data + off + entry_off, elen, &v)) {
                        e.v.i64_value = v;
                    }
                    break;
                }
                case CORE_CAPS_ENTRY_TAG_RANGE_U32_MIN: {
                    u32 v;
                    if (caps_read_u32_le(data + off + entry_off, elen, &v)) {
                        e.v.range_u32.min_value = v;
                    }
                    break;
                }
                case CORE_CAPS_ENTRY_TAG_RANGE_U32_MAX: {
                    u32 v;
                    if (caps_read_u32_le(data + off + entry_off, elen, &v)) {
                        e.v.range_u32.max_value = v;
                    }
                    break;
                }
                default:
                    break;
                }
                entry_off += elen;
            }
            if (have_key && have_type) {
                if (caps_set_entry(out_caps, e.key_id, e.type, &e.v) != CORE_CAPS_OK) {
                    return (dom_abi_result)-1;
                }
            }
        }
        off += len;
    }
    if (out_used) {
        *out_used = off;
    }
    if (saw_version && schema_version != CORE_CAPS_TLV_VERSION) {
        return (dom_abi_result)-1;
    }
    return 0;
}
