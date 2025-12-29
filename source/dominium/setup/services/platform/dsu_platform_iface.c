/*
FILE: source/dominium/setup/core/src/fs/dsu_platform_iface.c
MODULE: Dominium Setup
PURPOSE: Host OS interface for filesystem primitives (Plan S-4). All OS-specific behavior lives here.
*/
#include "dsu_platform_iface.h"

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#if defined(_WIN32)
#  define WIN32_LEAN_AND_MEAN
#  include <windows.h>
#  include <direct.h>
#else
#  include <errno.h>
#  include <dirent.h>
#  include <sys/stat.h>
#  include <sys/statvfs.h>
#  include <unistd.h>
#endif

static dsu_status_t dsu__dup_cstr(const char *s, char **out) {
    dsu_u32 n;
    char *p;
    if (!out) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out = NULL;
    if (!s) {
        return DSU_STATUS_INVALID_ARGS;
    }
    n = dsu__strlen(s);
    if (n == 0xFFFFFFFFu) {
        return DSU_STATUS_INVALID_ARGS;
    }
    p = (char *)dsu__malloc(n + 1u);
    if (!p) {
        return DSU_STATUS_IO_ERROR;
    }
    if (n) {
        memcpy(p, s, (size_t)n);
    }
    p[n] = '\0';
    *out = p;
    return DSU_STATUS_SUCCESS;
}

#if defined(_WIN32)
static dsu_status_t dsu__win32_path_to_native(const char *path_in, char **out_native) {
    dsu_u32 n;
    char *p;
    dsu_u32 i;
    if (!out_native) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_native = NULL;
    if (!path_in) {
        return DSU_STATUS_INVALID_ARGS;
    }
    n = dsu__strlen(path_in);
    if (n == 0xFFFFFFFFu) {
        return DSU_STATUS_INVALID_ARGS;
    }
    p = (char *)dsu__malloc(n + 1u);
    if (!p) {
        return DSU_STATUS_IO_ERROR;
    }
    for (i = 0u; i < n; ++i) {
        char c = path_in[i];
        if (c == '/') {
            p[i] = '\\';
        } else {
            p[i] = c;
        }
    }
    p[n] = '\0';
    *out_native = p;
    return DSU_STATUS_SUCCESS;
}
#endif

dsu_status_t dsu_platform_path_info(const char *path, dsu_u8 *out_exists, dsu_u8 *out_is_dir, dsu_u8 *out_is_symlink) {
    if (!path || !out_exists || !out_is_dir || !out_is_symlink) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_exists = 0u;
    *out_is_dir = 0u;
    *out_is_symlink = 0u;

#if defined(_WIN32)
    {
        DWORD attrs;
        char *native = NULL;
        dsu_status_t st = dsu__win32_path_to_native(path, &native);
        if (st != DSU_STATUS_SUCCESS) {
            return st;
        }
        attrs = GetFileAttributesA(native);
        dsu__free(native);
        if (attrs == INVALID_FILE_ATTRIBUTES) {
            return DSU_STATUS_SUCCESS;
        }
        *out_exists = 1u;
        if (attrs & FILE_ATTRIBUTE_DIRECTORY) {
            *out_is_dir = 1u;
        }
        if (attrs & FILE_ATTRIBUTE_REPARSE_POINT) {
            *out_is_symlink = 1u;
        }
        return DSU_STATUS_SUCCESS;
    }
#else
    {
        struct stat stbuf;
        struct stat lstbuf;
        if (stat(path, &stbuf) != 0) {
            return DSU_STATUS_SUCCESS;
        }
        *out_exists = 1u;
        if (S_ISDIR(stbuf.st_mode)) {
            *out_is_dir = 1u;
        }
        if (lstat(path, &lstbuf) == 0) {
            if (S_ISLNK(lstbuf.st_mode)) {
                *out_is_symlink = 1u;
            }
        }
        return DSU_STATUS_SUCCESS;
    }
#endif
}

dsu_status_t dsu_platform_mkdir(const char *path) {
    if (!path || path[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }
#if defined(_WIN32)
    {
        dsu_u8 exists;
        dsu_u8 is_dir;
        dsu_u8 is_symlink;
        char *native = NULL;
        dsu_status_t st = dsu__win32_path_to_native(path, &native);
        if (st != DSU_STATUS_SUCCESS) {
            return st;
        }
        if (_mkdir(native) != 0) {
            dsu__free(native);
            if (dsu_platform_path_info(path, &exists, &is_dir, &is_symlink) == DSU_STATUS_SUCCESS &&
                exists && is_dir && !is_symlink) {
                return DSU_STATUS_SUCCESS;
            }
            return DSU_STATUS_IO_ERROR;
        }
        dsu__free(native);
        return DSU_STATUS_SUCCESS;
    }
#else
    if (mkdir(path, 0755) != 0) {
        if (errno == EEXIST) {
            struct stat stbuf;
            if (stat(path, &stbuf) == 0 && S_ISDIR(stbuf.st_mode)) {
                return DSU_STATUS_SUCCESS;
            }
            return DSU_STATUS_IO_ERROR;
        }
        return DSU_STATUS_IO_ERROR;
    }
    return DSU_STATUS_SUCCESS;
#endif
}

dsu_status_t dsu_platform_rmdir(const char *path) {
    if (!path || path[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }
#if defined(_WIN32)
    {
        int rc;
        char *native = NULL;
        dsu_status_t st = dsu__win32_path_to_native(path, &native);
        if (st != DSU_STATUS_SUCCESS) {
            return st;
        }
        rc = _rmdir(native);
        dsu__free(native);
        if (rc != 0) {
            return DSU_STATUS_IO_ERROR;
        }
        return DSU_STATUS_SUCCESS;
    }
#else
    if (rmdir(path) != 0) {
        return DSU_STATUS_IO_ERROR;
    }
    return DSU_STATUS_SUCCESS;
#endif
}

dsu_status_t dsu_platform_remove_file(const char *path) {
    if (!path || path[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (remove(path) != 0) {
        return DSU_STATUS_IO_ERROR;
    }
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_platform_rename(const char *src, const char *dst, dsu_u8 replace_existing) {
    if (!src || !dst || src[0] == '\0' || dst[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (!replace_existing) {
        if (rename(src, dst) != 0) {
            return DSU_STATUS_IO_ERROR;
        }
        return DSU_STATUS_SUCCESS;
    }

#if defined(_WIN32)
    {
        char *src_native = NULL;
        char *dst_native = NULL;
        dsu_status_t st;
        st = dsu__win32_path_to_native(src, &src_native);
        if (st != DSU_STATUS_SUCCESS) {
            return st;
        }
        st = dsu__win32_path_to_native(dst, &dst_native);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(src_native);
            return st;
        }
        if (!MoveFileExA(src_native, dst_native, MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH)) {
            dsu__free(src_native);
            dsu__free(dst_native);
            return DSU_STATUS_IO_ERROR;
        }
        dsu__free(src_native);
        dsu__free(dst_native);
        return DSU_STATUS_SUCCESS;
    }
#else
    /* POSIX rename replaces destination atomically. */
    if (rename(src, dst) != 0) {
        return DSU_STATUS_IO_ERROR;
    }
    return DSU_STATUS_SUCCESS;
#endif
}

static int dsu__dir_entry_name_cmp(const void *a, const void *b) {
    const dsu_platform_dir_entry_t *ea = (const dsu_platform_dir_entry_t *)a;
    const dsu_platform_dir_entry_t *eb = (const dsu_platform_dir_entry_t *)b;
    const char *sa = ea->name ? ea->name : "";
    const char *sb = eb->name ? eb->name : "";
    return strcmp(sa, sb);
}

dsu_status_t dsu_platform_list_dir(const char *path, dsu_platform_dir_entry_t **out_entries, dsu_u32 *out_count) {
    if (!path || !out_entries || !out_count) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_entries = NULL;
    *out_count = 0u;

#if defined(_WIN32)
    {
        WIN32_FIND_DATAA fdata;
        HANDLE h;
        dsu_platform_dir_entry_t *items = NULL;
        dsu_u32 count = 0u;
        dsu_u32 cap = 0u;
        char *native_dir = NULL;
        char *native_pat = NULL;
        dsu_u32 dir_len;
        dsu_status_t st;

        st = dsu__win32_path_to_native(path, &native_dir);
        if (st != DSU_STATUS_SUCCESS) {
            return st;
        }
        dir_len = dsu__strlen(native_dir);
        if (dir_len == 0xFFFFFFFFu) {
            dsu__free(native_dir);
            return DSU_STATUS_INVALID_ARGS;
        }

        native_pat = (char *)dsu__malloc(dir_len + 3u);
        if (!native_pat) {
            dsu__free(native_dir);
            return DSU_STATUS_IO_ERROR;
        }
        memcpy(native_pat, native_dir, (size_t)dir_len);
        if (dir_len != 0u && native_pat[dir_len - 1u] != '\\' && native_pat[dir_len - 1u] != '/') {
            native_pat[dir_len++] = '\\';
        }
        native_pat[dir_len++] = '*';
        native_pat[dir_len] = '\0';

        h = FindFirstFileA(native_pat, &fdata);
        dsu__free(native_pat);
        dsu__free(native_dir);
        if (h == INVALID_HANDLE_VALUE) {
            return DSU_STATUS_IO_ERROR;
        }

        for (;;) {
            const char *name = fdata.cFileName;
            if (strcmp(name, ".") != 0 && strcmp(name, "..") != 0) {
                dsu_platform_dir_entry_t e;
                dsu_u32 new_cap;
                memset(&e, 0, sizeof(e));
                if (dsu__dup_cstr(name, &e.name) != DSU_STATUS_SUCCESS) {
                    FindClose(h);
                    dsu_platform_free_dir_entries(items, count);
                    return DSU_STATUS_IO_ERROR;
                }
                if (fdata.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
                    e.is_dir = 1u;
                }
                if (fdata.dwFileAttributes & FILE_ATTRIBUTE_REPARSE_POINT) {
                    e.is_symlink = 1u;
                }
                if (count == cap) {
                    new_cap = (cap == 0u) ? 16u : (cap * 2u);
                    items = (dsu_platform_dir_entry_t *)dsu__realloc(items, new_cap * (dsu_u32)sizeof(*items));
                    if (!items) {
                        FindClose(h);
                        return DSU_STATUS_IO_ERROR;
                    }
                    cap = new_cap;
                }
                items[count++] = e;
            }
            if (!FindNextFileA(h, &fdata)) {
                break;
            }
        }
        FindClose(h);

        if (count > 1u) {
            qsort(items, (size_t)count, sizeof(*items), dsu__dir_entry_name_cmp);
        }
        *out_entries = items;
        *out_count = count;
        return DSU_STATUS_SUCCESS;
    }
#else
    {
        DIR *d;
        struct dirent *de;
        dsu_platform_dir_entry_t *items = NULL;
        dsu_u32 count = 0u;
        dsu_u32 cap = 0u;

        d = opendir(path);
        if (!d) {
            return DSU_STATUS_IO_ERROR;
        }
        while ((de = readdir(d)) != NULL) {
            if (strcmp(de->d_name, ".") == 0 || strcmp(de->d_name, "..") == 0) {
                continue;
            }
            {
                dsu_platform_dir_entry_t e;
                dsu_u32 new_cap;
                memset(&e, 0, sizeof(e));
                if (dsu__dup_cstr(de->d_name, &e.name) != DSU_STATUS_SUCCESS) {
                    closedir(d);
                    dsu_platform_free_dir_entries(items, count);
                    return DSU_STATUS_IO_ERROR;
                }
                /* Determine kind (best-effort). */
                {
                    struct stat stbuf;
                    struct stat lstbuf;
                    dsu_u32 n = dsu__strlen(path);
                    dsu_u32 m = dsu__strlen(de->d_name);
                    char *full = (char *)dsu__malloc(n + 1u + m + 1u);
                    if (!full) {
                        closedir(d);
                        dsu__free(e.name);
                        dsu_platform_free_dir_entries(items, count);
                        return DSU_STATUS_IO_ERROR;
                    }
                    memcpy(full, path, (size_t)n);
                    full[n] = '/';
                    memcpy(full + n + 1u, de->d_name, (size_t)m);
                    full[n + 1u + m] = '\0';
                    if (stat(full, &stbuf) == 0) {
                        if (S_ISDIR(stbuf.st_mode)) {
                            e.is_dir = 1u;
                        }
                    }
                    if (lstat(full, &lstbuf) == 0) {
                        if (S_ISLNK(lstbuf.st_mode)) {
                            e.is_symlink = 1u;
                        }
                    }
                    dsu__free(full);
                }
                if (count == cap) {
                    new_cap = (cap == 0u) ? 16u : (cap * 2u);
                    items = (dsu_platform_dir_entry_t *)dsu__realloc(items, new_cap * (dsu_u32)sizeof(*items));
                    if (!items) {
                        closedir(d);
                        return DSU_STATUS_IO_ERROR;
                    }
                    cap = new_cap;
                }
                items[count++] = e;
            }
        }
        closedir(d);
        if (count > 1u) {
            qsort(items, (size_t)count, sizeof(*items), dsu__dir_entry_name_cmp);
        }
        *out_entries = items;
        *out_count = count;
        return DSU_STATUS_SUCCESS;
    }
#endif
}

void dsu_platform_free_dir_entries(dsu_platform_dir_entry_t *entries, dsu_u32 count) {
    dsu_u32 i;
    if (!entries) {
        return;
    }
    for (i = 0u; i < count; ++i) {
        dsu__free(entries[i].name);
        entries[i].name = NULL;
    }
    dsu__free(entries);
}

dsu_status_t dsu_platform_disk_free_bytes(const char *path, dsu_u64 *out_free_bytes) {
    if (!path || !out_free_bytes) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_free_bytes = 0u;
#if defined(_WIN32)
    {
        ULARGE_INTEGER free_bytes;
        ULARGE_INTEGER total_bytes;
        ULARGE_INTEGER total_free;
        char *native = NULL;
        dsu_status_t st = dsu__win32_path_to_native(path, &native);
        if (st != DSU_STATUS_SUCCESS) {
            return st;
        }
        if (!GetDiskFreeSpaceExA(native, &free_bytes, &total_bytes, &total_free)) {
            dsu__free(native);
            return DSU_STATUS_IO_ERROR;
        }
        dsu__free(native);
        *out_free_bytes = (dsu_u64)free_bytes.QuadPart;
        return DSU_STATUS_SUCCESS;
    }
#else
    {
        struct statvfs vfs;
        if (statvfs(path, &vfs) != 0) {
            return DSU_STATUS_IO_ERROR;
        }
        *out_free_bytes = (dsu_u64)vfs.f_bsize * (dsu_u64)vfs.f_bavail;
        return DSU_STATUS_SUCCESS;
    }
#endif
}

dsu_status_t dsu_platform_get_cwd(char *out_path, dsu_u32 out_path_cap) {
    if (!out_path || out_path_cap == 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    out_path[0] = '\0';

#if defined(_WIN32)
    {
        char buf[MAX_PATH];
        DWORD n = GetCurrentDirectoryA((DWORD)sizeof(buf), buf);
        dsu_u32 i;
        if (n == 0u || n >= (DWORD)sizeof(buf)) {
            return DSU_STATUS_IO_ERROR;
        }
        if ((dsu_u32)n + 1u > out_path_cap) {
            return DSU_STATUS_INVALID_ARGS;
        }
        for (i = 0u; i < (dsu_u32)n; ++i) {
            char c = buf[i];
            if (c == '\\') c = '/';
            if (i == 0u && ((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z')) && buf[1] == ':') {
                if (c >= 'A' && c <= 'Z') {
                    c = (char)(c - 'A' + 'a');
                }
            }
            out_path[i] = c;
        }
        out_path[n] = '\0';
        return DSU_STATUS_SUCCESS;
    }
#else
    {
        if (!getcwd(out_path, (size_t)out_path_cap)) {
            return DSU_STATUS_IO_ERROR;
        }
        return DSU_STATUS_SUCCESS;
    }
#endif
}
