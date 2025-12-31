/*
FILE: source/dominium/common/core_err.c
MODULE: Dominium
PURPOSE: Stable error model helpers and message catalog token lookup.
*/
#include "dominium/core_err.h"

#include <string.h>

typedef struct err_msg_token_entry_t {
    u32 id;
    const char* token;
} err_msg_token_entry;

typedef struct err_detail_key_entry_t {
    u32 id;
    const char* token;
} err_detail_key_entry;

static const err_msg_token_entry k_msg_tokens[] = {
    {ERRMSG_NONE, "OK"},

    {ERRMSG_COMMON_INVALID_ARGS, "COMMON.INVALID_ARGS"},
    {ERRMSG_COMMON_OUT_OF_MEMORY, "COMMON.OUT_OF_MEMORY"},
    {ERRMSG_COMMON_NOT_FOUND, "COMMON.NOT_FOUND"},
    {ERRMSG_COMMON_UNSUPPORTED, "COMMON.UNSUPPORTED"},
    {ERRMSG_COMMON_INTERNAL, "COMMON.INTERNAL_ERROR"},
    {ERRMSG_COMMON_BAD_STATE, "COMMON.BAD_STATE"},

    {ERRMSG_TLV_PARSE_FAILED, "TLV.PARSE_FAILED"},
    {ERRMSG_TLV_SCHEMA_VERSION, "TLV.UNSUPPORTED_VERSION"},
    {ERRMSG_TLV_MISSING_FIELD, "TLV.MISSING_FIELD"},
    {ERRMSG_TLV_INTEGRITY, "TLV.INTEGRITY_ERROR"},

    {ERRMSG_FS_OPEN_FAILED, "FS.OPEN_FAILED"},
    {ERRMSG_FS_READ_FAILED, "FS.READ_FAILED"},
    {ERRMSG_FS_WRITE_FAILED, "FS.WRITE_FAILED"},
    {ERRMSG_FS_PATH_INVALID, "FS.PATH_INVALID"},
    {ERRMSG_FS_NOT_FOUND, "FS.NOT_FOUND"},
    {ERRMSG_FS_PERMISSION, "FS.PERMISSION_DENIED"},

    {ERRMSG_PROC_SPAWN_FAILED, "PROC.SPAWN_FAILED"},
    {ERRMSG_PROC_WAIT_FAILED, "PROC.WAIT_FAILED"},

    {ERRMSG_CRYPTO_HASH_MISMATCH, "CRYPTO.HASH_MISMATCH"},
    {ERRMSG_CRYPTO_VERIFY_FAILED, "CRYPTO.VERIFY_FAILED"},

    {ERRMSG_ARCHIVE_OPEN_FAILED, "ARCHIVE.OPEN_FAILED"},
    {ERRMSG_ARCHIVE_EXTRACT_FAILED, "ARCHIVE.EXTRACT_FAILED"},

    {ERRMSG_NET_CONNECT_FAILED, "NET.CONNECT_FAILED"},
    {ERRMSG_NET_TIMEOUT, "NET.TIMEOUT"},
    {ERRMSG_NET_PROTOCOL, "NET.PROTOCOL_ERROR"},

    {ERRMSG_LAUNCHER_INSTANCE_ID_INVALID, "LAUNCHER.INSTANCE.ID_INVALID"},
    {ERRMSG_LAUNCHER_INSTANCE_NOT_FOUND, "LAUNCHER.INSTANCE.NOT_FOUND"},
    {ERRMSG_LAUNCHER_INSTANCE_EXISTS, "LAUNCHER.INSTANCE.ALREADY_EXISTS"},
    {ERRMSG_LAUNCHER_INSTANCE_MANIFEST_INVALID, "LAUNCHER.INSTANCE.MANIFEST_INVALID"},
    {ERRMSG_LAUNCHER_INSTANCE_MANIFEST_WRITE_FAILED, "LAUNCHER.INSTANCE.MANIFEST_WRITE_FAILED"},
    {ERRMSG_LAUNCHER_INSTANCE_PAYLOAD_HASH_MISMATCH, "LAUNCHER.INSTANCE.PAYLOAD_HASH_MISMATCH"},
    {ERRMSG_LAUNCHER_INSTANCE_PAYLOAD_MISSING, "LAUNCHER.INSTANCE.PAYLOAD_MISSING"},
    {ERRMSG_LAUNCHER_STATE_ROOT_UNAVAILABLE, "LAUNCHER.STATE_ROOT.UNAVAILABLE"},
    {ERRMSG_LAUNCHER_INSTANCE_EXPORT_FAILED, "LAUNCHER.INSTANCE.EXPORT_FAILED"},
    {ERRMSG_LAUNCHER_INSTANCE_IMPORT_FAILED, "LAUNCHER.INSTANCE.IMPORT_FAILED"},
    {ERRMSG_LAUNCHER_HANDSHAKE_INVALID, "LAUNCHER.HANDSHAKE.INVALID"},

    {ERRMSG_PACKS_DEPENDENCY_MISSING, "PACKS.DEPENDENCY.MISSING"},
    {ERRMSG_PACKS_DEPENDENCY_CONFLICT, "PACKS.DEPENDENCY.CONFLICT"},
    {ERRMSG_PACKS_PACK_NOT_FOUND, "PACKS.PACK.NOT_FOUND"},
    {ERRMSG_PACKS_PACK_INVALID, "PACKS.PACK.INVALID"},
    {ERRMSG_PACKS_SIM_FLAGS_MISSING, "PACKS.SIM_FLAGS.MISSING"},
    {ERRMSG_PACKS_OFFLINE_REFUSED, "PACKS.OFFLINE_REFUSED"},

    {ERRMSG_ARTIFACT_METADATA_NOT_FOUND, "ARTIFACT.METADATA.NOT_FOUND"},
    {ERRMSG_ARTIFACT_METADATA_INVALID, "ARTIFACT.METADATA.INVALID"},
    {ERRMSG_ARTIFACT_PAYLOAD_MISSING, "ARTIFACT.PAYLOAD.MISSING"},
    {ERRMSG_ARTIFACT_PAYLOAD_HASH_MISMATCH, "ARTIFACT.PAYLOAD.HASH_MISMATCH"},
    {ERRMSG_ARTIFACT_CONTENT_TYPE_MISMATCH, "ARTIFACT.CONTENT_TYPE.MISMATCH"},
    {ERRMSG_ARTIFACT_SIZE_MISMATCH, "ARTIFACT.SIZE.MISMATCH"},

    {ERRMSG_TXN_STAGE_FAILED, "TXN.STAGE.FAILED"},
    {ERRMSG_TXN_COMMIT_FAILED, "TXN.COMMIT.FAILED"},
    {ERRMSG_TXN_ROLLBACK_FAILED, "TXN.ROLLBACK.FAILED"},
    {ERRMSG_TXN_CANCELLED, "TXN.CANCELLED"},

    {ERRMSG_SETUP_INVALID_MANIFEST, "SETUP.MANIFEST.INVALID"},
    {ERRMSG_SETUP_UNSUPPORTED_PLATFORM, "SETUP.PLATFORM.UNSUPPORTED"},
    {ERRMSG_SETUP_DEPENDENCY_CONFLICT, "SETUP.DEPENDENCY.CONFLICT"},
    {ERRMSG_SETUP_OFFLINE_REFUSED, "SETUP.OFFLINE.REFUSED"},
    {ERRMSG_SETUP_INSTALL_FAILED, "SETUP.INSTALL.FAILED"},
    {ERRMSG_SETUP_REPAIR_FAILED, "SETUP.REPAIR.FAILED"},
    {ERRMSG_SETUP_UNINSTALL_FAILED, "SETUP.UNINSTALL.FAILED"},
    {ERRMSG_SETUP_VERIFY_FAILED, "SETUP.VERIFY.FAILED"},
    {ERRMSG_SETUP_PLAN_FAILED, "SETUP.PLAN.FAILED"},
    {ERRMSG_SETUP_APPLY_FAILED, "SETUP.APPLY.FAILED"},
    {ERRMSG_SETUP_RESOLVE_FAILED, "SETUP.RESOLVE.FAILED"},
    {ERRMSG_SETUP_MANIFEST_NOT_FOUND, "SETUP.MANIFEST.NOT_FOUND"}
};

static const err_detail_key_entry k_detail_keys[] = {
    {ERR_DETAIL_KEY_INSTANCE_ID, "instance_id"},
    {ERR_DETAIL_KEY_PROFILE_ID, "profile_id"},
    {ERR_DETAIL_KEY_PACK_ID, "pack_id"},
    {ERR_DETAIL_KEY_PACK_VERSION, "pack_version"},
    {ERR_DETAIL_KEY_ARTIFACT_HASH, "artifact_hash"},
    {ERR_DETAIL_KEY_EXPECTED_HASH64, "expected_hash64"},
    {ERR_DETAIL_KEY_ACTUAL_HASH64, "actual_hash64"},
    {ERR_DETAIL_KEY_PATH_HASH64, "path_hash64"},
    {ERR_DETAIL_KEY_STATE_ROOT_HASH64, "state_root_hash64"},
    {ERR_DETAIL_KEY_MANIFEST_HASH64, "manifest_hash64"},
    {ERR_DETAIL_KEY_COMPONENT_ID, "component_id"},
    {ERR_DETAIL_KEY_OPERATION, "operation"},
    {ERR_DETAIL_KEY_PLATFORM_ID, "platform_id"},
    {ERR_DETAIL_KEY_STAGE, "stage"},
    {ERR_DETAIL_KEY_TXN_STEP, "txn_step"},
    {ERR_DETAIL_KEY_OFFLINE_MODE, "offline_mode"},
    {ERR_DETAIL_KEY_STATUS_CODE, "status_code"},
    {ERR_DETAIL_KEY_SCHEMA_VERSION, "schema_version"},
    {ERR_DETAIL_KEY_REQUIRED_FIELD, "required_field"},
    {ERR_DETAIL_KEY_EXPORT_ROOT_HASH64, "export_root_hash64"},
    {ERR_DETAIL_KEY_IMPORT_ROOT_HASH64, "import_root_hash64"},
    {ERR_DETAIL_KEY_CONTENT_TYPE, "content_type"},
    {ERR_DETAIL_KEY_SAFE_MODE, "safe_mode"},
    {ERR_DETAIL_KEY_SUBCODE, "subcode"}
};

static int err_add_detail(err_t* err, u32 key_id, u32 type) {
    if (!err) {
        return 0;
    }
    if (err->detail_count >= (u32)ERR_DETAIL_MAX) {
        return 0;
    }
    err->details[err->detail_count].key_id = key_id;
    err->details[err->detail_count].type = type;
    return 1;
}

err_t err_ok(void) {
    err_t e;
    memset(&e, 0, sizeof(e));
    e.domain = (u16)ERRD_NONE;
    e.code = 0u;
    e.flags = 0u;
    e.msg_id = (u32)ERRMSG_NONE;
    e.detail_count = 0u;
    return e;
}

err_t err_make(u16 domain, u16 code, u32 flags, u32 msg_id) {
    err_t e;
    memset(&e, 0, sizeof(e));
    e.domain = domain;
    e.code = code;
    e.flags = flags;
    e.msg_id = msg_id;
    e.detail_count = 0u;
    return e;
}

err_t err_refuse(u16 domain, u16 code, u32 msg_id) {
    return err_make(domain, code, (u32)(ERRF_POLICY_REFUSAL | ERRF_USER_ACTIONABLE), msg_id);
}

int err_is_ok(const err_t* err) {
    if (!err) {
        return 1;
    }
    return (err->domain == (u16)ERRD_NONE &&
            err->code == 0u &&
            err->msg_id == (u32)ERRMSG_NONE);
}

void err_clear(err_t* err) {
    if (!err) {
        return;
    }
    *err = err_ok();
}

int err_add_detail_u32(err_t* err, u32 key_id, u32 value) {
    if (!err_add_detail(err, key_id, (u32)ERR_DETAIL_TYPE_U32)) {
        return 0;
    }
    err->details[err->detail_count].v.u32_value = value;
    err->detail_count += 1u;
    return 1;
}

int err_add_detail_u64(err_t* err, u32 key_id, u64 value) {
    if (!err_add_detail(err, key_id, (u32)ERR_DETAIL_TYPE_U64)) {
        return 0;
    }
    err->details[err->detail_count].v.u64_value = value;
    err->detail_count += 1u;
    return 1;
}

int err_add_detail_msg_id(err_t* err, u32 key_id, u32 msg_id) {
    if (!err_add_detail(err, key_id, (u32)ERR_DETAIL_TYPE_MSG_ID)) {
        return 0;
    }
    err->details[err->detail_count].v.msg_id = msg_id;
    err->detail_count += 1u;
    return 1;
}

int err_add_detail_hash64(err_t* err, u32 key_id, u64 hash64) {
    if (!err_add_detail(err, key_id, (u32)ERR_DETAIL_TYPE_HASH64)) {
        return 0;
    }
    err->details[err->detail_count].v.hash64 = hash64;
    err->detail_count += 1u;
    return 1;
}

void err_sort_details_by_key(err_t* err) {
    u32 i;
    u32 j;
    if (!err || err->detail_count < 2u) {
        return;
    }
    for (i = 0u; i + 1u < err->detail_count; ++i) {
        for (j = i + 1u; j < err->detail_count; ++j) {
            const err_detail* a = &err->details[i];
            const err_detail* b = &err->details[j];
            if (b->key_id < a->key_id || (b->key_id == a->key_id && b->type < a->type)) {
                err_detail tmp = err->details[i];
                err->details[i] = err->details[j];
                err->details[j] = tmp;
            }
        }
    }
}

const char* err_domain_token(u16 domain) {
    switch (domain) {
        case ERRD_NONE: return "NONE";
        case ERRD_COMMON: return "COMMON";
        case ERRD_TLV: return "TLV";
        case ERRD_FS: return "FS";
        case ERRD_PROC: return "PROC";
        case ERRD_CRYPTO: return "CRYPTO";
        case ERRD_ARCHIVE: return "ARCHIVE";
        case ERRD_NET: return "NET";
        case ERRD_LAUNCHER: return "LAUNCHER";
        case ERRD_SETUP: return "SETUP";
        case ERRD_PACKS: return "PACKS";
        case ERRD_ARTIFACT: return "ARTIFACT";
        case ERRD_TXN: return "TXN";
        default: return "UNKNOWN";
    }
}

const char* err_msg_id_token(u32 msg_id) {
    size_t i;
    if (msg_id == (u32)ERRMSG_NONE) {
        return "OK";
    }
    for (i = 0u; i < sizeof(k_msg_tokens) / sizeof(k_msg_tokens[0]); ++i) {
        if (k_msg_tokens[i].id == msg_id) {
            return k_msg_tokens[i].token;
        }
    }
    return "UNKNOWN";
}

const char* err_detail_key_token(u32 key_id) {
    size_t i;
    for (i = 0u; i < sizeof(k_detail_keys) / sizeof(k_detail_keys[0]); ++i) {
        if (k_detail_keys[i].id == key_id) {
            return k_detail_keys[i].token;
        }
    }
    return "unknown";
}

const char* err_to_string_id(const err_t* err) {
    if (!err) {
        return "OK";
    }
    return err_msg_id_token(err->msg_id);
}
