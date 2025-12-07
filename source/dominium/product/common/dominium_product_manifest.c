#include "dominium/product_manifest.h"
#include <ctype.h>
#include <stdio.h>
#include <string.h>

static const char* dom_trim(const char* s)
{
    while (s && *s && (*s == ' ' || *s == '\t' || *s == '\r' || *s == '\n')) {
        ++s;
    }
    return s;
}

static void dom_trim_end(char* s)
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

static int dom_parse_string(const char* line, const char* key,
                            char* out, size_t cap)
{
    const char* p;
    const char* start;
    size_t len;
    if (!line || !key || !out || cap == 0) return 0;
    p = dom_trim(line);
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

static int dom_parse_int(const char* line, const char* key, int* out_value)
{
    const char* p;
    int value = 0;
    int digits = 0;
    if (!line || !key || !out_value) return 0;
    p = dom_trim(line);
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

int dominium_product_load(const char* path, dominium_product_desc* out)
{
    FILE* f;
    char line[256];
    int in_compat = 0;
    dominium_product_desc desc;

    if (!path || !out) return -1;
    f = fopen(path, "r");
    if (!f) return -1;
    memset(&desc, 0, sizeof(desc));
    while (fgets(line, sizeof(line), f)) {
        dom_trim_end(line);
        if (strncmp(dom_trim(line), "[compat]", 8) == 0) {
            in_compat = 1;
            continue;
        }
        dom_parse_string(line, "id", desc.id, sizeof(desc.id));
        if (dom_parse_string(line, "version", line, sizeof(line))) {
            domino_semver_parse(line, &desc.version);
        }
        if (in_compat) {
            dom_parse_int(line, "content_api", &desc.content_api);
            dom_parse_int(line, "launcher_content_api", &desc.launcher_content_api);
            dom_parse_int(line, "launcher_ext_api", &desc.launcher_ext_api);
        }
    }
    fclose(f);
    *out = desc;
    if (!desc.id[0]) return -1;
    return 0;
}
