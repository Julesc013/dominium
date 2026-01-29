/*
FILE: source/domino/system/dsys_dir_sorted.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/dsys_dir_sorted
RESPONSIBILITY: Deterministic directory listing helpers (sorting + stable iteration).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89 standard headers.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Canonical ASCII case-folded ordering with stable tiebreaks.
VERSIONING / ABI / DATA FORMAT NOTES: Internal only.
EXTENSION POINTS: Replace enumeration with platform-native sorted listing if available.
*/
#include "dsys_dir_sorted.h"
#include "dsys_internal.h"

#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
#include <io.h>
#include <direct.h>
#else
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

static unsigned char dsys_ascii_lower(unsigned char c)
{
    if (c >= 'A' && c <= 'Z') {
        return (unsigned char)(c + ('a' - 'A'));
    }
    return c;
}

static int dsys_dir_name_cmp(const char* a, const char* b)
{
    unsigned char ca;
    unsigned char cb;
    if (!a && !b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    while (*a && *b) {
        ca = (unsigned char)*a;
        cb = (unsigned char)*b;
        ca = dsys_ascii_lower(ca);
        cb = dsys_ascii_lower(cb);
        if (ca != cb) {
            return (ca < cb) ? -1 : 1;
        }
        ++a;
        ++b;
    }
    if (*a) return 1;
    if (*b) return -1;
    return 0;
}

static int dsys_dir_entry_cmp(const void* pa, const void* pb)
{
    const dsys_dir_entry* a = (const dsys_dir_entry*)pa;
    const dsys_dir_entry* b = (const dsys_dir_entry*)pb;
    int primary = dsys_dir_name_cmp(a->name, b->name);
    if (primary != 0) {
        return primary;
    }
    return strcmp(a->name, b->name);
}

static int dsys_dir_push_entry(dsys_dir_entry** entries, uint32_t* count, uint32_t* cap, const dsys_dir_entry* entry)
{
    dsys_dir_entry* next;
    if (!entries || !count || !cap || !entry) {
        return 0;
    }
    if (*count >= *cap) {
        uint32_t new_cap = (*cap == 0u) ? 16u : (*cap * 2u);
        next = (dsys_dir_entry*)realloc(*entries, sizeof(dsys_dir_entry) * (size_t)new_cap);
        if (!next) {
            return 0;
        }
        *entries = next;
        *cap = new_cap;
    }
    (*entries)[*count] = *entry;
    *count += 1u;
    return 1;
}

int dsys_dir_collect_sorted(const char* path, dsys_dir_entry** out_entries, uint32_t* out_count)
{
    dsys_dir_entry* entries = NULL;
    uint32_t count = 0u;
    uint32_t cap = 0u;

    if (out_entries) {
        *out_entries = NULL;
    }
    if (out_count) {
        *out_count = 0u;
    }
    if (!path || !path[0]) {
        return 0;
    }

#if defined(_WIN32)
    {
        dsys_dir_entry entry;
        struct _finddata_t data;
        intptr_t handle;
        char pattern[260];
        size_t len = strlen(path);
        if (len + 3u >= sizeof(pattern)) {
            return 0;
        }
        memcpy(pattern, path, len);
        if (len == 0u || (pattern[len - 1u] != '/' && pattern[len - 1u] != '\\')) {
            pattern[len] = '\\';
            len += 1u;
        }
        pattern[len] = '*';
        pattern[len + 1u] = '\0';
        handle = _findfirst(pattern, &data);
        if (handle == -1) {
            return 0;
        }
        do {
            if (strcmp(data.name, ".") == 0 || strcmp(data.name, "..") == 0) {
                continue;
            }
            memset(&entry, 0, sizeof(entry));
            strncpy(entry.name, data.name, sizeof(entry.name) - 1u);
            entry.name[sizeof(entry.name) - 1u] = '\0';
            entry.is_dir = (data.attrib & _A_SUBDIR) != 0 ? true : false;
            if (!dsys_dir_push_entry(&entries, &count, &cap, &entry)) {
                _findclose(handle);
                free(entries);
                return 0;
            }
        } while (_findnext(handle, &data) == 0);
        _findclose(handle);
    }
#else
    {
        DIR* dir = opendir(path);
        if (!dir) {
            return 0;
        }
        while (1) {
            struct dirent* ent = readdir(dir);
            dsys_dir_entry entry;
            struct stat st;
            char full_path[260];
            size_t base_len;
            size_t name_len;
            if (!ent) {
                break;
            }
            if (strcmp(ent->d_name, ".") == 0 || strcmp(ent->d_name, "..") == 0) {
                continue;
            }
            memset(&entry, 0, sizeof(entry));
            strncpy(entry.name, ent->d_name, sizeof(entry.name) - 1u);
            entry.name[sizeof(entry.name) - 1u] = '\0';
            entry.is_dir = false;
            base_len = strlen(path);
            name_len = strlen(entry.name);
            if (base_len + name_len + 2u < sizeof(full_path)) {
                memcpy(full_path, path, base_len);
                if (base_len > 0u && full_path[base_len - 1u] != '/') {
                    full_path[base_len] = '/';
                    base_len += 1u;
                }
                memcpy(full_path + base_len, entry.name, name_len);
                full_path[base_len + name_len] = '\0';
                if (stat(full_path, &st) == 0 && S_ISDIR(st.st_mode)) {
                    entry.is_dir = true;
                }
            }
            if (!dsys_dir_push_entry(&entries, &count, &cap, &entry)) {
                closedir(dir);
                free(entries);
                return 0;
            }
        }
        closedir(dir);
    }
#endif

    if (count > 1u) {
        qsort(entries, (size_t)count, sizeof(dsys_dir_entry), dsys_dir_entry_cmp);
    }

    if (out_entries) {
        *out_entries = entries;
    } else if (entries) {
        free(entries);
        return 0;
    }
    if (out_count) {
        *out_count = count;
    }
    return 1;
}

bool dsys_dir_next_sorted(dsys_dir_iter* it, dsys_dir_entry* out)
{
    if (!it || !out) {
        return false;
    }
    if (!it->entries || it->entry_index >= it->entry_count) {
        return false;
    }
    *out = it->entries[it->entry_index++];
    return true;
}

void dsys_dir_free_sorted(dsys_dir_iter* it)
{
    if (!it) {
        return;
    }
    if (it->entries) {
        free(it->entries);
        it->entries = NULL;
    }
    it->entry_count = 0u;
    it->entry_index = 0u;
}
