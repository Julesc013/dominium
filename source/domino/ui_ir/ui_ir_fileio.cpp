/*
FILE: source/domino/ui_ir/ui_ir_fileio.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir fileio
RESPONSIBILITY: Atomic writes and backup rotation for UI IR files.
*/
#include "ui_ir_fileio.h"

#include <stdio.h>
#include <string.h>

#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#endif

static bool domui_file_exists(const char* path)
{
    FILE* f;
    if (!path || !path[0]) {
        return false;
    }
    f = fopen(path, "rb");
    if (f) {
        fclose(f);
        return true;
    }
    return false;
}

static bool domui_delete_file(const char* path)
{
    if (!path || !path[0]) {
        return false;
    }
#if defined(_WIN32)
    return DeleteFileA(path) != 0;
#else
    return remove(path) == 0;
#endif
}

static bool domui_move_file_replace(const char* from, const char* to)
{
    if (!from || !to) {
        return false;
    }
#if defined(_WIN32)
    return MoveFileExA(from, to, MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH) != 0;
#else
    return rename(from, to) == 0;
#endif
}

static bool domui_rotate_backups(const char* path, domui_diag* diag)
{
    int i;
    char buf_from[512];
    char buf_to[512];

    if (!path || !path[0]) {
        if (diag) {
            diag->add_error("rotate_backups: invalid path", 0u, "");
        }
        return false;
    }

    /* Drop the oldest backup. */
    snprintf(buf_to, sizeof(buf_to), "%s.bak10", path);
    if (domui_file_exists(buf_to)) {
        (void)domui_delete_file(buf_to);
    }

    for (i = 9; i >= 1; --i) {
        snprintf(buf_from, sizeof(buf_from), "%s.bak%d", path, i);
        snprintf(buf_to, sizeof(buf_to), "%s.bak%d", path, i + 1);
        if (!domui_file_exists(buf_from)) {
            continue;
        }
        if (!domui_move_file_replace(buf_from, buf_to)) {
            if (diag) {
                diag->add_warning("rotate_backups: move failed", 0u, buf_from);
            }
        }
    }

    snprintf(buf_to, sizeof(buf_to), "%s.bak1", path);
    if (domui_file_exists(path)) {
        if (!domui_move_file_replace(path, buf_to)) {
            if (diag) {
                diag->add_warning("rotate_backups: move current failed", 0u, path);
            }
            return false;
        }
    }
    return true;
}

static bool domui_write_bytes_to_file(const char* path, const void* data, size_t size, domui_diag* diag)
{
    FILE* f;
    size_t wrote;

    if (!path || !path[0]) {
        if (diag) {
            diag->add_error("write: invalid path", 0u, "");
        }
        return false;
    }
    f = fopen(path, "wb");
    if (!f) {
        if (diag) {
            diag->add_error("write: fopen failed", 0u, path);
        }
        return false;
    }
    if (size != 0u) {
        wrote = fwrite(data, 1u, size, f);
        if (wrote != size) {
            fclose(f);
            if (diag) {
                diag->add_error("write: fwrite failed", 0u, path);
            }
            return false;
        }
    }
    fflush(f);
    if (fclose(f) != 0) {
        if (diag) {
            diag->add_error("write: fclose failed", 0u, path);
        }
        return false;
    }
    return true;
}

bool domui_atomic_write_file(const char* path, const void* data, size_t size, domui_diag* diag)
{
    char tmp_path[512];

    if (!path || !path[0]) {
        if (diag) {
            diag->add_error("atomic_write: invalid path", 0u, "");
        }
        return false;
    }
    snprintf(tmp_path, sizeof(tmp_path), "%s.tmp", path);

    if (!domui_write_bytes_to_file(tmp_path, data, size, diag)) {
        return false;
    }

    (void)domui_rotate_backups(path, diag);

    if (!domui_move_file_replace(tmp_path, path)) {
        if (diag) {
            diag->add_error("atomic_write: rename failed", 0u, path);
        }
        return false;
    }
    return true;
}

bool domui_read_file_bytes(const char* path, std::vector<unsigned char>& out_bytes, domui_diag* diag)
{
    FILE* f;
    long size;
    size_t read_bytes;
    out_bytes.clear();

    if (!path || !path[0]) {
        if (diag) {
            diag->add_error("read: invalid path", 0u, "");
        }
        return false;
    }
    f = fopen(path, "rb");
    if (!f) {
        if (diag) {
            diag->add_error("read: fopen failed", 0u, path);
        }
        return false;
    }
    if (fseek(f, 0L, SEEK_END) != 0) {
        fclose(f);
        if (diag) {
            diag->add_error("read: fseek failed", 0u, path);
        }
        return false;
    }
    size = ftell(f);
    if (size < 0) {
        fclose(f);
        if (diag) {
            diag->add_error("read: ftell failed", 0u, path);
        }
        return false;
    }
    if (fseek(f, 0L, SEEK_SET) != 0) {
        fclose(f);
        if (diag) {
            diag->add_error("read: fseek reset failed", 0u, path);
        }
        return false;
    }
    if (size == 0) {
        fclose(f);
        return true;
    }
    out_bytes.resize((size_t)size);
    read_bytes = fread(&out_bytes[0], 1u, (size_t)size, f);
    fclose(f);
    if (read_bytes != (size_t)size) {
        if (diag) {
            diag->add_error("read: fread failed", 0u, path);
        }
        return false;
    }
    return true;
}
