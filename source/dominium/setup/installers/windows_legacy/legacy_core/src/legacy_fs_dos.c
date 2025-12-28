/*
FILE: source/dominium/setup/installers/windows_legacy/legacy_core/src/legacy_fs_dos.c
MODULE: Dominium Setup (Legacy Core)
PURPOSE: DOS filesystem helpers and DSUA extraction (archive-only payloads).
*/
#include "legacy_internal.h"

#include <errno.h>

#if defined(_MSC_VER)
#include <direct.h>
#define dsu_legacy_mkdir _mkdir
#elif defined(__WATCOMC__) || defined(__BORLANDC__)
#include <direct.h>
#define dsu_legacy_mkdir mkdir
#else
#include <dir.h>
#define dsu_legacy_mkdir mkdir
#endif

#define DSU_LEGACY_PATH_SEP '\\'

static int dsu_legacy_is_sep(char c) {
    return (c == '/' || c == '\\');
}

static char *dsu_legacy_path_join_sep(const char *a, const char *b, char sep) {
    dsu_legacy_u32 na;
    dsu_legacy_u32 nb;
    dsu_legacy_u32 need;
    char *out;
    if (!a || !b) return NULL;
    na = dsu_legacy_strlen(a);
    nb = dsu_legacy_strlen(b);
    if (na == 0u) return dsu_legacy_strdup(b);
    if (nb == 0u) return dsu_legacy_strdup(a);
    need = na + nb + 2u;
    out = (char *)malloc((size_t)need);
    if (!out) return NULL;
    memcpy(out, a, (size_t)na);
    out[na] = sep;
    memcpy(out + na + 1u, b, (size_t)nb);
    out[na + 1u + nb] = '\0';
    return out;
}

static char *dsu_legacy_path_join_native(const char *a, const char *b) {
    return dsu_legacy_path_join_sep(a, b, DSU_LEGACY_PATH_SEP);
}

static char *dsu_legacy_path_join_rel(const char *a, const char *b) {
    return dsu_legacy_path_join_sep(a, b, '/');
}

static char *dsu_legacy_path_dirname(const char *path) {
    dsu_legacy_u32 n;
    dsu_legacy_u32 i;
    char *out;
    if (!path) return NULL;
    n = dsu_legacy_strlen(path);
    if (n == 0u) return NULL;
    for (i = n; i > 0u; --i) {
        if (dsu_legacy_is_sep(path[i - 1u])) {
            break;
        }
    }
    if (i == 0u) return NULL;
    out = (char *)malloc((size_t)i + 1u);
    if (!out) return NULL;
    memcpy(out, path, (size_t)i);
    out[i] = '\0';
    return out;
}

static dsu_legacy_status_t dsu_legacy_mkdir_one(const char *path) {
    if (!path || path[0] == '\0') return DSU_LEGACY_STATUS_INVALID_ARGS;
    if (dsu_legacy_mkdir(path) == 0) return DSU_LEGACY_STATUS_SUCCESS;
    if (errno == EEXIST) return DSU_LEGACY_STATUS_SUCCESS;
    return DSU_LEGACY_STATUS_IO_ERROR;
}

static dsu_legacy_status_t dsu_legacy_mkdirs(const char *path) {
    dsu_legacy_u32 i;
    dsu_legacy_u32 n;
    char *tmp;
    if (!path) return DSU_LEGACY_STATUS_INVALID_ARGS;
    n = dsu_legacy_strlen(path);
    if (n == 0u) return DSU_LEGACY_STATUS_INVALID_ARGS;
    tmp = dsu_legacy_strdup(path);
    if (!tmp) return DSU_LEGACY_STATUS_IO_ERROR;
    for (i = 1u; i < n; ++i) {
        if (dsu_legacy_is_sep(tmp[i])) {
            tmp[i] = '\0';
            if (tmp[0] != '\0') {
                (void)dsu_legacy_mkdir_one(tmp);
            }
            tmp[i] = DSU_LEGACY_PATH_SEP;
        }
    }
    if (tmp[0] != '\0') {
        (void)dsu_legacy_mkdir_one(tmp);
    }
    free(tmp);
    return DSU_LEGACY_STATUS_SUCCESS;
}

dsu_legacy_status_t dsu_legacy_fs_copy_file(const char *src, const char *dst) {
    FILE *in;
    FILE *out;
    unsigned char buf[32768];
    size_t n;
    dsu_legacy_status_t st;
    char *dir;
    if (!src || !dst) return DSU_LEGACY_STATUS_INVALID_ARGS;
    dir = dsu_legacy_path_dirname(dst);
    if (dir) {
        st = dsu_legacy_mkdirs(dir);
        free(dir);
        if (st != DSU_LEGACY_STATUS_SUCCESS) return st;
    }
    in = fopen(src, "rb");
    if (!in) return DSU_LEGACY_STATUS_IO_ERROR;
    out = fopen(dst, "wb");
    if (!out) {
        fclose(in);
        return DSU_LEGACY_STATUS_IO_ERROR;
    }
    while ((n = fread(buf, 1u, sizeof(buf), in)) != 0u) {
        if (fwrite(buf, 1u, n, out) != n) {
            fclose(in);
            fclose(out);
            return DSU_LEGACY_STATUS_IO_ERROR;
        }
    }
    if (ferror(in)) {
        fclose(in);
        fclose(out);
        return DSU_LEGACY_STATUS_IO_ERROR;
    }
    fclose(in);
    if (fclose(out) != 0) return DSU_LEGACY_STATUS_IO_ERROR;
    return DSU_LEGACY_STATUS_SUCCESS;
}

dsu_legacy_status_t dsu_legacy_fs_copy_tree(const char *src_root,
                                            const char *dst_root,
                                            dsu_legacy_fs_copy_cb cb,
                                            void *user) {
    (void)src_root;
    (void)dst_root;
    (void)cb;
    (void)user;
    return DSU_LEGACY_STATUS_UNSUPPORTED;
}

static dsu_legacy_status_t dsu_legacy_read_u16le_file(FILE *f, dsu_legacy_u16 *out_v) {
    unsigned char b[2];
    if (!f || !out_v) return DSU_LEGACY_STATUS_INVALID_ARGS;
    if (fread(b, 1u, 2u, f) != 2u) return DSU_LEGACY_STATUS_IO_ERROR;
    *out_v = (dsu_legacy_u16)((dsu_legacy_u16)b[0] | ((dsu_legacy_u16)b[1] << 8));
    return DSU_LEGACY_STATUS_SUCCESS;
}

static dsu_legacy_status_t dsu_legacy_read_u32le_file(FILE *f, dsu_legacy_u32 *out_v) {
    unsigned char b[4];
    if (!f || !out_v) return DSU_LEGACY_STATUS_INVALID_ARGS;
    if (fread(b, 1u, 4u, f) != 4u) return DSU_LEGACY_STATUS_IO_ERROR;
    *out_v = (dsu_legacy_u32)b[0]
           | ((dsu_legacy_u32)b[1] << 8)
           | ((dsu_legacy_u32)b[2] << 16)
           | ((dsu_legacy_u32)b[3] << 24);
    return DSU_LEGACY_STATUS_SUCCESS;
}

static dsu_legacy_status_t dsu_legacy_read_u64le_file(FILE *f, dsu_legacy_u64 *out_v) {
    unsigned char b[8];
    dsu_legacy_u32 lo;
    if (!f || !out_v) return DSU_LEGACY_STATUS_INVALID_ARGS;
    if (fread(b, 1u, 8u, f) != 8u) return DSU_LEGACY_STATUS_IO_ERROR;
    lo = (dsu_legacy_u32)b[0]
       | ((dsu_legacy_u32)b[1] << 8)
       | ((dsu_legacy_u32)b[2] << 16)
       | ((dsu_legacy_u32)b[3] << 24);
    *out_v = (dsu_legacy_u64)lo;
    return DSU_LEGACY_STATUS_SUCCESS;
}

static dsu_legacy_status_t dsu_legacy_canon_rel_path(const char *in, char **out_canon) {
    dsu_legacy_u32 i;
    dsu_legacy_u32 n;
    dsu_legacy_u32 o = 0u;
    dsu_legacy_u32 seg_start = 0u;
    char *buf;
    if (!out_canon) return DSU_LEGACY_STATUS_INVALID_ARGS;
    *out_canon = NULL;
    if (!in || in[0] == '\0') return DSU_LEGACY_STATUS_INVALID_ARGS;
    if (dsu_legacy_is_sep(in[0])) return DSU_LEGACY_STATUS_INVALID_ARGS;
    if (strchr(in, ':') != NULL) return DSU_LEGACY_STATUS_INVALID_ARGS;
    n = dsu_legacy_strlen(in);
    if (n == 0u) return DSU_LEGACY_STATUS_INVALID_ARGS;
    buf = (char *)malloc((size_t)n + 1u);
    if (!buf) return DSU_LEGACY_STATUS_IO_ERROR;
    for (i = 0u; i <= n; ++i) {
        char c = (i < n) ? in[i] : '\0';
        if (c == '\\') c = '/';
        if (c == '/' || c == '\0') {
            dsu_legacy_u32 seg_len = (dsu_legacy_u32)(i - seg_start);
            if (seg_len == 0u) {
                /* skip */
            } else if (seg_len == 1u && in[seg_start] == '.') {
                /* skip */
            } else if (seg_len == 2u && in[seg_start] == '.' && in[seg_start + 1u] == '.') {
                free(buf);
                return DSU_LEGACY_STATUS_INVALID_ARGS;
            } else {
                if (o != 0u) buf[o++] = '/';
                while (seg_start < i) {
                    char cc = in[seg_start++];
                    if (cc == '\\') cc = '/';
                    buf[o++] = cc;
                }
            }
            seg_start = i + 1u;
        }
    }
    buf[o] = '\0';
    if (buf[0] == '\0') {
        free(buf);
        return DSU_LEGACY_STATUS_INVALID_ARGS;
    }
    *out_canon = buf;
    return DSU_LEGACY_STATUS_SUCCESS;
}

dsu_legacy_status_t dsu_legacy_fs_extract_archive(const char *archive_path,
                                                  const char *dst_root,
                                                  dsu_legacy_fs_copy_cb cb,
                                                  void *user) {
    FILE *f;
    unsigned char magic[4];
    dsu_legacy_u16 ver;
    dsu_legacy_u16 endian;
    dsu_legacy_u32 count;
    dsu_legacy_u32 reserved;
    dsu_legacy_u32 i;

    if (!archive_path || !dst_root) return DSU_LEGACY_STATUS_INVALID_ARGS;
    f = fopen(archive_path, "rb");
    if (!f) return DSU_LEGACY_STATUS_IO_ERROR;

    if (fread(magic, 1u, 4u, f) != 4u) {
        fclose(f);
        return DSU_LEGACY_STATUS_IO_ERROR;
    }
    if (magic[0] != 'D' || magic[1] != 'S' || magic[2] != 'U' || magic[3] != 'A') {
        fclose(f);
        return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
    }
    if (dsu_legacy_read_u16le_file(f, &ver) != DSU_LEGACY_STATUS_SUCCESS ||
        dsu_legacy_read_u16le_file(f, &endian) != DSU_LEGACY_STATUS_SUCCESS) {
        fclose(f);
        return DSU_LEGACY_STATUS_IO_ERROR;
    }
    if (ver != 1u || endian != (dsu_legacy_u16)DSU_LEGACY_ENDIAN_MARKER_LE) {
        fclose(f);
        return DSU_LEGACY_STATUS_UNSUPPORTED;
    }
    if (dsu_legacy_read_u32le_file(f, &count) != DSU_LEGACY_STATUS_SUCCESS ||
        dsu_legacy_read_u32le_file(f, &reserved) != DSU_LEGACY_STATUS_SUCCESS) {
        fclose(f);
        return DSU_LEGACY_STATUS_IO_ERROR;
    }
    (void)reserved;

    for (i = 0u; i < count; ++i) {
        dsu_legacy_u32 path_len = 0u;
        char *path_raw = NULL;
        char *path_canon = NULL;
        dsu_legacy_u64 size = 0u;
        unsigned char sha256[32];
        char *dst_path = NULL;
        dsu_legacy_status_t st;

        if (dsu_legacy_read_u32le_file(f, &path_len) != DSU_LEGACY_STATUS_SUCCESS) {
            fclose(f);
            return DSU_LEGACY_STATUS_IO_ERROR;
        }
        if (path_len == 0u || path_len > DSU_LEGACY_MAX_PATH) {
            fclose(f);
            return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
        }
        path_raw = (char *)malloc((size_t)path_len + 1u);
        if (!path_raw) {
            fclose(f);
            return DSU_LEGACY_STATUS_IO_ERROR;
        }
        if (fread(path_raw, 1u, (size_t)path_len, f) != (size_t)path_len) {
            free(path_raw);
            fclose(f);
            return DSU_LEGACY_STATUS_IO_ERROR;
        }
        path_raw[path_len] = '\0';
        st = dsu_legacy_canon_rel_path(path_raw, &path_canon);
        free(path_raw);
        if (st != DSU_LEGACY_STATUS_SUCCESS) {
            fclose(f);
            return st;
        }
        if (dsu_legacy_read_u64le_file(f, &size) != DSU_LEGACY_STATUS_SUCCESS) {
            free(path_canon);
            fclose(f);
            return DSU_LEGACY_STATUS_IO_ERROR;
        }
        if (fread(sha256, 1u, 32u, f) != 32u) {
            free(path_canon);
            fclose(f);
            return DSU_LEGACY_STATUS_IO_ERROR;
        }
        (void)sha256;

        dst_path = dsu_legacy_path_join_native(dst_root, path_canon);
        if (!dst_path) {
            free(path_canon);
            fclose(f);
            return DSU_LEGACY_STATUS_IO_ERROR;
        }

        {
            dsu_legacy_status_t st2;
            char *dir = dsu_legacy_path_dirname(dst_path);
            if (dir) {
                st2 = dsu_legacy_mkdirs(dir);
                free(dir);
                if (st2 != DSU_LEGACY_STATUS_SUCCESS) {
                    free(path_canon);
                    free(dst_path);
                    fclose(f);
                    return st2;
                }
            }
        }

        {
            FILE *out = fopen(dst_path, "wb");
            unsigned char buf[32768];
            dsu_legacy_u64 remaining = size;
            if (!out) {
                free(path_canon);
                free(dst_path);
                fclose(f);
                return DSU_LEGACY_STATUS_IO_ERROR;
            }
            while (remaining != 0u) {
                dsu_legacy_u32 want = (remaining > (dsu_legacy_u64)sizeof(buf)) ?
                    (dsu_legacy_u32)sizeof(buf) : (dsu_legacy_u32)remaining;
                size_t nr = fread(buf, 1u, (size_t)want, f);
                if (nr != (size_t)want) {
                    fclose(out);
                    free(path_canon);
                    free(dst_path);
                    fclose(f);
                    return DSU_LEGACY_STATUS_IO_ERROR;
                }
                if (fwrite(buf, 1u, nr, out) != nr) {
                    fclose(out);
                    free(path_canon);
                    free(dst_path);
                    fclose(f);
                    return DSU_LEGACY_STATUS_IO_ERROR;
                }
                remaining -= (dsu_legacy_u64)want;
            }
            if (fclose(out) != 0) {
                free(path_canon);
                free(dst_path);
                fclose(f);
                return DSU_LEGACY_STATUS_IO_ERROR;
            }
        }

        if (cb) {
            st = cb(path_canon, dst_path, user);
            if (st != DSU_LEGACY_STATUS_SUCCESS) {
                free(path_canon);
                free(dst_path);
                fclose(f);
                return st;
            }
        }
        free(path_canon);
        free(dst_path);
    }

    fclose(f);
    return DSU_LEGACY_STATUS_SUCCESS;
}
