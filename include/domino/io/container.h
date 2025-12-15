#ifndef DOMINO_IO_CONTAINER_H_INCLUDED
#define DOMINO_IO_CONTAINER_H_INCLUDED
/*
 * DTLV container reader/writer (C89/C++98 visible).
 *
 * Implements the public serialization container specified in:
 *   docs/SPEC_CONTAINER_TLV.md
 *
 * Notes:
 * - All on-disk values are little-endian; parsing is explicit.
 * - Reader supports memory-backed and file-backed containers.
 * - Writer supports memory-backed and file-backed containers.
 */

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/*------------------------------------------------------------
 * Constants
 *------------------------------------------------------------*/

#define DTLV_MAGIC_0 ((u8)'D')
#define DTLV_MAGIC_1 ((u8)'T')
#define DTLV_MAGIC_2 ((u8)'L')
#define DTLV_MAGIC_3 ((u8)'V')

#define DTLV_ENDIAN_MARK_LE ((u16)0xFFFEu)

#define DTLV_CONTAINER_VERSION_V1 ((u16)1u)
#define DTLV_HEADER_SIZE_V1       ((u32)32u)
#define DTLV_DIR_ENTRY_SIZE_V1    ((u32)32u)

/* Directory entry flags (u16). */
#define DTLV_CHUNK_F_HAS_CRC32 ((u16)0x0001u)

/*------------------------------------------------------------
 * Explicit little-endian helpers
 *------------------------------------------------------------*/

u16 dtlv_le_read_u16(const unsigned char* p);
u32 dtlv_le_read_u32(const unsigned char* p);
u64 dtlv_le_read_u64(const unsigned char* p);
void dtlv_le_write_u16(unsigned char* p, u16 v);
void dtlv_le_write_u32(unsigned char* p, u32 v);
void dtlv_le_write_u64(unsigned char* p, u64 v);

/*------------------------------------------------------------
 * TLV helpers (tag:u32_le, len:u32_le, payload bytes)
 *------------------------------------------------------------*/

int dtlv_tlv_next(
    const unsigned char* tlv,
    u32                  tlv_len,
    u32*                 offset,
    u32*                 tag_out,
    const unsigned char** payload_out,
    u32*                 payload_len_out
);

int dtlv_tlv_write(
    unsigned char* dst,
    u32            dst_cap,
    u32*           in_out_offset,
    u32            tag,
    const void*    payload,
    u32            payload_len
);

/*------------------------------------------------------------
 * Container directory entry (host-endian, parsed values)
 *------------------------------------------------------------*/

typedef struct dtlv_dir_entry {
    u32 type_id;
    u16 version;
    u16 flags;
    u64 offset;
    u64 size;
    u32 crc32;
} dtlv_dir_entry;

/*------------------------------------------------------------
 * Container reader
 *------------------------------------------------------------*/

typedef struct dtlv_reader {
    /* memory-backed */
    const unsigned char* mem;
    u64                  mem_size;

    /* file-backed (dsys_file_* handle) */
    void* fh;
    int   owns_fh;
    u64   file_size;

    /* parsed header */
    u64 dir_offset;
    u32 chunk_count;

    /* parsed directory */
    dtlv_dir_entry* entries;
} dtlv_reader;

void dtlv_reader_init(dtlv_reader* r);
void dtlv_reader_dispose(dtlv_reader* r);

int dtlv_reader_open_file(dtlv_reader* r, const char* path);
int dtlv_reader_init_file(dtlv_reader* r, void* fh); /* does not take ownership */
int dtlv_reader_init_mem(dtlv_reader* r, const void* data, u64 size);

u32 dtlv_reader_chunk_count(const dtlv_reader* r);
const dtlv_dir_entry* dtlv_reader_chunk_at(const dtlv_reader* r, u32 index);

const dtlv_dir_entry* dtlv_reader_find_first(
    const dtlv_reader* r,
    u32                type_id,
    u16                version /* pass 0 to ignore version */
);

/* Read chunk payload into caller buffer. Returns 0 on success. */
int dtlv_reader_read_chunk(
    dtlv_reader*         r,
    const dtlv_dir_entry* e,
    void*                dst,
    u64                  dst_cap
);

/* Read chunk payload into malloc-owned buffer. Returns 0 on success. */
int dtlv_reader_read_chunk_alloc(
    dtlv_reader*          r,
    const dtlv_dir_entry* e,
    unsigned char**       out_bytes,
    u32*                  out_size
);

/* If memory-backed, return direct pointer into the container bytes. */
int dtlv_reader_chunk_memview(
    const dtlv_reader*    r,
    const dtlv_dir_entry* e,
    const unsigned char** out_ptr,
    u32*                  out_size
);

/*------------------------------------------------------------
 * Container writer
 *------------------------------------------------------------*/

typedef struct dtlv_writer {
    /* memory-backed */
    unsigned char* mem;
    u32            mem_cap;

    /* file-backed (dsys_file_* handle) */
    void* fh;
    int   owns_fh;

    /* current write offset (bytes from start) */
    u64 off;

    /* current chunk tracking */
    int chunk_open;
    u64 chunk_start;

    /* collected directory entries (in write order) */
    dtlv_dir_entry* entries;
    u32             entry_count;
    u32             entry_cap;
} dtlv_writer;

void dtlv_writer_init(dtlv_writer* w);
void dtlv_writer_dispose(dtlv_writer* w);

int dtlv_writer_open_file(dtlv_writer* w, const char* path);
int dtlv_writer_init_file(dtlv_writer* w, void* fh); /* does not take ownership */
int dtlv_writer_init_mem(dtlv_writer* w, void* buf, u32 cap);

int dtlv_writer_begin_chunk(dtlv_writer* w, u32 type_id, u16 version, u16 flags);
int dtlv_writer_write(dtlv_writer* w, const void* bytes, u32 len);
int dtlv_writer_write_tlv(dtlv_writer* w, u32 tag, const void* payload, u32 payload_len);
int dtlv_writer_end_chunk(dtlv_writer* w);

/* Finalize directory + patch header. Returns 0 on success. */
int dtlv_writer_finalize(dtlv_writer* w);

/* For memory-backed writers: returns total bytes written after finalize. */
u32 dtlv_writer_mem_size(const dtlv_writer* w);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_IO_CONTAINER_H_INCLUDED */

