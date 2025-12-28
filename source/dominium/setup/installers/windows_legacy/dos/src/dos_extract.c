/*
FILE: source/dominium/setup/installers/windows_legacy/dos/src/dos_extract.c
MODULE: Dominium Setup (DOS)
PURPOSE: Embedded archive extraction helpers for DOS installers.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DSU_DOS_SFX_MAGIC "DSUX"
#define DSU_DOS_SFX_FOOTER_SIZE 12

static int dsu_dos_read_u32le(const unsigned char *buf, unsigned long *out_v) {
    if (!buf || !out_v) return 0;
    *out_v = (unsigned long)buf[0]
           | ((unsigned long)buf[1] << 8)
           | ((unsigned long)buf[2] << 16)
           | ((unsigned long)buf[3] << 24);
    return 1;
}

int dsu_dos_find_embedded_archive(const char *exe_path, unsigned long *out_offset, unsigned long *out_size) {
    FILE *f;
    long file_size;
    unsigned char footer[DSU_DOS_SFX_FOOTER_SIZE];
    unsigned long offset = 0ul;
    unsigned long size = 0ul;
    if (!exe_path || !out_offset || !out_size) return 0;
    *out_offset = 0ul;
    *out_size = 0ul;
    f = fopen(exe_path, "rb");
    if (!f) return 0;
    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return 0;
    }
    file_size = ftell(f);
    if (file_size < (long)DSU_DOS_SFX_FOOTER_SIZE) {
        fclose(f);
        return 0;
    }
    if (fseek(f, file_size - (long)DSU_DOS_SFX_FOOTER_SIZE, SEEK_SET) != 0) {
        fclose(f);
        return 0;
    }
    if (fread(footer, 1u, DSU_DOS_SFX_FOOTER_SIZE, f) != DSU_DOS_SFX_FOOTER_SIZE) {
        fclose(f);
        return 0;
    }
    if (memcmp(footer, DSU_DOS_SFX_MAGIC, 4u) != 0) {
        fclose(f);
        return 0;
    }
    if (!dsu_dos_read_u32le(footer + 4u, &offset) ||
        !dsu_dos_read_u32le(footer + 8u, &size)) {
        fclose(f);
        return 0;
    }
    if (offset + size > (unsigned long)file_size) {
        fclose(f);
        return 0;
    }
    fclose(f);
    *out_offset = offset;
    *out_size = size;
    return 1;
}

int dsu_dos_extract_embedded_archive(const char *exe_path, const char *out_path) {
    FILE *in;
    FILE *out;
    unsigned long offset = 0ul;
    unsigned long size = 0ul;
    unsigned char buf[8192];
    unsigned long remaining;
    if (!exe_path || !out_path) return 0;
    if (!dsu_dos_find_embedded_archive(exe_path, &offset, &size)) {
        return 0;
    }
    in = fopen(exe_path, "rb");
    if (!in) return 0;
    if (fseek(in, (long)offset, SEEK_SET) != 0) {
        fclose(in);
        return 0;
    }
    out = fopen(out_path, "wb");
    if (!out) {
        fclose(in);
        return 0;
    }
    remaining = size;
    while (remaining > 0ul) {
        unsigned long want = (remaining > (unsigned long)sizeof(buf)) ? (unsigned long)sizeof(buf) : remaining;
        size_t nr = fread(buf, 1u, (size_t)want, in);
        if (nr != (size_t)want) {
            fclose(in);
            fclose(out);
            return 0;
        }
        if (fwrite(buf, 1u, nr, out) != nr) {
            fclose(in);
            fclose(out);
            return 0;
        }
        remaining -= (unsigned long)want;
    }
    fclose(in);
    if (fclose(out) != 0) return 0;
    return 1;
}
