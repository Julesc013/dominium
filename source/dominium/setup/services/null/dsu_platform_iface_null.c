/*
FILE: source/dominium/setup/services/null/dsu_platform_iface_null.c
MODULE: Dominium Setup
PURPOSE: Null/platform-lite filesystem interface for kernel-only tests (no UI/toolkit deps).
*/
#include "dsu_platform_iface.h"

#include <errno.h>
#include <stdio.h>
#include <string.h>

#if defined(_WIN32)
#include <direct.h>
#include <io.h>
#include <sys/stat.h>
#define dsu__stat _stat
#else
#include <sys/stat.h>
#include <unistd.h>
#define dsu__stat stat
#endif

dsu_status_t dsu_platform_path_info(const char *path, dsu_u8 *out_exists, dsu_u8 *out_is_dir, dsu_u8 *out_is_symlink) {
    struct dsu__stat stbuf;
    if (!path || !out_exists || !out_is_dir || !out_is_symlink) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_exists = 0u;
    *out_is_dir = 0u;
    *out_is_symlink = 0u;
    if (dsu__stat(path, &stbuf) != 0) {
        return DSU_STATUS_SUCCESS;
    }
    *out_exists = 1u;
    if ((stbuf.st_mode & S_IFDIR) != 0) {
        *out_is_dir = 1u;
    }
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_platform_mkdir(const char *path) {
    if (!path || path[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }
#if defined(_WIN32)
    if (_mkdir(path) != 0) {
        if (errno == EEXIST) {
            return DSU_STATUS_SUCCESS;
        }
        return DSU_STATUS_IO_ERROR;
    }
#else
    if (mkdir(path, 0755) != 0) {
        if (errno == EEXIST) {
            return DSU_STATUS_SUCCESS;
        }
        return DSU_STATUS_IO_ERROR;
    }
#endif
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_platform_rmdir(const char *path) {
    if (!path || path[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }
#if defined(_WIN32)
    if (_rmdir(path) != 0) {
        return DSU_STATUS_IO_ERROR;
    }
#else
    if (rmdir(path) != 0) {
        return DSU_STATUS_IO_ERROR;
    }
#endif
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_platform_remove_file(const char *path) {
    if (!path || path[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (remove(path) != 0) {
        return DSU_STATUS_IO_ERROR;
    }
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_platform_rename(const char *src, const char *dst, dsu_u8 replace_existing) {
    if (!src || !dst || src[0] == '\0' || dst[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (replace_existing) {
        (void)remove(dst);
    }
    if (rename(src, dst) != 0) {
        return DSU_STATUS_IO_ERROR;
    }
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_platform_list_dir(const char *path, dsu_platform_dir_entry_t **out_entries, dsu_u32 *out_count) {
    if (!path || !out_entries || !out_count) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_entries = NULL;
    *out_count = 0u;
    (void)path;
    return DSU_STATUS_SUCCESS;
}

void dsu_platform_free_dir_entries(dsu_platform_dir_entry_t *entries, dsu_u32 count) {
    dsu_u32 i;
    if (!entries) {
        return;
    }
    for (i = 0u; i < count; ++i) {
        dsu__free(entries[i].name);
        entries[i].name = NULL;
    }
    dsu__free(entries);
}

dsu_status_t dsu_platform_disk_free_bytes(const char *path, dsu_u64 *out_free_bytes) {
    if (!path || !out_free_bytes) {
        return DSU_STATUS_INVALID_ARGS;
    }
    (void)path;
    *out_free_bytes = 0ull;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_platform_get_cwd(char *out_path, dsu_u32 out_path_cap) {
    if (!out_path || out_path_cap == 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    out_path[0] = '\0';
#if defined(_WIN32)
    if (!_getcwd(out_path, (int)out_path_cap)) {
        return DSU_STATUS_IO_ERROR;
    }
#else
    if (!getcwd(out_path, (size_t)out_path_cap)) {
        return DSU_STATUS_IO_ERROR;
    }
#endif
    return DSU_STATUS_SUCCESS;
}
