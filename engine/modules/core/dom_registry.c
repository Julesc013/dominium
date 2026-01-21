/*
FILE: source/domino/core/dom_registry.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/dom_registry
RESPONSIBILITY: Loads deterministic registries from text files.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89 headers.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
DETERMINISM: Sorted, stable key ordering (ASCII lexicographic).
*/
#include "domino/registry.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DOM_REGISTRY_MAX_LINE 512u
#define DOM_REGISTRY_MIN_CAPACITY 16u
#define DOM_REGISTRY_FNV_OFFSET 2166136261u
#define DOM_REGISTRY_FNV_PRIME 16777619u

static int reg_is_ascii_space(char c)
{
    return (c == ' ') || (c == '\t') || (c == '\r') || (c == '\n');
}

static char* reg_trim(char* s)
{
    size_t len;
    char* end;
    if (!s) {
        return s;
    }
    while (*s && reg_is_ascii_space(*s)) {
        ++s;
    }
    len = strlen(s);
    if (len == 0u) {
        return s;
    }
    end = s + len - 1u;
    while (end >= s && reg_is_ascii_space(*end)) {
        *end = '\0';
        if (end == s) {
            break;
        }
        --end;
    }
    return s;
}

static int reg_is_valid_key(const char* s)
{
    const unsigned char* p;
    if (!s || !*s) {
        return 0;
    }
    p = (const unsigned char*)s;
    while (*p) {
        if ((*p >= 'A' && *p <= 'Z') ||
            (*p >= '0' && *p <= '9') ||
            (*p == '_') || (*p == '.')) {
            ++p;
            continue;
        }
        return 0;
    }
    return 1;
}

static int reg_cmp_keys(const char* a, const char* b)
{
    return strcmp(a, b);
}

static void reg_sort_keys(char** keys, u32 count)
{
    u32 i;
    for (i = 1u; i < count; ++i) {
        char* key = keys[i];
        u32 j = i;
        while (j > 0u && reg_cmp_keys(keys[j - 1u], key) > 0) {
            keys[j] = keys[j - 1u];
            --j;
        }
        keys[j] = key;
    }
}

static u32 reg_hash_keys(char** keys, u32 count)
{
    u32 hash = DOM_REGISTRY_FNV_OFFSET;
    u32 i;
    for (i = 0u; i < count; ++i) {
        const unsigned char* p = (const unsigned char*)keys[i];
        while (*p) {
            hash ^= (u32)(*p);
            hash *= DOM_REGISTRY_FNV_PRIME;
            ++p;
        }
        if (i + 1u < count) {
            hash ^= (u32)('\n');
            hash *= DOM_REGISTRY_FNV_PRIME;
        }
    }
    return hash;
}

static void reg_free_keys(char** keys, u32 count)
{
    u32 i;
    if (!keys) {
        return;
    }
    for (i = 0u; i < count; ++i) {
        free(keys[i]);
    }
    free(keys);
}

dom_registry_result dom_registry_load_file(const char* path, dom_registry* out)
{
    FILE* fp;
    char line_buf[DOM_REGISTRY_MAX_LINE];
    char** keys = (char**)0;
    u32 count = 0u;
    u32 capacity = 0u;
    u32 i;

    if (!path || !out) {
        return DOM_REGISTRY_ERR_NULL;
    }

    out->entries = (dom_registry_entry*)0;
    out->count = 0u;
    out->capacity = 0u;
    out->hash = 0u;

    fp = fopen(path, "rb");
    if (!fp) {
        return DOM_REGISTRY_ERR_IO;
    }

    while (fgets(line_buf, sizeof(line_buf), fp)) {
        char* line;
        char* dup;
        size_t len;
        if (strchr(line_buf, '\n') == NULL && !feof(fp)) {
            fclose(fp);
            reg_free_keys(keys, count);
            return DOM_REGISTRY_ERR_FORMAT;
        }

        line = reg_trim(line_buf);
        if (*line == '\0' || *line == '#') {
            continue;
        }
        if (!reg_is_valid_key(line)) {
            fclose(fp);
            reg_free_keys(keys, count);
            return DOM_REGISTRY_ERR_FORMAT;
        }

        len = strlen(line);
        dup = (char*)malloc(len + 1u);
        if (!dup) {
            fclose(fp);
            reg_free_keys(keys, count);
            return DOM_REGISTRY_ERR_OOM;
        }
        memcpy(dup, line, len + 1u);

        for (i = 0u; i < count; ++i) {
            if (strcmp(keys[i], dup) == 0) {
                free(dup);
                fclose(fp);
                reg_free_keys(keys, count);
                return DOM_REGISTRY_ERR_DUPLICATE;
            }
        }

        if (count >= capacity) {
            u32 new_cap = capacity ? (capacity * 2u) : DOM_REGISTRY_MIN_CAPACITY;
            char** next = (char**)realloc(keys, sizeof(char*) * new_cap);
            if (!next) {
                free(dup);
                fclose(fp);
                reg_free_keys(keys, count);
                return DOM_REGISTRY_ERR_OOM;
            }
            keys = next;
            capacity = new_cap;
        }
        keys[count++] = dup;
    }
    fclose(fp);

    if (count == 0u) {
        reg_free_keys(keys, count);
        return DOM_REGISTRY_ERR_EMPTY;
    }

    reg_sort_keys(keys, count);

    out->entries = (dom_registry_entry*)malloc(sizeof(dom_registry_entry) * count);
    if (!out->entries) {
        reg_free_keys(keys, count);
        return DOM_REGISTRY_ERR_OOM;
    }
    out->count = count;
    out->capacity = count;
    out->hash = reg_hash_keys(keys, count);
    for (i = 0u; i < count; ++i) {
        out->entries[i].id = i + 1u;
        out->entries[i].key = keys[i];
    }

    free(keys);
    return DOM_REGISTRY_OK;
}

void dom_registry_free(dom_registry* reg)
{
    u32 i;
    if (!reg || !reg->entries) {
        return;
    }
    for (i = 0u; i < reg->count; ++i) {
        free((void*)reg->entries[i].key);
    }
    free(reg->entries);
    reg->entries = (dom_registry_entry*)0;
    reg->count = 0u;
    reg->capacity = 0u;
    reg->hash = 0u;
}

const dom_registry_entry* dom_registry_find(const dom_registry* reg, const char* key)
{
    u32 i;
    if (!reg || !reg->entries || !key) {
        return (const dom_registry_entry*)0;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (strcmp(reg->entries[i].key, key) == 0) {
            return &reg->entries[i];
        }
    }
    return (const dom_registry_entry*)0;
}

u32 dom_registry_id_from_key(const dom_registry* reg, const char* key)
{
    const dom_registry_entry* entry = dom_registry_find(reg, key);
    return entry ? entry->id : 0u;
}

const char* dom_registry_key_from_id(const dom_registry* reg, u32 id)
{
    if (!reg || !reg->entries || id == 0u || id > reg->count) {
        return (const char*)0;
    }
    return reg->entries[id - 1u].key;
}

u32 dom_registry_hash(const dom_registry* reg)
{
    if (!reg) {
        return 0u;
    }
    return reg->hash;
}

u32 dom_registry_count(const dom_registry* reg)
{
    if (!reg) {
        return 0u;
    }
    return reg->count;
}
