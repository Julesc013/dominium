/*
FILE: source/dominium/setup/core/src/util/dsu_util_archive.c
MODULE: Dominium Setup
PURPOSE: Minimal deterministic local archive format for payloads (Plan S-4).
*/
#include "dsu_util_internal.h"

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define DSU_ARCHIVE_MAGIC_0 'D'
#define DSU_ARCHIVE_MAGIC_1 'S'
#define DSU_ARCHIVE_MAGIC_2 'U'
#define DSU_ARCHIVE_MAGIC_3 'A'

#define DSU_ARCHIVE_VERSION 1u

static dsu_status_t dsu__read_exact(FILE *f, void *dst, dsu_u32 n) {
    size_t nr;
    if (!f || !dst) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (n == 0u) {
        return DSU_STATUS_SUCCESS;
    }
    nr = fread(dst, 1u, (size_t)n, f);
    if (nr != (size_t)n) {
        return DSU_STATUS_IO_ERROR;
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__read_u16le_file(FILE *f, dsu_u16 *out_v) {
    dsu_u8 b[2];
    if (!out_v) return DSU_STATUS_INVALID_ARGS;
    if (dsu__read_exact(f, b, 2u) != DSU_STATUS_SUCCESS) return DSU_STATUS_IO_ERROR;
    *out_v = (dsu_u16)((dsu_u16)b[0] | ((dsu_u16)b[1] << 8));
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__read_u32le_file(FILE *f, dsu_u32 *out_v) {
    dsu_u8 b[4];
    if (!out_v) return DSU_STATUS_INVALID_ARGS;
    if (dsu__read_exact(f, b, 4u) != DSU_STATUS_SUCCESS) return DSU_STATUS_IO_ERROR;
    *out_v = (dsu_u32)b[0]
           | ((dsu_u32)b[1] << 8)
           | ((dsu_u32)b[2] << 16)
           | ((dsu_u32)b[3] << 24);
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__read_u64le_file(FILE *f, dsu_u64 *out_v) {
    dsu_u8 b[8];
    dsu_u64 v;
    if (!out_v) return DSU_STATUS_INVALID_ARGS;
    if (dsu__read_exact(f, b, 8u) != DSU_STATUS_SUCCESS) return DSU_STATUS_IO_ERROR;
    v = (dsu_u64)b[0]
      | ((dsu_u64)b[1] << 8)
      | ((dsu_u64)b[2] << 16)
      | ((dsu_u64)b[3] << 24)
      | ((dsu_u64)b[4] << 32)
      | ((dsu_u64)b[5] << 40)
      | ((dsu_u64)b[6] << 48)
      | ((dsu_u64)b[7] << 56);
    *out_v = v;
    return DSU_STATUS_SUCCESS;
}

static int dsu__is_alpha(char c) {
    return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z');
}

static int dsu__is_abs_path_like(const char *p) {
    if (!p) return 0;
    if (p[0] == '/' || p[0] == '\\') return 1;
    if ((p[0] == '/' && p[1] == '/') || (p[0] == '\\' && p[1] == '\\')) return 1;
    if (dsu__is_alpha(p[0]) && p[1] == ':' && (p[2] == '/' || p[2] == '\\')) return 1;
    return 0;
}

static dsu_status_t dsu__canon_rel_path(const char *in, char **out_canon) {
    dsu_u32 i;
    dsu_u32 n;
    char *buf;
    dsu_u32 o = 0u;
    dsu_u32 seg_start = 0u;

    if (!out_canon) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_canon = NULL;
    if (!in) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (in[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (dsu__is_abs_path_like(in)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (!dsu__is_ascii_printable(in)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (strchr(in, ':') != NULL) {
        return DSU_STATUS_INVALID_ARGS;
    }

    n = dsu__strlen(in);
    if (n == 0xFFFFFFFFu) {
        return DSU_STATUS_INVALID_ARGS;
    }
    buf = (char *)dsu__malloc(n + 1u);
    if (!buf) {
        return DSU_STATUS_IO_ERROR;
    }

    for (i = 0u; i <= n; ++i) {
        char c = (i < n) ? in[i] : '\0';
        if (c == '\\') c = '/';
        if (c == '/' || c == '\0') {
            dsu_u32 seg_len = (dsu_u32)(i - seg_start);
            if (seg_len == 0u) {
                /* skip */
            } else if (seg_len == 1u && in[seg_start] == '.') {
                /* skip '.' */
            } else if (seg_len == 2u && in[seg_start] == '.' && in[seg_start + 1u] == '.') {
                dsu__free(buf);
                return DSU_STATUS_INVALID_ARGS;
            } else {
                if (o != 0u) {
                    buf[o++] = '/';
                }
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
        dsu__free(buf);
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_canon = buf;
    return DSU_STATUS_SUCCESS;
}

static int dsu__archive_entry_cmp(const void *a, const void *b) {
    const dsu__archive_entry_t *ea = (const dsu__archive_entry_t *)a;
    const dsu__archive_entry_t *eb = (const dsu__archive_entry_t *)b;
    return dsu__strcmp_bytes(ea->path, eb->path);
}

dsu_status_t dsu__archive_list(const char *archive_path, dsu__archive_entry_t **out_entries, dsu_u32 *out_count) {
    FILE *f;
    dsu_u8 magic[4];
    dsu_u16 ver;
    dsu_u16 endian;
    dsu_u32 count;
    dsu_u32 reserved32;
    dsu_u32 i;
    dsu__archive_entry_t *items;
    dsu_status_t st;

    if (!archive_path || !out_entries || !out_count) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_entries = NULL;
    *out_count = 0u;

    f = fopen(archive_path, "rb");
    if (!f) {
        return DSU_STATUS_IO_ERROR;
    }

    st = dsu__read_exact(f, magic, 4u);
    if (st != DSU_STATUS_SUCCESS) goto fail;
    if (magic[0] != (dsu_u8)DSU_ARCHIVE_MAGIC_0 ||
        magic[1] != (dsu_u8)DSU_ARCHIVE_MAGIC_1 ||
        magic[2] != (dsu_u8)DSU_ARCHIVE_MAGIC_2 ||
        magic[3] != (dsu_u8)DSU_ARCHIVE_MAGIC_3) {
        st = DSU_STATUS_INTEGRITY_ERROR;
        goto fail;
    }
    st = dsu__read_u16le_file(f, &ver);
    if (st != DSU_STATUS_SUCCESS) goto fail;
    st = dsu__read_u16le_file(f, &endian);
    if (st != DSU_STATUS_SUCCESS) goto fail;
    if ((dsu_u32)ver != DSU_ARCHIVE_VERSION || endian != (dsu_u16)DSU_ENDIAN_MARKER_LE) {
        st = DSU_STATUS_UNSUPPORTED_VERSION;
        goto fail;
    }
    st = dsu__read_u32le_file(f, &count);
    if (st != DSU_STATUS_SUCCESS) goto fail;
    st = dsu__read_u32le_file(f, &reserved32);
    if (st != DSU_STATUS_SUCCESS) goto fail;
    (void)reserved32;

    items = (dsu__archive_entry_t *)dsu__malloc(count * (dsu_u32)sizeof(*items));
    if (!items && count != 0u) {
        st = DSU_STATUS_IO_ERROR;
        goto fail;
    }
    if (count) {
        memset(items, 0, (size_t)count * sizeof(*items));
    }

    for (i = 0u; i < count; ++i) {
        dsu_u32 path_len;
        char *path_raw = NULL;
        char *path_canon = NULL;
        dsu_u64 size;
        long off;

        st = dsu__read_u32le_file(f, &path_len);
        if (st != DSU_STATUS_SUCCESS) break;
        if (path_len == 0u || path_len > 4096u) {
            st = DSU_STATUS_INTEGRITY_ERROR;
            break;
        }
        path_raw = (char *)dsu__malloc(path_len + 1u);
        if (!path_raw) {
            st = DSU_STATUS_IO_ERROR;
            break;
        }
        st = dsu__read_exact(f, path_raw, path_len);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(path_raw);
            break;
        }
        path_raw[path_len] = '\0';
        st = dsu__canon_rel_path(path_raw, &path_canon);
        dsu__free(path_raw);
        if (st != DSU_STATUS_SUCCESS) {
            break;
        }

        st = dsu__read_u64le_file(f, &size);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(path_canon);
            break;
        }
        st = dsu__read_exact(f, items[i].sha256, 32u);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(path_canon);
            break;
        }

        off = ftell(f);
        if (off < 0) {
            dsu__free(path_canon);
            st = DSU_STATUS_IO_ERROR;
            break;
        }
        items[i].path = path_canon;
        items[i].size = size;
        items[i].data_offset = (dsu_u64)(unsigned long)off;

        if (size != 0u) {
            if (fseek(f, (long)size, SEEK_CUR) != 0) {
                st = DSU_STATUS_IO_ERROR;
                break;
            }
        }
    }

    if (st != DSU_STATUS_SUCCESS) {
        dsu__archive_free_entries(items, i);
        goto fail;
    }

    if (count > 1u) {
        qsort(items, (size_t)count, sizeof(*items), dsu__archive_entry_cmp);
        for (i = 1u; i < count; ++i) {
            if (dsu__strcmp_bytes(items[i - 1u].path, items[i].path) == 0) {
                dsu__archive_free_entries(items, count);
                st = DSU_STATUS_INTEGRITY_ERROR;
                goto fail;
            }
        }
    }

    fclose(f);
    *out_entries = items;
    *out_count = count;
    return DSU_STATUS_SUCCESS;

fail:
    if (f) fclose(f);
    return st;
}

void dsu__archive_free_entries(dsu__archive_entry_t *entries, dsu_u32 count) {
    dsu_u32 i;
    if (!entries) {
        return;
    }
    for (i = 0u; i < count; ++i) {
        dsu__free(entries[i].path);
        entries[i].path = NULL;
    }
    dsu__free(entries);
}

dsu_status_t dsu__archive_extract_file(const char *archive_path,
                                      const char *member_path,
                                      const char *dst_path) {
    dsu__archive_entry_t *entries = NULL;
    dsu_u32 count = 0u;
    dsu_u32 i;
    dsu_status_t st;
    char *canon = NULL;
    FILE *in = NULL;
    FILE *out = NULL;
    unsigned char buf[32768];
    dsu_u64 remaining;

    if (!archive_path || !member_path || !dst_path) {
        return DSU_STATUS_INVALID_ARGS;
    }

    st = dsu__canon_rel_path(member_path, &canon);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    st = dsu__archive_list(archive_path, &entries, &count);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(canon);
        return st;
    }

    for (i = 0u; i < count; ++i) {
        if (dsu__strcmp_bytes(entries[i].path, canon) == 0) {
            break;
        }
    }
    dsu__free(canon);
    canon = NULL;
    if (i == count) {
        dsu__archive_free_entries(entries, count);
        return DSU_STATUS_IO_ERROR;
    }

    in = fopen(archive_path, "rb");
    if (!in) {
        dsu__archive_free_entries(entries, count);
        return DSU_STATUS_IO_ERROR;
    }
    if (fseek(in, (long)entries[i].data_offset, SEEK_SET) != 0) {
        fclose(in);
        dsu__archive_free_entries(entries, count);
        return DSU_STATUS_IO_ERROR;
    }
    out = fopen(dst_path, "wb");
    if (!out) {
        fclose(in);
        dsu__archive_free_entries(entries, count);
        return DSU_STATUS_IO_ERROR;
    }

    remaining = entries[i].size;
    while (remaining != 0u) {
        dsu_u32 want = (remaining > (dsu_u64)sizeof(buf)) ? (dsu_u32)sizeof(buf) : (dsu_u32)remaining;
        size_t nr = fread(buf, 1u, (size_t)want, in);
        if (nr != (size_t)want) {
            fclose(in);
            fclose(out);
            dsu__archive_free_entries(entries, count);
            return DSU_STATUS_IO_ERROR;
        }
        if (fwrite(buf, 1u, nr, out) != nr) {
            fclose(in);
            fclose(out);
            dsu__archive_free_entries(entries, count);
            return DSU_STATUS_IO_ERROR;
        }
        remaining -= (dsu_u64)want;
    }
    if (fclose(out) != 0) {
        fclose(in);
        dsu__archive_free_entries(entries, count);
        return DSU_STATUS_IO_ERROR;
    }
    out = NULL;
    fclose(in);
    in = NULL;

    {
        dsu_u8 digest[32];
        if (dsu__sha256_file(dst_path, digest) != DSU_STATUS_SUCCESS) {
            dsu__archive_free_entries(entries, count);
            return DSU_STATUS_IO_ERROR;
        }
        if (memcmp(digest, entries[i].sha256, 32u) != 0) {
            dsu__archive_free_entries(entries, count);
            return DSU_STATUS_INTEGRITY_ERROR;
        }
    }

    dsu__archive_free_entries(entries, count);
    return DSU_STATUS_SUCCESS;
}
