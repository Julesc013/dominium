/*
FILE: source/dominium/providers/provider_content_local_fs.c
MODULE: Dominium
PURPOSE: Local filesystem content provider (artifact store lookup).
*/
#include "dominium/provider_content_source.h"

#include <stdio.h>
#include <string.h>

static const char* provider_content_local_fs_id(void) {
    return "local_fs";
}

static dom_abi_result provider_content_local_fs_query_interface(dom_iid iid, void** out_iface);

static void set_err(err_t* out_err, u16 domain, u16 code, u32 flags, u32 msg_id) {
    if (out_err) {
        *out_err = err_make(domain, code, flags, msg_id);
    }
}

static int hex_from_bytes(const unsigned char* bytes, u32 len, char* out_hex, size_t cap) {
    static const char* hex = "0123456789abcdef";
    size_t need;
    u32 i;
    if (!out_hex || cap == 0u || !bytes || len == 0u) {
        return 0;
    }
    need = (size_t)len * 2u + 1u;
    if (cap < need) {
        return 0;
    }
    for (i = 0u; i < len; ++i) {
        unsigned v = (unsigned)bytes[i];
        out_hex[i * 2u] = hex[(v >> 4u) & 0xFu];
        out_hex[i * 2u + 1u] = hex[v & 0xFu];
    }
    out_hex[len * 2u] = '\0';
    return 1;
}

static int file_exists(const char* path) {
    FILE* f;
    if (!path || !path[0]) {
        return 0;
    }
    f = fopen(path, "rb");
    if (!f) {
        return 0;
    }
    fclose(f);
    return 1;
}

static int file_size_bytes(const char* path, u64* out_size) {
    FILE* f;
    long sz;
    if (!out_size) {
        return 0;
    }
    *out_size = 0u;
    if (!path || !path[0]) {
        return 0;
    }
    f = fopen(path, "rb");
    if (!f) {
        return 0;
    }
    if (fseek(f, 0L, SEEK_END) != 0) {
        fclose(f);
        return 0;
    }
    sz = ftell(f);
    if (sz < 0L) {
        fclose(f);
        return 0;
    }
    fclose(f);
    *out_size = (u64)sz;
    return 1;
}

static dom_abi_result provider_content_local_fs_enumerate(provider_content_source_list_v1* out_sources,
                                                          err_t* out_err) {
    if (out_sources) {
        out_sources->count = 0u;
        memset(out_sources->entries, 0, sizeof(out_sources->entries));
    }
    if (out_err) {
        *out_err = err_ok();
    }
    return 0;
}

static dom_abi_result provider_content_local_fs_resolve(const provider_content_request_v1* req,
                                                        provider_content_artifact_ref_v1* out_ref,
                                                        err_t* out_err) {
    char hex[PROVIDER_CONTENT_HASH_MAX * 2u + 1u];
    char artifact_dir[PROVIDER_CONTENT_PATH_MAX];
    char payload_path[PROVIDER_CONTENT_PATH_MAX];
    char meta_path[PROVIDER_CONTENT_PATH_MAX];
    const char* algo = "sha256";
    int n;
    u64 size_bytes = 0u;

    if (out_ref) {
        memset(out_ref, 0, sizeof(*out_ref));
    }
    if (!req || !out_ref || !req->state_root || !req->state_root[0] ||
        !req->hash_bytes || req->hash_len == 0u || req->hash_len > PROVIDER_CONTENT_HASH_MAX) {
        set_err(out_err,
                (u16)ERRD_COMMON,
                (u16)ERRC_COMMON_INVALID_ARGS,
                0u,
                (u32)ERRMSG_COMMON_INVALID_ARGS);
        return (dom_abi_result)-1;
    }

    if (!hex_from_bytes(req->hash_bytes, req->hash_len, hex, sizeof(hex))) {
        set_err(out_err,
                (u16)ERRD_COMMON,
                (u16)ERRC_COMMON_INVALID_ARGS,
                0u,
                (u32)ERRMSG_COMMON_INVALID_ARGS);
        return (dom_abi_result)-1;
    }

    n = snprintf(artifact_dir, sizeof(artifact_dir), "%s/artifacts/%s/%s", req->state_root, algo, hex);
    if (n <= 0 || (size_t)n >= sizeof(artifact_dir)) {
        set_err(out_err,
                (u16)ERRD_COMMON,
                (u16)ERRC_COMMON_INVALID_ARGS,
                0u,
                (u32)ERRMSG_COMMON_INVALID_ARGS);
        return (dom_abi_result)-1;
    }
    n = snprintf(meta_path, sizeof(meta_path), "%s/artifact.tlv", artifact_dir);
    if (n <= 0 || (size_t)n >= sizeof(meta_path)) {
        set_err(out_err,
                (u16)ERRD_COMMON,
                (u16)ERRC_COMMON_INVALID_ARGS,
                0u,
                (u32)ERRMSG_COMMON_INVALID_ARGS);
        return (dom_abi_result)-1;
    }
    n = snprintf(payload_path, sizeof(payload_path), "%s/payload/payload.bin", artifact_dir);
    if (n <= 0 || (size_t)n >= sizeof(payload_path)) {
        set_err(out_err,
                (u16)ERRD_COMMON,
                (u16)ERRC_COMMON_INVALID_ARGS,
                0u,
                (u32)ERRMSG_COMMON_INVALID_ARGS);
        return (dom_abi_result)-1;
    }

    if (!file_exists(meta_path)) {
        set_err(out_err,
                (u16)ERRD_ARTIFACT,
                (u16)ERRC_ARTIFACT_METADATA_NOT_FOUND,
                0u,
                (u32)ERRMSG_ARTIFACT_METADATA_NOT_FOUND);
        return (dom_abi_result)-1;
    }
    if (!file_exists(payload_path)) {
        set_err(out_err,
                (u16)ERRD_ARTIFACT,
                (u16)ERRC_ARTIFACT_PAYLOAD_MISSING,
                0u,
                (u32)ERRMSG_ARTIFACT_PAYLOAD_MISSING);
        return (dom_abi_result)-1;
    }
    (void)file_size_bytes(payload_path, &size_bytes);

    out_ref->struct_size = (u32)sizeof(*out_ref);
    out_ref->struct_version = 1u;
    out_ref->content_type = req->content_type;
    out_ref->hash_len = req->hash_len;
    memcpy(out_ref->hash_bytes, req->hash_bytes, req->hash_len);
    out_ref->size_bytes = size_bytes;
    out_ref->has_payload_path = 1u;
    out_ref->has_metadata_path = 1u;
    (void)snprintf(out_ref->payload_path, sizeof(out_ref->payload_path), "%s", payload_path);
    (void)snprintf(out_ref->metadata_path, sizeof(out_ref->metadata_path), "%s", meta_path);

    if (out_err) {
        *out_err = err_ok();
    }
    return 0;
}

static dom_abi_result provider_content_local_fs_acquire(const provider_content_request_v1* req,
                                                        const char* staging_path,
                                                        err_t* out_err) {
    (void)req;
    (void)staging_path;
    set_err(out_err,
            (u16)ERRD_COMMON,
            (u16)ERRC_COMMON_UNSUPPORTED,
            (u32)(ERRF_NOT_SUPPORTED | ERRF_POLICY_REFUSAL),
            (u32)ERRMSG_COMMON_UNSUPPORTED);
    return (dom_abi_result)-1;
}

static const provider_content_source_v1 g_provider_content_local_fs = {
    DOM_ABI_HEADER_INIT(PROVIDER_API_VERSION, provider_content_source_v1),
    provider_content_local_fs_query_interface,
    provider_content_local_fs_id,
    provider_content_local_fs_enumerate,
    provider_content_local_fs_resolve,
    provider_content_local_fs_acquire
};

static dom_abi_result provider_content_local_fs_query_interface(dom_iid iid, void** out_iface) {
    if (!out_iface) {
        return (dom_abi_result)-1;
    }
    *out_iface = 0;
    if (iid == PROVIDER_IID_CORE_V1 || iid == PROVIDER_IID_CONTENT_SOURCE_V1) {
        *out_iface = (void*)&g_provider_content_local_fs;
        return 0;
    }
    return (dom_abi_result)-1;
}

const provider_content_source_v1* provider_content_local_fs_v1(void) {
    return &g_provider_content_local_fs;
}
