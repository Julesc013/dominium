/*
FILE: source/domino/mod/manifest_io.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / mod/manifest_io
RESPONSIBILITY: Implements `manifest_io`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/mod.h"
#include <ctype.h>
#include <stdio.h>
#include <string.h>

static const char* domino_trim(const char* s)
{
    while (s && *s && (*s == ' ' || *s == '\t' || *s == '\r' || *s == '\n')) {
        ++s;
    }
    return s;
}

static void domino_trim_end(char* s)
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

static int domino_parse_string_value(const char* line, const char* key, char* out, size_t cap)
{
    const char* p;
    const char* start;
    size_t len;
    if (!line || !key || !out || cap == 0) return 0;
    p = domino_trim(line);
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

static int domino_parse_int_value(const char* line, const char* key, int* out_value)
{
    const char* p;
    int value = 0;
    int digits = 0;
    if (!line || !key || !out_value) return 0;
    p = domino_trim(line);
    if (strncmp(p, key, strlen(key)) != 0) return 0;
    p += strlen(key);
    while (*p == ' ' || *p == '\t') ++p;
    if (*p != '=') return 0;
    ++p;
    while (*p == ' ' || *p == '\t') ++p;
    while (*p >= '0' && *p <= '9') {
        value = value * 10 + (*p - '0');
        ++p;
        ++digits;
    }
    if (digits == 0) return 0;
    *out_value = value;
    return 1;
}

int domino_manifest_load_from_file(const char* path,
                                   domino_package_desc* out)
{
    FILE* f;
    char line[256];
    domino_package_desc desc;
    if (!path || !out) return -1;
    f = fopen(path, "r");
    if (!f) return -1;
    memset(&desc, 0, sizeof(desc));
    desc.kind = DOMINO_PACKAGE_KIND_UNKNOWN;
    while (fgets(line, sizeof(line), f)) {
        domino_trim_end(line);
        domino_parse_string_value(line, "id", desc.id, sizeof(desc.id));
        if (domino_parse_string_value(line, "version", line, sizeof(line))) {
            domino_semver_parse(line, &desc.version);
        }
        if (domino_parse_string_value(line, "kind", line, sizeof(line))) {
            if (strcmp(line, "mod") == 0) {
                desc.kind = DOMINO_PACKAGE_KIND_MOD;
            } else if (strcmp(line, "pack") == 0) {
                desc.kind = DOMINO_PACKAGE_KIND_PACK;
            }
        }
    }
    fclose(f);
    if (!desc.id[0]) return -1;
    *out = desc;
    return 0;
}
