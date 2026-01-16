/*
FILE: source/domino/core/fs_util.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/fs_util
RESPONSIBILITY: Implements `fs_util`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>
#include <errno.h>
#include <stdio.h>
#include "core_internal.h"

#if defined(_WIN32)
# include <direct.h>
#else
# include <sys/stat.h>
# include <unistd.h>
#endif

void dom_copy_string(char* dst, size_t cap, const char* src)
{
    size_t len;

    if (!dst || cap == 0u) {
        return;
    }

    if (!src) {
        dst[0] = '\0';
        return;
    }

    len = strlen(src);
    if (len >= cap) {
        len = cap - 1u;
    }
    memcpy(dst, src, len);
    dst[len] = '\0';
}

static bool dom_path_append(char* dst, size_t cap, const char* tail)
{
    size_t len;
    size_t i;

    if (!dst || !tail || cap == 0u) {
        return false;
    }

    len = strlen(dst);
    if (len > 0u && dst[len - 1u] != '/' && dst[len - 1u] != '\\') {
        if (len + 1u >= cap) {
            return false;
        }
        dst[len] = '/';
        dst[len + 1u] = '\0';
        len += 1u;
    }

    for (i = 0u; tail[i] != '\0'; ++i) {
        if (len + 1u >= cap) {
            dst[len] = '\0';
            return false;
        }
        dst[len] = tail[i];
        len += 1u;
    }
    dst[len] = '\0';
    return true;
}

bool dom_path_join(char* dst, size_t cap, const char* a, const char* b)
{
    if (!dst || cap == 0u) {
        return false;
    }
    dst[0] = '\0';
    if (a && a[0] != '\0') {
        dom_copy_string(dst, cap, a);
    }
    if (b && b[0] != '\0') {
        if (!dom_path_append(dst, cap, b)) {
            return false;
        }
    }
    return true;
}

bool dom_path_join3(char* dst, size_t cap, const char* a, const char* b, const char* c)
{
    if (!dom_path_join(dst, cap, a, b)) {
        return false;
    }
    if (c && c[0] != '\0') {
        return dom_path_append(dst, cap, c);
    }
    return true;
}

bool dom_path_last_segment(const char* path, char* out, size_t cap)
{
    const char* last;
    size_t len;

    if (!path || !out || cap == 0u) {
        return false;
    }

    last = strrchr(path, '/');
    if (!last) {
        last = strrchr(path, '\\');
    }
    if (last) {
        last += 1;
    } else {
        last = path;
    }

    len = strlen(last);
    if (len >= cap) {
        len = cap - 1u;
    }
    memcpy(out, last, len);
    out[len] = '\0';
    return true;
}

bool dom_fs_file_exists(const char* path)
{
    void* fh;

    fh = dsys_file_open(path, "rb");
    if (fh) {
        dsys_file_close(fh);
        return true;
    }
    return false;
}

bool dom_fs_dir_exists(const char* path)
{
    dsys_dir_iter* it;

    it = dsys_dir_open(path);
    if (it) {
        dsys_dir_close(it);
        return true;
    }
    return false;
}

static bool dom_fs_make_dir(const char* path)
{
    int res;

    if (!path || path[0] == '\0') {
        return false;
    }
#if defined(_WIN32)
    res = _mkdir(path);
#else
    res = mkdir(path, 0777);
#endif
    if (res == 0) {
        return true;
    }
    if (errno == EEXIST) {
        return true;
    }
    return false;
}

bool dom_fs_mkdirs(const char* path)
{
    char partial[260];
    size_t i;
    size_t len;

    if (!path || path[0] == '\0') {
        return false;
    }

    dom_copy_string(partial, sizeof(partial), path);
    len = strlen(partial);
    for (i = 0u; i < len; ++i) {
        if (partial[i] == '/' || partial[i] == '\\') {
            char saved;
            if (i == 0u) {
                continue;
            }
            saved = partial[i];
            partial[i] = '\0';
            (void)dom_fs_make_dir(partial);
            partial[i] = saved;
        }
    }
    return dom_fs_make_dir(partial);
}

bool dom_fs_read_text(const char* path, char* buf, size_t cap, size_t* out_len)
{
    void* fh;
    size_t total;
    size_t read_count;

    if (!path || !buf || cap == 0u) {
        return false;
    }

    fh = dsys_file_open(path, "rb");
    if (!fh) {
        return false;
    }

    total = 0u;
    while (total + 1u < cap) {
        read_count = dsys_file_read(fh, buf + total, cap - total - 1u);
        if (read_count == 0u) {
            break;
        }
        total += read_count;
    }
    buf[total] = '\0';
    if (out_len) {
        *out_len = total;
    }
    dsys_file_close(fh);
    return true;
}

bool dom_fs_write_text(const char* path, const char* text)
{
    void* fh;
    size_t len;
    size_t written;

    if (!path || !text) {
        return false;
    }

    fh = dsys_file_open(path, "wb");
    if (!fh) {
        return false;
    }

    len = strlen(text);
    written = dsys_file_write(fh, text, len);
    dsys_file_close(fh);
    return written == len;
}

bool dom_fs_copy_file(const char* src, const char* dst)
{
    void* src_fh;
    void* dst_fh;
    char   buf[1024];
    size_t read_count;

    if (!src || !dst) {
        return false;
    }

    src_fh = dsys_file_open(src, "rb");
    if (!src_fh) {
        return false;
    }
    dst_fh = dsys_file_open(dst, "wb");
    if (!dst_fh) {
        dsys_file_close(src_fh);
        return false;
    }

    while (1) {
        read_count = dsys_file_read(src_fh, buf, sizeof(buf));
        if (read_count == 0u) {
            break;
        }
        if (dsys_file_write(dst_fh, buf, read_count) != read_count) {
            dsys_file_close(src_fh);
            dsys_file_close(dst_fh);
            return false;
        }
    }

    dsys_file_close(src_fh);
    dsys_file_close(dst_fh);
    return true;
}

bool dom_fs_copy_tree(const char* src, const char* dst)
{
    dsys_dir_iter* it;
    dsys_dir_entry ent;
    char           src_child[260];
    char           dst_child[260];

    if (!src || !dst) {
        return false;
    }

    if (!dom_fs_mkdirs(dst)) {
        return false;
    }

    it = dsys_dir_open(src);
    if (!it) {
        return false;
    }

    while (dsys_dir_next(it, &ent)) {
        if (ent.name[0] == '.' && (ent.name[1] == '\0' ||
                                   (ent.name[1] == '.' && ent.name[2] == '\0'))) {
            continue;
        }
        if (!dom_path_join(src_child, sizeof(src_child), src, ent.name) ||
            !dom_path_join(dst_child, sizeof(dst_child), dst, ent.name)) {
            dsys_dir_close(it);
            return false;
        }
        if (ent.is_dir) {
            if (!dom_fs_copy_tree(src_child, dst_child)) {
                dsys_dir_close(it);
                return false;
            }
        } else {
            if (!dom_fs_copy_file(src_child, dst_child)) {
                dsys_dir_close(it);
                return false;
            }
        }
    }

    dsys_dir_close(it);
    return true;
}

static bool dom_fs_remove_tree_inner(const char* path)
{
    dsys_dir_iter* it;
    dsys_dir_entry ent;
    char           child[260];

    it = dsys_dir_open(path);
    if (it) {
        while (dsys_dir_next(it, &ent)) {
            if (ent.name[0] == '.' && (ent.name[1] == '\0' ||
                                       (ent.name[1] == '.' && ent.name[2] == '\0'))) {
                continue;
            }
            if (!dom_path_join(child, sizeof(child), path, ent.name)) {
                dsys_dir_close(it);
                return false;
            }
            if (ent.is_dir) {
                if (!dom_fs_remove_tree_inner(child)) {
                    dsys_dir_close(it);
                    return false;
                }
#if defined(_WIN32)
                _rmdir(child);
#else
                rmdir(child);
#endif
            } else {
                remove(child);
            }
        }
        dsys_dir_close(it);
    }

#if defined(_WIN32)
    if (_rmdir(path) != 0) {
        return false;
    }
#else
    if (rmdir(path) != 0) {
        return false;
    }
#endif
    return true;
}

bool dom_fs_remove_tree(const char* path)
{
    if (!path || path[0] == '\0') {
        return false;
    }
    if (!dom_fs_dir_exists(path)) {
        return true;
    }
    return dom_fs_remove_tree_inner(path);
}
