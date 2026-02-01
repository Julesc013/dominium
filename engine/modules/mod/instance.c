/*
FILE: source/domino/mod/instance.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / mod/instance
RESPONSIBILITY: Implements `instance`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/mod.h"
#include <stdio.h>
#include <string.h>

static const char* domino_trim_ws(const char* s)
{
    while (s && *s && (*s == ' ' || *s == '\t' || *s == '\r' || *s == '\n')) {
        ++s;
    }
    return s;
}

static void domino_trim_ws_end(char* s)
{
    int len;
    if (!s) return;
    len = (int)strlen(s);
    while (len > 0) {
        char c = s[len - 1];
        if (c == ' ' || c == '\t' || c == '\r' || c == '\n') {
            s[len - 1] = '\0';
            --len;
        } else {
            break;
        }
    }
}

static int domino_parse_string(const char* line, const char* key,
                               char* out, size_t cap)
{
    const char* p;
    const char* start;
    size_t len;
    if (!line || !key || !out || cap == 0) return 0;
    p = domino_trim_ws(line);
    if (strncmp(p, key, strlen(key)) != 0) return 0;
    p += strlen(key);
    while (*p == ' ' || *p == '\t') ++p;
    if (*p != '=') return 0;
    ++p;
    while (*p == ' ' || *p == '\t') ++p;
    if (*p != '\"') return 0;
    ++p;
    start = p;
    while (*p && *p != '\"') ++p;
    len = (size_t)(p - start);
    if (len >= cap) len = cap - 1;
    strncpy(out, start, len);
    out[len] = '\0';
    return 1;
}

static void domino_parse_string_list(const char* line,
                                     const char* key,
                                     char entries[][64],
                                     unsigned int max_entries,
                                     unsigned int* out_count)
{
    const char* p;
    unsigned int count = 0;
    if (!line || !key || !entries || !out_count) return;
    p = domino_trim_ws(line);
    if (strncmp(p, key, strlen(key)) != 0) return;
    p += strlen(key);
    while (*p == ' ' || *p == '\t') ++p;
    if (*p != '=') return;
    ++p;
    while (*p == ' ' || *p == '\t') ++p;
    if (*p != '[') return;
    ++p;
    while (*p && *p != ']' && count < max_entries) {
        while (*p == ' ' || *p == '\t' || *p == ',') ++p;
        if (*p == '\"') {
            const char* start = ++p;
            size_t len = 0;
            while (*p && *p != '\"') {
                ++p;
            }
            len = (size_t)(p - start);
            if (len >= sizeof(entries[0])) len = sizeof(entries[0]) - 1;
            strncpy(entries[count], start, len);
            entries[count][len] = '\0';
            ++count;
            if (*p == '\"') ++p;
        } else {
            while (*p && *p != ',' && *p != ']') ++p;
        }
    }
    *out_count = count;
}

int domino_instance_load(const char* path, domino_instance_desc* out)
{
    FILE* f;
    char line[256];
    domino_instance_desc inst;
    if (!path || !out) return -1;
    f = fopen(path, "r");
    if (!f) return -1;
    memset(&inst, 0, sizeof(inst));
    while (fgets(line, sizeof(line), f)) {
        domino_trim_ws_end(line);
        domino_parse_string(line, "id", inst.id, sizeof(inst.id));
        domino_parse_string(line, "label", inst.label, sizeof(inst.label));
        domino_parse_string(line, "product_id", inst.product_id, sizeof(inst.product_id));
        if (domino_parse_string(line, "product_version", line, sizeof(line))) {
            domino_semver_parse(line, &inst.product_version);
        }
        domino_parse_string_list(line, "mods", inst.mods_enabled,
                                 DOMINO_MAX_INSTANCE_MODS, &inst.mod_count);
        domino_parse_string_list(line, "packs", inst.packs_enabled,
                                 DOMINO_MAX_INSTANCE_PACKS, &inst.pack_count);
    }
    fclose(f);
    strncpy(inst.root_path, path, sizeof(inst.root_path) - 1);
    inst.root_path[sizeof(inst.root_path) - 1] = '\0';
    *out = inst;
    return 0;
}

int domino_instance_save(const char* path, const domino_instance_desc* inst)
{
    FILE* f;
    unsigned int i;
    if (!path || !inst) return -1;
    f = fopen(path, "w");
    if (!f) return -1;
    fprintf(f, "id = \"%s\"\n", inst->id);
    fprintf(f, "label = \"%s\"\n", inst->label);
    fprintf(f, "product_id = \"%s\"\n", inst->product_id);
    fprintf(f, "product_version = \"%d.%d.%d\"\n",
            inst->product_version.major,
            inst->product_version.minor,
            inst->product_version.patch);
    fprintf(f, "mods = [");
    for (i = 0; i < inst->mod_count; ++i) {
        fprintf(f, "\"%s\"%s", inst->mods_enabled[i],
                (i + 1 < inst->mod_count) ? ", " : "");
    }
    fprintf(f, "]\n");
    fprintf(f, "packs = [");
    for (i = 0; i < inst->pack_count; ++i) {
        fprintf(f, "\"%s\"%s", inst->packs_enabled[i],
                (i + 1 < inst->pack_count) ? ", " : "");
    }
    fprintf(f, "]\n");
    fclose(f);
    return 0;
}

static void domino_set_error(domino_resolve_error* err,
                             const char* prefix,
                             const char* id)
{
    size_t len;
    if (!err || !err->message) return;
    err->message[0] = '\0';
    if (prefix) {
        strncpy(err->message, prefix, sizeof(err->message) - 1);
        err->message[sizeof(err->message) - 1] = '\0';
    }
    len = strlen(err->message);
    if (id && len + 1 < sizeof(err->message)) {
        if (len > 0 && err->message[len - 1] != ' ') {
            err->message[len++] = ' ';
            err->message[len] = '\0';
        }
        strncat(err->message, id, sizeof(err->message) - len - 1);
    }
}

int domino_instance_resolve(domino_package_registry* reg,
                            const domino_instance_desc* inst,
                            domino_resolve_error* out_err)
{
    unsigned int i;
    if (out_err) {
        memset(out_err->message, 0, sizeof(out_err->message));
    }
    if (!reg || !inst) return -1;
    for (i = 0; i < inst->mod_count; ++i) {
        const domino_package_desc* pkg = domino_package_registry_find(reg, inst->mods_enabled[i]);
        if (!pkg) {
            domino_set_error(out_err, "Missing mod:", inst->mods_enabled[i]);
            return -1;
        }
        (void)pkg;
    }
    for (i = 0; i < inst->pack_count; ++i) {
        const domino_package_desc* pkg = domino_package_registry_find(reg, inst->packs_enabled[i]);
        if (!pkg) {
            domino_set_error(out_err, "Missing pack:", inst->packs_enabled[i]);
            return -1;
        }
        (void)pkg;
    }
    return 0;
}
