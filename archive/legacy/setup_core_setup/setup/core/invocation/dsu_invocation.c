/*
FILE: source/dominium/setup/core/src/invocation/dsu_invocation.c
MODULE: Dominium Setup
PURPOSE: Invocation payload load/validate/digest (installer UX contract input).
*/
#include "../../include/dsu/dsu_invocation.h"
#include "../../include/dsu/dsu_plan.h"
#include "../../include/dsu/dsu_resolve.h"

#include "../dsu_ctx_internal.h"
#include "../util/dsu_util_internal.h"

#include <string.h>

#define DSU_INVOCATION_MAGIC_0 'D'
#define DSU_INVOCATION_MAGIC_1 'S'
#define DSU_INVOCATION_MAGIC_2 'U'
#define DSU_INVOCATION_MAGIC_3 'I'

#define DSU_INVOCATION_FORMAT_VERSION 1u

/* TLV schema (v1). */
#define DSU_INVOCATION_TLV_ROOT 0x0100u
#define DSU_INVOCATION_TLV_ROOT_VERSION 0x0101u /* u32 */
#define DSU_INVOCATION_TLV_OPERATION 0x0110u /* u8 */
#define DSU_INVOCATION_TLV_SCOPE 0x0111u /* u8 */
#define DSU_INVOCATION_TLV_PLATFORM_TRIPLE 0x0120u /* string */
#define DSU_INVOCATION_TLV_INSTALL_ROOT 0x0130u /* string (repeatable) */
#define DSU_INVOCATION_TLV_POLICY_FLAGS 0x0140u /* u32 */
#define DSU_INVOCATION_TLV_UI_MODE 0x0150u /* string */
#define DSU_INVOCATION_TLV_FRONTEND_ID 0x0151u /* string */
#define DSU_INVOCATION_TLV_SELECTED_COMPONENT 0x0160u /* string (repeatable) */
#define DSU_INVOCATION_TLV_EXCLUDED_COMPONENT 0x0161u /* string (repeatable) */

#define DSU_INVOCATION_POLICY_ALL (DSU_INVOCATION_POLICY_OFFLINE | \
                                   DSU_INVOCATION_POLICY_DETERMINISTIC | \
                                   DSU_INVOCATION_POLICY_ALLOW_PRERELEASE | \
                                   DSU_INVOCATION_POLICY_LEGACY_MODE | \
                                   DSU_INVOCATION_POLICY_ENABLE_SHORTCUTS | \
                                   DSU_INVOCATION_POLICY_ENABLE_FILE_ASSOC | \
                                   DSU_INVOCATION_POLICY_ENABLE_URL_HANDLERS)

typedef struct dsu__invocation_canon_t {
    dsu_u8 operation;
    dsu_u8 scope;
    dsu_u8 reserved8[2];
    dsu_u32 policy_flags;
    char *platform_triple;
    char *ui_mode;
    char *frontend_id;
    char **install_roots;
    dsu_u32 install_root_count;
    char **selected_components;
    dsu_u32 selected_component_count;
    char **excluded_components;
    dsu_u32 excluded_component_count;
} dsu__invocation_canon_t;

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

static int dsu__is_ascii_ws(dsu_u8 c) {
    return (c == (dsu_u8)' ' || c == (dsu_u8)'\t' || c == (dsu_u8)'\r' ||
            c == (dsu_u8)'\n' || c == (dsu_u8)'\v' || c == (dsu_u8)'\f');
}

static dsu_status_t dsu__trim_dup(const char *s, char **out_trimmed) {
    const char *start;
    const char *end;
    dsu_u32 n;
    dsu_u32 len;
    char *t;
    if (!out_trimmed) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_trimmed = NULL;
    if (!s) {
        return DSU_STATUS_INVALID_REQUEST;
    }
    n = dsu__strlen(s);
    if (n == 0xFFFFFFFFu) {
        return DSU_STATUS_INVALID_REQUEST;
    }
    start = s;
    while (*start && dsu__is_ascii_ws((dsu_u8)*start)) {
        ++start;
    }
    end = s + n;
    while (end > start && dsu__is_ascii_ws((dsu_u8)end[-1])) {
        --end;
    }
    len = (dsu_u32)(end - start);
    t = (char *)dsu__malloc(len + 1u);
    if (!t) {
        return DSU_STATUS_IO_ERROR;
    }
    if (len) {
        memcpy(t, start, (size_t)len);
    }
    t[len] = '\0';
    *out_trimmed = t;
    return DSU_STATUS_SUCCESS;
}

static dsu_u8 dsu__ascii_lower_u8(dsu_u8 c) {
    if (c >= (dsu_u8)'A' && c <= (dsu_u8)'Z') {
        return (dsu_u8)(c - (dsu_u8)'A' + (dsu_u8)'a');
    }
    return c;
}

static int dsu__strcmp_lowercase(const char *a, const char *b) {
    const dsu_u8 *pa;
    const dsu_u8 *pb;
    dsu_u8 ca;
    dsu_u8 cb;
    if (a == b) {
        return 0;
    }
    if (!a) {
        return -1;
    }
    if (!b) {
        return 1;
    }
    pa = (const dsu_u8 *)a;
    pb = (const dsu_u8 *)b;
    for (;;) {
        ca = dsu__ascii_lower_u8(*pa++);
        cb = dsu__ascii_lower_u8(*pb++);
        if (ca != cb) {
            return (ca < cb) ? -1 : 1;
        }
        if (ca == 0u) {
            return 0;
        }
    }
}

static int dsu__cmp_lowercase_then_raw(const char *a, const char *b) {
    int c = dsu__strcmp_lowercase(a, b);
    if (c != 0) {
        return c;
    }
    return dsu__strcmp_bytes(a, b);
}

static void dsu__sort_str_ptrs_casefold(char **items, dsu_u32 count) {
    dsu_u32 i;
    if (!items || count < 2u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        char *key = items[i];
        dsu_u32 j = i;
        while (j > 0u && dsu__cmp_lowercase_then_raw(items[j - 1u], key) > 0) {
            items[j] = items[j - 1u];
            --j;
        }
        items[j] = key;
    }
}

static void dsu__free_str_list(char **items, dsu_u32 count) {
    dsu_u32 i;
    if (!items) {
        return;
    }
    for (i = 0u; i < count; ++i) {
        dsu__free(items[i]);
    }
    dsu__free(items);
}

static dsu_status_t dsu__canon_list(const char *const *items,
                                   dsu_u32 count,
                                   dsu_u8 require_ascii_id,
                                   dsu_u8 lowercase,
                                   dsu_u8 casefold_sort,
                                   char ***out_items,
                                   dsu_u32 *out_count) {
    dsu_u32 i;
    char **tmp;
    if (!out_items || !out_count) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_items = NULL;
    *out_count = 0u;
    if (count == 0u) {
        return DSU_STATUS_SUCCESS;
    }
    if (!items) {
        return DSU_STATUS_INVALID_ARGS;
    }
    tmp = (char **)dsu__malloc(count * (dsu_u32)sizeof(*tmp));
    if (!tmp) {
        return DSU_STATUS_IO_ERROR;
    }
    memset(tmp, 0, (size_t)count * sizeof(*tmp));
    for (i = 0u; i < count; ++i) {
        char *trimmed = NULL;
        dsu_status_t st;
        const char *src = items[i];
        if (!src) {
            dsu__free_str_list(tmp, count);
            return DSU_STATUS_INVALID_REQUEST;
        }
        st = dsu__trim_dup(src, &trimmed);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free_str_list(tmp, count);
            return st;
        }
        if (!trimmed || trimmed[0] == '\0') {
            dsu__free(trimmed);
            dsu__free_str_list(tmp, count);
            return DSU_STATUS_INVALID_REQUEST;
        }
        if (!dsu__is_ascii_printable(trimmed)) {
            dsu__free(trimmed);
            dsu__free_str_list(tmp, count);
            return DSU_STATUS_INVALID_REQUEST;
        }
        if (lowercase) {
            if (dsu__ascii_to_lower_inplace(trimmed) != DSU_STATUS_SUCCESS) {
                dsu__free(trimmed);
                dsu__free_str_list(tmp, count);
                return DSU_STATUS_INVALID_REQUEST;
            }
        }
        if (require_ascii_id && !dsu__is_ascii_id(trimmed)) {
            dsu__free(trimmed);
            dsu__free_str_list(tmp, count);
            return DSU_STATUS_INVALID_REQUEST;
        }
        tmp[i] = trimmed;
    }
    if (casefold_sort) {
        dsu__sort_str_ptrs_casefold(tmp, count);
    } else {
        dsu__sort_str_ptrs(tmp, count);
    }
    for (i = 1u; i < count; ++i) {
        if (dsu__strcmp_bytes(tmp[i - 1u], tmp[i]) == 0) {
            dsu__free_str_list(tmp, count);
            return DSU_STATUS_INVALID_REQUEST;
        }
    }
    *out_items = tmp;
    *out_count = count;
    return DSU_STATUS_SUCCESS;
}

static void dsu__invocation_canon_free(dsu__invocation_canon_t *canon) {
    if (!canon) {
        return;
    }
    dsu__free(canon->platform_triple);
    dsu__free(canon->ui_mode);
    dsu__free(canon->frontend_id);
    dsu__free_str_list(canon->install_roots, canon->install_root_count);
    dsu__free_str_list(canon->selected_components, canon->selected_component_count);
    dsu__free_str_list(canon->excluded_components, canon->excluded_component_count);
    memset(canon, 0, sizeof(*canon));
}

static dsu_status_t dsu__invocation_canonize(const dsu_invocation_t *inv,
                                            dsu__invocation_canon_t *out) {
    dsu_status_t st;
    if (!inv || !out) {
        return DSU_STATUS_INVALID_ARGS;
    }
    memset(out, 0, sizeof(*out));

    if (inv->struct_version != 1u || inv->struct_size < (dsu_u32)sizeof(*inv)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (inv->operation > (dsu_u8)DSU_INVOCATION_OPERATION_UNINSTALL) {
        return DSU_STATUS_INVALID_REQUEST;
    }
    if (inv->scope > (dsu_u8)DSU_INVOCATION_SCOPE_SYSTEM) {
        return DSU_STATUS_INVALID_REQUEST;
    }
    if ((inv->policy_flags & ~DSU_INVOCATION_POLICY_ALL) != 0u) {
        return DSU_STATUS_INVALID_REQUEST;
    }
    if ((inv->policy_flags & DSU_INVOCATION_POLICY_LEGACY_MODE) != 0u) {
        if (inv->operation != (dsu_u8)DSU_INVOCATION_OPERATION_INSTALL &&
            inv->operation != (dsu_u8)DSU_INVOCATION_OPERATION_UNINSTALL) {
            return DSU_STATUS_INVALID_REQUEST;
        }
    }

    out->operation = inv->operation;
    out->scope = inv->scope;
    out->policy_flags = inv->policy_flags;

    st = dsu__trim_dup(inv->platform_triple, &out->platform_triple);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__invocation_canon_free(out);
        return st;
    }
    if (!out->platform_triple || out->platform_triple[0] == '\0') {
        dsu__invocation_canon_free(out);
        return DSU_STATUS_INVALID_REQUEST;
    }
    if (!dsu__is_ascii_printable(out->platform_triple)) {
        dsu__invocation_canon_free(out);
        return DSU_STATUS_INVALID_REQUEST;
    }

    st = dsu__trim_dup(inv->ui_mode, &out->ui_mode);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__invocation_canon_free(out);
        return st;
    }
    if (!out->ui_mode || out->ui_mode[0] == '\0') {
        dsu__invocation_canon_free(out);
        return DSU_STATUS_INVALID_REQUEST;
    }
    if (!dsu__is_ascii_printable(out->ui_mode)) {
        dsu__invocation_canon_free(out);
        return DSU_STATUS_INVALID_REQUEST;
    }
    if (dsu__ascii_to_lower_inplace(out->ui_mode) != DSU_STATUS_SUCCESS) {
        dsu__invocation_canon_free(out);
        return DSU_STATUS_INVALID_REQUEST;
    }
    if (!dsu__streq(out->ui_mode, "gui") &&
        !dsu__streq(out->ui_mode, "tui") &&
        !dsu__streq(out->ui_mode, "cli")) {
        dsu__invocation_canon_free(out);
        return DSU_STATUS_INVALID_REQUEST;
    }

    st = dsu__trim_dup(inv->frontend_id, &out->frontend_id);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__invocation_canon_free(out);
        return st;
    }
    if (!out->frontend_id || out->frontend_id[0] == '\0') {
        dsu__invocation_canon_free(out);
        return DSU_STATUS_INVALID_REQUEST;
    }
    if (!dsu__is_ascii_printable(out->frontend_id)) {
        dsu__invocation_canon_free(out);
        return DSU_STATUS_INVALID_REQUEST;
    }

    st = dsu__canon_list((const char *const *)inv->install_roots,
                         inv->install_root_count,
                         0u,
                         0u,
                         1u,
                         &out->install_roots,
                         &out->install_root_count);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__invocation_canon_free(out);
        return st;
    }

    st = dsu__canon_list((const char *const *)inv->selected_components,
                         inv->selected_component_count,
                         1u,
                         1u,
                         0u,
                         &out->selected_components,
                         &out->selected_component_count);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__invocation_canon_free(out);
        return st;
    }

    st = dsu__canon_list((const char *const *)inv->excluded_components,
                         inv->excluded_component_count,
                         1u,
                         1u,
                         0u,
                         &out->excluded_components,
                         &out->excluded_component_count);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__invocation_canon_free(out);
        return st;
    }

    if (out->selected_component_count != 0u && out->excluded_component_count != 0u) {
        dsu_u32 i = 0u;
        dsu_u32 j = 0u;
        while (i < out->selected_component_count && j < out->excluded_component_count) {
            int c = dsu__strcmp_bytes(out->selected_components[i], out->excluded_components[j]);
            if (c == 0) {
                dsu__invocation_canon_free(out);
                return DSU_STATUS_INVALID_REQUEST;
            }
            if (c < 0) {
                ++i;
            } else {
                ++j;
            }
        }
    }

    if (out->install_root_count > 1u) {
        dsu__invocation_canon_free(out);
        return DSU_STATUS_INVALID_REQUEST;
    }
    if ((out->operation == (dsu_u8)DSU_INVOCATION_OPERATION_INSTALL ||
         out->operation == (dsu_u8)DSU_INVOCATION_OPERATION_UPGRADE) &&
        out->install_root_count == 0u) {
        dsu__invocation_canon_free(out);
        return DSU_STATUS_INVALID_REQUEST;
    }

    return DSU_STATUS_SUCCESS;
}

static void dsu__u32_to_le_bytes(dsu_u32 v, dsu_u8 out[4]) {
    out[0] = (dsu_u8)(v & 0xFFu);
    out[1] = (dsu_u8)((v >> 8) & 0xFFu);
    out[2] = (dsu_u8)((v >> 16) & 0xFFu);
    out[3] = (dsu_u8)((v >> 24) & 0xFFu);
}

static dsu_u64 dsu__invocation_digest_canon(const dsu__invocation_canon_t *canon) {
    dsu_u64 h;
    dsu_u8 sep = 0u;
    dsu_u8 tmp32[4];
    dsu_u32 i;
    if (!canon) {
        return (dsu_u64)0u;
    }
    h = dsu_digest64_init();

    h = dsu_digest64_update(h, &canon->operation, 1u);
    h = dsu_digest64_update(h, &sep, 1u);
    h = dsu_digest64_update(h, &canon->scope, 1u);
    h = dsu_digest64_update(h, &sep, 1u);

    h = dsu_digest64_update(h, canon->platform_triple, dsu__strlen(canon->platform_triple));
    h = dsu_digest64_update(h, &sep, 1u);

    for (i = 0u; i < canon->install_root_count; ++i) {
        const char *r = canon->install_roots[i] ? canon->install_roots[i] : "";
        h = dsu_digest64_update(h, r, dsu__strlen(r));
        h = dsu_digest64_update(h, &sep, 1u);
    }

    for (i = 0u; i < canon->selected_component_count; ++i) {
        const char *c = canon->selected_components[i] ? canon->selected_components[i] : "";
        h = dsu_digest64_update(h, c, dsu__strlen(c));
        h = dsu_digest64_update(h, &sep, 1u);
    }

    for (i = 0u; i < canon->excluded_component_count; ++i) {
        const char *c = canon->excluded_components[i] ? canon->excluded_components[i] : "";
        h = dsu_digest64_update(h, c, dsu__strlen(c));
        h = dsu_digest64_update(h, &sep, 1u);
    }

    dsu__u32_to_le_bytes(canon->policy_flags, tmp32);
    h = dsu_digest64_update(h, tmp32, 4u);
    h = dsu_digest64_update(h, &sep, 1u);
    return h;
}

static dsu_status_t dsu__str_list_push(char ***items,
                                      dsu_u32 *io_count,
                                      dsu_u32 *io_cap,
                                      char *owned) {
    dsu_u32 count;
    dsu_u32 cap;
    char **p;
    if (!items || !io_count || !io_cap || !owned) {
        return DSU_STATUS_INVALID_ARGS;
    }
    count = *io_count;
    cap = *io_cap;
    if (count == cap) {
        dsu_u32 new_cap = (cap == 0u) ? 8u : (cap * 2u);
        p = (char **)dsu__realloc(*items, new_cap * (dsu_u32)sizeof(*p));
        if (!p) {
            return DSU_STATUS_IO_ERROR;
        }
        *items = p;
        *io_cap = new_cap;
    }
    (*items)[count] = owned;
    *io_count = count + 1u;
    return DSU_STATUS_SUCCESS;
}

void dsu_invocation_init(dsu_invocation_t *inv) {
    if (!inv) {
        return;
    }
    memset(inv, 0, sizeof(*inv));
    inv->struct_size = (dsu_u32)sizeof(*inv);
    inv->struct_version = 1u;
    inv->operation = (dsu_u8)DSU_INVOCATION_OPERATION_INSTALL;
    inv->scope = (dsu_u8)DSU_INVOCATION_SCOPE_PORTABLE;
    inv->policy_flags = 0u;
}

void dsu_invocation_destroy(dsu_ctx_t *ctx, dsu_invocation_t *inv) {
    dsu_u32 i;
    (void)ctx;
    if (!inv) {
        return;
    }
    dsu__free(inv->platform_triple);
    dsu__free(inv->ui_mode);
    dsu__free(inv->frontend_id);
    for (i = 0u; i < inv->install_root_count; ++i) {
        dsu__free(inv->install_roots[i]);
    }
    dsu__free(inv->install_roots);
    for (i = 0u; i < inv->selected_component_count; ++i) {
        dsu__free(inv->selected_components[i]);
    }
    dsu__free(inv->selected_components);
    for (i = 0u; i < inv->excluded_component_count; ++i) {
        dsu__free(inv->excluded_components[i]);
    }
    dsu__free(inv->excluded_components);
    memset(inv, 0, sizeof(*inv));
}

dsu_status_t dsu_invocation_load(dsu_ctx_t *ctx,
                                const char *path,
                                dsu_invocation_t **out_invocation) {
    dsu_u8 *file_bytes = NULL;
    dsu_u32 file_len = 0u;
    dsu_u8 magic[4];
    const dsu_u8 *payload = NULL;
    dsu_u32 payload_len = 0u;
    dsu_u32 off = 0u;
    dsu_status_t st;
    dsu_invocation_t *inv;
    dsu_u32 root_seen = 0u;

    if (!ctx || !path || !out_invocation) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_invocation = NULL;

    st = dsu__fs_read_all(&ctx->config, path, &file_bytes, &file_len);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    magic[0] = (dsu_u8)DSU_INVOCATION_MAGIC_0;
    magic[1] = (dsu_u8)DSU_INVOCATION_MAGIC_1;
    magic[2] = (dsu_u8)DSU_INVOCATION_MAGIC_2;
    magic[3] = (dsu_u8)DSU_INVOCATION_MAGIC_3;

    st = dsu__file_unwrap_payload(file_bytes,
                                  file_len,
                                  magic,
                                  (dsu_u16)DSU_INVOCATION_FORMAT_VERSION,
                                  &payload,
                                  &payload_len);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(file_bytes);
        return st;
    }

    inv = (dsu_invocation_t *)dsu__malloc((dsu_u32)sizeof(*inv));
    if (!inv) {
        dsu__free(file_bytes);
        return DSU_STATUS_IO_ERROR;
    }
    dsu_invocation_init(inv);

    while (off < payload_len && st == DSU_STATUS_SUCCESS) {
        dsu_u16 t;
        dsu_u32 n;
        const dsu_u8 *v;
        st = dsu__tlv_read_header(payload, payload_len, &off, &t, &n);
        if (st != DSU_STATUS_SUCCESS) break;
        if (payload_len - off < n) {
            st = DSU_STATUS_INTEGRITY_ERROR;
            break;
        }
        v = payload + off;
        if (t == (dsu_u16)DSU_INVOCATION_TLV_ROOT) {
            dsu_u32 off2 = 0u;
            dsu_u32 root_version = 0u;
            dsu_u32 have_root_version = 0u;
            dsu_u32 have_op = 0u;
            dsu_u32 have_scope = 0u;
            dsu_u32 have_platform = 0u;
            dsu_u32 have_policy = 0u;
            dsu_u32 have_ui = 0u;
            dsu_u32 have_frontend = 0u;
            dsu_u32 cap_install = 0u;
            dsu_u32 cap_selected = 0u;
            dsu_u32 cap_excluded = 0u;
            if (root_seen) {
                st = DSU_STATUS_INTEGRITY_ERROR;
                break;
            }
            root_seen = 1u;
            while (off2 < n && st == DSU_STATUS_SUCCESS) {
                dsu_u16 t2;
                dsu_u32 n2;
                const dsu_u8 *v2;
                st = dsu__tlv_read_header(v, n, &off2, &t2, &n2);
                if (st != DSU_STATUS_SUCCESS) break;
                if (n - off2 < n2) {
                    st = DSU_STATUS_INTEGRITY_ERROR;
                    break;
                }
                v2 = v + off2;
                if (t2 == (dsu_u16)DSU_INVOCATION_TLV_ROOT_VERSION) {
                    if (n2 != 4u) {
                        st = DSU_STATUS_INTEGRITY_ERROR;
                        break;
                    }
                    root_version = (dsu_u32)v2[0]
                                 | ((dsu_u32)v2[1] << 8)
                                 | ((dsu_u32)v2[2] << 16)
                                 | ((dsu_u32)v2[3] << 24);
                    have_root_version = 1u;
                } else if (t2 == (dsu_u16)DSU_INVOCATION_TLV_OPERATION) {
                    if (n2 != 1u) {
                        st = DSU_STATUS_INTEGRITY_ERROR;
                        break;
                    }
                    inv->operation = v2[0];
                    have_op = 1u;
                } else if (t2 == (dsu_u16)DSU_INVOCATION_TLV_SCOPE) {
                    if (n2 != 1u) {
                        st = DSU_STATUS_INTEGRITY_ERROR;
                        break;
                    }
                    inv->scope = v2[0];
                    have_scope = 1u;
                } else if (t2 == (dsu_u16)DSU_INVOCATION_TLV_PLATFORM_TRIPLE) {
                    if (have_platform) {
                        st = DSU_STATUS_INTEGRITY_ERROR;
                        break;
                    }
                    st = dsu__dup_bytes_cstr(v2, n2, &inv->platform_triple);
                    if (st != DSU_STATUS_SUCCESS) break;
                    have_platform = 1u;
                } else if (t2 == (dsu_u16)DSU_INVOCATION_TLV_INSTALL_ROOT) {
                    char *tmp = NULL;
                    st = dsu__dup_bytes_cstr(v2, n2, &tmp);
                    if (st != DSU_STATUS_SUCCESS) break;
                    st = dsu__str_list_push(&inv->install_roots,
                                            &inv->install_root_count,
                                            &cap_install,
                                            tmp);
                    if (st != DSU_STATUS_SUCCESS) {
                        dsu__free(tmp);
                        break;
                    }
                } else if (t2 == (dsu_u16)DSU_INVOCATION_TLV_POLICY_FLAGS) {
                    if (n2 != 4u) {
                        st = DSU_STATUS_INTEGRITY_ERROR;
                        break;
                    }
                    inv->policy_flags = (dsu_u32)v2[0]
                                      | ((dsu_u32)v2[1] << 8)
                                      | ((dsu_u32)v2[2] << 16)
                                      | ((dsu_u32)v2[3] << 24);
                    have_policy = 1u;
                } else if (t2 == (dsu_u16)DSU_INVOCATION_TLV_UI_MODE) {
                    if (have_ui) {
                        st = DSU_STATUS_INTEGRITY_ERROR;
                        break;
                    }
                    st = dsu__dup_bytes_cstr(v2, n2, &inv->ui_mode);
                    if (st != DSU_STATUS_SUCCESS) break;
                    have_ui = 1u;
                } else if (t2 == (dsu_u16)DSU_INVOCATION_TLV_FRONTEND_ID) {
                    if (have_frontend) {
                        st = DSU_STATUS_INTEGRITY_ERROR;
                        break;
                    }
                    st = dsu__dup_bytes_cstr(v2, n2, &inv->frontend_id);
                    if (st != DSU_STATUS_SUCCESS) break;
                    have_frontend = 1u;
                } else if (t2 == (dsu_u16)DSU_INVOCATION_TLV_SELECTED_COMPONENT) {
                    char *tmp = NULL;
                    st = dsu__dup_bytes_cstr(v2, n2, &tmp);
                    if (st != DSU_STATUS_SUCCESS) break;
                    st = dsu__str_list_push(&inv->selected_components,
                                            &inv->selected_component_count,
                                            &cap_selected,
                                            tmp);
                    if (st != DSU_STATUS_SUCCESS) {
                        dsu__free(tmp);
                        break;
                    }
                } else if (t2 == (dsu_u16)DSU_INVOCATION_TLV_EXCLUDED_COMPONENT) {
                    char *tmp = NULL;
                    st = dsu__dup_bytes_cstr(v2, n2, &tmp);
                    if (st != DSU_STATUS_SUCCESS) break;
                    st = dsu__str_list_push(&inv->excluded_components,
                                            &inv->excluded_component_count,
                                            &cap_excluded,
                                            tmp);
                    if (st != DSU_STATUS_SUCCESS) {
                        dsu__free(tmp);
                        break;
                    }
                } else {
                    /* skip */
                }
                off2 += n2;
            }
            if (st != DSU_STATUS_SUCCESS) {
                break;
            }
            if (!have_root_version) {
                st = DSU_STATUS_INTEGRITY_ERROR;
                break;
            }
            if (root_version != 1u) {
                st = DSU_STATUS_UNSUPPORTED_VERSION;
                break;
            }
            if (!have_op || !have_scope || !have_platform || !have_policy || !have_ui || !have_frontend) {
                st = DSU_STATUS_INTEGRITY_ERROR;
                break;
            }
        }
        off += n;
    }

    dsu__free(file_bytes);
    if (st != DSU_STATUS_SUCCESS) {
        dsu_invocation_destroy(ctx, inv);
        dsu__free(inv);
        return st;
    }
    if (!root_seen) {
        dsu_invocation_destroy(ctx, inv);
        dsu__free(inv);
        return DSU_STATUS_INTEGRITY_ERROR;
    }

    st = dsu_invocation_validate(inv);
    if (st != DSU_STATUS_SUCCESS) {
        dsu_invocation_destroy(ctx, inv);
        dsu__free(inv);
        return st;
    }

    *out_invocation = inv;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__blob_put_tlv_u8(dsu_blob_t *b, dsu_u16 type, dsu_u8 v) {
    return dsu__blob_put_tlv(b, type, &v, 1u);
}

static dsu_status_t dsu__blob_put_tlv_u32(dsu_blob_t *b, dsu_u16 type, dsu_u32 v) {
    dsu_u8 tmp[4];
    dsu__u32_to_le_bytes(v, tmp);
    return dsu__blob_put_tlv(b, type, tmp, 4u);
}

static dsu_status_t dsu__blob_put_tlv_str(dsu_blob_t *b, dsu_u16 type, const char *s) {
    if (!s) s = "";
    return dsu__blob_put_tlv(b, type, s, dsu__strlen(s));
}

dsu_status_t dsu_invocation_write_file(dsu_ctx_t *ctx,
                                      const dsu_invocation_t *invocation,
                                      const char *path) {
    dsu_blob_t root;
    dsu_blob_t payload;
    dsu_blob_t file_bytes;
    dsu_u8 magic[4];
    dsu__invocation_canon_t canon;
    dsu_status_t st;
    dsu_u32 i;

    if (!ctx || !invocation || !path) {
        return DSU_STATUS_INVALID_ARGS;
    }

    st = dsu__invocation_canonize(invocation, &canon);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    dsu__blob_init(&root);
    dsu__blob_init(&payload);
    dsu__blob_init(&file_bytes);

    st = dsu__blob_put_tlv_u32(&root, (dsu_u16)DSU_INVOCATION_TLV_ROOT_VERSION, 1u);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&root, (dsu_u16)DSU_INVOCATION_TLV_OPERATION, canon.operation);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&root, (dsu_u16)DSU_INVOCATION_TLV_SCOPE, canon.scope);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&root, (dsu_u16)DSU_INVOCATION_TLV_PLATFORM_TRIPLE, canon.platform_triple);
    for (i = 0u; st == DSU_STATUS_SUCCESS && i < canon.install_root_count; ++i) {
        st = dsu__blob_put_tlv_str(&root, (dsu_u16)DSU_INVOCATION_TLV_INSTALL_ROOT, canon.install_roots[i]);
    }
    for (i = 0u; st == DSU_STATUS_SUCCESS && i < canon.selected_component_count; ++i) {
        st = dsu__blob_put_tlv_str(&root, (dsu_u16)DSU_INVOCATION_TLV_SELECTED_COMPONENT, canon.selected_components[i]);
    }
    for (i = 0u; st == DSU_STATUS_SUCCESS && i < canon.excluded_component_count; ++i) {
        st = dsu__blob_put_tlv_str(&root, (dsu_u16)DSU_INVOCATION_TLV_EXCLUDED_COMPONENT, canon.excluded_components[i]);
    }
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u32(&root, (dsu_u16)DSU_INVOCATION_TLV_POLICY_FLAGS, canon.policy_flags);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&root, (dsu_u16)DSU_INVOCATION_TLV_UI_MODE, canon.ui_mode);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&root, (dsu_u16)DSU_INVOCATION_TLV_FRONTEND_ID, canon.frontend_id);

    if (st == DSU_STATUS_SUCCESS) {
        st = dsu__blob_put_tlv(&payload, (dsu_u16)DSU_INVOCATION_TLV_ROOT, root.data, root.size);
    }
    dsu__blob_free(&root);

    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(&payload);
        dsu__blob_free(&file_bytes);
        dsu__invocation_canon_free(&canon);
        return st;
    }

    magic[0] = (dsu_u8)DSU_INVOCATION_MAGIC_0;
    magic[1] = (dsu_u8)DSU_INVOCATION_MAGIC_1;
    magic[2] = (dsu_u8)DSU_INVOCATION_MAGIC_2;
    magic[3] = (dsu_u8)DSU_INVOCATION_MAGIC_3;

    st = dsu__file_wrap_payload(magic,
                                (dsu_u16)DSU_INVOCATION_FORMAT_VERSION,
                                payload.data,
                                payload.size,
                                &file_bytes);
    dsu__blob_free(&payload);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(&file_bytes);
        dsu__invocation_canon_free(&canon);
        return st;
    }

    st = dsu__fs_write_all(path, file_bytes.data, file_bytes.size);
    dsu__blob_free(&file_bytes);
    dsu__invocation_canon_free(&canon);
    return st;
}

dsu_status_t dsu_invocation_validate(const dsu_invocation_t *invocation) {
    dsu__invocation_canon_t canon;
    dsu_status_t st;
    if (!invocation) {
        return DSU_STATUS_INVALID_ARGS;
    }
    st = dsu__invocation_canonize(invocation, &canon);
    dsu__invocation_canon_free(&canon);
    return st;
}

dsu_u64 dsu_invocation_digest(const dsu_invocation_t *invocation) {
    dsu__invocation_canon_t canon;
    dsu_status_t st;
    dsu_u64 digest;
    if (!invocation) {
        return (dsu_u64)0u;
    }
    st = dsu__invocation_canonize(invocation, &canon);
    if (st != DSU_STATUS_SUCCESS) {
        return (dsu_u64)0u;
    }
    digest = dsu__invocation_digest_canon(&canon);
    dsu__invocation_canon_free(&canon);
    return digest;
}

dsu_status_t dsu_resolve_components_from_invocation(dsu_ctx_t *ctx,
                                                   const dsu_manifest_t *manifest,
                                                   const dsu_state_t *installed_state,
                                                   const dsu_invocation_t *invocation,
                                                   dsu_resolve_result_t **out_result,
                                                   dsu_u64 *out_invocation_digest) {
    dsu__invocation_canon_t canon;
    dsu_resolve_request_t req;
    dsu_status_t st;
    dsu_u64 digest;

    if (out_invocation_digest) {
        *out_invocation_digest = (dsu_u64)0u;
    }
    if (!ctx || !manifest || !invocation || !out_result) {
        return DSU_STATUS_INVALID_ARGS;
    }

    st = dsu__invocation_canonize(invocation, &canon);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    digest = dsu__invocation_digest_canon(&canon);

    dsu_resolve_request_init(&req);
    req.operation = (dsu_resolve_operation_t)canon.operation;
    req.scope = (dsu_manifest_install_scope_t)canon.scope;
    req.allow_prerelease = (canon.policy_flags & DSU_INVOCATION_POLICY_ALLOW_PRERELEASE) ? DSU_TRUE : DSU_FALSE;
    req.target_platform = canon.platform_triple;
    req.install_roots = (const char *const *)canon.install_roots;
    req.install_root_count = canon.install_root_count;
    req.requested_components = (const char *const *)canon.selected_components;
    req.requested_component_count = canon.selected_component_count;
    req.excluded_components = (const char *const *)canon.excluded_components;
    req.excluded_component_count = canon.excluded_component_count;
    req.pins = NULL;
    req.pin_count = 0u;

    st = dsu_resolve_components(ctx, manifest, installed_state, &req, out_result);
    dsu__invocation_canon_free(&canon);

    if (st == DSU_STATUS_SUCCESS && out_invocation_digest) {
        *out_invocation_digest = digest;
    }
    return st;
}

dsu_status_t dsu_plan_build_from_invocation(dsu_ctx_t *ctx,
                                           const dsu_manifest_t *manifest,
                                           const char *manifest_path,
                                           const dsu_state_t *installed_state,
                                           const dsu_invocation_t *invocation,
                                           dsu_plan_t **out_plan) {
    dsu_resolve_result_t *resolved = NULL;
    dsu_u64 invocation_digest = 0u;
    dsu_status_t st;
    if (!out_plan) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_plan = NULL;
    st = dsu_resolve_components_from_invocation(ctx,
                                                manifest,
                                                installed_state,
                                                invocation,
                                                &resolved,
                                                &invocation_digest);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    st = dsu_plan_build(ctx, manifest, manifest_path, resolved, invocation_digest, out_plan);
    dsu_resolve_result_destroy(ctx, resolved);
    return st;
}
