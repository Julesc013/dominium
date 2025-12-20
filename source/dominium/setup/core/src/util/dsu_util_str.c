/*
FILE: source/dominium/setup/core/src/util/dsu_util_str.c
MODULE: Dominium Setup
PURPOSE: ASCII-only string helpers for deterministic parsing and ordering.
*/
#include "dsu_util_internal.h"

#include <string.h>

dsu_u32 dsu__strlen(const char *s) {
    size_t n;
    if (!s) {
        return 0u;
    }
    n = strlen(s);
    if (n > 0xFFFFFFFFu) {
        return 0xFFFFFFFFu;
    }
    return (dsu_u32)n;
}

char *dsu__strdup(const char *s) {
    dsu_u32 n;
    char *out;
    if (!s) {
        return NULL;
    }
    n = dsu__strlen(s);
    if (n == 0xFFFFFFFFu) {
        return NULL;
    }
    out = (char *)dsu__malloc(n + 1u);
    if (!out) {
        return NULL;
    }
    if (n) {
        memcpy(out, s, (size_t)n);
    }
    out[n] = '\0';
    return out;
}

int dsu__streq(const char *a, const char *b) {
    if (a == b) {
        return 1;
    }
    if (!a || !b) {
        return 0;
    }
    return strcmp(a, b) == 0;
}

int dsu__strcmp_bytes(const char *a, const char *b) {
    const unsigned char *pa;
    const unsigned char *pb;
    unsigned char ca;
    unsigned char cb;
    if (a == b) {
        return 0;
    }
    if (!a) {
        return -1;
    }
    if (!b) {
        return 1;
    }
    pa = (const unsigned char *)a;
    pb = (const unsigned char *)b;
    for (;;) {
        ca = *pa++;
        cb = *pb++;
        if (ca != cb) {
            return (ca < cb) ? -1 : 1;
        }
        if (ca == 0u) {
            return 0;
        }
    }
}

int dsu__is_ascii_printable(const char *s) {
    const unsigned char *p;
    unsigned char c;
    if (!s) {
        return 0;
    }
    p = (const unsigned char *)s;
    while ((c = *p++) != 0u) {
        if (c < 0x20u || c > 0x7Eu) {
            return 0;
        }
    }
    return 1;
}

int dsu__is_ascii_id(const char *s) {
    const unsigned char *p;
    unsigned char c;
    if (!s || s[0] == '\0') {
        return 0;
    }
    p = (const unsigned char *)s;
    while ((c = *p++) != 0u) {
        if (c >= 'a' && c <= 'z') {
            continue;
        }
        if (c >= '0' && c <= '9') {
            continue;
        }
        if (c == '_' || c == '-' || c == '.') {
            continue;
        }
        return 0;
    }
    return 1;
}

dsu_status_t dsu__ascii_to_lower_inplace(char *s) {
    unsigned char *p;
    unsigned char c;
    if (!s) {
        return DSU_STATUS_INVALID_ARGS;
    }
    p = (unsigned char *)s;
    while ((c = *p) != 0u) {
        if (c > 0x7Fu) {
            return DSU_STATUS_PARSE_ERROR;
        }
        if (c >= 'A' && c <= 'Z') {
            *p = (unsigned char)(c + ('a' - 'A'));
        }
        ++p;
    }
    return DSU_STATUS_SUCCESS;
}

