/*
FILE: source/dominium/setup/core/src/state/dsu_state.c
MODULE: Dominium Setup
PURPOSE: Installed-state load/save (Plan S-3; deterministic TLV format).
*/
#include "../../include/dsu/dsu_state.h"

#include "../dsu_ctx_internal.h"
#include "../util/dsu_util_internal.h"

#include <string.h>

#define DSU_STATE_MAGIC_0 'D'
#define DSU_STATE_MAGIC_1 'S'
#define DSU_STATE_MAGIC_2 'U'
#define DSU_STATE_MAGIC_3 'S'

#define DSU_STATE_FORMAT_VERSION 1u
#define DSU_STATE_ROOT_SCHEMA_VERSION 1u

#define DSU_TLV_STATE_ROOT 0x0001u
#define DSU_TLV_STATE_ROOT_VERSION 0x0002u /* u32 */

#define DSU_TLV_STATE_PRODUCT_ID 0x0010u      /* string (ascii id) */
#define DSU_TLV_STATE_PRODUCT_VERSION 0x0011u /* string (semver-ish) */

#define DSU_TLV_STATE_PLATFORM 0x0020u        /* string (platform triple) */
#define DSU_TLV_STATE_SCOPE 0x0021u           /* u8 enum (same as manifest scope) */
#define DSU_TLV_STATE_INSTALL_ROOT 0x0022u    /* string (path, canonical /) */

#define DSU_TLV_STATE_COMPONENT 0x0040u         /* container */
#define DSU_TLV_STATE_COMPONENT_VERSION 0x0041u /* u32 */
#define DSU_TLV_STATE_COMPONENT_ID 0x0042u      /* string (ascii id) */
#define DSU_TLV_STATE_COMPONENT_VERSTR 0x0043u  /* string (semver-ish) */

typedef struct dsu_state_component_t {
    char *id;
    char *version;
} dsu_state_component_t;

struct dsu_state {
    dsu_u32 root_version;
    char *product_id;
    char *product_version;
    char *platform;
    dsu_u8 scope;
    char *install_root;

    dsu_u32 component_count;
    dsu_u32 component_cap;
    dsu_state_component_t *components;
};

static void dsu__state_component_free(dsu_state_component_t *c) {
    if (!c) {
        return;
    }
    dsu__free(c->id);
    dsu__free(c->version);
    c->id = NULL;
    c->version = NULL;
}

static void dsu__state_free(dsu_state_t *s) {
    dsu_u32 i;
    if (!s) {
        return;
    }
    dsu__free(s->product_id);
    dsu__free(s->product_version);
    dsu__free(s->platform);
    dsu__free(s->install_root);
    for (i = 0u; i < s->component_count; ++i) {
        dsu__state_component_free(&s->components[i]);
    }
    dsu__free(s->components);
    s->components = NULL;
    s->component_count = 0u;
    s->component_cap = 0u;
}

static int dsu__bytes_contains_nul(const dsu_u8 *bytes, dsu_u32 len) {
    dsu_u32 i;
    if (!bytes) {
        return 0;
    }
    for (i = 0u; i < len; ++i) {
        if (bytes[i] == 0u) {
            return 1;
        }
    }
    return 0;
}

static dsu_status_t dsu__dup_bytes_cstr(const dsu_u8 *bytes, dsu_u32 len, char **out_str) {
    char *s;
    if (!out_str) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_str = NULL;
    if (!bytes && len != 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (dsu__bytes_contains_nul(bytes, len)) {
        return DSU_STATUS_PARSE_ERROR;
    }
    s = (char *)dsu__malloc(len + 1u);
    if (!s) {
        return DSU_STATUS_IO_ERROR;
    }
    if (len) {
        memcpy(s, bytes, (size_t)len);
    }
    s[len] = '\0';
    *out_str = s;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__read_tlv_u8(const dsu_u8 *v, dsu_u32 len, dsu_u8 *out) {
    dsu_u32 off = 0u;
    if (!v || !out) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (len != 1u) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    return dsu__read_u8(v, len, &off, out);
}

static dsu_status_t dsu__read_tlv_u32(const dsu_u8 *v, dsu_u32 len, dsu_u32 *out) {
    dsu_u32 off = 0u;
    if (!v || !out) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (len != 4u) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    return dsu__read_u32le(v, len, &off, out);
}

static int dsu__is_platform_triple(const char *s) {
    const char *dash;
    dsu_u32 os_len;
    char os[16];
    const char *arch;
    dsu_u32 i;
    if (!s || s[0] == '\0') {
        return 0;
    }
    if (!dsu__is_ascii_printable(s)) {
        return 0;
    }
    dash = strchr(s, '-');
    if (!dash) {
        return 0;
    }
    os_len = (dsu_u32)(dash - s);
    if (os_len == 0u || os_len >= (dsu_u32)sizeof(os)) {
        return 0;
    }
    for (i = 0u; i < os_len; ++i) {
        os[i] = s[i];
    }
    os[os_len] = '\0';
    arch = dash + 1;
    if (*arch == '\0') {
        return 0;
    }

    if (!((os_len == 5u && memcmp(os, "win32", 5u) == 0) ||
          (os_len == 5u && memcmp(os, "win64", 5u) == 0) ||
          (os_len == 5u && memcmp(os, "linux", 5u) == 0) ||
          (os_len == 5u && memcmp(os, "macos", 5u) == 0) ||
          (os_len == 3u && memcmp(os, "any", 3u) == 0))) {
        return 0;
    }
    if (!(dsu__streq(arch, "x86") || dsu__streq(arch, "x64") || dsu__streq(arch, "arm64") || dsu__streq(arch, "any"))) {
        return 0;
    }
    return 1;
}

static int dsu__is_semverish(const char *s) {
    const unsigned char *p;
    dsu_u32 digits;
    if (!s || s[0] == '\0') {
        return 0;
    }
    if (!dsu__is_ascii_printable(s)) {
        return 0;
    }
    p = (const unsigned char *)s;

    digits = 0u;
    while (*p >= '0' && *p <= '9') {
        ++p;
        ++digits;
    }
    if (digits == 0u || *p != '.') return 0;
    ++p;
    digits = 0u;
    while (*p >= '0' && *p <= '9') {
        ++p;
        ++digits;
    }
    if (digits == 0u || *p != '.') return 0;
    ++p;
    digits = 0u;
    while (*p >= '0' && *p <= '9') {
        ++p;
        ++digits;
    }
    if (digits == 0u) return 0;
    if (*p == '\0') return 1;
    if (*p != '-') return 0;
    ++p;
    if (*p == '\0') return 0;
    while (*p) {
        unsigned char c = *p++;
        if ((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '.' || c == '_' || c == '-') {
            continue;
        }
        return 0;
    }
    return 1;
}

static int dsu__component_cmp(const dsu_state_component_t *a, const dsu_state_component_t *b) {
    return dsu__strcmp_bytes(a ? a->id : NULL, b ? b->id : NULL);
}

static void dsu__sort_components(dsu_state_component_t *items, dsu_u32 count) {
    dsu_u32 i;
    if (!items || count < 2u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dsu_state_component_t key = items[i];
        dsu_u32 j = i;
        while (j > 0u && dsu__component_cmp(&items[j - 1u], &key) > 0) {
            items[j] = items[j - 1u];
            --j;
        }
        items[j] = key;
    }
}

static dsu_status_t dsu__component_push(dsu_state_t *s, const dsu_state_component_t *src) {
    dsu_state_component_t *p;
    dsu_u32 count;
    dsu_u32 cap;
    dsu_u32 new_cap;

    if (!s || !src) {
        return DSU_STATUS_INVALID_ARGS;
    }

    count = s->component_count;
    cap = s->component_cap;
    if (count == cap) {
        new_cap = (cap == 0u) ? 4u : (cap * 2u);
        p = (dsu_state_component_t *)dsu__realloc(s->components, new_cap * (dsu_u32)sizeof(*p));
        if (!p) {
            return DSU_STATUS_IO_ERROR;
        }
        s->components = p;
        s->component_cap = new_cap;
    }

    s->components[count] = *src;
    s->component_count = count + 1u;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__parse_component_container(const dsu_u8 *buf,
                                                  dsu_u32 len,
                                                  dsu_state_component_t *out_c) {
    dsu_u32 off;
    dsu_u32 version;
    dsu_state_component_t c;
    dsu_status_t st;

    if (!buf || !out_c) {
        return DSU_STATUS_INVALID_ARGS;
    }
    memset(&c, 0, sizeof(c));
    off = 0u;
    version = 0u;

    while (off < len) {
        dsu_u16 type;
        dsu_u32 n;
        const dsu_u8 *v;
        st = dsu__tlv_read_header(buf, len, &off, &type, &n);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__state_component_free(&c);
            return st;
        }
        if (off + n > len) {
            dsu__state_component_free(&c);
            return DSU_STATUS_INTEGRITY_ERROR;
        }
        v = buf + off;

        if (type == (dsu_u16)DSU_TLV_STATE_COMPONENT_VERSION) {
            st = dsu__read_tlv_u32(v, n, &version);
        } else if (type == (dsu_u16)DSU_TLV_STATE_COMPONENT_ID) {
            dsu__free(c.id);
            c.id = NULL;
            st = dsu__dup_bytes_cstr(v, n, &c.id);
        } else if (type == (dsu_u16)DSU_TLV_STATE_COMPONENT_VERSTR) {
            dsu__free(c.version);
            c.version = NULL;
            st = dsu__dup_bytes_cstr(v, n, &c.version);
        } else {
            st = DSU_STATUS_SUCCESS;
        }

        if (st != DSU_STATUS_SUCCESS) {
            dsu__state_component_free(&c);
            return st;
        }
        off += n;
    }

    if (version != 1u) {
        dsu__state_component_free(&c);
        return DSU_STATUS_UNSUPPORTED_VERSION;
    }
    if (!c.id || c.id[0] == '\0' || !c.version || c.version[0] == '\0') {
        dsu__state_component_free(&c);
        return DSU_STATUS_PARSE_ERROR;
    }

    *out_c = c;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__canonicalize_and_validate(dsu_state_t *s) {
    dsu_u32 i;
    dsu_status_t st;

    if (!s) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (s->root_version != DSU_STATE_ROOT_SCHEMA_VERSION) {
        return DSU_STATUS_UNSUPPORTED_VERSION;
    }
    if (!s->product_id || !s->product_version || !s->platform || !s->install_root) {
        return DSU_STATUS_PARSE_ERROR;
    }

    st = dsu__ascii_to_lower_inplace(s->product_id);
    if (st != DSU_STATUS_SUCCESS) return DSU_STATUS_PARSE_ERROR;
    st = dsu__ascii_to_lower_inplace(s->platform);
    if (st != DSU_STATUS_SUCCESS) return DSU_STATUS_PARSE_ERROR;

    if (!dsu__is_ascii_id(s->product_id)) {
        return DSU_STATUS_PARSE_ERROR;
    }
    if (!dsu__is_semverish(s->product_version)) {
        return DSU_STATUS_PARSE_ERROR;
    }
    if (!dsu__is_platform_triple(s->platform)) {
        return DSU_STATUS_PARSE_ERROR;
    }
    if (s->scope > (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_SYSTEM) {
        return DSU_STATUS_PARSE_ERROR;
    }
    if (!dsu__is_ascii_printable(s->install_root) || s->install_root[0] == '\0') {
        return DSU_STATUS_PARSE_ERROR;
    }

    for (i = 0u; i < s->component_count; ++i) {
        dsu_state_component_t *c = &s->components[i];
        if (!c->id || !c->version) {
            return DSU_STATUS_PARSE_ERROR;
        }
        st = dsu__ascii_to_lower_inplace(c->id);
        if (st != DSU_STATUS_SUCCESS) return DSU_STATUS_PARSE_ERROR;
        if (!dsu__is_ascii_id(c->id)) {
            return DSU_STATUS_PARSE_ERROR;
        }
        if (!dsu__is_semverish(c->version)) {
            return DSU_STATUS_PARSE_ERROR;
        }
    }

    dsu__sort_components(s->components, s->component_count);
    for (i = 1u; i < s->component_count; ++i) {
        if (dsu__streq(s->components[i - 1u].id, s->components[i].id)) {
            return DSU_STATUS_PARSE_ERROR;
        }
    }
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_state_load_file(dsu_ctx_t *ctx,
                                const char *path,
                                dsu_state_t **out_state) {
    dsu_u8 *file_bytes = NULL;
    dsu_u32 file_len = 0u;
    const dsu_u8 *payload = NULL;
    dsu_u32 payload_len = 0u;
    dsu_state_t *s = NULL;
    dsu_status_t st;
    dsu_u8 magic[4];
    dsu_u32 off;

    if (!ctx || !path || !out_state) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_state = NULL;

    st = dsu__fs_read_all(&ctx->config, path, &file_bytes, &file_len);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    magic[0] = (dsu_u8)DSU_STATE_MAGIC_0;
    magic[1] = (dsu_u8)DSU_STATE_MAGIC_1;
    magic[2] = (dsu_u8)DSU_STATE_MAGIC_2;
    magic[3] = (dsu_u8)DSU_STATE_MAGIC_3;

    st = dsu__file_unwrap_payload(file_bytes,
                                  file_len,
                                  magic,
                                  (dsu_u16)DSU_STATE_FORMAT_VERSION,
                                  &payload,
                                  &payload_len);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(file_bytes);
        return st;
    }

    s = (dsu_state_t *)dsu__malloc((dsu_u32)sizeof(*s));
    if (!s) {
        dsu__free(file_bytes);
        return DSU_STATUS_IO_ERROR;
    }
    memset(s, 0, sizeof(*s));

    off = 0u;
    while (off < payload_len) {
        dsu_u16 type;
        dsu_u32 n;
        const dsu_u8 *v;
        st = dsu__tlv_read_header(payload, payload_len, &off, &type, &n);
        if (st != DSU_STATUS_SUCCESS) break;
        if (off + n > payload_len) {
            st = DSU_STATUS_INTEGRITY_ERROR;
            break;
        }
        v = payload + off;

        if (type == (dsu_u16)DSU_TLV_STATE_ROOT) {
            dsu_u32 roff = 0u;
            while (roff < n) {
                dsu_u16 t2;
                dsu_u32 n2;
                const dsu_u8 *v2;
                st = dsu__tlv_read_header(v, n, &roff, &t2, &n2);
                if (st != DSU_STATUS_SUCCESS) break;
                if (roff + n2 > n) {
                    st = DSU_STATUS_INTEGRITY_ERROR;
                    break;
                }
                v2 = v + roff;

                if (t2 == (dsu_u16)DSU_TLV_STATE_ROOT_VERSION) {
                    st = dsu__read_tlv_u32(v2, n2, &s->root_version);
                } else if (t2 == (dsu_u16)DSU_TLV_STATE_PRODUCT_ID) {
                    dsu__free(s->product_id);
                    s->product_id = NULL;
                    st = dsu__dup_bytes_cstr(v2, n2, &s->product_id);
                } else if (t2 == (dsu_u16)DSU_TLV_STATE_PRODUCT_VERSION) {
                    dsu__free(s->product_version);
                    s->product_version = NULL;
                    st = dsu__dup_bytes_cstr(v2, n2, &s->product_version);
                } else if (t2 == (dsu_u16)DSU_TLV_STATE_PLATFORM) {
                    dsu__free(s->platform);
                    s->platform = NULL;
                    st = dsu__dup_bytes_cstr(v2, n2, &s->platform);
                } else if (t2 == (dsu_u16)DSU_TLV_STATE_SCOPE) {
                    st = dsu__read_tlv_u8(v2, n2, &s->scope);
                } else if (t2 == (dsu_u16)DSU_TLV_STATE_INSTALL_ROOT) {
                    dsu__free(s->install_root);
                    s->install_root = NULL;
                    st = dsu__dup_bytes_cstr(v2, n2, &s->install_root);
                } else if (t2 == (dsu_u16)DSU_TLV_STATE_COMPONENT) {
                    dsu_state_component_t c;
                    memset(&c, 0, sizeof(c));
                    st = dsu__parse_component_container(v2, n2, &c);
                    if (st == DSU_STATUS_SUCCESS) {
                        st = dsu__component_push(s, &c);
                        if (st != DSU_STATUS_SUCCESS) {
                            dsu__state_component_free(&c);
                        }
                    }
                } else {
                    st = DSU_STATUS_SUCCESS;
                }

                if (st != DSU_STATUS_SUCCESS) break;
                roff += n2;
            }
        } else {
            st = DSU_STATUS_SUCCESS;
        }

        if (st != DSU_STATUS_SUCCESS) break;
        off += n;
    }

    dsu__free(file_bytes);
    file_bytes = NULL;

    if (st == DSU_STATUS_SUCCESS) {
        st = dsu__canonicalize_and_validate(s);
    }
    if (st != DSU_STATUS_SUCCESS) {
        dsu_state_destroy(ctx, s);
        return st;
    }

    *out_state = s;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__blob_put_tlv_u8(dsu_blob_t *b, dsu_u16 type, dsu_u8 v) {
    return dsu__blob_put_tlv(b, type, &v, 1u);
}

static dsu_status_t dsu__blob_put_tlv_u32(dsu_blob_t *b, dsu_u16 type, dsu_u32 v) {
    dsu_u8 tmp[4];
    tmp[0] = (dsu_u8)(v & 0xFFu);
    tmp[1] = (dsu_u8)((v >> 8) & 0xFFu);
    tmp[2] = (dsu_u8)((v >> 16) & 0xFFu);
    tmp[3] = (dsu_u8)((v >> 24) & 0xFFu);
    return dsu__blob_put_tlv(b, type, tmp, 4u);
}

static dsu_status_t dsu__blob_put_tlv_str(dsu_blob_t *b, dsu_u16 type, const char *s) {
    dsu_u32 n;
    if (!s) s = "";
    n = dsu__strlen(s);
    return dsu__blob_put_tlv(b, type, s, n);
}

static void dsu__sort_component_ptrs(dsu_state_component_t **items, dsu_u32 count) {
    dsu_u32 i;
    if (!items || count < 2u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dsu_state_component_t *key = items[i];
        dsu_u32 j = i;
        while (j > 0u && dsu__strcmp_bytes(items[j - 1u]->id, key->id) > 0) {
            items[j] = items[j - 1u];
            --j;
        }
        items[j] = key;
    }
}

dsu_status_t dsu_state_write_file(dsu_ctx_t *ctx,
                                 const dsu_state_t *state,
                                 const char *path) {
    dsu_blob_t root;
    dsu_blob_t payload;
    dsu_blob_t file_bytes;
    dsu_status_t st;
    dsu_u8 magic[4];
    dsu_u32 i;
    dsu_state_component_t **ptrs = NULL;

    if (!ctx || !state || !path || path[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }

    dsu__blob_init(&root);
    dsu__blob_init(&payload);
    dsu__blob_init(&file_bytes);

    st = dsu__blob_put_tlv_u32(&root, (dsu_u16)DSU_TLV_STATE_ROOT_VERSION, DSU_STATE_ROOT_SCHEMA_VERSION);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&root, (dsu_u16)DSU_TLV_STATE_PRODUCT_ID, dsu_state_product_id(state));
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&root, (dsu_u16)DSU_TLV_STATE_PRODUCT_VERSION, dsu_state_product_version(state));
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&root, (dsu_u16)DSU_TLV_STATE_PLATFORM, dsu_state_platform(state));
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&root, (dsu_u16)DSU_TLV_STATE_SCOPE, (dsu_u8)dsu_state_scope(state));
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&root, (dsu_u16)DSU_TLV_STATE_INSTALL_ROOT, dsu_state_install_root(state));
    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(&root);
        dsu__blob_free(&payload);
        dsu__blob_free(&file_bytes);
        return st;
    }

    if (state->component_count != 0u) {
        ptrs = (dsu_state_component_t **)dsu__malloc(state->component_count * (dsu_u32)sizeof(*ptrs));
        if (!ptrs) {
            dsu__blob_free(&root);
            dsu__blob_free(&payload);
            dsu__blob_free(&file_bytes);
            return DSU_STATUS_IO_ERROR;
        }
        for (i = 0u; i < state->component_count; ++i) {
            ptrs[i] = (dsu_state_component_t *)&state->components[i];
        }
        dsu__sort_component_ptrs(ptrs, state->component_count);
    }

    for (i = 0u; i < state->component_count && st == DSU_STATUS_SUCCESS; ++i) {
        dsu_blob_t comp;
        dsu_state_component_t *c = ptrs ? ptrs[i] : (dsu_state_component_t *)&state->components[i];
        dsu__blob_init(&comp);
        st = dsu__blob_put_tlv_u32(&comp, (dsu_u16)DSU_TLV_STATE_COMPONENT_VERSION, 1u);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&comp, (dsu_u16)DSU_TLV_STATE_COMPONENT_ID, c->id ? c->id : "");
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&comp, (dsu_u16)DSU_TLV_STATE_COMPONENT_VERSTR, c->version ? c->version : "");
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv(&root, (dsu_u16)DSU_TLV_STATE_COMPONENT, comp.data, comp.size);
        dsu__blob_free(&comp);
    }
    dsu__free(ptrs);
    ptrs = NULL;
    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(&root);
        dsu__blob_free(&payload);
        dsu__blob_free(&file_bytes);
        return st;
    }

    st = dsu__blob_put_tlv(&payload, (dsu_u16)DSU_TLV_STATE_ROOT, root.data, root.size);
    dsu__blob_free(&root);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(&payload);
        dsu__blob_free(&file_bytes);
        return st;
    }

    magic[0] = (dsu_u8)DSU_STATE_MAGIC_0;
    magic[1] = (dsu_u8)DSU_STATE_MAGIC_1;
    magic[2] = (dsu_u8)DSU_STATE_MAGIC_2;
    magic[3] = (dsu_u8)DSU_STATE_MAGIC_3;

    st = dsu__file_wrap_payload(magic, (dsu_u16)DSU_STATE_FORMAT_VERSION, payload.data, payload.size, &file_bytes);
    dsu__blob_free(&payload);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(&file_bytes);
        return st;
    }

    st = dsu__fs_write_all(path, file_bytes.data, file_bytes.size);
    dsu__blob_free(&file_bytes);
    return st;
}

void dsu_state_destroy(dsu_ctx_t *ctx, dsu_state_t *state) {
    (void)ctx;
    if (!state) {
        return;
    }
    dsu__state_free(state);
    dsu__free(state);
}

const char *dsu_state_product_id(const dsu_state_t *state) {
    if (!state || !state->product_id) {
        return "";
    }
    return state->product_id;
}

const char *dsu_state_product_version(const dsu_state_t *state) {
    if (!state || !state->product_version) {
        return "";
    }
    return state->product_version;
}

const char *dsu_state_platform(const dsu_state_t *state) {
    if (!state || !state->platform) {
        return "";
    }
    return state->platform;
}

dsu_manifest_install_scope_t dsu_state_scope(const dsu_state_t *state) {
    if (!state) {
        return DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    }
    return (dsu_manifest_install_scope_t)state->scope;
}

const char *dsu_state_install_root(const dsu_state_t *state) {
    if (!state || !state->install_root) {
        return "";
    }
    return state->install_root;
}

dsu_u32 dsu_state_component_count(const dsu_state_t *state) {
    if (!state) {
        return 0u;
    }
    return state->component_count;
}

const char *dsu_state_component_id(const dsu_state_t *state, dsu_u32 index) {
    if (!state || index >= state->component_count) {
        return NULL;
    }
    return state->components[index].id;
}

const char *dsu_state_component_version(const dsu_state_t *state, dsu_u32 index) {
    if (!state || index >= state->component_count) {
        return NULL;
    }
    return state->components[index].version;
}
