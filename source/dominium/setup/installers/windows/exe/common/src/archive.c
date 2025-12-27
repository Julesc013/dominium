/*
FILE: source/dominium/setup/installers/windows/exe/common/src/archive.c
MODULE: Dominium Setup EXE
PURPOSE: Embedded archive discovery and extraction.
*/
#include "dsu_exe_archive.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#endif

typedef struct dsu_exe_archive_t {
    FILE *fp;
    unsigned long long header_offset;
    unsigned long long table_offset;
    unsigned long long data_offset;
    unsigned long long table_size;
    unsigned long long data_size;
    unsigned long file_count;
} dsu_exe_archive_t;

#define DSU_EXE_ARCHIVE_MAGIC "DSUARCH1"
#define DSU_EXE_ARCHIVE_TAIL_MAGIC "DSUTAIL1"

static unsigned long dsu__crc32_update(unsigned long crc, const unsigned char *buf, unsigned long len) {
    unsigned long c = crc ^ 0xFFFFFFFFu;
    unsigned long i;
    for (i = 0; i < len; ++i) {
        unsigned long x = (c ^ buf[i]) & 0xFFu;
        unsigned long j;
        for (j = 0; j < 8; ++j) {
            if (x & 1u) {
                x = (x >> 1) ^ 0xEDB88320u;
            } else {
                x >>= 1;
            }
        }
        c = (c >> 8) ^ x;
    }
    return c ^ 0xFFFFFFFFu;
}

static unsigned long dsu__crc32(const unsigned char *buf, unsigned long len) {
    return dsu__crc32_update(0u, buf, len);
}

static int dsu__read_u16(FILE *fp, unsigned short *out) {
    unsigned char b[2];
    if (fread(b, 1, 2, fp) != 2) return 0;
    *out = (unsigned short)(b[0] | (b[1] << 8));
    return 1;
}

static int dsu__read_u32(FILE *fp, unsigned long *out) {
    unsigned char b[4];
    if (fread(b, 1, 4, fp) != 4) return 0;
    *out = (unsigned long)(b[0] | (b[1] << 8) | (b[2] << 16) | (b[3] << 24));
    return 1;
}

static int dsu__read_u64(FILE *fp, unsigned long long *out) {
    unsigned char b[8];
    if (fread(b, 1, 8, fp) != 8) return 0;
    *out = (unsigned long long)b[0]
        | ((unsigned long long)b[1] << 8)
        | ((unsigned long long)b[2] << 16)
        | ((unsigned long long)b[3] << 24)
        | ((unsigned long long)b[4] << 32)
        | ((unsigned long long)b[5] << 40)
        | ((unsigned long long)b[6] << 48)
        | ((unsigned long long)b[7] << 56);
    return 1;
}

static int dsu__path_is_safe(const char *path) {
    const char *p = path;
    const char *seg = path;
    if (!path || !path[0]) return 0;
    if (path[0] == '\\' || path[0] == '/') return 0;
    if (((path[0] >= 'A' && path[0] <= 'Z') || (path[0] >= 'a' && path[0] <= 'z')) && path[1] == ':') {
        return 0;
    }
    while (*p) {
        char c = *p;
        if (c == '\\' || c == '/') {
            size_t seg_len = (size_t)(p - seg);
            if (seg_len == 0) return 0;
            if (seg_len == 1 && seg[0] == '.') return 0;
            if (seg_len == 2 && seg[0] == '.' && seg[1] == '.') return 0;
            seg = p + 1;
        } else if (c == ':') {
            return 0;
        }
        ++p;
    }
    if (seg && *seg) {
        size_t seg_len = (size_t)(p - seg);
        if (seg_len == 0) return 0;
        if (seg_len == 1 && seg[0] == '.') return 0;
        if (seg_len == 2 && seg[0] == '.' && seg[1] == '.') return 0;
    }
    return 1;
}

static int dsu__path_join(char *out, size_t cap, const char *root, const char *rel) {
    size_t nroot;
    size_t nrel;
    if (!out || !root || !rel) return 0;
    nroot = strlen(root);
    nrel = strlen(rel);
    if (nroot + nrel + 2 > cap) return 0;
    memcpy(out, root, nroot);
    if (nroot && root[nroot - 1] != '\\' && root[nroot - 1] != '/') {
        out[nroot++] = '\\';
    }
    memcpy(out + nroot, rel, nrel);
    out[nroot + nrel] = '\0';
    return 1;
}

static int dsu__ensure_dir(const char *path) {
#if defined(_WIN32)
    char buf[MAX_PATH];
    size_t n = strlen(path);
    size_t i;
    if (n >= sizeof(buf)) return 0;
    memcpy(buf, path, n + 1);
    for (i = 0; i < n; ++i) {
        if (buf[i] == '\\' || buf[i] == '/') {
            char saved = buf[i];
            buf[i] = '\0';
            if (buf[0] != '\0') {
                CreateDirectoryA(buf, NULL);
            }
            buf[i] = saved;
        }
    }
    CreateDirectoryA(buf, NULL);
#else
    (void)path;
#endif
    return 1;
}

static int dsu__read_tail(FILE *fp, unsigned long long *out_header_offset) {
    unsigned char tail[16];
    unsigned long long size;
    if (!fp || !out_header_offset) return 0;
    if (fseek(fp, 0, SEEK_END) != 0) return 0;
    size = (unsigned long long)ftell(fp);
    if (size < sizeof(tail)) return 0;
    if (fseek(fp, (long)(size - sizeof(tail)), SEEK_SET) != 0) return 0;
    if (fread(tail, 1, sizeof(tail), fp) != sizeof(tail)) return 0;
    if (memcmp(tail, DSU_EXE_ARCHIVE_TAIL_MAGIC, 8) != 0) return 0;
    *out_header_offset = (unsigned long long)tail[8]
        | ((unsigned long long)tail[9] << 8)
        | ((unsigned long long)tail[10] << 16)
        | ((unsigned long long)tail[11] << 24)
        | ((unsigned long long)tail[12] << 32)
        | ((unsigned long long)tail[13] << 40)
        | ((unsigned long long)tail[14] << 48)
        | ((unsigned long long)tail[15] << 56);
    return 1;
}

int dsu_exe_archive_open(const char *exe_path, dsu_exe_archive_t **out_archive) {
    dsu_exe_archive_t *arch = NULL;
    unsigned char magic[8];
    unsigned long version = 0;
    unsigned long file_count = 0;
    unsigned long long table_size = 0;
    unsigned long long data_size = 0;
    unsigned long table_crc = 0;
    unsigned long header_offset = 0;

    if (!exe_path || !out_archive) return 0;
    *out_archive = NULL;

    arch = (dsu_exe_archive_t *)calloc(1, sizeof(*arch));
    if (!arch) return 0;
    arch->fp = fopen(exe_path, "rb");
    if (!arch->fp) {
        free(arch);
        return 0;
    }

    if (!dsu__read_tail(arch->fp, &arch->header_offset)) {
        fclose(arch->fp);
        free(arch);
        return 0;
    }

    if (fseek(arch->fp, (long)arch->header_offset, SEEK_SET) != 0) {
        fclose(arch->fp);
        free(arch);
        return 0;
    }
    if (fread(magic, 1, 8, arch->fp) != 8) {
        fclose(arch->fp);
        free(arch);
        return 0;
    }
    if (memcmp(magic, DSU_EXE_ARCHIVE_MAGIC, 8) != 0) {
        fclose(arch->fp);
        free(arch);
        return 0;
    }
    if (!dsu__read_u32(arch->fp, &version)) {
        fclose(arch->fp);
        free(arch);
        return 0;
    }
    if (version != 1u) {
        fclose(arch->fp);
        free(arch);
        return 0;
    }
    if (!dsu__read_u32(arch->fp, &file_count)) {
        fclose(arch->fp);
        free(arch);
        return 0;
    }
    if (!dsu__read_u64(arch->fp, &table_size)) {
        fclose(arch->fp);
        free(arch);
        return 0;
    }
    if (!dsu__read_u64(arch->fp, &data_size)) {
        fclose(arch->fp);
        free(arch);
        return 0;
    }
    if (!dsu__read_u32(arch->fp, &table_crc)) {
        fclose(arch->fp);
        free(arch);
        return 0;
    }

    arch->file_count = file_count;
    arch->table_size = table_size;
    arch->data_size = data_size;
    arch->table_offset = (unsigned long long)ftell(arch->fp);
    arch->data_offset = arch->table_offset + arch->table_size;

    {
        unsigned char *table_bytes = (unsigned char *)malloc((size_t)table_size);
        unsigned long crc;
        if (!table_bytes) {
            fclose(arch->fp);
            free(arch);
            return 0;
        }
        if (fread(table_bytes, 1, (size_t)table_size, arch->fp) != (size_t)table_size) {
            free(table_bytes);
            fclose(arch->fp);
            free(arch);
            return 0;
        }
        crc = dsu__crc32(table_bytes, (unsigned long)table_size);
        free(table_bytes);
        if (crc != table_crc) {
            fclose(arch->fp);
            free(arch);
            return 0;
        }
    }

    *out_archive = arch;
    return 1;
}

void dsu_exe_archive_close(dsu_exe_archive_t *archive) {
    if (!archive) return;
    if (archive->fp) fclose(archive->fp);
    free(archive);
}

static int dsu__iter_entries(dsu_exe_archive_t *archive,
                             int (*cb)(dsu_exe_archive_t *, const char *, unsigned long long, unsigned long long, unsigned long, void *),
                             void *user) {
    unsigned long i;
    unsigned long long pos;
    if (!archive || !archive->fp || !cb) return 0;
    if (fseek(archive->fp, (long)archive->table_offset, SEEK_SET) != 0) return 0;
    pos = archive->table_offset;
    for (i = 0; i < archive->file_count; ++i) {
        unsigned short path_len = 0;
        unsigned short flags = 0;
        unsigned long long offset = 0;
        unsigned long long size = 0;
        unsigned long crc = 0;
        char *path = NULL;
        if (!dsu__read_u16(archive->fp, &path_len)) return 0;
        if (!dsu__read_u16(archive->fp, &flags)) return 0;
        if (!dsu__read_u64(archive->fp, &offset)) return 0;
        if (!dsu__read_u64(archive->fp, &size)) return 0;
        if (!dsu__read_u32(archive->fp, &crc)) return 0;
        if (path_len == 0) return 0;
        path = (char *)malloc(path_len + 1u);
        if (!path) return 0;
        if (fread(path, 1, path_len, archive->fp) != path_len) {
            free(path);
            return 0;
        }
        path[path_len] = '\0';
        if (!cb(archive, path, offset, size, crc, user)) {
            free(path);
            return 0;
        }
        free(path);
        pos = (unsigned long long)ftell(archive->fp);
        (void)flags;
        (void)pos;
    }
    return 1;
}

static int dsu__validate_cb(dsu_exe_archive_t *archive,
                            const char *path,
                            unsigned long long offset,
                            unsigned long long size,
                            unsigned long crc,
                            void *user) {
    (void)archive;
    (void)offset;
    (void)size;
    (void)crc;
    (void)user;
    return dsu__path_is_safe(path);
}

int dsu_exe_archive_validate_paths(dsu_exe_archive_t *archive) {
    return dsu__iter_entries(archive, dsu__validate_cb, NULL);
}

typedef struct dsu__extract_ctx_t {
    const char *dest_root;
} dsu__extract_ctx_t;

static int dsu__extract_cb(dsu_exe_archive_t *archive,
                           const char *path,
                           unsigned long long offset,
                           unsigned long long size,
                           unsigned long crc,
                           void *user) {
    dsu__extract_ctx_t *ctx = (dsu__extract_ctx_t *)user;
    char full_path[1024];
    unsigned char buf[16384];
    unsigned long long remaining = size;
    unsigned long crc_calc = 0u;
    FILE *out = NULL;
    unsigned long long data_pos;

    if (!ctx || !ctx->dest_root) return 0;
    if (!dsu__path_is_safe(path)) return 0;
    if (!dsu__path_join(full_path, sizeof(full_path), ctx->dest_root, path)) return 0;

    dsu__ensure_dir(full_path);
    out = fopen(full_path, "wb");
    if (!out) return 0;

    data_pos = archive->data_offset + offset;
    if (fseek(archive->fp, (long)data_pos, SEEK_SET) != 0) {
        fclose(out);
        return 0;
    }
    while (remaining > 0u) {
        unsigned long chunk = (remaining > sizeof(buf)) ? (unsigned long)sizeof(buf) : (unsigned long)remaining;
        if (fread(buf, 1, chunk, archive->fp) != chunk) {
            fclose(out);
            return 0;
        }
        if (fwrite(buf, 1, chunk, out) != chunk) {
            fclose(out);
            return 0;
        }
        crc_calc = dsu__crc32_update(crc_calc, buf, chunk);
        remaining -= chunk;
    }
    fclose(out);
    if (crc != crc_calc) {
        return 0;
    }
    return 1;
}

int dsu_exe_archive_extract(dsu_exe_archive_t *archive, const char *dest_root) {
    dsu__extract_ctx_t ctx;
    if (!archive || !dest_root) return 0;
    ctx.dest_root = dest_root;
    if (!dsu_exe_archive_validate_paths(archive)) return 0;
    return dsu__iter_entries(archive, dsu__extract_cb, &ctx);
}
