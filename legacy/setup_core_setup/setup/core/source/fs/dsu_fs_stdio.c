/*
FILE: source/dominium/setup/core/src/fs/dsu_fs_stdio.c
MODULE: Dominium Setup
PURPOSE: Temporary stdio-backed filesystem adapter for Setup Core.
*/
#include "../util/dsu_util_internal.h"

#include <stdio.h>
#include <string.h>

#define DSU_FS_DEFAULT_MAX_FILE_BYTES (16u * 1024u * 1024u)

dsu_status_t dsu__fs_read_all(const dsu_config_t *cfg,
                             const char *path,
                             dsu_u8 **out_bytes,
                             dsu_u32 *out_len) {
    FILE *f;
    long size_long;
    dsu_u32 size_u32;
    dsu_u32 max_bytes;
    dsu_u8 *buf;
    size_t nread;

    if (!path || !out_bytes || !out_len) {
        return DSU_STATUS_INVALID_ARGS;
    }

    *out_bytes = NULL;
    *out_len = 0u;

    max_bytes = DSU_FS_DEFAULT_MAX_FILE_BYTES;
    if (cfg && cfg->max_file_bytes != 0u) {
        max_bytes = cfg->max_file_bytes;
    }

    f = fopen(path, "rb");
    if (!f) {
        return DSU_STATUS_IO_ERROR;
    }

    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return DSU_STATUS_IO_ERROR;
    }
    size_long = ftell(f);
    if (size_long < 0) {
        fclose(f);
        return DSU_STATUS_IO_ERROR;
    }
    if ((unsigned long)size_long > 0xFFFFFFFFul) {
        fclose(f);
        return DSU_STATUS_IO_ERROR;
    }
    size_u32 = (dsu_u32)size_long;
    if (size_u32 > max_bytes) {
        fclose(f);
        return DSU_STATUS_IO_ERROR;
    }
    if (fseek(f, 0, SEEK_SET) != 0) {
        fclose(f);
        return DSU_STATUS_IO_ERROR;
    }

    if (size_u32 == 0u) {
        fclose(f);
        *out_bytes = NULL;
        *out_len = 0u;
        return DSU_STATUS_SUCCESS;
    }

    buf = (dsu_u8 *)dsu__malloc(size_u32);
    if (!buf) {
        fclose(f);
        return DSU_STATUS_IO_ERROR;
    }

    nread = fread(buf, 1u, (size_t)size_u32, f);
    fclose(f);
    if (nread != (size_t)size_u32) {
        dsu__free(buf);
        return DSU_STATUS_IO_ERROR;
    }

    *out_bytes = buf;
    *out_len = size_u32;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu__fs_write_all(const char *path, const dsu_u8 *bytes, dsu_u32 len) {
    FILE *f;
    size_t nwritten;

    if (!path) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (!bytes && len != 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }

    f = fopen(path, "wb");
    if (!f) {
        return DSU_STATUS_IO_ERROR;
    }
    if (len == 0u) {
        fclose(f);
        return DSU_STATUS_SUCCESS;
    }
    nwritten = fwrite(bytes, 1u, (size_t)len, f);
    if (nwritten != (size_t)len) {
        fclose(f);
        return DSU_STATUS_IO_ERROR;
    }
    if (fclose(f) != 0) {
        return DSU_STATUS_IO_ERROR;
    }
    return DSU_STATUS_SUCCESS;
}

