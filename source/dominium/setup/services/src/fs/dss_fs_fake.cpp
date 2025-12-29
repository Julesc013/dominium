#include "dss_fs_internal.h"

#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>

#if defined(_WIN32)
#include <direct.h>
#include <io.h>
#include <sys/stat.h>
#else
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

enum {
    DSS_FS_KIND_REAL = 1u,
    DSS_FS_KIND_FAKE = 2u
};

static dss_error_t dss_fs_fake_resolve(dss_fs_context_t *ctx,
                                       const char *path,
                                       std::string *out_path) {
    dss_error_t st;
    std::string canon;
    if (!ctx || !path || !out_path) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    st = dss_fs_canonicalize_path(path, DSS_TRUE, &canon);
    if (!dss_error_is_ok(st)) {
        return st;
    }
    if (dss_fs_is_abs_path(canon)) {
        if (!dss_fs_path_has_prefix(canon, ctx->root)) {
            return dss_error_make(DSS_DOMAIN_SERVICES,
                                  DSS_CODE_SANDBOX_VIOLATION,
                                  DSS_SUBCODE_OUTSIDE_SANDBOX,
                                  DSS_ERROR_FLAG_USER_ACTIONABLE);
        }
        *out_path = canon;
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
    }
    st = dss_fs_join_path(ctx->root.c_str(), canon.c_str(), out_path);
    if (!dss_error_is_ok(st)) {
        return st;
    }
    if (!dss_fs_path_has_prefix(*out_path, ctx->root)) {
        return dss_error_make(DSS_DOMAIN_SERVICES,
                              DSS_CODE_SANDBOX_VIOLATION,
                              DSS_SUBCODE_OUTSIDE_SANDBOX,
                              DSS_ERROR_FLAG_USER_ACTIONABLE);
    }
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_fs_fake_read_file_bytes(void *vctx,
                                               const char *path,
                                               std::vector<dss_u8> *out_bytes) {
    dss_fs_context_t *ctx = reinterpret_cast<dss_fs_context_t *>(vctx);
    std::string resolved;
    dss_error_t st = dss_fs_fake_resolve(ctx, path, &resolved);
    if (!dss_error_is_ok(st)) {
        return st;
    }
    return dss_fs_real_read_file_bytes(0, resolved.c_str(), out_bytes);
}

static dss_error_t dss_fs_fake_write_file_bytes_atomic(void *vctx,
                                                       const char *path,
                                                       const dss_u8 *data,
                                                       dss_u32 len) {
    dss_fs_context_t *ctx = reinterpret_cast<dss_fs_context_t *>(vctx);
    std::string resolved;
    dss_error_t st = dss_fs_fake_resolve(ctx, path, &resolved);
    if (!dss_error_is_ok(st)) {
        return st;
    }
    return dss_fs_real_write_file_bytes_atomic(0, resolved.c_str(), data, len);
}

static dss_error_t dss_fs_fake_make_dir(void *vctx, const char *path) {
    dss_fs_context_t *ctx = reinterpret_cast<dss_fs_context_t *>(vctx);
    std::string resolved;
    dss_error_t st = dss_fs_fake_resolve(ctx, path, &resolved);
    if (!dss_error_is_ok(st)) {
        return st;
    }
#if defined(_WIN32)
    if (_mkdir(resolved.c_str()) != 0) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
#else
    if (mkdir(resolved.c_str(), 0755) != 0) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
#endif
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_fs_fake_remove_file(void *vctx, const char *path) {
    dss_fs_context_t *ctx = reinterpret_cast<dss_fs_context_t *>(vctx);
    std::string resolved;
    dss_error_t st = dss_fs_fake_resolve(ctx, path, &resolved);
    if (!dss_error_is_ok(st)) {
        return st;
    }
    if (std::remove(resolved.c_str()) != 0) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_fs_fake_remove_dir_if_empty(void *vctx, const char *path) {
    dss_fs_context_t *ctx = reinterpret_cast<dss_fs_context_t *>(vctx);
    std::string resolved;
    dss_error_t st = dss_fs_fake_resolve(ctx, path, &resolved);
    if (!dss_error_is_ok(st)) {
        return st;
    }
#if defined(_WIN32)
    if (_rmdir(resolved.c_str()) != 0) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
#else
    if (rmdir(resolved.c_str()) != 0) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
#endif
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_fs_fake_list_dir(void *vctx,
                                        const char *path,
                                        std::vector<std::string> *out_entries) {
    dss_fs_context_t *ctx = reinterpret_cast<dss_fs_context_t *>(vctx);
    std::string resolved;
    dss_error_t st = dss_fs_fake_resolve(ctx, path, &resolved);
    if (!dss_error_is_ok(st)) {
        return st;
    }
    out_entries->clear();
#if defined(_WIN32)
    {
        std::string pattern = resolved + "\\*";
        struct _finddata_t data;
        intptr_t handle = _findfirst(pattern.c_str(), &data);
        if (handle == -1) {
            return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
        }
        do {
            const char *name = data.name;
            if (std::strcmp(name, ".") == 0 || std::strcmp(name, "..") == 0) {
                continue;
            }
            out_entries->push_back(name);
        } while (_findnext(handle, &data) == 0);
        _findclose(handle);
    }
#else
    {
        DIR *dir = opendir(resolved.c_str());
        struct dirent *ent;
        if (!dir) {
            return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
        }
        while ((ent = readdir(dir)) != NULL) {
            const char *name = ent->d_name;
            if (std::strcmp(name, ".") == 0 || std::strcmp(name, "..") == 0) {
                continue;
            }
            out_entries->push_back(name);
        }
        closedir(dir);
    }
#endif
    std::sort(out_entries->begin(), out_entries->end());
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_fs_fake_canonicalize(void *vctx,
                                            const char *path,
                                            std::string *out_path) {
    dss_fs_context_t *ctx = reinterpret_cast<dss_fs_context_t *>(vctx);
    return dss_fs_fake_resolve(ctx, path, out_path);
}

static dss_error_t dss_fs_fake_join_path(void *vctx,
                                         const char *a,
                                         const char *b,
                                         std::string *out_path) {
    dss_fs_context_t *ctx = reinterpret_cast<dss_fs_context_t *>(vctx);
    std::string joined;
    dss_error_t st = dss_fs_join_path(a, b, &joined);
    if (!dss_error_is_ok(st)) {
        return st;
    }
    return dss_fs_fake_resolve(ctx, joined.c_str(), out_path);
}

static dss_error_t dss_fs_fake_temp_dir(void *vctx, std::string *out_path) {
    dss_fs_context_t *ctx = reinterpret_cast<dss_fs_context_t *>(vctx);
    if (!ctx || !out_path) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    *out_path = ctx->temp_root;
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_fs_fake_atomic_rename(void *vctx,
                                             const char *src,
                                             const char *dst) {
    dss_fs_context_t *ctx = reinterpret_cast<dss_fs_context_t *>(vctx);
    std::string src_path;
    std::string dst_path;
    dss_error_t st;
    st = dss_fs_fake_resolve(ctx, src, &src_path);
    if (!dss_error_is_ok(st)) {
        return st;
    }
    st = dss_fs_fake_resolve(ctx, dst, &dst_path);
    if (!dss_error_is_ok(st)) {
        return st;
    }
    if (std::rename(src_path.c_str(), dst_path.c_str()) != 0) {
        std::remove(dst_path.c_str());
        if (std::rename(src_path.c_str(), dst_path.c_str()) != 0) {
            return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
        }
    }
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_fs_fake_dir_swap(void *vctx,
                                        const char *src_dir,
                                        const char *dst_dir) {
    dss_fs_context_t *ctx = reinterpret_cast<dss_fs_context_t *>(vctx);
    std::string src_path;
    std::string dst_path;
    std::string backup;
    dss_error_t st;
    st = dss_fs_fake_resolve(ctx, src_dir, &src_path);
    if (!dss_error_is_ok(st)) {
        return st;
    }
    st = dss_fs_fake_resolve(ctx, dst_dir, &dst_path);
    if (!dss_error_is_ok(st)) {
        return st;
    }
    backup = dst_path + ".swap";
    std::remove(backup.c_str());
    if (std::rename(dst_path.c_str(), backup.c_str()) != 0) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
    if (std::rename(src_path.c_str(), dst_path.c_str()) != 0) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
    std::rename(backup.c_str(), src_path.c_str());
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_fs_fake_exists(void *vctx,
                                      const char *path,
                                      dss_bool *out_exists) {
    dss_fs_context_t *ctx = reinterpret_cast<dss_fs_context_t *>(vctx);
    std::string resolved;
    dss_error_t st = dss_fs_fake_resolve(ctx, path, &resolved);
    if (!dss_error_is_ok(st)) {
        return st;
    }
    return dss_fs_real_exists(0, resolved.c_str(), out_exists);
}

static dss_error_t dss_fs_fake_file_size(void *vctx,
                                         const char *path,
                                         dss_u64 *out_size) {
    dss_fs_context_t *ctx = reinterpret_cast<dss_fs_context_t *>(vctx);
    std::string resolved;
    dss_error_t st = dss_fs_fake_resolve(ctx, path, &resolved);
    if (!dss_error_is_ok(st)) {
        return st;
    }
    return dss_fs_real_file_size(0, resolved.c_str(), out_size);
}

void dss_fs_init_fake(dss_fs_api_t *api, const char *sandbox_root) {
    dss_fs_context_t *ctx;
    dss_error_t st;
    std::string root;
    if (!api) {
        return;
    }
    ctx = new dss_fs_context_t();
    ctx->kind = DSS_FS_KIND_FAKE;
    st = dss_fs_canonicalize_path(sandbox_root ? sandbox_root : ".", DSS_FALSE, &root);
    if (!dss_error_is_ok(st)) {
        root = ".";
    }
    ctx->root = root;
    ctx->temp_root = root + "/tmp";
    api->ctx = ctx;
    api->read_file_bytes = dss_fs_fake_read_file_bytes;
    api->write_file_bytes_atomic = dss_fs_fake_write_file_bytes_atomic;
    api->make_dir = dss_fs_fake_make_dir;
    api->remove_file = dss_fs_fake_remove_file;
    api->remove_dir_if_empty = dss_fs_fake_remove_dir_if_empty;
    api->list_dir = dss_fs_fake_list_dir;
    api->canonicalize_path = dss_fs_fake_canonicalize;
    api->join_path = dss_fs_fake_join_path;
    api->temp_dir = dss_fs_fake_temp_dir;
    api->atomic_rename = dss_fs_fake_atomic_rename;
    api->dir_swap = dss_fs_fake_dir_swap;
    api->exists = dss_fs_fake_exists;
    api->file_size = dss_fs_fake_file_size;
}
