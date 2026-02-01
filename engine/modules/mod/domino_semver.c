/*
FILE: source/domino/mod/domino_semver.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / mod/domino_semver
RESPONSIBILITY: Implements `domino_semver`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/version.h"
#include <ctype.h>
#include <stdio.h>
#include <string.h>

static int domino_parse_component(const char* str, int* out_value)
{
    int value = 0;
    const char* p = str;
    int digits = 0;
    if (!str || !out_value) return -1;
    while (*p && *p >= '0' && *p <= '9') {
        value = value * 10 + (*p - '0');
        ++p;
        ++digits;
    }
    if (digits == 0) return -1;
    *out_value = value;
    return (int)(p - str);
}

int domino_semver_parse(const char* str, domino_semver* out)
{
    int len1, len2;
    const char* p;
    if (!str || !out) return -1;
    memset(out, 0, sizeof(*out));
    p = str;
    len1 = domino_parse_component(p, &out->major);
    if (len1 <= 0 || p[len1] != '.') return -1;
    p += len1 + 1;
    len2 = domino_parse_component(p, &out->minor);
    if (len2 <= 0 || p[len2] != '.') return -1;
    p += len2 + 1;
    if (domino_parse_component(p, &out->patch) <= 0) return -1;
    return 0;
}

int domino_semver_compare(const domino_semver* a, const domino_semver* b)
{
    if (!a || !b) return 0;
    if (a->major != b->major) return (a->major < b->major) ? -1 : 1;
    if (a->minor != b->minor) return (a->minor < b->minor) ? -1 : 1;
    if (a->patch != b->patch) return (a->patch < b->patch) ? -1 : 1;
    return 0;
}

int domino_semver_in_range(const domino_semver* v,
                           const domino_semver_range* range)
{
    if (!v || !range) return 0;
    if (range->has_min) {
        if (domino_semver_compare(v, &range->min_version) < 0) return 0;
    }
    if (range->has_max) {
        if (domino_semver_compare(v, &range->max_version) > 0) return 0;
    }
    return 1;
}
