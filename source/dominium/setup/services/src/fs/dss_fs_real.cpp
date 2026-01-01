#include "dss_fs_internal.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <algorithm>
#include <vector>
#include <errno.h>

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

dss_error_t dss_fs_real_read_file_bytes(void *ctx,
                                        const char *path,
                                        std::vector<dss_u8> *out_bytes) {
    FILE *f;
    long len;
    size_t read_count;
    (void)ctx;
    if (!path || !out_bytes) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    out_bytes->clear();
    f = std::fopen(path, "rb");
    if (!f) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
    if (std::fseek(f, 0, SEEK_END) != 0) {
        std::fclose(f);
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
    len = std::ftell(f);
    if (len < 0) {
        std::fclose(f);
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
    if (std::fseek(f, 0, SEEK_SET) != 0) {
        std::fclose(f);
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
    out_bytes->resize((size_t)len);
    read_count = (len > 0) ? std::fread(&(*out_bytes)[0], 1u, (size_t)len, f) : 0u;
    std::fclose(f);
    if (read_count != (size_t)len) {
        out_bytes->clear();
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_fs_real_atomic_rename_internal(const char *src, const char *dst) {
    if (!src || !dst) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    if (std::rename(src, dst) != 0) {
        std::remove(dst);
        if (std::rename(src, dst) != 0) {
            return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
        }
    }
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

dss_error_t dss_fs_real_write_file_bytes_atomic(void *ctx,
                                                const char *path,
                                                const dss_u8 *data,
                                                dss_u32 len) {
    std::string tmp;
    FILE *f;
    size_t wrote;
    (void)ctx;
    if (!path || (!data && len)) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    tmp = std::string(path) + ".tmp";
    f = std::fopen(tmp.c_str(), "wb");
    if (!f) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
    wrote = len ? std::fwrite(data, 1u, len, f) : 0u;
    if (std::fclose(f) != 0) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
    if (wrote != len) {
        std::remove(tmp.c_str());
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
    return dss_fs_real_atomic_rename_internal(tmp.c_str(), path);
}

static dss_error_t dss_fs_real_make_dir(void *ctx, const char *path) {
    (void)ctx;
    if (!path) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
#if defined(_WIN32)
    if (_mkdir(path) != 0) {
        if (errno == EEXIST) {
            return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
        }
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
#else
    if (mkdir(path, 0755) != 0) {
        if (errno == EEXIST) {
            return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
        }
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
#endif
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_fs_real_remove_file(void *ctx, const char *path) {
    (void)ctx;
    if (!path) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    if (std::remove(path) != 0) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_fs_real_remove_dir_if_empty(void *ctx, const char *path) {
    (void)ctx;
    if (!path) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
#if defined(_WIN32)
    if (_rmdir(path) != 0) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
#else
    if (rmdir(path) != 0) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
#endif
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_fs_real_list_dir(void *ctx,
                                        const char *path,
                                        std::vector<std::string> *out_entries) {
    (void)ctx;
    if (!path || !out_entries) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    out_entries->clear();
#if defined(_WIN32)
    {
        std::string pattern = std::string(path) + "\\*";
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
        DIR *dir = opendir(path);
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

static dss_error_t dss_fs_real_canonicalize(void *ctx,
                                            const char *path,
                                            std::string *out_path) {
    (void)ctx;
    return dss_fs_canonicalize_path(path, DSS_FALSE, out_path);
}

static dss_error_t dss_fs_real_join_path(void *ctx,
                                         const char *a,
                                         const char *b,
                                         std::string *out_path) {
    (void)ctx;
    return dss_fs_join_path(a, b, out_path);
}

static dss_error_t dss_fs_real_temp_dir(void *ctx, std::string *out_path) {
    const char *env = std::getenv("TEMP");
    (void)ctx;
    if (!out_path) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    if (!env || !env[0]) {
        env = std::getenv("TMP");
    }
    if (!env || !env[0]) {
        env = std::getenv("TMPDIR");
    }
    if (!env || !env[0]) {
        env = ".";
    }
    return dss_fs_canonicalize_path(env, DSS_FALSE, out_path);
}

static dss_error_t dss_fs_real_atomic_rename(void *ctx,
                                             const char *src,
                                             const char *dst) {
    (void)ctx;
    return dss_fs_real_atomic_rename_internal(src, dst);
}

static dss_error_t dss_fs_real_dir_swap(void *ctx,
                                        const char *src_dir,
                                        const char *dst_dir) {
    std::string backup;
    dss_bool exists = DSS_FALSE;
    dss_error_t st;
    (void)ctx;
    if (!src_dir || !dst_dir) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    st = dss_fs_real_exists(ctx, dst_dir, &exists);
    if (dss_error_is_ok(st) && !exists) {
        return dss_fs_real_atomic_rename_internal(src_dir, dst_dir);
    }
    backup = std::string(dst_dir) + ".swap";
    std::remove(backup.c_str());
    if (std::rename(dst_dir, backup.c_str()) != 0) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
    st = dss_fs_real_atomic_rename_internal(src_dir, dst_dir);
    if (!dss_error_is_ok(st)) {
        return st;
    }
    std::rename(backup.c_str(), src_dir);
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

dss_error_t dss_fs_real_exists(void *ctx,
                               const char *path,
                               dss_bool *out_exists) {
    (void)ctx;
    if (!path || !out_exists) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
#if defined(_WIN32)
    *out_exists = (_access(path, 0) == 0) ? DSS_TRUE : DSS_FALSE;
#else
    *out_exists = (access(path, F_OK) == 0) ? DSS_TRUE : DSS_FALSE;
#endif
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

dss_error_t dss_fs_real_file_size(void *ctx,
                                  const char *path,
                                  dss_u64 *out_size) {
    (void)ctx;
    if (!path || !out_size) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
#if defined(_WIN32)
    struct _stat info;
    if (_stat(path, &info) != 0) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
    *out_size = (dss_u64)info.st_size;
#else
    struct stat info;
    if (stat(path, &info) != 0) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
    *out_size = (dss_u64)info.st_size;
#endif
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

void dss_fs_init_real(dss_fs_api_t *api) {
    dss_fs_context_t *ctx;
    if (!api) {
        return;
    }
    ctx = new dss_fs_context_t();
    ctx->kind = DSS_FS_KIND_REAL;
    api->ctx = ctx;
    api->read_file_bytes = dss_fs_real_read_file_bytes;
    api->write_file_bytes_atomic = dss_fs_real_write_file_bytes_atomic;
    api->make_dir = dss_fs_real_make_dir;
    api->remove_file = dss_fs_real_remove_file;
    api->remove_dir_if_empty = dss_fs_real_remove_dir_if_empty;
    api->list_dir = dss_fs_real_list_dir;
    api->canonicalize_path = dss_fs_real_canonicalize;
    api->join_path = dss_fs_real_join_path;
    api->temp_dir = dss_fs_real_temp_dir;
    api->atomic_rename = dss_fs_real_atomic_rename;
    api->dir_swap = dss_fs_real_dir_swap;
    api->exists = dss_fs_real_exists;
    api->file_size = dss_fs_real_file_size;
}

void dss_fs_shutdown(dss_fs_api_t *api) {
    if (!api) {
        return;
    }
    delete reinterpret_cast<dss_fs_context_t *>(api->ctx);
    api->ctx = 0;
    api->read_file_bytes = 0;
    api->write_file_bytes_atomic = 0;
    api->make_dir = 0;
    api->remove_file = 0;
    api->remove_dir_if_empty = 0;
    api->list_dir = 0;
    api->canonicalize_path = 0;
    api->join_path = 0;
    api->temp_dir = 0;
    api->atomic_rename = 0;
    api->dir_swap = 0;
    api->exists = 0;
    api->file_size = 0;
}
