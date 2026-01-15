/*
FILE: include/domino/io/container.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / io/container
RESPONSIBILITY: Defines the public contract for `container` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Determinism-friendly container framing (explicit little-endian parsing); see `docs/SPEC_CONTAINER_TLV.md`.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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

/* dtlv_le_read_u16
 * Purpose: Read a `u16_le` from a byte buffer.
 * Parameters:
 *   p (in): Pointer to at least 2 readable bytes (non-NULL).
 * Returns:
 *   The decoded value.
 */
u16 dtlv_le_read_u16(const unsigned char* p);
/* dtlv_le_read_u32
 * Purpose: Read a `u32_le` from a byte buffer.
 * Parameters:
 *   p (in): Pointer to at least 4 readable bytes (non-NULL).
 * Returns:
 *   The decoded value.
 */
u32 dtlv_le_read_u32(const unsigned char* p);
/* dtlv_le_read_u64
 * Purpose: Read a `u64_le` from a byte buffer.
 * Parameters:
 *   p (in): Pointer to at least 8 readable bytes (non-NULL).
 * Returns:
 *   The decoded value.
 */
u64 dtlv_le_read_u64(const unsigned char* p);
/* dtlv_le_write_u16
 * Purpose: Write a `u16_le` to a byte buffer.
 * Parameters:
 *   p (out): Pointer to at least 2 writable bytes (non-NULL).
 *   v (in): Value to encode.
 */
void dtlv_le_write_u16(unsigned char* p, u16 v);
/* dtlv_le_write_u32
 * Purpose: Write a `u32_le` to a byte buffer.
 * Parameters:
 *   p (out): Pointer to at least 4 writable bytes (non-NULL).
 *   v (in): Value to encode.
 */
void dtlv_le_write_u32(unsigned char* p, u32 v);
/* dtlv_le_write_u64
 * Purpose: Write a `u64_le` to a byte buffer.
 * Parameters:
 *   p (out): Pointer to at least 8 writable bytes (non-NULL).
 *   v (in): Value to encode.
 */
void dtlv_le_write_u64(unsigned char* p, u64 v);

/*------------------------------------------------------------
 * TLV helpers (tag:u32_le, len:u32_le, payload bytes)
 *------------------------------------------------------------*/

/* dtlv_tlv_next
 * Purpose: Iterate a TLV record stream (`u32_le tag`, `u32_le len`, payload bytes).
 * Parameters:
 *   tlv (in): TLV byte stream (may be NULL only when `tlv_len == 0`).
 *   tlv_len (in): Total bytes in `tlv`.
 *   offset (inout): Byte offset into the stream; advanced on success/end.
 *   tag_out (out): Receives decoded tag.
 *   payload_out (out): Receives pointer to the payload bytes within `tlv`.
 *   payload_len_out (out): Receives payload length.
 * Return values / errors:
 *   0 on success (outputs filled; *offset advanced)
 *   1 when `*offset >= tlv_len` (end of stream)
 *  <0 on malformed input or invalid parameters
 */
int dtlv_tlv_next(
    const unsigned char* tlv,
    u32                  tlv_len,
    u32*                 offset,
    u32*                 tag_out,
    const unsigned char** payload_out,
    u32*                 payload_len_out
);

/* dtlv_tlv_write
 * Purpose: Append a TLV record to a destination buffer at `*in_out_offset`.
 * Parameters:
 *   dst (out): Destination buffer (non-NULL).
 *   dst_cap (in): Total capacity of `dst` in bytes.
 *   in_out_offset (inout): Write cursor; advanced on success.
 *   tag (in): Tag to encode as `u32_le`.
 *   payload (in): Payload bytes (may be NULL only when `payload_len == 0`).
 *   payload_len (in): Payload size in bytes.
 * Return values / errors:
 *   0 on success; non-zero on invalid parameters or insufficient space.
 */
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

/* dtlv_dir_entry
 * Purpose: Parsed directory entry values (host-endian) for a DTLV container.
 * Notes:
 * - Field meanings and on-disk encodings are specified in `docs/SPEC_CONTAINER_TLV.md`.
 * - `crc32` is meaningful only when `flags & DTLV_CHUNK_F_HAS_CRC32` is set.
 */
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

/* dtlv_reader
 * Purpose: Reader state for a DTLV container (memory-backed or file-backed).
 * Ownership:
 * - `entries` is allocated/owned by the reader and released by `dtlv_reader_dispose`.
 * - File-backed mode uses a `dsys_file_*` handle (see `include/domino/sys.h`).
 * Thread-safety:
 * - No internal synchronization; each reader instance must be externally serialized.
 */
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

/* dtlv_reader_init
 * Purpose: Initialize a reader to the empty state.
 * Parameters:
 *   r (out): Reader instance to initialize (may be NULL; no-op).
 */
void dtlv_reader_init(dtlv_reader* r);
/* dtlv_reader_dispose
 * Purpose: Release reader-owned resources and return to the empty state.
 * Parameters:
 *   r (inout): Reader instance (may be NULL; no-op).
 */
void dtlv_reader_dispose(dtlv_reader* r);

/* dtlv_reader_open_file
 * Purpose: Open and parse a DTLV container from a file path.
 * Parameters:
 *   r (inout): Reader to populate (non-NULL).
 *   path (in): File path (non-NULL, NUL-terminated).
 * Return values / errors:
 *   0 on success; non-zero on I/O or malformed container.
 */
int dtlv_reader_open_file(dtlv_reader* r, const char* path);
/* dtlv_reader_init_file
 * Purpose: Initialize a reader from an already-open `dsys_file_*` handle.
 * Parameters:
 *   r (inout): Reader to populate (non-NULL).
 *   fh (in): File handle (non-NULL). Ownership is not taken.
 * Return values / errors:
 *   0 on success; non-zero on I/O or malformed container.
 */
int dtlv_reader_init_file(dtlv_reader* r, void* fh); /* does not take ownership */
/* dtlv_reader_init_mem
 * Purpose: Initialize a reader from an in-memory buffer containing a full container.
 * Parameters:
 *   r (inout): Reader to populate (non-NULL).
 *   data (in): Buffer pointer (may be NULL only when `size == 0`).
 *   size (in): Buffer size in bytes.
 * Return values / errors:
 *   0 on success; non-zero on malformed container.
 */
int dtlv_reader_init_mem(dtlv_reader* r, const void* data, u64 size);

/* dtlv_reader_chunk_count
 * Purpose: Return the number of directory entries in the opened container.
 * Parameters:
 *   r (in): Reader (may be NULL).
 * Returns:
 *   Chunk count, or 0 when `r` is NULL/uninitialized.
 */
u32 dtlv_reader_chunk_count(const dtlv_reader* r);
/* dtlv_reader_chunk_at
 * Purpose: Return the Nth directory entry.
 * Parameters:
 *   r (in): Reader (non-NULL).
 *   index (in): Entry index (0..chunk_count-1).
 * Returns:
 *   Pointer to an internal entry on success; NULL when out of range or invalid.
 */
const dtlv_dir_entry* dtlv_reader_chunk_at(const dtlv_reader* r, u32 index);

/* dtlv_reader_find_first
 * Purpose: Find the first directory entry matching `type_id` and (optionally) `version`.
 * Parameters:
 *   r (in): Reader (non-NULL).
 *   type_id (in): Chunk type id to match.
 *   version (in): Version to match; pass 0 to ignore version.
 * Returns:
 *   Pointer to an internal entry on success; NULL when not found.
 */
const dtlv_dir_entry* dtlv_reader_find_first(
    const dtlv_reader* r,
    u32                type_id,
    u16                version /* pass 0 to ignore version */
);

/* dtlv_reader_read_chunk
 * Purpose: Read a chunk payload into a caller-provided buffer.
 * Parameters:
 *   r (inout): Reader (non-NULL).
 *   e (in): Directory entry (non-NULL; typically from `dtlv_reader_*`).
 *   dst (out): Output buffer (non-NULL).
 *   dst_cap (in): Capacity of `dst` in bytes.
 * Return values / errors:
 *   0 on success; non-zero on I/O or insufficient capacity.
 */
int dtlv_reader_read_chunk(
    dtlv_reader*         r,
    const dtlv_dir_entry* e,
    void*                dst,
    u64                  dst_cap
);

/* dtlv_reader_read_chunk_alloc
 * Purpose: Read a chunk payload into a newly allocated buffer.
 * Parameters:
 *   r (inout): Reader (non-NULL).
 *   e (in): Directory entry (non-NULL).
 *   out_bytes (out): Receives malloc-owned buffer pointer on success (non-NULL).
 *   out_size (out): Receives payload size in bytes on success (non-NULL).
 * Return values / errors:
 *   0 on success; non-zero on I/O or allocation failure.
 */
int dtlv_reader_read_chunk_alloc(
    dtlv_reader*          r,
    const dtlv_dir_entry* e,
    unsigned char**       out_bytes,
    u32*                  out_size
);

/* dtlv_reader_chunk_memview
 * Purpose: For memory-backed readers, return a pointer to the chunk payload bytes.
 * Parameters:
 *   r (in): Reader (non-NULL).
 *   e (in): Directory entry (non-NULL).
 *   out_ptr (out): Receives pointer into the container memory on success (non-NULL).
 *   out_size (out): Receives payload size in bytes on success (non-NULL).
 * Return values / errors:
 *   0 on success; non-zero when not memory-backed or on invalid parameters.
 * Ownership:
 *   The returned pointer is borrowed and becomes invalid when the reader is disposed.
 */
int dtlv_reader_chunk_memview(
    const dtlv_reader*    r,
    const dtlv_dir_entry* e,
    const unsigned char** out_ptr,
    u32*                  out_size
);

/*------------------------------------------------------------
 * Container writer
 *------------------------------------------------------------*/

/* dtlv_writer
 * Purpose: Writer state for building a DTLV container (memory-backed or file-backed).
 * Ownership:
 * - In memory-backed mode, bytes are written into the caller-provided buffer.
 * - In file-backed mode, the writer may own the file handle when opened via `dtlv_writer_open_file`.
 * - `entries` is allocated/owned by the writer and released by `dtlv_writer_dispose`.
 * Thread-safety:
 * - No internal synchronization; each writer instance must be externally serialized.
 */
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

/* dtlv_writer_init
 * Purpose: Initialize a writer to the empty state.
 * Parameters:
 *   w (out): Writer instance to initialize (may be NULL; no-op).
 */
void dtlv_writer_init(dtlv_writer* w);
/* dtlv_writer_dispose
 * Purpose: Release writer-owned resources and return to the empty state.
 * Parameters:
 *   w (inout): Writer instance (may be NULL; no-op).
 */
void dtlv_writer_dispose(dtlv_writer* w);

/* dtlv_writer_open_file
 * Purpose: Open a file for writing and write a placeholder container header.
 * Parameters:
 *   w (inout): Writer to populate (non-NULL).
 *   path (in): File path (non-NULL, NUL-terminated).
 * Return values / errors:
 *   0 on success; non-zero on I/O failure.
 */
int dtlv_writer_open_file(dtlv_writer* w, const char* path);
/* dtlv_writer_init_file
 * Purpose: Initialize a writer from an already-open `dsys_file_*` handle.
 * Parameters:
 *   w (inout): Writer to populate (non-NULL).
 *   fh (in): File handle (non-NULL). Ownership is not taken.
 * Return values / errors:
 *   0 on success; non-zero on I/O failure.
 */
int dtlv_writer_init_file(dtlv_writer* w, void* fh); /* does not take ownership */
/* dtlv_writer_init_mem
 * Purpose: Initialize a writer that writes into a caller-provided memory buffer.
 * Parameters:
 *   w (inout): Writer to populate (non-NULL).
 *   buf (out): Destination buffer (non-NULL).
 *   cap (in): Buffer capacity in bytes.
 * Return values / errors:
 *   0 on success; non-zero on invalid parameters or insufficient capacity.
 */
int dtlv_writer_init_mem(dtlv_writer* w, void* buf, u32 cap);

/* dtlv_writer_begin_chunk
 * Purpose: Begin a new chunk payload; must be paired with `dtlv_writer_end_chunk`.
 * Parameters:
 *   w (inout): Writer (non-NULL).
 *   type_id (in): Chunk type id (ABI).
 *   version (in): Chunk schema version.
 *   flags (in): Chunk flags (e.g., CRC presence).
 * Return values / errors:
 *   0 on success; non-zero on invalid state or allocation failure.
 */
int dtlv_writer_begin_chunk(dtlv_writer* w, u32 type_id, u16 version, u16 flags);
/* dtlv_writer_write
 * Purpose: Append raw bytes to the currently-open chunk.
 * Parameters:
 *   w (inout): Writer (non-NULL).
 *   bytes (in): Bytes to write (may be NULL only when `len == 0`).
 *   len (in): Number of bytes to write.
 * Return values / errors:
 *   0 on success; non-zero on invalid state or I/O failure.
 */
int dtlv_writer_write(dtlv_writer* w, const void* bytes, u32 len);
/* dtlv_writer_write_tlv
 * Purpose: Append one TLV record (`u32_le tag`, `u32_le len`, payload bytes) to the open chunk.
 * Parameters:
 *   w (inout): Writer (non-NULL).
 *   tag (in): TLV tag (`u32_le` on disk).
 *   payload (in): Payload bytes (may be NULL only when `payload_len == 0`).
 *   payload_len (in): Payload size in bytes.
 * Return values / errors:
 *   0 on success; non-zero on invalid state or I/O failure.
 */
int dtlv_writer_write_tlv(dtlv_writer* w, u32 tag, const void* payload, u32 payload_len);
/* dtlv_writer_end_chunk
 * Purpose: Close the current chunk and record its size in the directory.
 * Parameters:
 *   w (inout): Writer (non-NULL).
 * Return values / errors:
 *   0 on success; non-zero on invalid state.
 */
int dtlv_writer_end_chunk(dtlv_writer* w);

/* dtlv_writer_finalize
 * Purpose: Write the directory and patch the container header (DTLV v1).
 * Parameters:
 *   w (inout): Writer (non-NULL). No chunk may be open.
 * Return values / errors:
 *   0 on success; non-zero on I/O failure or invalid state.
 */
int dtlv_writer_finalize(dtlv_writer* w);

/* dtlv_writer_mem_size
 * Purpose: For memory-backed writers, report total bytes written after finalize.
 * Parameters:
 *   w (in): Writer (may be NULL).
 * Returns:
 *   Total bytes written, or 0 when unknown/invalid.
 */
u32 dtlv_writer_mem_size(const dtlv_writer* w);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_IO_CONTAINER_H_INCLUDED */
