/*
FILE: source/dominium/setup/tests/dsu_exe_archive_test.c
MODULE: Dominium Setup EXE
PURPOSE: Validate embedded archive safety and extraction behavior.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dsu_exe_archive.h"

#if defined(_MSC_VER)
#define dsu_exe_snprintf _snprintf
#else
#define dsu_exe_snprintf snprintf
#endif

#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#else
#include <sys/stat.h>
#endif

static unsigned long crc32_update(unsigned long crc, const unsigned char *buf, unsigned long len) {
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

static unsigned long crc32(const unsigned char *buf, unsigned long len) {
    return crc32_update(0u, buf, len);
}

static int write_u16(FILE *f, unsigned short v) {
    unsigned char b[2];
    b[0] = (unsigned char)(v & 0xFFu);
    b[1] = (unsigned char)((v >> 8) & 0xFFu);
    return fwrite(b, 1, 2, f) == 2;
}

static int write_u32(FILE *f, unsigned long v) {
    unsigned char b[4];
    b[0] = (unsigned char)(v & 0xFFu);
    b[1] = (unsigned char)((v >> 8) & 0xFFu);
    b[2] = (unsigned char)((v >> 16) & 0xFFu);
    b[3] = (unsigned char)((v >> 24) & 0xFFu);
    return fwrite(b, 1, 4, f) == 4;
}

static int write_u64(FILE *f, unsigned long long v) {
    unsigned char b[8];
    b[0] = (unsigned char)(v & 0xFFu);
    b[1] = (unsigned char)((v >> 8) & 0xFFu);
    b[2] = (unsigned char)((v >> 16) & 0xFFu);
    b[3] = (unsigned char)((v >> 24) & 0xFFu);
    b[4] = (unsigned char)((v >> 32) & 0xFFu);
    b[5] = (unsigned char)((v >> 40) & 0xFFu);
    b[6] = (unsigned char)((v >> 48) & 0xFFu);
    b[7] = (unsigned char)((v >> 56) & 0xFFu);
    return fwrite(b, 1, 8, f) == 8;
}

static int write_archive(const char *path, const char *entry_path, const unsigned char *data, unsigned long size) {
    FILE *f;
    unsigned long table_crc;
    unsigned long data_crc;
    unsigned long long header_offset = 0u;
    unsigned short path_len;

    const char magic[] = "DSUARCH1";
    const char tail[] = "DSUTAIL1";

    if (!path || !entry_path) return 0;
    f = fopen(path, "wb");
    if (!f) return 0;

    header_offset = 0u;
    if (fwrite(magic, 1, 8, f) != 8) { fclose(f); return 0; }
    if (!write_u32(f, 1u)) { fclose(f); return 0; }
    if (!write_u32(f, 1u)) { fclose(f); return 0; }

    path_len = (unsigned short)strlen(entry_path);
    {
        unsigned char table_buf[256];
        size_t pos = 0u;
        unsigned long long offset = 0u;
        unsigned long long size64 = (unsigned long long)size;
        data_crc = crc32(data, size);

        table_buf[pos++] = (unsigned char)(path_len & 0xFFu);
        table_buf[pos++] = (unsigned char)((path_len >> 8) & 0xFFu);
        table_buf[pos++] = 0u;
        table_buf[pos++] = 0u;

        memcpy(table_buf + pos, &offset, 8); pos += 8;
        memcpy(table_buf + pos, &size64, 8); pos += 8;
        memcpy(table_buf + pos, &data_crc, 4); pos += 4;
        memcpy(table_buf + pos, entry_path, path_len); pos += path_len;

        table_crc = crc32(table_buf, (unsigned long)pos);

        write_u64(f, (unsigned long long)pos);
        write_u64(f, (unsigned long long)size);
        write_u32(f, table_crc);
        fwrite(table_buf, 1, pos, f);
    }

    fwrite(data, 1, size, f);
    fwrite(tail, 1, 8, f);
    write_u64(f, header_offset);
    fclose(f);
    return 1;
}

static int read_file(const char *path, unsigned char *out, unsigned long cap, unsigned long *out_size) {
    FILE *f;
    unsigned long n;
    if (!path || !out) return 0;
    f = fopen(path, "rb");
    if (!f) return 0;
    n = (unsigned long)fread(out, 1, cap, f);
    fclose(f);
    if (out_size) *out_size = n;
    return 1;
}

int main(void) {
    int ok = 1;
    char temp_dir[512];
    char arch_path[512];
    char out_dir[512];
    char out_file[512];
    unsigned char buf[64];
    unsigned long n = 0u;

    const unsigned char payload[] = "ok";

#if defined(_WIN32)
    {
        DWORD len = GetTempPathA((DWORD)sizeof(temp_dir), temp_dir);
        if (len == 0u || len >= sizeof(temp_dir)) return 1;
        strncat(temp_dir, "dsu_exe_archive_test", sizeof(temp_dir) - strlen(temp_dir) - 1u);
        CreateDirectoryA(temp_dir, NULL);
    }
#else
    strcpy(temp_dir, "./dsu_exe_archive_test");
    mkdir(temp_dir, 0755);
#endif

    dsu_exe_snprintf(arch_path, sizeof(arch_path), "%s\\archive_safe.bin", temp_dir);
    dsu_exe_snprintf(out_dir, sizeof(out_dir), "%s\\out", temp_dir);
    dsu_exe_snprintf(out_file, sizeof(out_file), "%s\\payloads\\test.txt", out_dir);

#if defined(_WIN32)
    CreateDirectoryA(out_dir, NULL);
#else
    mkdir(out_dir, 0755);
#endif

    ok &= write_archive(arch_path, "payloads/test.txt", payload, (unsigned long)strlen((const char *)payload));
    if (ok) {
        dsu_exe_archive_t *arch = NULL;
        ok &= dsu_exe_archive_open(arch_path, &arch);
        ok &= dsu_exe_archive_validate_paths(arch);
        ok &= dsu_exe_archive_extract(arch, out_dir);
        dsu_exe_archive_close(arch);
        ok &= read_file(out_file, buf, sizeof(buf), &n);
        ok &= (n == 2u && buf[0] == 'o' && buf[1] == 'k');
    }

    dsu_exe_snprintf(arch_path, sizeof(arch_path), "%s\\archive_bad.bin", temp_dir);
    ok &= write_archive(arch_path, "..\\evil.txt", payload, (unsigned long)strlen((const char *)payload));
    if (ok) {
        dsu_exe_archive_t *arch = NULL;
        ok &= dsu_exe_archive_open(arch_path, &arch);
        ok &= !dsu_exe_archive_validate_paths(arch);
        dsu_exe_archive_close(arch);
    }

    if (!ok) {
        fprintf(stderr, "archive test failed\n");
    }
    return ok ? 0 : 1;
}
