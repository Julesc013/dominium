/* DTLV container implementation (C89).
 *
 * See docs/SPEC_CONTAINER_TLV.md for the authoritative format contract.
 */

#include "domino/io/container.h"

#include <stdlib.h>
#include <string.h>

#include "domino/sys.h"

/*------------------------------------------------------------
 * Explicit little-endian helpers
 *------------------------------------------------------------*/

u16 dtlv_le_read_u16(const unsigned char* p) {
    return (u16)((u16)p[0] | (u16)((u16)p[1] << 8));
}

u32 dtlv_le_read_u32(const unsigned char* p) {
    return (u32)(
        (u32)p[0] |
        ((u32)p[1] << 8) |
        ((u32)p[2] << 16) |
        ((u32)p[3] << 24)
    );
}

u64 dtlv_le_read_u64(const unsigned char* p) {
    u32 lo = dtlv_le_read_u32(p);
    u32 hi = dtlv_le_read_u32(p + 4u);
    return (u64)lo | ((u64)hi << 32);
}

void dtlv_le_write_u16(unsigned char* p, u16 v) {
    p[0] = (unsigned char)(v & 0xFFu);
    p[1] = (unsigned char)((v >> 8) & 0xFFu);
}

void dtlv_le_write_u32(unsigned char* p, u32 v) {
    p[0] = (unsigned char)(v & 0xFFu);
    p[1] = (unsigned char)((v >> 8) & 0xFFu);
    p[2] = (unsigned char)((v >> 16) & 0xFFu);
    p[3] = (unsigned char)((v >> 24) & 0xFFu);
}

void dtlv_le_write_u64(unsigned char* p, u64 v) {
    dtlv_le_write_u32(p, (u32)(v & 0xFFFFFFFFu));
    dtlv_le_write_u32(p + 4u, (u32)(v >> 32));
}

/*------------------------------------------------------------
 * TLV helpers
 *------------------------------------------------------------*/

int dtlv_tlv_next(
    const unsigned char* tlv,
    u32                  tlv_len,
    u32*                 offset,
    u32*                 tag_out,
    const unsigned char** payload_out,
    u32*                 payload_len_out
) {
    u32 off;
    u32 remaining;
    u32 len;

    if (!offset || !tag_out || !payload_out || !payload_len_out) {
        return -1;
    }

    off = *offset;
    if (off >= tlv_len) {
        return 1;
    }

    remaining = tlv_len - off;
    if (!tlv || remaining < 8u) {
        return -2;
    }

    *tag_out = dtlv_le_read_u32(tlv + off);
    len = dtlv_le_read_u32(tlv + off + 4u);
    off += 8u;

    if (len > (tlv_len - off)) {
        return -3;
    }

    *payload_out = tlv + off;
    *payload_len_out = len;
    off += len;
    *offset = off;
    return 0;
}

int dtlv_tlv_write(
    unsigned char* dst,
    u32            dst_cap,
    u32*           in_out_offset,
    u32            tag,
    const void*    payload,
    u32            payload_len
) {
    u32 off;
    unsigned char* p;

    if (!dst || !in_out_offset) {
        return -1;
    }
    if (payload_len != 0u && !payload) {
        return -2;
    }

    off = *in_out_offset;
    if (dst_cap < off || (dst_cap - off) < (8u + payload_len)) {
        return -3;
    }

    p = dst + off;
    dtlv_le_write_u32(p, tag);
    dtlv_le_write_u32(p + 4u, payload_len);
    off += 8u;

    if (payload_len != 0u) {
        memcpy(dst + off, payload, (size_t)payload_len);
        off += payload_len;
    }

    *in_out_offset = off;
    return 0;
}

/*------------------------------------------------------------
 * Internal file helpers (dsys_file_*)
 *------------------------------------------------------------*/

static int dtlv_file_seek_abs(void* fh, u64 offset) {
    if (!fh) {
        return -1;
    }
    /* dsys_file_seek takes a long; keep v1 readers/writers within 2GiB. */
    if (offset > 0x7FFFFFFFULL) {
        return -2;
    }
    return (dsys_file_seek(fh, (long)offset, 0 /* SEEK_SET */) == 0) ? 0 : -3;
}

static int dtlv_file_get_size(void* fh, u64* out_size) {
    long end;
    if (!out_size) {
        return -1;
    }
    *out_size = 0u;
    if (!fh) {
        return -2;
    }
    if (dsys_file_seek(fh, 0L, 2 /* SEEK_END */) != 0) {
        return -3;
    }
    end = dsys_file_tell(fh);
    if (end < 0L) {
        return -4;
    }
    if (dsys_file_seek(fh, 0L, 0 /* SEEK_SET */) != 0) {
        return -5;
    }
    *out_size = (u64)end;
    return 0;
}

static int dtlv_file_read_exact(void* fh, void* dst, u64 size) {
    size_t got;
    if (!fh || (!dst && size != 0u)) {
        return -1;
    }
    if (size > (u64)0xFFFFFFFFu) {
        return -2;
    }
    if (size == 0u) {
        return 0;
    }
    got = dsys_file_read(fh, dst, (size_t)size);
    return (got == (size_t)size) ? 0 : -3;
}

static int dtlv_file_write_exact(void* fh, const void* src, u64 size) {
    size_t wrote;
    if (!fh || (!src && size != 0u)) {
        return -1;
    }
    if (size > (u64)0xFFFFFFFFu) {
        return -2;
    }
    if (size == 0u) {
        return 0;
    }
    wrote = dsys_file_write(fh, src, (size_t)size);
    return (wrote == (size_t)size) ? 0 : -3;
}

/*------------------------------------------------------------
 * Reader
 *------------------------------------------------------------*/

static void dtlv_reader_reset(dtlv_reader* r) {
    if (!r) {
        return;
    }
    r->mem = (const unsigned char*)0;
    r->mem_size = 0u;
    r->fh = (void*)0;
    r->owns_fh = 0;
    r->file_size = 0u;
    r->dir_offset = 0u;
    r->chunk_count = 0u;
    r->entries = (dtlv_dir_entry*)0;
}

void dtlv_reader_init(dtlv_reader* r) {
    dtlv_reader_reset(r);
}

void dtlv_reader_dispose(dtlv_reader* r) {
    if (!r) {
        return;
    }
    if (r->entries) {
        free(r->entries);
    }
    r->entries = (dtlv_dir_entry*)0;
    if (r->owns_fh && r->fh) {
        (void)dsys_file_close(r->fh);
    }
    dtlv_reader_reset(r);
}

static int dtlv_reader_parse_from_bytes(
    dtlv_reader*          r,
    const unsigned char*  bytes,
    u64                   size
) {
    u16 endian;
    u16 ver;
    u32 header_size;
    u64 dir_offset;
    u32 chunk_count;
    u32 dir_entry_size;
    u64 dir_bytes;
    u32 i;

    if (!r || !bytes) {
        return -1;
    }
    if (size < (u64)DTLV_HEADER_SIZE_V1) {
        return -2;
    }

    if (bytes[0] != DTLV_MAGIC_0 ||
        bytes[1] != DTLV_MAGIC_1 ||
        bytes[2] != DTLV_MAGIC_2 ||
        bytes[3] != DTLV_MAGIC_3) {
        return -3;
    }

    endian = dtlv_le_read_u16(bytes + 4u);
    if (endian != DTLV_ENDIAN_MARK_LE) {
        return -4;
    }

    ver = dtlv_le_read_u16(bytes + 6u);
    if (ver != DTLV_CONTAINER_VERSION_V1) {
        return -5;
    }

    header_size = dtlv_le_read_u32(bytes + 8u);
    if (header_size < DTLV_HEADER_SIZE_V1) {
        return -6;
    }
    if ((u64)header_size > size) {
        return -7;
    }

    dir_offset = dtlv_le_read_u64(bytes + 12u);
    chunk_count = dtlv_le_read_u32(bytes + 20u);
    dir_entry_size = dtlv_le_read_u32(bytes + 24u);

    if (dir_entry_size != DTLV_DIR_ENTRY_SIZE_V1) {
        return -8;
    }

    dir_bytes = (u64)chunk_count * (u64)dir_entry_size;
    if (dir_offset > size || dir_bytes > (size - dir_offset)) {
        return -9;
    }

    r->dir_offset = dir_offset;
    r->chunk_count = chunk_count;

    if (chunk_count != 0u) {
        const unsigned char* p;
        dtlv_dir_entry* entries;
        if (dir_offset > (u64)((size_t)-1)) {
            return -10;
        }
        p = bytes + (size_t)dir_offset;
        entries = (dtlv_dir_entry*)malloc(sizeof(dtlv_dir_entry) * (size_t)chunk_count);
        if (!entries) {
            return -11;
        }
        for (i = 0u; i < chunk_count; ++i) {
            u32 type_id = dtlv_le_read_u32(p);
            u16 cver = dtlv_le_read_u16(p + 4u);
            u16 flags = dtlv_le_read_u16(p + 6u);
            u64 off = dtlv_le_read_u64(p + 8u);
            u64 clen = dtlv_le_read_u64(p + 16u);
            u32 crc32 = dtlv_le_read_u32(p + 24u);

            if (off > size || clen > (size - off)) {
                free(entries);
                return -12;
            }

            entries[i].type_id = type_id;
            entries[i].version = cver;
            entries[i].flags = flags;
            entries[i].offset = off;
            entries[i].size = clen;
            entries[i].crc32 = crc32;

            p += DTLV_DIR_ENTRY_SIZE_V1;
        }
        r->entries = entries;
    }

    return 0;
}

int dtlv_reader_init_mem(dtlv_reader* r, const void* data, u64 size) {
    int rc;
    if (!r || (!data && size != 0u)) {
        return -1;
    }
    dtlv_reader_dispose(r);
    r->mem = (const unsigned char*)data;
    r->mem_size = size;
    r->file_size = size;
    rc = dtlv_reader_parse_from_bytes(r, r->mem, r->mem_size);
    if (rc != 0) {
        dtlv_reader_dispose(r);
        return rc;
    }
    return 0;
}

int dtlv_reader_init_file(dtlv_reader* r, void* fh) {
    unsigned char hdr[DTLV_HEADER_SIZE_V1];
    u16 endian;
    u16 ver;
    u32 header_size;
    u64 dir_offset;
    u32 chunk_count;
    u32 dir_entry_size;
    u64 dir_bytes;
    u64 fsize;
    u32 i;

    if (!r || !fh) {
        return -1;
    }

    dtlv_reader_dispose(r);
    r->fh = fh;
    r->owns_fh = 0;

    if (dtlv_file_get_size(fh, &fsize) != 0) {
        dtlv_reader_dispose(r);
        return -2;
    }
    r->file_size = fsize;

    if (dtlv_file_seek_abs(fh, 0u) != 0) {
        dtlv_reader_dispose(r);
        return -3;
    }
    if (dtlv_file_read_exact(fh, hdr, (u64)sizeof(hdr)) != 0) {
        dtlv_reader_dispose(r);
        return -4;
    }

    if (fsize < (u64)DTLV_HEADER_SIZE_V1) {
        dtlv_reader_dispose(r);
        return -5;
    }

    if (hdr[0] != DTLV_MAGIC_0 ||
        hdr[1] != DTLV_MAGIC_1 ||
        hdr[2] != DTLV_MAGIC_2 ||
        hdr[3] != DTLV_MAGIC_3) {
        dtlv_reader_dispose(r);
        return -6;
    }

    endian = dtlv_le_read_u16(hdr + 4u);
    if (endian != DTLV_ENDIAN_MARK_LE) {
        dtlv_reader_dispose(r);
        return -7;
    }

    ver = dtlv_le_read_u16(hdr + 6u);
    if (ver != DTLV_CONTAINER_VERSION_V1) {
        dtlv_reader_dispose(r);
        return -8;
    }

    header_size = dtlv_le_read_u32(hdr + 8u);
    if (header_size < DTLV_HEADER_SIZE_V1 || (u64)header_size > fsize) {
        dtlv_reader_dispose(r);
        return -9;
    }

    dir_offset = dtlv_le_read_u64(hdr + 12u);
    chunk_count = dtlv_le_read_u32(hdr + 20u);
    dir_entry_size = dtlv_le_read_u32(hdr + 24u);

    if (dir_entry_size != DTLV_DIR_ENTRY_SIZE_V1) {
        dtlv_reader_dispose(r);
        return -10;
    }

    dir_bytes = (u64)chunk_count * (u64)dir_entry_size;
    if (dir_offset > fsize || dir_bytes > (fsize - dir_offset)) {
        dtlv_reader_dispose(r);
        return -11;
    }

    r->dir_offset = dir_offset;
    r->chunk_count = chunk_count;

    if (chunk_count != 0u) {
        unsigned char* dir = (unsigned char*)malloc((size_t)dir_bytes);
        dtlv_dir_entry* entries;
        const unsigned char* p;
        if (!dir) {
            dtlv_reader_dispose(r);
            return -12;
        }
        if (dtlv_file_seek_abs(fh, dir_offset) != 0) {
            free(dir);
            dtlv_reader_dispose(r);
            return -13;
        }
        if (dtlv_file_read_exact(fh, dir, dir_bytes) != 0) {
            free(dir);
            dtlv_reader_dispose(r);
            return -14;
        }

        entries = (dtlv_dir_entry*)malloc(sizeof(dtlv_dir_entry) * (size_t)chunk_count);
        if (!entries) {
            free(dir);
            dtlv_reader_dispose(r);
            return -15;
        }
        p = dir;
        for (i = 0u; i < chunk_count; ++i) {
            u32 type_id = dtlv_le_read_u32(p);
            u16 cver = dtlv_le_read_u16(p + 4u);
            u16 flags = dtlv_le_read_u16(p + 6u);
            u64 off = dtlv_le_read_u64(p + 8u);
            u64 clen = dtlv_le_read_u64(p + 16u);
            u32 crc32 = dtlv_le_read_u32(p + 24u);

            if (off > fsize || clen > (fsize - off)) {
                free(entries);
                free(dir);
                dtlv_reader_dispose(r);
                return -16;
            }

            entries[i].type_id = type_id;
            entries[i].version = cver;
            entries[i].flags = flags;
            entries[i].offset = off;
            entries[i].size = clen;
            entries[i].crc32 = crc32;
            p += DTLV_DIR_ENTRY_SIZE_V1;
        }
        free(dir);
        r->entries = entries;
    }

    return 0;
}

int dtlv_reader_open_file(dtlv_reader* r, const char* path) {
    void* fh;
    int rc;
    if (!r || !path) {
        return -1;
    }
    fh = dsys_file_open(path, "rb");
    if (!fh) {
        return -2;
    }
    rc = dtlv_reader_init_file(r, fh);
    if (rc != 0) {
        (void)dsys_file_close(fh);
        return rc;
    }
    r->fh = fh;
    r->owns_fh = 1;
    return 0;
}

u32 dtlv_reader_chunk_count(const dtlv_reader* r) {
    return r ? r->chunk_count : 0u;
}

const dtlv_dir_entry* dtlv_reader_chunk_at(const dtlv_reader* r, u32 index) {
    if (!r || !r->entries) {
        return (const dtlv_dir_entry*)0;
    }
    if (index >= r->chunk_count) {
        return (const dtlv_dir_entry*)0;
    }
    return &r->entries[index];
}

const dtlv_dir_entry* dtlv_reader_find_first(
    const dtlv_reader* r,
    u32                type_id,
    u16                version
) {
    u32 i;
    if (!r || !r->entries) {
        return (const dtlv_dir_entry*)0;
    }
    for (i = 0u; i < r->chunk_count; ++i) {
        const dtlv_dir_entry* e = &r->entries[i];
        if (e->type_id != type_id) {
            continue;
        }
        if (version != 0u && e->version != version) {
            continue;
        }
        return e;
    }
    return (const dtlv_dir_entry*)0;
}

int dtlv_reader_chunk_memview(
    const dtlv_reader*     r,
    const dtlv_dir_entry*  e,
    const unsigned char**  out_ptr,
    u32*                   out_size
) {
    if (!out_ptr || !out_size) {
        return -1;
    }
    *out_ptr = (const unsigned char*)0;
    *out_size = 0u;

    if (!r || !e) {
        return -2;
    }
    if (!r->mem) {
        return -3;
    }
    if (e->offset > r->mem_size || e->size > (r->mem_size - e->offset)) {
        return -4;
    }
    if (e->size > (u64)0xFFFFFFFFu) {
        return -5;
    }
    if (e->offset > (u64)((size_t)-1)) {
        return -6;
    }
    *out_ptr = r->mem + (size_t)e->offset;
    *out_size = (u32)e->size;
    return 0;
}

int dtlv_reader_read_chunk(
    dtlv_reader*          r,
    const dtlv_dir_entry* e,
    void*                 dst,
    u64                   dst_cap
) {
    if (!r || !e || (!dst && e->size != 0u)) {
        return -1;
    }
    if (dst_cap < e->size) {
        return -2;
    }

    if (r->mem) {
        if (e->offset > r->mem_size || e->size > (r->mem_size - e->offset)) {
            return -3;
        }
        if (e->size != 0u) {
            if (e->offset > (u64)((size_t)-1)) {
                return -6;
            }
            memcpy(dst, r->mem + (size_t)e->offset, (size_t)e->size);
        }
        return 0;
    }

    if (!r->fh) {
        return -4;
    }
    if (e->offset > r->file_size || e->size > (r->file_size - e->offset)) {
        return -5;
    }
    if (e->size > (u64)0xFFFFFFFFu) {
        return -6;
    }
    if (dtlv_file_seek_abs(r->fh, e->offset) != 0) {
        return -7;
    }
    return dtlv_file_read_exact(r->fh, dst, e->size);
}

int dtlv_reader_read_chunk_alloc(
    dtlv_reader*          r,
    const dtlv_dir_entry* e,
    unsigned char**       out_bytes,
    u32*                  out_size
) {
    unsigned char* buf;
    int rc;
    if (!out_bytes || !out_size) {
        return -1;
    }
    *out_bytes = (unsigned char*)0;
    *out_size = 0u;
    if (!r || !e) {
        return -2;
    }
    if (e->size > (u64)0xFFFFFFFFu) {
        return -3;
    }
    buf = (unsigned char*)0;
    if (e->size != 0u) {
        buf = (unsigned char*)malloc((size_t)e->size);
        if (!buf) {
            return -4;
        }
    }
    rc = dtlv_reader_read_chunk(r, e, buf, e->size);
    if (rc != 0) {
        if (buf) {
            free(buf);
        }
        return rc;
    }
    *out_bytes = buf;
    *out_size = (u32)e->size;
    return 0;
}

/*------------------------------------------------------------
 * Writer
 *------------------------------------------------------------*/

static void dtlv_writer_reset(dtlv_writer* w) {
    if (!w) {
        return;
    }
    w->mem = (unsigned char*)0;
    w->mem_cap = 0u;
    w->fh = (void*)0;
    w->owns_fh = 0;
    w->off = 0u;
    w->chunk_open = 0;
    w->chunk_start = 0u;
    w->entries = (dtlv_dir_entry*)0;
    w->entry_count = 0u;
    w->entry_cap = 0u;
}

void dtlv_writer_init(dtlv_writer* w) {
    dtlv_writer_reset(w);
}

void dtlv_writer_dispose(dtlv_writer* w) {
    if (!w) {
        return;
    }
    if (w->entries) {
        free(w->entries);
    }
    w->entries = (dtlv_dir_entry*)0;
    if (w->owns_fh && w->fh) {
        (void)dsys_file_close(w->fh);
    }
    dtlv_writer_reset(w);
}

static int dtlv_writer_write_bytes(dtlv_writer* w, const void* bytes, u32 len) {
    if (!w || (!bytes && len != 0u)) {
        return -1;
    }
    if (w->mem) {
        if ((u64)len > (u64)w->mem_cap - w->off) {
            return -2;
        }
        if (len != 0u) {
            if (w->off > (u64)((size_t)-1)) {
                return -5;
            }
            memcpy(w->mem + (size_t)w->off, bytes, (size_t)len);
        }
        w->off += (u64)len;
        return 0;
    }
    if (!w->fh) {
        return -3;
    }
    if (dtlv_file_write_exact(w->fh, bytes, (u64)len) != 0) {
        return -4;
    }
    w->off += (u64)len;
    return 0;
}

static void dtlv_write_header_v1(unsigned char* out32, u64 dir_offset, u32 chunk_count) {
    memset(out32, 0, (size_t)DTLV_HEADER_SIZE_V1);
    out32[0] = DTLV_MAGIC_0;
    out32[1] = DTLV_MAGIC_1;
    out32[2] = DTLV_MAGIC_2;
    out32[3] = DTLV_MAGIC_3;
    dtlv_le_write_u16(out32 + 4u, DTLV_ENDIAN_MARK_LE);
    dtlv_le_write_u16(out32 + 6u, DTLV_CONTAINER_VERSION_V1);
    dtlv_le_write_u32(out32 + 8u, DTLV_HEADER_SIZE_V1);
    dtlv_le_write_u64(out32 + 12u, dir_offset);
    dtlv_le_write_u32(out32 + 20u, chunk_count);
    dtlv_le_write_u32(out32 + 24u, DTLV_DIR_ENTRY_SIZE_V1);
    dtlv_le_write_u32(out32 + 28u, 0u);
}

static int dtlv_writer_write_header_placeholder(dtlv_writer* w) {
    unsigned char hdr[DTLV_HEADER_SIZE_V1];
    dtlv_write_header_v1(hdr, 0u, 0u);
    return dtlv_writer_write_bytes(w, hdr, (u32)sizeof(hdr));
}

static int dtlv_writer_reserve_entry(dtlv_writer* w) {
    u32 new_cap;
    dtlv_dir_entry* new_entries;
    if (!w) {
        return -1;
    }
    if (w->entry_count < w->entry_cap) {
        return 0;
    }
    new_cap = (w->entry_cap == 0u) ? 8u : (w->entry_cap * 2u);
    new_entries = (dtlv_dir_entry*)realloc(w->entries, sizeof(dtlv_dir_entry) * (size_t)new_cap);
    if (!new_entries) {
        return -2;
    }
    w->entries = new_entries;
    w->entry_cap = new_cap;
    return 0;
}

int dtlv_writer_init_mem(dtlv_writer* w, void* buf, u32 cap) {
    if (!w || (!buf && cap != 0u)) {
        return -1;
    }
    dtlv_writer_dispose(w);
    w->mem = (unsigned char*)buf;
    w->mem_cap = cap;
    w->off = 0u;
    if (cap < DTLV_HEADER_SIZE_V1) {
        dtlv_writer_dispose(w);
        return -2;
    }
    if (dtlv_writer_write_header_placeholder(w) != 0) {
        dtlv_writer_dispose(w);
        return -3;
    }
    return 0;
}

int dtlv_writer_init_file(dtlv_writer* w, void* fh) {
    if (!w || !fh) {
        return -1;
    }
    dtlv_writer_dispose(w);
    w->fh = fh;
    w->owns_fh = 0;
    w->off = 0u;
    if (dtlv_file_seek_abs(fh, 0u) != 0) {
        dtlv_writer_dispose(w);
        return -2;
    }
    if (dtlv_writer_write_header_placeholder(w) != 0) {
        dtlv_writer_dispose(w);
        return -3;
    }
    return 0;
}

int dtlv_writer_open_file(dtlv_writer* w, const char* path) {
    void* fh;
    int rc;
    if (!w || !path) {
        return -1;
    }
    fh = dsys_file_open(path, "wb");
    if (!fh) {
        return -2;
    }
    rc = dtlv_writer_init_file(w, fh);
    if (rc != 0) {
        (void)dsys_file_close(fh);
        return rc;
    }
    w->fh = fh;
    w->owns_fh = 1;
    return 0;
}

int dtlv_writer_begin_chunk(dtlv_writer* w, u32 type_id, u16 version, u16 flags) {
    dtlv_dir_entry* e;
    if (!w) {
        return -1;
    }
    if (w->chunk_open) {
        return -2;
    }
    if (dtlv_writer_reserve_entry(w) != 0) {
        return -3;
    }

    e = &w->entries[w->entry_count++];
    e->type_id = type_id;
    e->version = version;
    e->flags = flags;
    e->offset = w->off;
    e->size = 0u;
    e->crc32 = 0u;

    w->chunk_open = 1;
    w->chunk_start = w->off;
    return 0;
}

int dtlv_writer_write(dtlv_writer* w, const void* bytes, u32 len) {
    if (!w) {
        return -1;
    }
    if (!w->chunk_open) {
        return -2;
    }
    return dtlv_writer_write_bytes(w, bytes, len);
}

int dtlv_writer_write_tlv(dtlv_writer* w, u32 tag, const void* payload, u32 payload_len) {
    unsigned char hdr[8];
    int rc;
    if (!w) {
        return -1;
    }
    if (payload_len != 0u && !payload) {
        return -2;
    }
    dtlv_le_write_u32(hdr, tag);
    dtlv_le_write_u32(hdr + 4u, payload_len);
    rc = dtlv_writer_write(w, hdr, 8u);
    if (rc != 0) {
        return rc;
    }
    if (payload_len != 0u) {
        rc = dtlv_writer_write(w, payload, payload_len);
        if (rc != 0) {
            return rc;
        }
    }
    return 0;
}

int dtlv_writer_end_chunk(dtlv_writer* w) {
    dtlv_dir_entry* e;
    if (!w) {
        return -1;
    }
    if (!w->chunk_open) {
        return -2;
    }
    if (w->entry_count == 0u) {
        return -3;
    }
    e = &w->entries[w->entry_count - 1u];
    e->size = w->off - w->chunk_start;
    w->chunk_open = 0;
    w->chunk_start = 0u;
    return 0;
}

static int dtlv_dir_entry_cmp(const void* a, const void* b) {
    const dtlv_dir_entry* ea = (const dtlv_dir_entry*)a;
    const dtlv_dir_entry* eb = (const dtlv_dir_entry*)b;
    if (ea->type_id < eb->type_id) return -1;
    if (ea->type_id > eb->type_id) return 1;
    if (ea->version < eb->version) return -1;
    if (ea->version > eb->version) return 1;
    if (ea->offset < eb->offset) return -1;
    if (ea->offset > eb->offset) return 1;
    return 0;
}

int dtlv_writer_finalize(dtlv_writer* w) {
    u64 dir_offset;
    u32 i;
    int rc;
    unsigned char hdr[DTLV_HEADER_SIZE_V1];

    if (!w) {
        return -1;
    }
    if (w->chunk_open) {
        return -2;
    }

    dir_offset = w->off;

    /* Deterministic directory order, independent of chunk append order. */
    if (w->entry_count > 1u) {
        qsort(w->entries, (size_t)w->entry_count, sizeof(dtlv_dir_entry), dtlv_dir_entry_cmp);
    }

    /* Write directory entries */
    for (i = 0u; i < w->entry_count; ++i) {
        unsigned char ent[DTLV_DIR_ENTRY_SIZE_V1];
        memset(ent, 0, sizeof(ent));
        dtlv_le_write_u32(ent + 0u, w->entries[i].type_id);
        dtlv_le_write_u16(ent + 4u, w->entries[i].version);
        dtlv_le_write_u16(ent + 6u, w->entries[i].flags);
        dtlv_le_write_u64(ent + 8u, w->entries[i].offset);
        dtlv_le_write_u64(ent + 16u, w->entries[i].size);
        dtlv_le_write_u32(ent + 24u, w->entries[i].crc32);
        dtlv_le_write_u32(ent + 28u, 0u);
        rc = dtlv_writer_write_bytes(w, ent, (u32)sizeof(ent));
        if (rc != 0) {
            return -3;
        }
    }

    /* Patch header */
    dtlv_write_header_v1(hdr, dir_offset, w->entry_count);
    if (w->mem) {
        memcpy(w->mem, hdr, (size_t)sizeof(hdr));
        return 0;
    }
    if (!w->fh) {
        return -4;
    }
    if (dtlv_file_seek_abs(w->fh, 0u) != 0) {
        return -5;
    }
    if (dtlv_file_write_exact(w->fh, hdr, (u64)sizeof(hdr)) != 0) {
        return -6;
    }
    return 0;
}

u32 dtlv_writer_mem_size(const dtlv_writer* w) {
    if (!w) {
        return 0u;
    }
    if (w->off > (u64)0xFFFFFFFFu) {
        return 0u;
    }
    return (u32)w->off;
}
