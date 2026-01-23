/*
FILE: source/domino/ups/d_ups.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ups
RESPONSIBILITY: Implements UPS manifest parsing and registry/capability resolution.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Registry indexing and resolution ordering are deterministic.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/ups.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct dom_ups_pack_internal {
    dom_ups_manifest  manifest;
    u32               precedence;
    u64               manifest_hash;
    dom_capability_id provides_ids[DOM_UPS_MAX_CAPS_PER_PACK];
    dom_capability_id dependency_ids[DOM_UPS_MAX_DEPS_PER_PACK];
} dom_ups_pack_internal;

typedef struct dom_ups_provider_internal {
    dom_capability_id cap_id;
    u32               pack_index;
    u32               precedence;
} dom_ups_provider_internal;

struct dom_ups_registry {
    dom_ups_pack_internal packs[DOM_UPS_MAX_PACKS];
    u32                   pack_count;

    dom_capability_id     provided_ids[DOM_UPS_MAX_CAPABILITIES];
    u32                   provided_count;
    dom_capability_id     required_ids[DOM_UPS_MAX_REQUIREMENTS];
    u32                   required_count;
    dom_capability_id     optional_ids[DOM_UPS_MAX_REQUIREMENTS];
    u32                   optional_count;

    dom_ups_provider_internal providers[DOM_UPS_MAX_PROVIDERS];
    u32                       provider_count;

    dom_ups_fallback_event fallbacks[DOM_UPS_MAX_FALLBACKS];
    u32                    fallback_count;

    dom_compat_decision compat_decision;
    d_bool              has_compat_decision;

    d_bool index_dirty;
};

static void dom_ups_copy_string(char* dst, size_t cap, const char* src)
{
    size_t i = 0u;
    if (!dst || cap == 0u) {
        return;
    }
    if (!src) {
        dst[0] = '\0';
        return;
    }
    while (src[i] != '\0' && i + 1u < cap) {
        dst[i] = src[i];
        ++i;
    }
    dst[i] = '\0';
}

static const char* dom_ups_trim_start(const char* s)
{
    const char* p = s;
    if (!p) {
        return "";
    }
    while (*p && (*p == ' ' || *p == '\t' || *p == '\r' || *p == '\n')) {
        ++p;
    }
    return p;
}

static void dom_ups_trim_end(char* s)
{
    size_t len;
    if (!s) {
        return;
    }
    len = strlen(s);
    while (len > 0u) {
        char c = s[len - 1u];
        if (c == ' ' || c == '\t' || c == '\r' || c == '\n') {
            s[len - 1u] = '\0';
            --len;
        } else {
            break;
        }
    }
}

static char* dom_ups_trim_both(char* s)
{
    char* start = (char*)dom_ups_trim_start(s);
    dom_ups_trim_end(start);
    return start;
}

static int dom_ups_ascii_equal(const char* a, const char* b)
{
    const char* pa = a;
    const char* pb = b;
    if (!pa || !pb) {
        return 0;
    }
    while (*pa && *pb) {
        char ca = (char)tolower((unsigned char)*pa);
        char cb = (char)tolower((unsigned char)*pb);
        if (ca != cb) {
            return 0;
        }
        ++pa;
        ++pb;
    }
    return (*pa == '\0' && *pb == '\0') ? 1 : 0;
}

static int dom_ups_parse_bool(const char* value, d_bool* out_value)
{
    if (!value || !out_value) {
        return 0;
    }
    if (dom_ups_ascii_equal(value, "true") || strcmp(value, "1") == 0) {
        *out_value = D_TRUE;
        return 1;
    }
    if (dom_ups_ascii_equal(value, "false") || strcmp(value, "0") == 0) {
        *out_value = D_FALSE;
        return 1;
    }
    return 0;
}

static int dom_ups_parse_u32(const char* value, u32* out_value)
{
    const char* p = value;
    u32 v = 0u;
    int digits = 0;
    if (!value || !out_value) {
        return 0;
    }
    while (*p && *p >= '0' && *p <= '9') {
        v = v * 10u + (u32)(*p - '0');
        ++p;
        ++digits;
    }
    if (digits == 0) {
        return 0;
    }
    *out_value = v;
    return 1;
}

static int dom_ups_parse_string(const char* value, char* out, size_t cap)
{
    const char* start = value;
    const char* end;
    size_t len;
    if (!value || !out || cap == 0u) {
        return 0;
    }
    if (start[0] == '"') {
        start += 1;
        end = strchr(start, '"');
        if (!end) {
            return 0;
        }
    } else {
        end = start + strlen(start);
    }
    len = (size_t)(end - start);
    if (len >= cap) {
        len = cap - 1u;
    }
    strncpy(out, start, len);
    out[len] = '\0';
    return 1;
}

static int dom_ups_parse_cap_list(const char* value,
                                  char out[][DOM_UPS_MAX_CAP_ID],
                                  u32 max_out,
                                  u32* out_count)
{
    const char* p = value;
    u32 count = 0u;
    if (!value || !out || !out_count) {
        return 0;
    }
    while (*p) {
        const char* start;
        const char* end;
        size_t len;
        while (*p && (*p == ' ' || *p == '\t' || *p == ',')) {
            ++p;
        }
        if (!*p) {
            break;
        }
        start = p;
        if (*start == '"') {
            start += 1;
            end = strchr(start, '"');
            if (!end) {
                return 0;
            }
            p = end + 1;
        } else {
            end = start;
            while (*end && *end != ',') {
                ++end;
            }
            p = end;
        }
        while (end > start && (*(end - 1) == ' ' || *(end - 1) == '\t')) {
            --end;
        }
        len = (size_t)(end - start);
        if (len == 0u) {
            continue;
        }
        if (count >= max_out) {
            return 0;
        }
        if (len >= DOM_UPS_MAX_CAP_ID) {
            len = DOM_UPS_MAX_CAP_ID - 1u;
        }
        strncpy(out[count], start, len);
        out[count][len] = '\0';
        count += 1u;
    }
    *out_count = count;
    return 1;
}

static int dom_ups_parse_protocol_list(const char* value,
                                       dom_ups_protocol_requirement* out,
                                       u32 max_out,
                                       u32* out_count)
{
    const char* p = value;
    u32 count = 0u;
    if (!value || !out || !out_count) {
        return 0;
    }
    while (*p) {
        const char* start;
        const char* end;
        const char* sep;
        size_t len;
        u32 ver;
        while (*p && (*p == ' ' || *p == '\t' || *p == ',')) {
            ++p;
        }
        if (!*p) {
            break;
        }
        start = p;
        end = start;
        while (*end && *end != ',') {
            ++end;
        }
        p = end;
        while (end > start && (*(end - 1) == ' ' || *(end - 1) == '\t')) {
            --end;
        }
        len = (size_t)(end - start);
        if (len == 0u) {
            continue;
        }
        if (count >= max_out) {
            return 0;
        }
        sep = memchr(start, ':', len);
        if (!sep) {
            sep = memchr(start, '=', len);
        }
        if (!sep) {
            return 0;
        }
        if ((size_t)(sep - start) >= DOM_UPS_MAX_PROTOCOL_ID) {
            return 0;
        }
        strncpy(out[count].protocol_id, start, (size_t)(sep - start));
        out[count].protocol_id[sep - start] = '\0';
        if (!dom_ups_parse_u32(sep + 1, &ver)) {
            return 0;
        }
        out[count].version = ver;
        count += 1u;
    }
    *out_count = count;
    return 1;
}

static void dom_ups_set_error(dom_ups_manifest_error* out_error,
                              dom_ups_manifest_error_code code,
                              u32 line,
                              const char* message)
{
    if (!out_error) {
        return;
    }
    out_error->code = code;
    out_error->line = line;
    dom_ups_copy_string(out_error->message, sizeof(out_error->message), message);
}

static int dom_ups_is_pack_id_valid(const char* id)
{
    size_t i;
    int has_dot = 0;
    if (!id || !id[0]) {
        return 0;
    }
    if (id[0] == '.' || id[strlen(id) - 1u] == '.') {
        return 0;
    }
    for (i = 0u; id[i] != '\0'; ++i) {
        char c = id[i];
        if (c == '.') {
            has_dot = 1;
            continue;
        }
        if (c == '-' || c == '_' || (c >= '0' && c <= '9') ||
            (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')) {
            continue;
        }
        return 0;
    }
    return has_dot;
}

void dom_ups_manifest_init(dom_ups_manifest* out_manifest)
{
    if (!out_manifest) {
        return;
    }
    memset(out_manifest, 0, sizeof(*out_manifest));
    out_manifest->optional = D_FALSE;
    out_manifest->has_pack_version = D_FALSE;
    out_manifest->has_required_engine_version = D_FALSE;
}

static int dom_ups_manifest_parse_line(dom_ups_manifest* manifest,
                                       char* line,
                                       u32 line_no,
                                       dom_ups_manifest_error* out_error)
{
    char* eq;
    char* key;
    char* value;
    char* trimmed;
    if (!manifest || !line) {
        return 1;
    }
    dom_ups_trim_end(line);
    trimmed = dom_ups_trim_both(line);
    if (trimmed[0] == '\0') {
        return 0;
    }
    if (trimmed[0] == '#' || trimmed[0] == ';') {
        return 0;
    }
    eq = strchr(trimmed, '=');
    if (!eq) {
        return 0;
    }
    *eq = '\0';
    key = dom_ups_trim_both(trimmed);
    value = dom_ups_trim_both(eq + 1);
    if (key[0] == '\0' || value[0] == '\0') {
        return 0;
    }
    if (strcmp(key, "pack_id") == 0) {
        if (!dom_ups_parse_string(value, manifest->pack_id, sizeof(manifest->pack_id))) {
            dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_INVALID, line_no, "Invalid pack_id");
            return 1;
        }
        return 0;
    }
    if (strcmp(key, "pack_version") == 0) {
        char buf[32];
        if (!dom_ups_parse_string(value, buf, sizeof(buf))) {
            dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_BAD_VERSION, line_no, "Invalid pack_version");
            return 1;
        }
        if (domino_semver_parse(buf, &manifest->pack_version) != 0) {
            dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_BAD_VERSION, line_no, "Invalid pack_version");
            return 1;
        }
        manifest->has_pack_version = D_TRUE;
        return 0;
    }
    if (strcmp(key, "pack_format_version") == 0) {
        u32 v = 0u;
        if (!dom_ups_parse_u32(value, &v)) {
            dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_BAD_VERSION, line_no, "Invalid pack_format_version");
            return 1;
        }
        manifest->pack_format_version = v;
        return 0;
    }
    if (strcmp(key, "required_engine_version") == 0) {
        char buf[32];
        if (!dom_ups_parse_string(value, buf, sizeof(buf))) {
            dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_BAD_VERSION, line_no, "Invalid required_engine_version");
            return 1;
        }
        if (domino_semver_parse(buf, &manifest->required_engine_version) != 0) {
            dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_BAD_VERSION, line_no, "Invalid required_engine_version");
            return 1;
        }
        manifest->has_required_engine_version = D_TRUE;
        return 0;
    }
    if (strcmp(key, "required_protocols") == 0) {
        u32 count = 0u;
        if (!dom_ups_parse_protocol_list(value, manifest->required_protocols,
                                         DOM_UPS_MAX_PROTOCOLS, &count)) {
            dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_BAD_PROTOCOL, line_no, "Invalid required_protocols");
            return 1;
        }
        manifest->required_protocol_count = count;
        return 0;
    }
    if (strcmp(key, "provides") == 0) {
        u32 count = 0u;
        if (!dom_ups_parse_cap_list(value, manifest->provides,
                                    DOM_UPS_MAX_CAPS_PER_PACK, &count)) {
            dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_BAD_CAPABILITY, line_no, "Invalid provides");
            return 1;
        }
        manifest->provides_count = count;
        return 0;
    }
    if (strcmp(key, "dependencies") == 0) {
        u32 count = 0u;
        if (!dom_ups_parse_cap_list(value, manifest->dependencies,
                                    DOM_UPS_MAX_DEPS_PER_PACK, &count)) {
            dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_BAD_CAPABILITY, line_no, "Invalid dependencies");
            return 1;
        }
        manifest->dependency_count = count;
        return 0;
    }
    if (strcmp(key, "optional") == 0) {
        d_bool flag = D_FALSE;
        if (!dom_ups_parse_bool(value, &flag)) {
            dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_INVALID, line_no, "Invalid optional flag");
            return 1;
        }
        manifest->optional = flag;
        return 0;
    }
    return 0;
}

int dom_ups_manifest_parse_text(const char* text,
                                dom_ups_manifest* out_manifest,
                                dom_ups_manifest_error* out_error)
{
    const char* p;
    char line[512];
    u32 line_no = 0u;
    size_t len = 0u;
    if (out_error) {
        memset(out_error, 0, sizeof(*out_error));
        out_error->code = DOM_UPS_MANIFEST_OK;
    }
    if (!text || !out_manifest) {
        dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_INVALID, 0u, "Null input");
        return -1;
    }
    dom_ups_manifest_init(out_manifest);
    p = text;
    while (*p) {
        len = 0u;
        while (p[len] && p[len] != '\n' && p[len] != '\r' && len + 1u < sizeof(line)) {
            line[len] = p[len];
            len += 1u;
        }
        line[len] = '\0';
        line_no += 1u;
        if (dom_ups_manifest_parse_line(out_manifest, line, line_no, out_error) != 0) {
            return -2;
        }
        while (*p && *p != '\n' && *p != '\r') {
            ++p;
        }
        if (*p == '\r') {
            ++p;
        }
        if (*p == '\n') {
            ++p;
        }
    }
    return 0;
}

int dom_ups_manifest_parse_file(const char* path,
                                dom_ups_manifest* out_manifest,
                                dom_ups_manifest_error* out_error)
{
    FILE* f;
    char line[512];
    u32 line_no = 0u;
    if (out_error) {
        memset(out_error, 0, sizeof(*out_error));
        out_error->code = DOM_UPS_MANIFEST_OK;
    }
    if (!path || !out_manifest) {
        dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_INVALID, 0u, "Null input");
        return -1;
    }
    f = fopen(path, "r");
    if (!f) {
        dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_INVALID, 0u, "Failed to open file");
        return -2;
    }
    dom_ups_manifest_init(out_manifest);
    while (fgets(line, sizeof(line), f)) {
        line_no += 1u;
        if (dom_ups_manifest_parse_line(out_manifest, line, line_no, out_error) != 0) {
            fclose(f);
            return -3;
        }
    }
    fclose(f);
    return 0;
}

int dom_ups_manifest_validate(const dom_ups_manifest* manifest,
                              dom_ups_manifest_error* out_error)
{
    u32 i;
    if (out_error) {
        memset(out_error, 0, sizeof(*out_error));
        out_error->code = DOM_UPS_MANIFEST_OK;
    }
    if (!manifest) {
        dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_INVALID, 0u, "Null manifest");
        return 0;
    }
    if (!manifest->pack_id[0] || !dom_ups_is_pack_id_valid(manifest->pack_id)) {
        dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_MISSING_FIELD, 0u, "Missing or invalid pack_id");
        return 0;
    }
    if (!manifest->has_pack_version) {
        dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_MISSING_FIELD, 0u, "Missing pack_version");
        return 0;
    }
    if (manifest->pack_format_version == 0u) {
        dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_MISSING_FIELD, 0u, "Missing pack_format_version");
        return 0;
    }
    if (!manifest->has_required_engine_version) {
        dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_MISSING_FIELD, 0u, "Missing required_engine_version");
        return 0;
    }
    for (i = 0u; i < manifest->required_protocol_count; ++i) {
        if (!manifest->required_protocols[i].protocol_id[0] ||
            manifest->required_protocols[i].version == 0u) {
            dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_BAD_PROTOCOL, 0u, "Invalid required_protocols entry");
            return 0;
        }
    }
    return 1;
}

static dom_capability_id dom_ups_hash_capability(const char* key)
{
    u64 hash = (u64)0xcbf29ce484222325ULL;
    const unsigned char* p = (const unsigned char*)key;
    if (!key) {
        return 0u;
    }
    while (*p) {
        hash ^= (u64)(*p++);
        hash *= (u64)0x100000001b3ULL;
    }
    return (dom_capability_id)hash;
}

static void dom_ups_registry_mark_dirty(dom_ups_registry* reg)
{
    if (!reg) {
        return;
    }
    reg->index_dirty = D_TRUE;
}

static void dom_ups_sort_u64(dom_capability_id* ids, u32 count)
{
    u32 i;
    u32 j;
    if (!ids) {
        return;
    }
    for (i = 0u; i + 1u < count; ++i) {
        for (j = i + 1u; j < count; ++j) {
            if (ids[j] < ids[i]) {
                dom_capability_id tmp = ids[i];
                ids[i] = ids[j];
                ids[j] = tmp;
            }
        }
    }
}

static u32 dom_ups_unique_u64(dom_capability_id* ids, u32 count)
{
    u32 i;
    u32 out = 0u;
    if (!ids || count == 0u) {
        return 0u;
    }
    for (i = 0u; i < count; ++i) {
        if (out == 0u || ids[i] != ids[out - 1u]) {
            ids[out++] = ids[i];
        }
    }
    return out;
}

static int dom_ups_provider_compare(const dom_ups_registry* reg,
                                    const dom_ups_provider_internal* a,
                                    const dom_ups_provider_internal* b)
{
    const dom_ups_pack_internal* pack_a;
    const dom_ups_pack_internal* pack_b;
    int cmp;
    if (a->cap_id < b->cap_id) {
        return -1;
    }
    if (a->cap_id > b->cap_id) {
        return 1;
    }
    if (a->precedence > b->precedence) {
        return -1;
    }
    if (a->precedence < b->precedence) {
        return 1;
    }
    pack_a = &reg->packs[a->pack_index];
    pack_b = &reg->packs[b->pack_index];
    cmp = strcmp(pack_a->manifest.pack_id, pack_b->manifest.pack_id);
    if (cmp != 0) {
        return cmp;
    }
    cmp = domino_semver_compare(&pack_a->manifest.pack_version, &pack_b->manifest.pack_version);
    if (cmp != 0) {
        return -cmp;
    }
    if (a->pack_index < b->pack_index) {
        return -1;
    }
    if (a->pack_index > b->pack_index) {
        return 1;
    }
    return 0;
}

static void dom_ups_registry_build_index(dom_ups_registry* reg)
{
    u32 i;
    u32 j;
    if (!reg) {
        return;
    }
    reg->provider_count = 0u;
    reg->provided_count = 0u;
    reg->required_count = 0u;
    reg->optional_count = 0u;

    for (i = 0u; i < reg->pack_count; ++i) {
        dom_ups_pack_internal* pack = &reg->packs[i];
        for (j = 0u; j < pack->manifest.provides_count; ++j) {
            if (reg->provider_count < DOM_UPS_MAX_PROVIDERS) {
                reg->providers[reg->provider_count].cap_id = pack->provides_ids[j];
                reg->providers[reg->provider_count].pack_index = i;
                reg->providers[reg->provider_count].precedence = pack->precedence;
                reg->provider_count += 1u;
            }
            if (reg->provided_count < DOM_UPS_MAX_CAPABILITIES) {
                reg->provided_ids[reg->provided_count++] = pack->provides_ids[j];
            }
        }
        for (j = 0u; j < pack->manifest.dependency_count; ++j) {
            if (pack->manifest.optional) {
                if (reg->optional_count < DOM_UPS_MAX_REQUIREMENTS) {
                    reg->optional_ids[reg->optional_count++] = pack->dependency_ids[j];
                }
            } else {
                if (reg->required_count < DOM_UPS_MAX_REQUIREMENTS) {
                    reg->required_ids[reg->required_count++] = pack->dependency_ids[j];
                }
            }
        }
    }

    for (i = 0u; i + 1u < reg->provider_count; ++i) {
        for (j = i + 1u; j < reg->provider_count; ++j) {
            if (dom_ups_provider_compare(reg, &reg->providers[j], &reg->providers[i]) < 0) {
                dom_ups_provider_internal tmp = reg->providers[i];
                reg->providers[i] = reg->providers[j];
                reg->providers[j] = tmp;
            }
        }
    }

    dom_ups_sort_u64(reg->provided_ids, reg->provided_count);
    reg->provided_count = dom_ups_unique_u64(reg->provided_ids, reg->provided_count);
    dom_ups_sort_u64(reg->required_ids, reg->required_count);
    reg->required_count = dom_ups_unique_u64(reg->required_ids, reg->required_count);
    dom_ups_sort_u64(reg->optional_ids, reg->optional_count);
    reg->optional_count = dom_ups_unique_u64(reg->optional_ids, reg->optional_count);

    reg->index_dirty = D_FALSE;
}

static void dom_ups_registry_ensure_index(dom_ups_registry* reg)
{
    if (!reg || !reg->index_dirty) {
        return;
    }
    dom_ups_registry_build_index(reg);
}

dom_ups_registry* dom_ups_registry_create(void)
{
    dom_ups_registry* reg = (dom_ups_registry*)malloc(sizeof(dom_ups_registry));
    if (!reg) {
        return NULL;
    }
    memset(reg, 0, sizeof(*reg));
    reg->index_dirty = D_TRUE;
    return reg;
}

void dom_ups_registry_destroy(dom_ups_registry* reg)
{
    if (!reg) {
        return;
    }
    free(reg);
}

void dom_ups_registry_clear(dom_ups_registry* reg)
{
    if (!reg) {
        return;
    }
    memset(reg, 0, sizeof(*reg));
    reg->index_dirty = D_TRUE;
}

int dom_ups_registry_add_pack(dom_ups_registry* reg,
                              const dom_ups_manifest* manifest,
                              u32 precedence,
                              u64 manifest_hash,
                              dom_ups_manifest_error* out_error)
{
    u32 i;
    u32 total_provides = 0u;
    u32 total_deps = 0u;
    if (!reg || !manifest) {
        dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_INVALID, 0u, "Null input");
        return -1;
    }
    if (!dom_ups_manifest_validate(manifest, out_error)) {
        return -2;
    }
    if (reg->pack_count >= DOM_UPS_MAX_PACKS) {
        dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_TOO_MANY, 0u, "Too many packs");
        return -3;
    }
    for (i = 0u; i < reg->pack_count; ++i) {
        total_provides += reg->packs[i].manifest.provides_count;
        total_deps += reg->packs[i].manifest.dependency_count;
    }
    total_provides += manifest->provides_count;
    total_deps += manifest->dependency_count;
    if (total_provides > DOM_UPS_MAX_PROVIDERS || total_provides > DOM_UPS_MAX_CAPABILITIES) {
        dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_TOO_MANY, 0u, "Too many provided capabilities");
        return -4;
    }
    if (total_deps > DOM_UPS_MAX_REQUIREMENTS) {
        dom_ups_set_error(out_error, DOM_UPS_MANIFEST_ERR_TOO_MANY, 0u, "Too many dependencies");
        return -5;
    }
    reg->packs[reg->pack_count].manifest = *manifest;
    reg->packs[reg->pack_count].precedence = precedence;
    reg->packs[reg->pack_count].manifest_hash = manifest_hash;
    for (i = 0u; i < manifest->provides_count; ++i) {
        reg->packs[reg->pack_count].provides_ids[i] =
            dom_ups_hash_capability(manifest->provides[i]);
    }
    for (i = 0u; i < manifest->dependency_count; ++i) {
        reg->packs[reg->pack_count].dependency_ids[i] =
            dom_ups_hash_capability(manifest->dependencies[i]);
    }
    reg->pack_count += 1u;
    dom_ups_registry_mark_dirty(reg);
    return 0;
}

u32 dom_ups_registry_pack_count(const dom_ups_registry* reg)
{
    return reg ? reg->pack_count : 0u;
}

int dom_ups_registry_pack_get(const dom_ups_registry* reg,
                              u32 index,
                              dom_ups_pack_entry* out_entry)
{
    if (!reg || !out_entry) {
        return -1;
    }
    if (index >= reg->pack_count) {
        return -2;
    }
    out_entry->manifest = reg->packs[index].manifest;
    out_entry->precedence = reg->packs[index].precedence;
    out_entry->manifest_hash = reg->packs[index].manifest_hash;
    return 0;
}

dom_capability_set_view dom_ups_registry_provided_caps(const dom_ups_registry* reg)
{
    dom_capability_set_view view;
    view.ids = NULL;
    view.count = 0u;
    if (!reg) {
        return view;
    }
    dom_ups_registry_ensure_index((dom_ups_registry*)reg);
    view.ids = reg->provided_ids;
    view.count = reg->provided_count;
    return view;
}

dom_capability_set_view dom_ups_registry_required_caps(const dom_ups_registry* reg)
{
    dom_capability_set_view view;
    view.ids = NULL;
    view.count = 0u;
    if (!reg) {
        return view;
    }
    dom_ups_registry_ensure_index((dom_ups_registry*)reg);
    view.ids = reg->required_ids;
    view.count = reg->required_count;
    return view;
}

dom_capability_set_view dom_ups_registry_optional_caps(const dom_ups_registry* reg)
{
    dom_capability_set_view view;
    view.ids = NULL;
    view.count = 0u;
    if (!reg) {
        return view;
    }
    dom_ups_registry_ensure_index((dom_ups_registry*)reg);
    view.ids = reg->optional_ids;
    view.count = reg->optional_count;
    return view;
}

static int dom_ups_fill_provider_entry(const dom_ups_registry* reg,
                                       const dom_ups_provider_internal* provider,
                                       const char* capability_id,
                                       dom_ups_provider_entry* out_entry)
{
    const dom_ups_pack_internal* pack;
    if (!reg || !provider || !out_entry || !capability_id) {
        return -1;
    }
    pack = &reg->packs[provider->pack_index];
    dom_ups_copy_string(out_entry->capability_id,
                        sizeof(out_entry->capability_id),
                        capability_id);
    dom_ups_copy_string(out_entry->pack_id,
                        sizeof(out_entry->pack_id),
                        pack->manifest.pack_id);
    out_entry->pack_version = pack->manifest.pack_version;
    out_entry->precedence = provider->precedence;
    return 0;
}

int dom_ups_registry_resolve_capability(const dom_ups_registry* reg,
                                        const char* capability_id,
                                        dom_ups_provider_entry* out_entry)
{
    dom_capability_id cap_id;
    u32 i;
    if (!reg || !capability_id || !out_entry) {
        return -1;
    }
    dom_ups_registry_ensure_index((dom_ups_registry*)reg);
    cap_id = dom_ups_hash_capability(capability_id);
    for (i = 0u; i < reg->provider_count; ++i) {
        if (reg->providers[i].cap_id == cap_id) {
            return dom_ups_fill_provider_entry(reg, &reg->providers[i], capability_id, out_entry);
        }
    }
    return -2;
}

u32 dom_ups_registry_list_providers(const dom_ups_registry* reg,
                                    const char* capability_id,
                                    dom_ups_provider_entry* out_entries,
                                    u32 max_out)
{
    dom_capability_id cap_id;
    u32 i;
    u32 count = 0u;
    if (!reg || !capability_id || !out_entries || max_out == 0u) {
        return 0u;
    }
    dom_ups_registry_ensure_index((dom_ups_registry*)reg);
    cap_id = dom_ups_hash_capability(capability_id);
    for (i = 0u; i < reg->provider_count && count < max_out; ++i) {
        if (reg->providers[i].cap_id == cap_id) {
            if (dom_ups_fill_provider_entry(reg, &reg->providers[i],
                                            capability_id, &out_entries[count]) == 0) {
                count += 1u;
            }
        }
    }
    return count;
}

int dom_ups_registry_report_fallback(dom_ups_registry* reg,
                                     const char* capability_id,
                                     const char* fallback_id,
                                     const char* reason)
{
    dom_ups_fallback_event* evt;
    if (!reg || !capability_id || !fallback_id) {
        return -1;
    }
    if (reg->fallback_count >= DOM_UPS_MAX_FALLBACKS) {
        return -2;
    }
    evt = &reg->fallbacks[reg->fallback_count++];
    dom_ups_copy_string(evt->capability_id, sizeof(evt->capability_id), capability_id);
    dom_ups_copy_string(evt->fallback_id, sizeof(evt->fallback_id), fallback_id);
    dom_ups_copy_string(evt->reason, sizeof(evt->reason), reason ? reason : "");
    return 0;
}

u32 dom_ups_registry_fallback_count(const dom_ups_registry* reg)
{
    return reg ? reg->fallback_count : 0u;
}

int dom_ups_registry_fallback_get(const dom_ups_registry* reg,
                                  u32 index,
                                  dom_ups_fallback_event* out_event)
{
    if (!reg || !out_event) {
        return -1;
    }
    if (index >= reg->fallback_count) {
        return -2;
    }
    *out_event = reg->fallbacks[index];
    return 0;
}

void dom_ups_registry_set_compat_decision(dom_ups_registry* reg,
                                          dom_compat_decision decision)
{
    if (!reg) {
        return;
    }
    reg->compat_decision = decision;
    reg->has_compat_decision = D_TRUE;
}

dom_compat_decision dom_ups_registry_get_compat_decision(const dom_ups_registry* reg)
{
    dom_compat_decision decision;
    decision.mode = DOM_COMPAT_MODE_INCOMPATIBLE;
    decision.missing_required = 0u;
    decision.missing_optional = 0u;
    if (!reg || !reg->has_compat_decision) {
        return decision;
    }
    return reg->compat_decision;
}

d_bool dom_ups_registry_has_compat_decision(const dom_ups_registry* reg)
{
    return (reg && reg->has_compat_decision) ? D_TRUE : D_FALSE;
}
