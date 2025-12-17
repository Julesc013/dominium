/*
FILE: source/dominium/setup/core/src/util/dsu_util_internal.h
MODULE: Dominium Setup
PURPOSE: Internal-only utilities shared across Setup Core modules.
*/
#ifndef DSU_UTIL_INTERNAL_H_INCLUDED
#define DSU_UTIL_INTERNAL_H_INCLUDED

#include <stddef.h>

#include "../../include/dsu/dsu_callbacks.h"
#include "../../include/dsu/dsu_config.h"
#include "../../include/dsu/dsu_types.h"

#define DSU_ARRAY_COUNT(a) ((dsu_u32)(sizeof(a) / sizeof((a)[0])))

/* Implemented in util/dsu_util_mem.c */
void *dsu__malloc(dsu_u32 size);
void *dsu__realloc(void *ptr, dsu_u32 size);
void dsu__free(void *ptr);

/* Implemented in util/dsu_util_str.c */
dsu_u32 dsu__strlen(const char *s);
char *dsu__strdup(const char *s);
int dsu__streq(const char *a, const char *b);
int dsu__strcmp_bytes(const char *a, const char *b);
int dsu__is_ascii_printable(const char *s);
int dsu__is_ascii_id(const char *s);
dsu_status_t dsu__ascii_to_lower_inplace(char *s);

/* Implemented in util/dsu_util_sort.c */
void dsu__sort_str_ptrs(char **items, dsu_u32 count);

/* Implemented in util/dsu_util_hash.c */
dsu_u32 dsu_hash32_bytes(const void *bytes, dsu_u32 len);
dsu_u32 dsu_hash32_str(const char *s);

/* Implemented in util/dsu_util_blob.c */
typedef struct dsu_blob_t {
    dsu_u8 *data;
    dsu_u32 size;
    dsu_u32 cap;
} dsu_blob_t;

void dsu__blob_init(dsu_blob_t *b);
void dsu__blob_free(dsu_blob_t *b);
dsu_status_t dsu__blob_reserve(dsu_blob_t *b, dsu_u32 additional);
dsu_status_t dsu__blob_append(dsu_blob_t *b, const void *bytes, dsu_u32 len);

/* Implemented in util/dsu_util_le.c */
dsu_status_t dsu__blob_put_u8(dsu_blob_t *b, dsu_u8 v);
dsu_status_t dsu__blob_put_u16le(dsu_blob_t *b, dsu_u16 v);
dsu_status_t dsu__blob_put_u32le(dsu_blob_t *b, dsu_u32 v);

dsu_status_t dsu__read_u8(const dsu_u8 *buf, dsu_u32 len, dsu_u32 *io_off, dsu_u8 *out_v);
dsu_status_t dsu__read_u16le(const dsu_u8 *buf, dsu_u32 len, dsu_u32 *io_off, dsu_u16 *out_v);
dsu_status_t dsu__read_u32le(const dsu_u8 *buf, dsu_u32 len, dsu_u32 *io_off, dsu_u32 *out_v);
dsu_status_t dsu__read_bytes(const dsu_u8 *buf, dsu_u32 len, dsu_u32 *io_off, void *out_bytes, dsu_u32 n);

/* Implemented in util/dsu_util_filefmt.c */
#define DSU_ENDIAN_MARKER_LE 0xFFFEu
#define DSU_FILE_HEADER_BASE_SIZE 20u

dsu_u32 dsu__header_checksum32_base(const dsu_u8 header_base[DSU_FILE_HEADER_BASE_SIZE]);
dsu_status_t dsu__file_wrap_payload(const dsu_u8 magic[4],
                                   dsu_u16 format_version,
                                   const dsu_u8 *payload,
                                   dsu_u32 payload_len,
                                   dsu_blob_t *out_file_bytes);

dsu_status_t dsu__file_unwrap_payload(const dsu_u8 *file_bytes,
                                     dsu_u32 file_len,
                                     const dsu_u8 expected_magic[4],
                                     dsu_u16 expected_format_version,
                                     const dsu_u8 **out_payload,
                                     dsu_u32 *out_payload_len);

/* Implemented in fs/dsu_fs_stdio.c */
dsu_status_t dsu__fs_read_all(const dsu_config_t *cfg,
                             const char *path,
                             dsu_u8 **out_bytes,
                             dsu_u32 *out_len);
dsu_status_t dsu__fs_write_all(const char *path, const dsu_u8 *bytes, dsu_u32 len);

#endif /* DSU_UTIL_INTERNAL_H_INCLUDED */
