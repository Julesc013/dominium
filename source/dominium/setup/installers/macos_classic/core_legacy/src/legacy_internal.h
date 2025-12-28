/*
FILE: source/dominium/setup/installers/macos_classic/core_legacy/src/legacy_internal.h
MODULE: Dominium Setup (Legacy Core)
PURPOSE: Internal helpers for Classic-compatible legacy core.
*/
#ifndef DSU_LEGACY_INTERNAL_H_INCLUDED
#define DSU_LEGACY_INTERNAL_H_INCLUDED

#include "../include/dsu_legacy_core.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef DSU_LEGACY_MAX_PATH
#define DSU_LEGACY_MAX_PATH 4096u
#endif

typedef struct dsu_legacy_blob_t {
    unsigned char *data;
    dsu_legacy_u32 size;
    dsu_legacy_u32 cap;
} dsu_legacy_blob_t;

typedef struct dsu_legacy_log_t {
    FILE *f;
} dsu_legacy_log_t;

typedef dsu_legacy_status_t (*dsu_legacy_fs_copy_cb)(const char *rel_path,
                                                     const char *dst_path,
                                                     void *user);

static void dsu_legacy_blob_init(dsu_legacy_blob_t *b) {
    if (!b) return;
    b->data = NULL;
    b->size = 0u;
    b->cap = 0u;
}

static void dsu_legacy_blob_free(dsu_legacy_blob_t *b) {
    if (!b) return;
    free(b->data);
    b->data = NULL;
    b->size = 0u;
    b->cap = 0u;
}

static dsu_legacy_status_t dsu_legacy_blob_reserve(dsu_legacy_blob_t *b, dsu_legacy_u32 add) {
    dsu_legacy_u32 need;
    dsu_legacy_u32 new_cap;
    unsigned char *p;
    if (!b) return DSU_LEGACY_STATUS_INVALID_ARGS;
    if (add == 0u) return DSU_LEGACY_STATUS_SUCCESS;
    need = b->size + add;
    if (need < b->size) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
    if (need <= b->cap) return DSU_LEGACY_STATUS_SUCCESS;
    new_cap = (b->cap == 0u) ? 256u : b->cap;
    while (new_cap < need) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = need;
            break;
        }
        new_cap *= 2u;
    }
    p = (unsigned char *)realloc(b->data, (size_t)new_cap);
    if (!p) return DSU_LEGACY_STATUS_IO_ERROR;
    b->data = p;
    b->cap = new_cap;
    return DSU_LEGACY_STATUS_SUCCESS;
}

static dsu_legacy_status_t dsu_legacy_blob_append(dsu_legacy_blob_t *b, const void *bytes, dsu_legacy_u32 n) {
    dsu_legacy_status_t st;
    if (!b) return DSU_LEGACY_STATUS_INVALID_ARGS;
    if (n == 0u) return DSU_LEGACY_STATUS_SUCCESS;
    if (!bytes) return DSU_LEGACY_STATUS_INVALID_ARGS;
    st = dsu_legacy_blob_reserve(b, n);
    if (st != DSU_LEGACY_STATUS_SUCCESS) return st;
    memcpy(b->data + b->size, bytes, (size_t)n);
    b->size += n;
    return DSU_LEGACY_STATUS_SUCCESS;
}

static dsu_legacy_status_t dsu_legacy_blob_put_u16le(dsu_legacy_blob_t *b, dsu_legacy_u16 v) {
    unsigned char tmp[2];
    tmp[0] = (unsigned char)(v & 0xFFu);
    tmp[1] = (unsigned char)((v >> 8) & 0xFFu);
    return dsu_legacy_blob_append(b, tmp, 2u);
}

static dsu_legacy_status_t dsu_legacy_blob_put_u32le(dsu_legacy_blob_t *b, dsu_legacy_u32 v) {
    unsigned char tmp[4];
    tmp[0] = (unsigned char)(v & 0xFFu);
    tmp[1] = (unsigned char)((v >> 8) & 0xFFu);
    tmp[2] = (unsigned char)((v >> 16) & 0xFFu);
    tmp[3] = (unsigned char)((v >> 24) & 0xFFu);
    return dsu_legacy_blob_append(b, tmp, 4u);
}

static dsu_legacy_status_t dsu_legacy_blob_put_u64le(dsu_legacy_blob_t *b, dsu_legacy_u64 v) {
    unsigned char tmp[8];
    tmp[0] = (unsigned char)(v & 0xFFu);
    tmp[1] = (unsigned char)((v >> 8) & 0xFFu);
    tmp[2] = (unsigned char)((v >> 16) & 0xFFu);
    tmp[3] = (unsigned char)((v >> 24) & 0xFFu);
    tmp[4] = 0u;
    tmp[5] = 0u;
    tmp[6] = 0u;
    tmp[7] = 0u;
    return dsu_legacy_blob_append(b, tmp, 8u);
}

static dsu_legacy_status_t dsu_legacy_blob_put_tlv(dsu_legacy_blob_t *b,
                                                   dsu_legacy_u16 type,
                                                   const void *payload,
                                                   dsu_legacy_u32 payload_len) {
    dsu_legacy_status_t st;
    if (!b) return DSU_LEGACY_STATUS_INVALID_ARGS;
    if (!payload && payload_len != 0u) return DSU_LEGACY_STATUS_INVALID_ARGS;
    st = dsu_legacy_blob_put_u16le(b, type);
    if (st != DSU_LEGACY_STATUS_SUCCESS) return st;
    st = dsu_legacy_blob_put_u32le(b, payload_len);
    if (st != DSU_LEGACY_STATUS_SUCCESS) return st;
    return dsu_legacy_blob_append(b, payload, payload_len);
}

static dsu_legacy_u32 dsu_legacy_strlen(const char *s) {
    size_t n;
    if (!s) return 0u;
    n = strlen(s);
    if (n > 0xFFFFFFFFu) return 0u;
    return (dsu_legacy_u32)n;
}

static int dsu_legacy_is_ascii_printable(const char *s) {
    const unsigned char *p;
    if (!s) return 0;
    p = (const unsigned char *)s;
    while (*p) {
        unsigned char c = *p++;
        if (c < 32u || c > 126u) return 0;
    }
    return 1;
}

static int dsu_legacy_is_ascii_id(const char *s) {
    const unsigned char *p;
    if (!s || s[0] == '\0') return 0;
    p = (const unsigned char *)s;
    while (*p) {
        unsigned char c = *p++;
        if ((c >= 'a' && c <= 'z') ||
            (c >= '0' && c <= '9') ||
            c == '_' || c == '.' || c == '-') {
            continue;
        }
        return 0;
    }
    return 1;
}

static void dsu_legacy_ascii_lower_inplace(char *s) {
    unsigned char *p;
    if (!s) return;
    p = (unsigned char *)s;
    while (*p) {
        if (*p >= 'A' && *p <= 'Z') {
            *p = (unsigned char)(*p - 'A' + 'a');
        }
        ++p;
    }
}

static char *dsu_legacy_strdup(const char *s) {
    size_t n;
    char *p;
    if (!s) return NULL;
    n = strlen(s);
    p = (char *)malloc(n + 1u);
    if (!p) return NULL;
    if (n) memcpy(p, s, n);
    p[n] = '\0';
    return p;
}

static dsu_legacy_status_t dsu_legacy_read_file_all(const char *path,
                                                    unsigned char **out_bytes,
                                                    dsu_legacy_u32 *out_len) {
    FILE *f;
    long sz;
    unsigned char *buf;
    size_t nread;
    if (!path || !out_bytes || !out_len) return DSU_LEGACY_STATUS_INVALID_ARGS;
    *out_bytes = NULL;
    *out_len = 0u;
    f = fopen(path, "rb");
    if (!f) return DSU_LEGACY_STATUS_IO_ERROR;
    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return DSU_LEGACY_STATUS_IO_ERROR;
    }
    sz = ftell(f);
    if (sz < 0) {
        fclose(f);
        return DSU_LEGACY_STATUS_IO_ERROR;
    }
    if (fseek(f, 0, SEEK_SET) != 0) {
        fclose(f);
        return DSU_LEGACY_STATUS_IO_ERROR;
    }
    buf = (unsigned char *)malloc((size_t)sz);
    if (!buf && sz != 0) {
        fclose(f);
        return DSU_LEGACY_STATUS_IO_ERROR;
    }
    nread = (sz == 0) ? 0u : fread(buf, 1u, (size_t)sz, f);
    fclose(f);
    if (nread != (size_t)sz) {
        free(buf);
        return DSU_LEGACY_STATUS_IO_ERROR;
    }
    *out_bytes = buf;
    *out_len = (dsu_legacy_u32)sz;
    return DSU_LEGACY_STATUS_SUCCESS;
}

static dsu_legacy_status_t dsu_legacy_write_file_all(const char *path,
                                                     const unsigned char *bytes,
                                                     dsu_legacy_u32 len) {
    FILE *f;
    size_t nw;
    if (!path || (!bytes && len != 0u)) return DSU_LEGACY_STATUS_INVALID_ARGS;
    f = fopen(path, "wb");
    if (!f) return DSU_LEGACY_STATUS_IO_ERROR;
    nw = (len == 0u) ? 0u : fwrite(bytes, 1u, (size_t)len, f);
    if (nw != (size_t)len) {
        fclose(f);
        return DSU_LEGACY_STATUS_IO_ERROR;
    }
    if (fclose(f) != 0) return DSU_LEGACY_STATUS_IO_ERROR;
    return DSU_LEGACY_STATUS_SUCCESS;
}

static dsu_legacy_status_t dsu_legacy_read_u16le(const unsigned char *buf,
                                                 dsu_legacy_u32 len,
                                                 dsu_legacy_u32 *io_off,
                                                 dsu_legacy_u16 *out_v) {
    dsu_legacy_u32 off;
    if (!buf || !io_off || !out_v) return DSU_LEGACY_STATUS_INVALID_ARGS;
    off = *io_off;
    if (len - off < 2u) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
    *out_v = (dsu_legacy_u16)((dsu_legacy_u16)buf[off]
                            | ((dsu_legacy_u16)buf[off + 1u] << 8));
    *io_off = off + 2u;
    return DSU_LEGACY_STATUS_SUCCESS;
}

static dsu_legacy_status_t dsu_legacy_read_u32le(const unsigned char *buf,
                                                 dsu_legacy_u32 len,
                                                 dsu_legacy_u32 *io_off,
                                                 dsu_legacy_u32 *out_v) {
    dsu_legacy_u32 off;
    if (!buf || !io_off || !out_v) return DSU_LEGACY_STATUS_INVALID_ARGS;
    off = *io_off;
    if (len - off < 4u) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
    *out_v = (dsu_legacy_u32)buf[off]
           | ((dsu_legacy_u32)buf[off + 1u] << 8)
           | ((dsu_legacy_u32)buf[off + 2u] << 16)
           | ((dsu_legacy_u32)buf[off + 3u] << 24);
    *io_off = off + 4u;
    return DSU_LEGACY_STATUS_SUCCESS;
}

static dsu_legacy_status_t dsu_legacy_read_u64le(const unsigned char *buf,
                                                 dsu_legacy_u32 len,
                                                 dsu_legacy_u32 *io_off,
                                                 dsu_legacy_u64 *out_v) {
    dsu_legacy_u32 off;
    dsu_legacy_u32 lo = 0u;
    if (!buf || !io_off || !out_v) return DSU_LEGACY_STATUS_INVALID_ARGS;
    off = *io_off;
    if (len - off < 8u) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
    lo = (dsu_legacy_u32)buf[off]
       | ((dsu_legacy_u32)buf[off + 1u] << 8)
       | ((dsu_legacy_u32)buf[off + 2u] << 16)
       | ((dsu_legacy_u32)buf[off + 3u] << 24);
    *out_v = (dsu_legacy_u64)lo;
    *io_off = off + 8u;
    return DSU_LEGACY_STATUS_SUCCESS;
}

static dsu_legacy_status_t dsu_legacy_tlv_read_header(const unsigned char *buf,
                                                      dsu_legacy_u32 len,
                                                      dsu_legacy_u32 *io_off,
                                                      dsu_legacy_u16 *out_type,
                                                      dsu_legacy_u32 *out_len) {
    dsu_legacy_status_t st;
    dsu_legacy_u16 t;
    dsu_legacy_u32 n;
    if (!buf || !io_off || !out_type || !out_len) return DSU_LEGACY_STATUS_INVALID_ARGS;
    st = dsu_legacy_read_u16le(buf, len, io_off, &t);
    if (st != DSU_LEGACY_STATUS_SUCCESS) return st;
    st = dsu_legacy_read_u32le(buf, len, io_off, &n);
    if (st != DSU_LEGACY_STATUS_SUCCESS) return st;
    if (n > len - *io_off) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
    *out_type = t;
    *out_len = n;
    return DSU_LEGACY_STATUS_SUCCESS;
}

static dsu_legacy_status_t dsu_legacy_tlv_skip_value(dsu_legacy_u32 len,
                                                     dsu_legacy_u32 *io_off,
                                                     dsu_legacy_u32 payload_len) {
    dsu_legacy_u32 off;
    if (!io_off) return DSU_LEGACY_STATUS_INVALID_ARGS;
    off = *io_off;
    if (payload_len > len - off) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
    *io_off = off + payload_len;
    return DSU_LEGACY_STATUS_SUCCESS;
}

static dsu_legacy_status_t dsu_legacy_dup_bytes_cstr(const unsigned char *bytes,
                                                     dsu_legacy_u32 len,
                                                     char **out_str) {
    char *s;
    if (!out_str) return DSU_LEGACY_STATUS_INVALID_ARGS;
    *out_str = NULL;
    if (!bytes && len != 0u) return DSU_LEGACY_STATUS_INVALID_ARGS;
    s = (char *)malloc((size_t)len + 1u);
    if (!s) return DSU_LEGACY_STATUS_IO_ERROR;
    if (len) memcpy(s, bytes, (size_t)len);
    s[len] = '\0';
    *out_str = s;
    return DSU_LEGACY_STATUS_SUCCESS;
}

static dsu_legacy_status_t dsu_legacy_list_push(char ***items,
                                                dsu_legacy_u32 *io_count,
                                                dsu_legacy_u32 *io_cap,
                                                char *owned) {
    dsu_legacy_u32 count;
    dsu_legacy_u32 cap;
    char **p;
    if (!items || !io_count || !io_cap || !owned) return DSU_LEGACY_STATUS_INVALID_ARGS;
    count = *io_count;
    cap = *io_cap;
    if (count == cap) {
        dsu_legacy_u32 new_cap = (cap == 0u) ? 4u : (cap * 2u);
        p = (char **)realloc(*items, (size_t)new_cap * sizeof(*p));
        if (!p) return DSU_LEGACY_STATUS_IO_ERROR;
        *items = p;
        *io_cap = new_cap;
    }
    (*items)[count] = owned;
    *io_count = count + 1u;
    return DSU_LEGACY_STATUS_SUCCESS;
}

#define DSU_LEGACY_FILE_HEADER_BASE_SIZE 20u
#define DSU_LEGACY_ENDIAN_MARKER_LE 0xFFFEu

static dsu_legacy_u32 dsu_legacy_header_checksum32_base(const unsigned char hdr[DSU_LEGACY_FILE_HEADER_BASE_SIZE]) {
    dsu_legacy_u32 sum = 0u;
    dsu_legacy_u32 i;
    if (!hdr) return 0u;
    for (i = 0u; i < (DSU_LEGACY_FILE_HEADER_BASE_SIZE - 4u); ++i) {
        sum += (dsu_legacy_u32)hdr[i];
    }
    return sum;
}

static dsu_legacy_status_t dsu_legacy_file_wrap_payload(const unsigned char magic[4],
                                                        dsu_legacy_u16 version,
                                                        const unsigned char *payload,
                                                        dsu_legacy_u32 payload_len,
                                                        dsu_legacy_blob_t *out_file) {
    unsigned char hdr[DSU_LEGACY_FILE_HEADER_BASE_SIZE];
    dsu_legacy_u32 checksum;
    if (!magic || !out_file) return DSU_LEGACY_STATUS_INVALID_ARGS;
    if (!payload && payload_len != 0u) return DSU_LEGACY_STATUS_INVALID_ARGS;
    dsu_legacy_blob_init(out_file);
    hdr[0] = magic[0];
    hdr[1] = magic[1];
    hdr[2] = magic[2];
    hdr[3] = magic[3];
    hdr[4] = (unsigned char)(version & 0xFFu);
    hdr[5] = (unsigned char)((version >> 8) & 0xFFu);
    hdr[6] = (unsigned char)(DSU_LEGACY_ENDIAN_MARKER_LE & 0xFFu);
    hdr[7] = (unsigned char)((DSU_LEGACY_ENDIAN_MARKER_LE >> 8) & 0xFFu);
    hdr[8] = (unsigned char)(DSU_LEGACY_FILE_HEADER_BASE_SIZE & 0xFFu);
    hdr[9] = (unsigned char)((DSU_LEGACY_FILE_HEADER_BASE_SIZE >> 8) & 0xFFu);
    hdr[10] = 0u;
    hdr[11] = 0u;
    hdr[12] = (unsigned char)(payload_len & 0xFFu);
    hdr[13] = (unsigned char)((payload_len >> 8) & 0xFFu);
    hdr[14] = (unsigned char)((payload_len >> 16) & 0xFFu);
    hdr[15] = (unsigned char)((payload_len >> 24) & 0xFFu);
    hdr[16] = 0u;
    hdr[17] = 0u;
    hdr[18] = 0u;
    hdr[19] = 0u;
    checksum = dsu_legacy_header_checksum32_base(hdr);
    hdr[16] = (unsigned char)(checksum & 0xFFu);
    hdr[17] = (unsigned char)((checksum >> 8) & 0xFFu);
    hdr[18] = (unsigned char)((checksum >> 16) & 0xFFu);
    hdr[19] = (unsigned char)((checksum >> 24) & 0xFFu);
    if (dsu_legacy_blob_append(out_file, hdr, DSU_LEGACY_FILE_HEADER_BASE_SIZE) != DSU_LEGACY_STATUS_SUCCESS) {
        dsu_legacy_blob_free(out_file);
        return DSU_LEGACY_STATUS_IO_ERROR;
    }
    if (payload_len) {
        if (dsu_legacy_blob_append(out_file, payload, payload_len) != DSU_LEGACY_STATUS_SUCCESS) {
            dsu_legacy_blob_free(out_file);
            return DSU_LEGACY_STATUS_IO_ERROR;
        }
    }
    return DSU_LEGACY_STATUS_SUCCESS;
}

static dsu_legacy_status_t dsu_legacy_file_unwrap_payload(const unsigned char *file_bytes,
                                                          dsu_legacy_u32 file_len,
                                                          const unsigned char magic[4],
                                                          dsu_legacy_u16 version,
                                                          const unsigned char **out_payload,
                                                          dsu_legacy_u32 *out_payload_len) {
    dsu_legacy_u32 header_size;
    dsu_legacy_u32 payload_len;
    dsu_legacy_u16 file_ver;
    dsu_legacy_u16 endian;
    dsu_legacy_u32 checksum_stored;
    dsu_legacy_u32 checksum_calc;
    if (!file_bytes || !magic || !out_payload || !out_payload_len) return DSU_LEGACY_STATUS_INVALID_ARGS;
    if (file_len < DSU_LEGACY_FILE_HEADER_BASE_SIZE) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
    if (memcmp(file_bytes, magic, 4u) != 0) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
    file_ver = (dsu_legacy_u16)((dsu_legacy_u16)file_bytes[4] | ((dsu_legacy_u16)file_bytes[5] << 8));
    if (file_ver != version) return DSU_LEGACY_STATUS_UNSUPPORTED;
    endian = (dsu_legacy_u16)((dsu_legacy_u16)file_bytes[6] | ((dsu_legacy_u16)file_bytes[7] << 8));
    if (endian != (dsu_legacy_u16)DSU_LEGACY_ENDIAN_MARKER_LE) return DSU_LEGACY_STATUS_UNSUPPORTED;
    header_size = (dsu_legacy_u32)file_bytes[8]
                | ((dsu_legacy_u32)file_bytes[9] << 8)
                | ((dsu_legacy_u32)file_bytes[10] << 16)
                | ((dsu_legacy_u32)file_bytes[11] << 24);
    if (header_size < DSU_LEGACY_FILE_HEADER_BASE_SIZE) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
    if (header_size > file_len) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
    payload_len = (dsu_legacy_u32)file_bytes[12]
                | ((dsu_legacy_u32)file_bytes[13] << 8)
                | ((dsu_legacy_u32)file_bytes[14] << 16)
                | ((dsu_legacy_u32)file_bytes[15] << 24);
    checksum_stored = (dsu_legacy_u32)file_bytes[16]
                    | ((dsu_legacy_u32)file_bytes[17] << 8)
                    | ((dsu_legacy_u32)file_bytes[18] << 16)
                    | ((dsu_legacy_u32)file_bytes[19] << 24);
    checksum_calc = dsu_legacy_header_checksum32_base(file_bytes);
    if (checksum_calc != checksum_stored) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
    if (file_len - header_size < payload_len) return DSU_LEGACY_STATUS_INTEGRITY_ERROR;
    *out_payload = file_bytes + header_size;
    *out_payload_len = payload_len;
    return DSU_LEGACY_STATUS_SUCCESS;
}

dsu_legacy_status_t dsu_legacy_log_open(dsu_legacy_log_t *log, const char *path);
void dsu_legacy_log_close(dsu_legacy_log_t *log);
void dsu_legacy_log_printf(dsu_legacy_log_t *log, const char *fmt, ...);

dsu_legacy_status_t dsu_legacy_fs_copy_tree(const char *src_root,
                                            const char *dst_root,
                                            dsu_legacy_fs_copy_cb cb,
                                            void *user);
dsu_legacy_status_t dsu_legacy_fs_copy_file(const char *src, const char *dst);
dsu_legacy_status_t dsu_legacy_fs_extract_archive(const char *archive_path,
                                                  const char *dst_root,
                                                  dsu_legacy_fs_copy_cb cb,
                                                  void *user);

#endif /* DSU_LEGACY_INTERNAL_H_INCLUDED */
