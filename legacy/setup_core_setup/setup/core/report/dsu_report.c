/*
FILE: source/dominium/setup/core/src/report/dsu_report.c
MODULE: Dominium Setup
PURPOSE: Deterministic reporting/forensics over installed state (Plan S-5).
*/
#include "../../include/dsu/dsu_report.h"

#include "../../include/dsu/dsu_fs.h"

#include "../dsu_ctx_internal.h"
#include "../fs/dsu_platform_iface.h"
#include "../util/dsu_util_internal.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct dsu__str_list_t {
    dsu_u32 count;
    dsu_u32 cap;
    char **items;
} dsu__str_list_t;

static void dsu__str_list_init(dsu__str_list_t *l) {
    if (!l) return;
    memset(l, 0, sizeof(*l));
}

static void dsu__str_list_free(dsu__str_list_t *l) {
    dsu_u32 i;
    if (!l) return;
    for (i = 0u; i < l->count; ++i) {
        dsu__free(l->items[i]);
        l->items[i] = NULL;
    }
    dsu__free(l->items);
    memset(l, 0, sizeof(*l));
}

static dsu_status_t dsu__str_list_push_dup(dsu__str_list_t *l, const char *s) {
    dsu_u32 new_cap;
    char **p;
    char *dup;
    if (!l) return DSU_STATUS_INVALID_ARGS;
    if (!s) s = "";
    if (l->count == l->cap) {
        new_cap = (l->cap == 0u) ? 16u : (l->cap * 2u);
        p = (char **)dsu__realloc(l->items, new_cap * (dsu_u32)sizeof(*p));
        if (!p) return DSU_STATUS_IO_ERROR;
        l->items = p;
        l->cap = new_cap;
    }
    dup = dsu__strdup(s);
    if (!dup) return DSU_STATUS_IO_ERROR;
    l->items[l->count++] = dup;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__str_list_push_take(dsu__str_list_t *l, char *s_owned) {
    dsu_u32 new_cap;
    char **p;
    if (!l || !s_owned) return DSU_STATUS_INVALID_ARGS;
    if (l->count == l->cap) {
        new_cap = (l->cap == 0u) ? 16u : (l->cap * 2u);
        p = (char **)dsu__realloc(l->items, new_cap * (dsu_u32)sizeof(*p));
        if (!p) return DSU_STATUS_IO_ERROR;
        l->items = p;
        l->cap = new_cap;
    }
    l->items[l->count++] = s_owned;
    return DSU_STATUS_SUCCESS;
}

static void dsu__str_list_sort(dsu__str_list_t *l) {
    if (!l || l->count < 2u) return;
    dsu__sort_str_ptrs(l->items, l->count);
}

static void dsu__str_list_dedup_sorted(dsu__str_list_t *l) {
    dsu_u32 r;
    dsu_u32 w;
    if (!l || l->count < 2u) return;
    w = 1u;
    for (r = 1u; r < l->count; ++r) {
        if (dsu__strcmp_bytes(l->items[r - 1u], l->items[r]) == 0) {
            dsu__free(l->items[r]);
            l->items[r] = NULL;
        } else {
            l->items[w++] = l->items[r];
        }
    }
    l->count = w;
}

static dsu_status_t dsu__collect_parent_dirs(dsu__str_list_t *dirs, const char *rel_path) {
    dsu_u32 i;
    dsu_u32 n;
    char tmp[1024];
    if (!dirs || !rel_path) return DSU_STATUS_INVALID_ARGS;
    n = dsu__strlen(rel_path);
    if (n == 0xFFFFFFFFu) return DSU_STATUS_INVALID_ARGS;
    if (n >= (dsu_u32)sizeof(tmp)) return DSU_STATUS_INVALID_ARGS;
    if (n == 0u) return DSU_STATUS_SUCCESS;
    memcpy(tmp, rel_path, (size_t)n + 1u);
    for (i = 0u; i < n; ++i) {
        if (tmp[i] == '/') {
            tmp[i] = '\0';
            if (tmp[0] != '\0') {
                dsu_status_t st = dsu__str_list_push_dup(dirs, tmp);
                if (st != DSU_STATUS_SUCCESS) return st;
            }
            tmp[i] = '/';
        }
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__str_list_push_root_path(dsu__str_list_t *l, dsu_u32 root_index, const char *rel_path) {
    char num[32];
    dsu_u32 a;
    dsu_u32 b;
    char *s;
    if (!l || !rel_path) return DSU_STATUS_INVALID_ARGS;
    sprintf(num, "%lu", (unsigned long)root_index);
    a = dsu__strlen(num);
    b = dsu__strlen(rel_path);
    if (a == 0xFFFFFFFFu || b == 0xFFFFFFFFu) return DSU_STATUS_INVALID_ARGS;
    if (a > 0xFFFFFFFFu - 1u - b) return DSU_STATUS_IO_ERROR;
    s = (char *)dsu__malloc(a + 1u + b + 1u);
    if (!s) return DSU_STATUS_IO_ERROR;
    memcpy(s, num, (size_t)a);
    s[a] = ':';
    memcpy(s + a + 1u, rel_path, (size_t)b);
    s[a + 1u + b] = '\0';
    return dsu__str_list_push_take(l, s);
}

typedef struct dsu__expected_item_t {
    dsu_u32 root_index;
    const char *path; /* non-owned pointer */
} dsu__expected_item_t;

static int dsu__expected_item_cmp(const void *a, const void *b) {
    const dsu__expected_item_t *ea = (const dsu__expected_item_t *)a;
    const dsu__expected_item_t *eb = (const dsu__expected_item_t *)b;
    if (ea->root_index != eb->root_index) {
        return (ea->root_index < eb->root_index) ? -1 : 1;
    }
    return dsu__strcmp_bytes(ea->path ? ea->path : "", eb->path ? eb->path : "");
}

static dsu_bool dsu__expected_contains(const dsu__expected_item_t *items,
                                      dsu_u32 count,
                                      dsu_u32 root_index,
                                      const char *path) {
    dsu_u32 lo = 0u;
    dsu_u32 hi = count;
    if (!items || !path) return 0;
    while (lo < hi) {
        dsu_u32 mid = lo + (hi - lo) / 2u;
        const dsu__expected_item_t *e = &items[mid];
        int cmp;
        if (e->root_index != root_index) {
            cmp = (e->root_index < root_index) ? -1 : 1;
        } else {
            cmp = dsu__strcmp_bytes(e->path ? e->path : "", path);
        }
        if (cmp < 0) lo = mid + 1u;
        else hi = mid;
    }
    if (lo < count) {
        const dsu__expected_item_t *e = &items[lo];
        if (e->root_index == root_index && dsu__strcmp_bytes(e->path ? e->path : "", path) == 0) {
            return 1;
        }
    }
    return 0;
}

static dsu_bool dsu__name_is_safe_leaf(const char *name) {
    const unsigned char *p = (const unsigned char *)(name ? name : "");
    unsigned char c;
    if (!name || name[0] == '\0') return 0;
    if (strcmp(name, ".") == 0 || strcmp(name, "..") == 0) return 0;
    while ((c = *p++) != 0u) {
        if (c == '/' || c == '\\' || c == ':') return 0;
        if (c < 0x20u) return 0;
    }
    return 1;
}

static dsu_bool dsu__segment_is_internal_dsu(const char *name) {
    if (!name) return 0;
    return (name[0] == '.' && name[1] == 'd' && name[2] == 's' && name[3] == 'u');
}

static dsu_status_t dsu__scan_extras_dir(const dsu__expected_item_t *expected,
                                        dsu_u32 expected_count,
                                        dsu_u32 root_index,
                                        const char *root_abs,
                                        const char *rel_dir,
                                        dsu__str_list_t *out_extra) {
    char abs_dir[1024];
    dsu_status_t st;
    dsu_platform_dir_entry_t *entries = NULL;
    dsu_u32 count = 0u;
    dsu_u32 i;

    if (!root_abs || !out_extra) return DSU_STATUS_INVALID_ARGS;
    if (!rel_dir) rel_dir = "";

    if (rel_dir[0] == '\0') {
        dsu_u32 n = dsu__strlen(root_abs);
        if (n == 0xFFFFFFFFu || n >= (dsu_u32)sizeof(abs_dir)) return DSU_STATUS_INVALID_ARGS;
        memcpy(abs_dir, root_abs, (size_t)n + 1u);
    } else {
        st = dsu_fs_path_join(root_abs, rel_dir, abs_dir, (dsu_u32)sizeof(abs_dir));
        if (st != DSU_STATUS_SUCCESS) return st;
    }

    st = dsu_platform_list_dir(abs_dir, &entries, &count);
    if (st != DSU_STATUS_SUCCESS) return st;

    for (i = 0u; i < count; ++i) {
        const dsu_platform_dir_entry_t *e = &entries[i];
        const char *name = e->name;
        char child_rel[1024];
        if (!dsu__name_is_safe_leaf(name)) continue;
        if (dsu__segment_is_internal_dsu(name)) continue;
        if (rel_dir[0] == '\0') {
            dsu_u32 n = dsu__strlen(name);
            if (n == 0xFFFFFFFFu || n >= (dsu_u32)sizeof(child_rel)) {
                st = DSU_STATUS_INVALID_ARGS;
                break;
            }
            memcpy(child_rel, name, (size_t)n + 1u);
        } else {
            st = dsu_fs_path_join(rel_dir, name, child_rel, (dsu_u32)sizeof(child_rel));
            if (st != DSU_STATUS_SUCCESS) break;
        }

        if (e->is_symlink) {
            continue;
        }
        if (e->is_dir) {
            st = dsu__scan_extras_dir(expected, expected_count, root_index, root_abs, child_rel, out_extra);
            if (st != DSU_STATUS_SUCCESS) break;
            continue;
        }

        if (!dsu__expected_contains(expected, expected_count, root_index, child_rel)) {
            st = dsu__str_list_push_root_path(out_extra, root_index, child_rel);
            if (st != DSU_STATUS_SUCCESS) break;
        }
    }

    dsu_platform_free_dir_entries(entries, count);
    return st;
}

static void dsu__u64_hex16(char out16[17], dsu_u64 v) {
    static const char *hex = "0123456789abcdef";
    int i;
    for (i = 0; i < 16; ++i) {
        int shift = (15 - i) * 4;
        out16[i] = hex[(unsigned char)((v >> shift) & 0xFu)];
    }
    out16[16] = '\0';
}

static dsu_status_t dsu__blob_append_cstr(dsu_blob_t *b, const char *s) {
    dsu_u32 n;
    if (!b) return DSU_STATUS_INVALID_ARGS;
    if (!s) s = "";
    n = dsu__strlen(s);
    if (n == 0xFFFFFFFFu) return DSU_STATUS_INVALID_ARGS;
    return dsu__blob_append(b, s, n);
}

static dsu_status_t dsu__json_put_escaped(dsu_blob_t *b, const char *s) {
    static const char hex[] = "0123456789abcdef";
    const unsigned char *p = (const unsigned char *)(s ? s : "");
    dsu_status_t st;
    unsigned char c;

    st = dsu__blob_put_u8(b, (dsu_u8)'"');
    if (st != DSU_STATUS_SUCCESS) return st;

    while ((c = *p++) != 0u) {
        if (c == '\\' || c == '"') {
            st = dsu__blob_put_u8(b, (dsu_u8)'\\');
            if (st != DSU_STATUS_SUCCESS) return st;
            st = dsu__blob_put_u8(b, (dsu_u8)c);
            if (st != DSU_STATUS_SUCCESS) return st;
        } else if (c == '\b') {
            st = dsu__blob_append_cstr(b, "\\b");
            if (st != DSU_STATUS_SUCCESS) return st;
        } else if (c == '\f') {
            st = dsu__blob_append_cstr(b, "\\f");
            if (st != DSU_STATUS_SUCCESS) return st;
        } else if (c == '\n') {
            st = dsu__blob_append_cstr(b, "\\n");
            if (st != DSU_STATUS_SUCCESS) return st;
        } else if (c == '\r') {
            st = dsu__blob_append_cstr(b, "\\r");
            if (st != DSU_STATUS_SUCCESS) return st;
        } else if (c == '\t') {
            st = dsu__blob_append_cstr(b, "\\t");
            if (st != DSU_STATUS_SUCCESS) return st;
        } else if (c < 0x20u) {
            dsu_u8 tmp[6];
            tmp[0] = (dsu_u8)'\\';
            tmp[1] = (dsu_u8)'u';
            tmp[2] = (dsu_u8)'0';
            tmp[3] = (dsu_u8)'0';
            tmp[4] = (dsu_u8)hex[(c >> 4) & 0xFu];
            tmp[5] = (dsu_u8)hex[c & 0xFu];
            st = dsu__blob_append(b, tmp, 6u);
            if (st != DSU_STATUS_SUCCESS) return st;
        } else {
            st = dsu__blob_put_u8(b, (dsu_u8)c);
            if (st != DSU_STATUS_SUCCESS) return st;
        }
    }

    return dsu__blob_put_u8(b, (dsu_u8)'"');
}

static dsu_status_t dsu__blob_to_cstr_take(dsu_blob_t *b, char **out_str) {
    char *s;
    if (!out_str) return DSU_STATUS_INVALID_ARGS;
    *out_str = NULL;
    if (!b) return DSU_STATUS_INVALID_ARGS;

    s = (char *)dsu__malloc(b->size + 1u);
    if (!s) return DSU_STATUS_IO_ERROR;
    if (b->size) memcpy(s, b->data, (size_t)b->size);
    s[b->size] = '\0';
    *out_str = s;
    return DSU_STATUS_SUCCESS;
}

void dsu_report_verify_summary_init(dsu_report_verify_summary_t *s) {
    if (!s) return;
    memset(s, 0, sizeof(*s));
    s->struct_size = (dsu_u32)sizeof(*s);
    s->struct_version = 1u;
}

void dsu_report_free(dsu_ctx_t *ctx, void *p) {
    (void)ctx;
    dsu__free(p);
}

/* Implementations are added incrementally to avoid tool patch-size limits. */

dsu_status_t dsu_report_list_installed(dsu_ctx_t *ctx,
                                      const dsu_state_t *state,
                                      dsu_report_format_t format,
                                      char **out_report) {
    dsu_status_t st;
    dsu_blob_t b;
    dsu_u32 i;
    char hx[17];
    char num[32];

    if (!ctx || !state || !out_report) return DSU_STATUS_INVALID_ARGS;
    *out_report = NULL;

    dsu__blob_init(&b);

    if (format == DSU_REPORT_FORMAT_JSON) {
        st = dsu__blob_append_cstr(&b, "{");
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "\"product_id\":");
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, dsu_state_product_id(state));
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"product_version_installed\":");
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, dsu_state_product_version_installed(state));
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"build_channel\":");
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, dsu_state_build_channel(state));
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"platform_triple\":");
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, dsu_state_platform(state));
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"install_scope\":");
        if (st == DSU_STATUS_SUCCESS) {
            sprintf(num, "%lu", (unsigned long)dsu_state_install_scope(state));
            st = dsu__blob_append_cstr(&b, num);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"install_instance_id\":\"0x");
        if (st == DSU_STATUS_SUCCESS) {
            dsu__u64_hex16(hx, dsu_state_install_instance_id(state));
            st = dsu__blob_append_cstr(&b, hx);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "\"");

        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"manifest_digest64\":\"0x");
        if (st == DSU_STATUS_SUCCESS) {
            dsu__u64_hex16(hx, dsu_state_manifest_digest64(state));
            st = dsu__blob_append_cstr(&b, hx);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "\"");

        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"resolved_set_digest64\":\"0x");
        if (st == DSU_STATUS_SUCCESS) {
            dsu__u64_hex16(hx, dsu_state_resolved_set_digest64(state));
            st = dsu__blob_append_cstr(&b, hx);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "\"");

        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"plan_digest64\":\"0x");
        if (st == DSU_STATUS_SUCCESS) {
            dsu__u64_hex16(hx, dsu_state_plan_digest64(state));
            st = dsu__blob_append_cstr(&b, hx);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "\"");

        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"install_roots\":[");
        for (i = 0u; st == DSU_STATUS_SUCCESS && i < dsu_state_install_root_count(state); ++i) {
            if (i != 0u) st = dsu__blob_put_u8(&b, (dsu_u8)',');
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "{\"index\":");
            if (st != DSU_STATUS_SUCCESS) break;
            sprintf(num, "%lu", (unsigned long)i);
            st = dsu__blob_append_cstr(&b, num);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, ",\"role\":");
            if (st != DSU_STATUS_SUCCESS) break;
            sprintf(num, "%lu", (unsigned long)dsu_state_install_root_role(state, i));
            st = dsu__blob_append_cstr(&b, num);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, ",\"path\":");
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__json_put_escaped(&b, dsu_state_install_root_path(state, i));
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "}");
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "]");

        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"components\":[");
        for (i = 0u; st == DSU_STATUS_SUCCESS && i < dsu_state_component_count(state); ++i) {
            if (i != 0u) st = dsu__blob_put_u8(&b, (dsu_u8)',');
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "{\"component_id\":");
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__json_put_escaped(&b, dsu_state_component_id(state, i));
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, ",\"component_version\":");
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__json_put_escaped(&b, dsu_state_component_version(state, i));
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, ",\"component_kind\":");
            if (st != DSU_STATUS_SUCCESS) break;
            sprintf(num, "%lu", (unsigned long)dsu_state_component_kind(state, i));
            st = dsu__blob_append_cstr(&b, num);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, ",\"file_count\":");
            if (st != DSU_STATUS_SUCCESS) break;
            sprintf(num, "%lu", (unsigned long)dsu_state_component_file_count(state, i));
            st = dsu__blob_append_cstr(&b, num);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "}");
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "]}");
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u8(&b, (dsu_u8)'\n');
    } else {
        st = dsu__blob_append_cstr(&b, "Installed State\n");
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "Product: ");
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, dsu_state_product_id(state));
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, " ");
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, dsu_state_product_version_installed(state));
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "\nChannel: ");
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, dsu_state_build_channel(state));
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "\nPlatform: ");
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, dsu_state_platform(state));
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "\nScope: ");
        if (st == DSU_STATUS_SUCCESS) {
            sprintf(num, "%lu", (unsigned long)dsu_state_install_scope(state));
            st = dsu__blob_append_cstr(&b, num);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "\nInstance: 0x");
        if (st == DSU_STATUS_SUCCESS) {
            dsu__u64_hex16(hx, dsu_state_install_instance_id(state));
            st = dsu__blob_append_cstr(&b, hx);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "\nDigests: manifest=0x");
        if (st == DSU_STATUS_SUCCESS) {
            dsu__u64_hex16(hx, dsu_state_manifest_digest64(state));
            st = dsu__blob_append_cstr(&b, hx);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, " resolved=0x");
        if (st == DSU_STATUS_SUCCESS) {
            dsu__u64_hex16(hx, dsu_state_resolved_set_digest64(state));
            st = dsu__blob_append_cstr(&b, hx);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, " plan=0x");
        if (st == DSU_STATUS_SUCCESS) {
            dsu__u64_hex16(hx, dsu_state_plan_digest64(state));
            st = dsu__blob_append_cstr(&b, hx);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "\nInstall Roots:\n");
        for (i = 0u; st == DSU_STATUS_SUCCESS && i < dsu_state_install_root_count(state); ++i) {
            st = dsu__blob_append_cstr(&b, "  [");
            if (st != DSU_STATUS_SUCCESS) break;
            sprintf(num, "%lu", (unsigned long)i);
            st = dsu__blob_append_cstr(&b, num);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "] role=");
            if (st != DSU_STATUS_SUCCESS) break;
            sprintf(num, "%lu", (unsigned long)dsu_state_install_root_role(state, i));
            st = dsu__blob_append_cstr(&b, num);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, " path=");
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, dsu_state_install_root_path(state, i));
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "\n");
        }

        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "Components:\n");
        for (i = 0u; st == DSU_STATUS_SUCCESS && i < dsu_state_component_count(state); ++i) {
            st = dsu__blob_append_cstr(&b, "  - ");
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, dsu_state_component_id(state, i));
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, " ");
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, dsu_state_component_version(state, i));
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, " kind=");
            if (st != DSU_STATUS_SUCCESS) break;
            sprintf(num, "%lu", (unsigned long)dsu_state_component_kind(state, i));
            st = dsu__blob_append_cstr(&b, num);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, " files=");
            if (st != DSU_STATUS_SUCCESS) break;
            sprintf(num, "%lu", (unsigned long)dsu_state_component_file_count(state, i));
            st = dsu__blob_append_cstr(&b, num);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "\n");
        }
    }

    if (st == DSU_STATUS_SUCCESS) {
        st = dsu__blob_to_cstr_take(&b, out_report);
    }
    dsu__blob_free(&b);
    return st;
}

dsu_status_t dsu_report_touched_paths(dsu_ctx_t *ctx,
                                     const dsu_state_t *state,
                                     dsu_report_format_t format,
                                     char **out_report) {
    dsu_status_t st;
    dsu_blob_t b;
    dsu_u32 root_count;
    dsu_u32 ci;
    dsu_u32 fi;
    dsu_u32 ri;
    char num[32];

    dsu__str_list_t *owned_files = NULL;
    dsu__str_list_t *owned_dirs = NULL;
    dsu__str_list_t *user_files = NULL;
    dsu__str_list_t *cache_files = NULL;

    if (!ctx || !state || !out_report) return DSU_STATUS_INVALID_ARGS;
    *out_report = NULL;

    root_count = dsu_state_install_root_count(state);
    if (root_count == 0u) return DSU_STATUS_INVALID_ARGS;

    owned_files = (dsu__str_list_t *)dsu__malloc(root_count * (dsu_u32)sizeof(*owned_files));
    owned_dirs = (dsu__str_list_t *)dsu__malloc(root_count * (dsu_u32)sizeof(*owned_dirs));
    user_files = (dsu__str_list_t *)dsu__malloc(root_count * (dsu_u32)sizeof(*user_files));
    cache_files = (dsu__str_list_t *)dsu__malloc(root_count * (dsu_u32)sizeof(*cache_files));
    if (!owned_files || !owned_dirs || !user_files || !cache_files) {
        dsu__free(owned_files);
        dsu__free(owned_dirs);
        dsu__free(user_files);
        dsu__free(cache_files);
        return DSU_STATUS_IO_ERROR;
    }
    for (ri = 0u; ri < root_count; ++ri) {
        dsu__str_list_init(&owned_files[ri]);
        dsu__str_list_init(&owned_dirs[ri]);
        dsu__str_list_init(&user_files[ri]);
        dsu__str_list_init(&cache_files[ri]);
    }

    st = DSU_STATUS_SUCCESS;
    for (ci = 0u; st == DSU_STATUS_SUCCESS && ci < dsu_state_component_count(state); ++ci) {
        for (fi = 0u; st == DSU_STATUS_SUCCESS && fi < dsu_state_component_file_count(state, ci); ++fi) {
            dsu_state_file_ownership_t own;
            dsu_u32 root_index = dsu_state_component_file_root_index(state, ci, fi);
            const char *path = dsu_state_component_file_path(state, ci, fi);
            if (root_index >= root_count) {
                st = DSU_STATUS_INTEGRITY_ERROR;
                break;
            }
            own = dsu_state_component_file_ownership(state, ci, fi);
            if (own == DSU_STATE_FILE_OWNERSHIP_OWNED) {
                st = dsu__str_list_push_dup(&owned_files[root_index], path);
                if (st == DSU_STATUS_SUCCESS) st = dsu__collect_parent_dirs(&owned_dirs[root_index], path ? path : "");
            } else if (own == DSU_STATE_FILE_OWNERSHIP_CACHE) {
                st = dsu__str_list_push_dup(&cache_files[root_index], path);
            } else {
                st = dsu__str_list_push_dup(&user_files[root_index], path);
            }
        }
    }

    if (st == DSU_STATUS_SUCCESS) {
        for (ri = 0u; ri < root_count; ++ri) {
            dsu__str_list_sort(&owned_files[ri]);
            dsu__str_list_sort(&user_files[ri]);
            dsu__str_list_sort(&cache_files[ri]);
            dsu__str_list_sort(&owned_dirs[ri]);
            dsu__str_list_dedup_sorted(&owned_dirs[ri]);
        }
    }

    dsu__blob_init(&b);
    if (st == DSU_STATUS_SUCCESS && format == DSU_REPORT_FORMAT_JSON) {
        st = dsu__blob_append_cstr(&b, "{\"roots\":[");
        for (ri = 0u; st == DSU_STATUS_SUCCESS && ri < root_count; ++ri) {
            if (ri != 0u) st = dsu__blob_put_u8(&b, (dsu_u8)',');
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "{\"index\":");
            if (st != DSU_STATUS_SUCCESS) break;
            sprintf(num, "%lu", (unsigned long)ri);
            st = dsu__blob_append_cstr(&b, num);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, ",\"role\":");
            if (st != DSU_STATUS_SUCCESS) break;
            sprintf(num, "%lu", (unsigned long)dsu_state_install_root_role(state, ri));
            st = dsu__blob_append_cstr(&b, num);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, ",\"path\":");
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__json_put_escaped(&b, dsu_state_install_root_path(state, ri));
            if (st != DSU_STATUS_SUCCESS) break;

            st = dsu__blob_append_cstr(&b, ",\"owned_files\":[");
            for (fi = 0u; st == DSU_STATUS_SUCCESS && fi < owned_files[ri].count; ++fi) {
                if (fi != 0u) st = dsu__blob_put_u8(&b, (dsu_u8)',');
                if (st != DSU_STATUS_SUCCESS) break;
                st = dsu__json_put_escaped(&b, owned_files[ri].items[fi]);
            }
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "]");

            if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"owned_dirs\":[");
            for (fi = 0u; st == DSU_STATUS_SUCCESS && fi < owned_dirs[ri].count; ++fi) {
                if (fi != 0u) st = dsu__blob_put_u8(&b, (dsu_u8)',');
                if (st != DSU_STATUS_SUCCESS) break;
                st = dsu__json_put_escaped(&b, owned_dirs[ri].items[fi]);
            }
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "]");

            if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"user_data_files\":[");
            for (fi = 0u; st == DSU_STATUS_SUCCESS && fi < user_files[ri].count; ++fi) {
                if (fi != 0u) st = dsu__blob_put_u8(&b, (dsu_u8)',');
                if (st != DSU_STATUS_SUCCESS) break;
                st = dsu__json_put_escaped(&b, user_files[ri].items[fi]);
            }
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "]");

            if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"cache_files\":[");
            for (fi = 0u; st == DSU_STATUS_SUCCESS && fi < cache_files[ri].count; ++fi) {
                if (fi != 0u) st = dsu__blob_put_u8(&b, (dsu_u8)',');
                if (st != DSU_STATUS_SUCCESS) break;
                st = dsu__json_put_escaped(&b, cache_files[ri].items[fi]);
            }
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "]}");
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "]}\n");
    } else if (st == DSU_STATUS_SUCCESS) {
        st = dsu__blob_append_cstr(&b, "Touched Paths\n");
        for (ri = 0u; st == DSU_STATUS_SUCCESS && ri < root_count; ++ri) {
            st = dsu__blob_append_cstr(&b, "Root[");
            if (st != DSU_STATUS_SUCCESS) break;
            sprintf(num, "%lu", (unsigned long)ri);
            st = dsu__blob_append_cstr(&b, num);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "] role=");
            if (st != DSU_STATUS_SUCCESS) break;
            sprintf(num, "%lu", (unsigned long)dsu_state_install_root_role(state, ri));
            st = dsu__blob_append_cstr(&b, num);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, " path=");
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, dsu_state_install_root_path(state, ri));
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "\n  owned_files:\n");
            for (fi = 0u; st == DSU_STATUS_SUCCESS && fi < owned_files[ri].count; ++fi) {
                st = dsu__blob_append_cstr(&b, "    - ");
                if (st != DSU_STATUS_SUCCESS) break;
                st = dsu__blob_append_cstr(&b, owned_files[ri].items[fi]);
                if (st != DSU_STATUS_SUCCESS) break;
                st = dsu__blob_append_cstr(&b, "\n");
            }
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "  owned_dirs:\n");
            for (fi = 0u; st == DSU_STATUS_SUCCESS && fi < owned_dirs[ri].count; ++fi) {
                st = dsu__blob_append_cstr(&b, "    - ");
                if (st != DSU_STATUS_SUCCESS) break;
                st = dsu__blob_append_cstr(&b, owned_dirs[ri].items[fi]);
                if (st != DSU_STATUS_SUCCESS) break;
                st = dsu__blob_append_cstr(&b, "\n");
            }
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "  user_data_files: ");
            if (st != DSU_STATUS_SUCCESS) break;
            sprintf(num, "%lu", (unsigned long)user_files[ri].count);
            st = dsu__blob_append_cstr(&b, num);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "\n  cache_files: ");
            if (st != DSU_STATUS_SUCCESS) break;
            sprintf(num, "%lu", (unsigned long)cache_files[ri].count);
            st = dsu__blob_append_cstr(&b, num);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "\n");
        }
    }

    if (st == DSU_STATUS_SUCCESS) {
        st = dsu__blob_to_cstr_take(&b, out_report);
    }
    dsu__blob_free(&b);

    for (ri = 0u; ri < root_count; ++ri) {
        dsu__str_list_free(&owned_files[ri]);
        dsu__str_list_free(&owned_dirs[ri]);
        dsu__str_list_free(&user_files[ri]);
        dsu__str_list_free(&cache_files[ri]);
    }
    dsu__free(owned_files);
    dsu__free(owned_dirs);
    dsu__free(user_files);
    dsu__free(cache_files);
    return st;
}

dsu_status_t dsu_report_uninstall_preview(dsu_ctx_t *ctx,
                                         const dsu_state_t *state,
                                         const char *const *components,
                                         dsu_u32 component_count,
                                         dsu_report_format_t format,
                                         char **out_report) {
    dsu_status_t st;
    dsu_blob_t b;
    dsu_u32 root_count;
    dsu_u32 comp_total;
    dsu_u32 ci;
    dsu_u32 fi;
    dsu_u32 ri;
    dsu_u32 preserve_user_data = 0u;
    dsu_u32 preserve_cache = 0u;
    dsu_u8 *selected = NULL;
    dsu__str_list_t selected_ids;
    char num[32];

    dsu__str_list_t *remove_files = NULL;
    dsu__str_list_t *remove_dirs = NULL;

    if (!ctx || !state || !out_report) return DSU_STATUS_INVALID_ARGS;
    *out_report = NULL;

    root_count = dsu_state_install_root_count(state);
    comp_total = dsu_state_component_count(state);
    if (root_count == 0u) return DSU_STATUS_INVALID_ARGS;

    selected = (dsu_u8 *)dsu__malloc(comp_total);
    if (!selected && comp_total != 0u) return DSU_STATUS_IO_ERROR;
    if (comp_total) memset(selected, 0, comp_total);

    if (!components || component_count == 0u) {
        for (ci = 0u; ci < comp_total; ++ci) selected[ci] = 1u;
    } else {
        for (ci = 0u; ci < component_count; ++ci) {
            dsu_u32 j;
            dsu_bool found = 0;
            const char *want = components[ci] ? components[ci] : "";
            for (j = 0u; j < comp_total; ++j) {
                const char *have = dsu_state_component_id(state, j);
                if (dsu__strcmp_bytes(want, have ? have : "") == 0) {
                    selected[j] = 1u;
                    found = 1;
                }
            }
            if (!found) {
                dsu__free(selected);
                return DSU_STATUS_MISSING_COMPONENT;
            }
        }
    }

    remove_files = (dsu__str_list_t *)dsu__malloc(root_count * (dsu_u32)sizeof(*remove_files));
    remove_dirs = (dsu__str_list_t *)dsu__malloc(root_count * (dsu_u32)sizeof(*remove_dirs));
    if (!remove_files || !remove_dirs) {
        dsu__free(remove_files);
        dsu__free(remove_dirs);
        dsu__free(selected);
        return DSU_STATUS_IO_ERROR;
    }
    for (ri = 0u; ri < root_count; ++ri) {
        dsu__str_list_init(&remove_files[ri]);
        dsu__str_list_init(&remove_dirs[ri]);
    }
    dsu__str_list_init(&selected_ids);

    st = DSU_STATUS_SUCCESS;
    for (ci = 0u; st == DSU_STATUS_SUCCESS && ci < comp_total; ++ci) {
        if (!selected[ci]) continue;
        st = dsu__str_list_push_dup(&selected_ids, dsu_state_component_id(state, ci));
        if (st != DSU_STATUS_SUCCESS) break;
        for (fi = 0u; st == DSU_STATUS_SUCCESS && fi < dsu_state_component_file_count(state, ci); ++fi) {
            dsu_state_file_ownership_t own = dsu_state_component_file_ownership(state, ci, fi);
            dsu_u32 root_index = dsu_state_component_file_root_index(state, ci, fi);
            const char *path = dsu_state_component_file_path(state, ci, fi);
            if (root_index >= root_count) {
                st = DSU_STATUS_INTEGRITY_ERROR;
                break;
            }
            if (own == DSU_STATE_FILE_OWNERSHIP_OWNED) {
                st = dsu__str_list_push_dup(&remove_files[root_index], path);
                if (st == DSU_STATUS_SUCCESS) st = dsu__collect_parent_dirs(&remove_dirs[root_index], path ? path : "");
            } else if (own == DSU_STATE_FILE_OWNERSHIP_CACHE) {
                preserve_cache += 1u;
            } else {
                preserve_user_data += 1u;
            }
        }
    }

    if (st == DSU_STATUS_SUCCESS) {
        dsu__str_list_sort(&selected_ids);
        dsu__str_list_dedup_sorted(&selected_ids);
        for (ri = 0u; ri < root_count; ++ri) {
            dsu__str_list_sort(&remove_files[ri]);
            dsu__str_list_sort(&remove_dirs[ri]);
            dsu__str_list_dedup_sorted(&remove_dirs[ri]);
        }
    }

    dsu__blob_init(&b);
    if (st == DSU_STATUS_SUCCESS && format == DSU_REPORT_FORMAT_JSON) {
        st = dsu__blob_append_cstr(&b, "{\"selected_components\":[");
        for (ci = 0u; st == DSU_STATUS_SUCCESS && ci < selected_ids.count; ++ci) {
            if (ci != 0u) st = dsu__blob_put_u8(&b, (dsu_u8)',');
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__json_put_escaped(&b, selected_ids.items[ci]);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "],\"preserve_user_data_files\":");
        if (st == DSU_STATUS_SUCCESS) {
            sprintf(num, "%lu", (unsigned long)preserve_user_data);
            st = dsu__blob_append_cstr(&b, num);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"preserve_cache_files\":");
        if (st == DSU_STATUS_SUCCESS) {
            sprintf(num, "%lu", (unsigned long)preserve_cache);
            st = dsu__blob_append_cstr(&b, num);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"remove\":[");
        for (ri = 0u; st == DSU_STATUS_SUCCESS && ri < root_count; ++ri) {
            if (ri != 0u) st = dsu__blob_put_u8(&b, (dsu_u8)',');
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "{\"root_index\":");
            if (st != DSU_STATUS_SUCCESS) break;
            sprintf(num, "%lu", (unsigned long)ri);
            st = dsu__blob_append_cstr(&b, num);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, ",\"root_path\":");
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__json_put_escaped(&b, dsu_state_install_root_path(state, ri));
            if (st != DSU_STATUS_SUCCESS) break;

            st = dsu__blob_append_cstr(&b, ",\"remove_owned_files\":[");
            for (fi = 0u; st == DSU_STATUS_SUCCESS && fi < remove_files[ri].count; ++fi) {
                if (fi != 0u) st = dsu__blob_put_u8(&b, (dsu_u8)',');
                if (st != DSU_STATUS_SUCCESS) break;
                st = dsu__json_put_escaped(&b, remove_files[ri].items[fi]);
            }
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "]");

            if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"remove_dirs_if_empty\":[");
            for (fi = 0u; st == DSU_STATUS_SUCCESS && fi < remove_dirs[ri].count; ++fi) {
                if (fi != 0u) st = dsu__blob_put_u8(&b, (dsu_u8)',');
                if (st != DSU_STATUS_SUCCESS) break;
                st = dsu__json_put_escaped(&b, remove_dirs[ri].items[fi]);
            }
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "]}");
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "]}\n");
    } else if (st == DSU_STATUS_SUCCESS) {
        st = dsu__blob_append_cstr(&b, "Uninstall Preview\nSelected components:\n");
        for (ci = 0u; st == DSU_STATUS_SUCCESS && ci < selected_ids.count; ++ci) {
            st = dsu__blob_append_cstr(&b, "  - ");
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, selected_ids.items[ci]);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "\n");
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "Preserve user data files: ");
        if (st == DSU_STATUS_SUCCESS) {
            sprintf(num, "%lu", (unsigned long)preserve_user_data);
            st = dsu__blob_append_cstr(&b, num);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "\nPreserve cache files: ");
        if (st == DSU_STATUS_SUCCESS) {
            sprintf(num, "%lu", (unsigned long)preserve_cache);
            st = dsu__blob_append_cstr(&b, num);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "\n");
        for (ri = 0u; st == DSU_STATUS_SUCCESS && ri < root_count; ++ri) {
            st = dsu__blob_append_cstr(&b, "Root[");
            if (st != DSU_STATUS_SUCCESS) break;
            sprintf(num, "%lu", (unsigned long)ri);
            st = dsu__blob_append_cstr(&b, num);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "] remove_owned_files:\n");
            for (fi = 0u; st == DSU_STATUS_SUCCESS && fi < remove_files[ri].count; ++fi) {
                st = dsu__blob_append_cstr(&b, "  - ");
                if (st != DSU_STATUS_SUCCESS) break;
                st = dsu__blob_append_cstr(&b, remove_files[ri].items[fi]);
                if (st != DSU_STATUS_SUCCESS) break;
                st = dsu__blob_append_cstr(&b, "\n");
            }
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "Root[");
            if (st != DSU_STATUS_SUCCESS) break;
            sprintf(num, "%lu", (unsigned long)ri);
            st = dsu__blob_append_cstr(&b, num);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "] remove_dirs_if_empty:\n");
            for (fi = 0u; st == DSU_STATUS_SUCCESS && fi < remove_dirs[ri].count; ++fi) {
                st = dsu__blob_append_cstr(&b, "  - ");
                if (st != DSU_STATUS_SUCCESS) break;
                st = dsu__blob_append_cstr(&b, remove_dirs[ri].items[fi]);
                if (st != DSU_STATUS_SUCCESS) break;
                st = dsu__blob_append_cstr(&b, "\n");
            }
        }
    }

    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_to_cstr_take(&b, out_report);
    dsu__blob_free(&b);

    for (ri = 0u; ri < root_count; ++ri) {
        dsu__str_list_free(&remove_files[ri]);
        dsu__str_list_free(&remove_dirs[ri]);
    }
    dsu__free(remove_files);
    dsu__free(remove_dirs);
    dsu__str_list_free(&selected_ids);
    dsu__free(selected);
    return st;
}

dsu_status_t dsu_report_verify(dsu_ctx_t *ctx,
                              const dsu_state_t *state,
                              dsu_report_format_t format,
                              char **out_report,
                              dsu_report_verify_summary_t *out_summary) {
    dsu_status_t st;
    dsu_blob_t b;
    dsu_report_verify_summary_t sum;
    dsu_fs_options_t fs_opts;
    dsu_fs_t *fs = NULL;
    dsu_u32 root_count;
    dsu_u32 comp_total;
    dsu_u32 total_files = 0u;
    dsu_u32 ci;
    dsu_u32 fi;
    dsu_u32 ri;
    const char **roots = NULL;
    dsu__expected_item_t *expected = NULL;
    dsu_u32 expected_count = 0u;

    dsu__str_list_t missing;
    dsu__str_list_t modified;
    dsu__str_list_t extra;
    dsu__str_list_t errors;
    dsu_u32 i;
    char num[32];

    if (!ctx || !state || !out_report) return DSU_STATUS_INVALID_ARGS;
    *out_report = NULL;
    dsu_report_verify_summary_init(&sum);
    if (out_summary) {
        dsu_report_verify_summary_init(out_summary);
        if (out_summary->struct_version != 1u || out_summary->struct_size < (dsu_u32)sizeof(*out_summary)) {
            return DSU_STATUS_INVALID_ARGS;
        }
    }

    root_count = dsu_state_install_root_count(state);
    comp_total = dsu_state_component_count(state);
    if (root_count == 0u) return DSU_STATUS_INVALID_ARGS;

    dsu__str_list_init(&missing);
    dsu__str_list_init(&modified);
    dsu__str_list_init(&extra);
    dsu__str_list_init(&errors);
    dsu__blob_init(&b);

    /* Build expected set for "extra" detection (all file entries, any ownership). */
    for (ci = 0u; ci < comp_total; ++ci) {
        dsu_u32 n = dsu_state_component_file_count(state, ci);
        if (total_files > 0xFFFFFFFFu - n) {
            st = DSU_STATUS_IO_ERROR;
            goto done;
        }
        total_files += n;
    }
    expected = (dsu__expected_item_t *)dsu__malloc(total_files * (dsu_u32)sizeof(*expected));
    if (!expected && total_files != 0u) {
        st = DSU_STATUS_IO_ERROR;
        goto done;
    }
    expected_count = 0u;
    for (ci = 0u; ci < comp_total; ++ci) {
        for (fi = 0u; fi < dsu_state_component_file_count(state, ci); ++fi) {
            dsu_u32 root_index = dsu_state_component_file_root_index(state, ci, fi);
            const char *path = dsu_state_component_file_path(state, ci, fi);
            if (root_index >= root_count) {
                st = DSU_STATUS_INTEGRITY_ERROR;
                goto done;
            }
            expected[expected_count].root_index = root_index;
            expected[expected_count].path = path ? path : "";
            expected_count += 1u;
        }
    }
    if (expected_count > 1u) {
        qsort(expected, (size_t)expected_count, sizeof(*expected), dsu__expected_item_cmp);
    }

    roots = (const char **)dsu__malloc(root_count * (dsu_u32)sizeof(*roots));
    if (!roots) {
        st = DSU_STATUS_IO_ERROR;
        goto done;
    }
    for (ri = 0u; ri < root_count; ++ri) {
        roots[ri] = dsu_state_install_root_path(state, ri);
    }
    dsu_fs_options_init(&fs_opts);
    fs_opts.allowed_roots = roots;
    fs_opts.allowed_root_count = root_count;
    st = dsu_fs_create(ctx, &fs_opts, &fs);
    if (st != DSU_STATUS_SUCCESS) goto done;

    /* Verify owned files. */
    for (ci = 0u; ci < comp_total; ++ci) {
        for (fi = 0u; fi < dsu_state_component_file_count(state, ci); ++fi) {
            dsu_state_file_ownership_t own = dsu_state_component_file_ownership(state, ci, fi);
            dsu_u32 root_index = dsu_state_component_file_root_index(state, ci, fi);
            const char *path = dsu_state_component_file_path(state, ci, fi);
            dsu_u8 sha[32];
            dsu_u64 actual64;
            dsu_u64 expected64;

            if (own != DSU_STATE_FILE_OWNERSHIP_OWNED) continue;
            sum.checked += 1u;

            st = dsu_fs_hash_file(fs, root_index, path ? path : "", sha);
            if (st != DSU_STATUS_SUCCESS) {
                sum.missing += 1u;
                if (dsu__str_list_push_root_path(&missing, root_index, path ? path : "") != DSU_STATUS_SUCCESS) {
                    st = DSU_STATUS_IO_ERROR;
                    goto done;
                }
                if (st != DSU_STATUS_IO_ERROR) {
                    sum.errors += 1u;
                    if (dsu__str_list_push_root_path(&errors, root_index, path ? path : "") != DSU_STATUS_SUCCESS) {
                        st = DSU_STATUS_IO_ERROR;
                        goto done;
                    }
                }
                st = DSU_STATUS_SUCCESS;
                continue;
            }

            actual64 = dsu_digest64_bytes(sha, 32u);
            expected64 = dsu_state_component_file_digest64(state, ci, fi);
            if (actual64 != expected64) {
                sum.modified += 1u;
                if (dsu__str_list_push_root_path(&modified, root_index, path ? path : "") != DSU_STATUS_SUCCESS) {
                    st = DSU_STATUS_IO_ERROR;
                    goto done;
                }
            } else {
                sum.ok += 1u;
            }
        }
    }

    /* Extra files: scan roots (excluding .dsu* segments). */
    for (ri = 0u; ri < root_count; ++ri) {
        st = dsu__scan_extras_dir(expected, expected_count, ri, dsu_state_install_root_path(state, ri), "", &extra);
        if (st != DSU_STATUS_SUCCESS) {
            sum.errors += 1u;
            st = DSU_STATUS_SUCCESS;
        }
    }
    dsu__str_list_sort(&missing);
    dsu__str_list_dedup_sorted(&missing);
    dsu__str_list_sort(&modified);
    dsu__str_list_dedup_sorted(&modified);
    dsu__str_list_sort(&extra);
    dsu__str_list_dedup_sorted(&extra);
    dsu__str_list_sort(&errors);
    dsu__str_list_dedup_sorted(&errors);
    sum.missing = missing.count;
    sum.modified = modified.count;
    sum.extra = extra.count;
    sum.errors = errors.count;

    if (format == DSU_REPORT_FORMAT_JSON) {
        st = dsu__blob_append_cstr(&b, "{\"checked\":");
        if (st == DSU_STATUS_SUCCESS) {
            sprintf(num, "%lu", (unsigned long)sum.checked);
            st = dsu__blob_append_cstr(&b, num);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"ok\":");
        if (st == DSU_STATUS_SUCCESS) {
            sprintf(num, "%lu", (unsigned long)sum.ok);
            st = dsu__blob_append_cstr(&b, num);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"missing\":");
        if (st == DSU_STATUS_SUCCESS) {
            sprintf(num, "%lu", (unsigned long)missing.count);
            st = dsu__blob_append_cstr(&b, num);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"modified\":");
        if (st == DSU_STATUS_SUCCESS) {
            sprintf(num, "%lu", (unsigned long)modified.count);
            st = dsu__blob_append_cstr(&b, num);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"extra\":");
        if (st == DSU_STATUS_SUCCESS) {
            sprintf(num, "%lu", (unsigned long)extra.count);
            st = dsu__blob_append_cstr(&b, num);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"errors\":");
        if (st == DSU_STATUS_SUCCESS) {
            sprintf(num, "%lu", (unsigned long)errors.count);
            st = dsu__blob_append_cstr(&b, num);
        }

        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"missing_paths\":[");
        for (i = 0u; st == DSU_STATUS_SUCCESS && i < missing.count; ++i) {
            if (i != 0u) st = dsu__blob_put_u8(&b, (dsu_u8)',');
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__json_put_escaped(&b, missing.items[i]);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "]");

        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"modified_paths\":[");
        for (i = 0u; st == DSU_STATUS_SUCCESS && i < modified.count; ++i) {
            if (i != 0u) st = dsu__blob_put_u8(&b, (dsu_u8)',');
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__json_put_escaped(&b, modified.items[i]);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "]");

        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"extra_paths\":[");
        for (i = 0u; st == DSU_STATUS_SUCCESS && i < extra.count; ++i) {
            if (i != 0u) st = dsu__blob_put_u8(&b, (dsu_u8)',');
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__json_put_escaped(&b, extra.items[i]);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "]");

        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"error_paths\":[");
        for (i = 0u; st == DSU_STATUS_SUCCESS && i < errors.count; ++i) {
            if (i != 0u) st = dsu__blob_put_u8(&b, (dsu_u8)',');
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__json_put_escaped(&b, errors.items[i]);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "]}\n");
    } else {
        st = dsu__blob_append_cstr(&b, "Verify Report\nChecked: ");
        if (st == DSU_STATUS_SUCCESS) {
            sprintf(num, "%lu", (unsigned long)sum.checked);
            st = dsu__blob_append_cstr(&b, num);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, " OK: ");
        if (st == DSU_STATUS_SUCCESS) {
            sprintf(num, "%lu", (unsigned long)sum.ok);
            st = dsu__blob_append_cstr(&b, num);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, " Missing: ");
        if (st == DSU_STATUS_SUCCESS) {
            sprintf(num, "%lu", (unsigned long)missing.count);
            st = dsu__blob_append_cstr(&b, num);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, " Modified: ");
        if (st == DSU_STATUS_SUCCESS) {
            sprintf(num, "%lu", (unsigned long)modified.count);
            st = dsu__blob_append_cstr(&b, num);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, " Extra: ");
        if (st == DSU_STATUS_SUCCESS) {
            sprintf(num, "%lu", (unsigned long)extra.count);
            st = dsu__blob_append_cstr(&b, num);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, " Errors: ");
        if (st == DSU_STATUS_SUCCESS) {
            sprintf(num, "%lu", (unsigned long)errors.count);
            st = dsu__blob_append_cstr(&b, num);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "\n");

        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "Missing:\n");
        for (i = 0u; st == DSU_STATUS_SUCCESS && i < missing.count; ++i) {
            st = dsu__blob_append_cstr(&b, "  - ");
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, missing.items[i]);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "\n");
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "Modified:\n");
        for (i = 0u; st == DSU_STATUS_SUCCESS && i < modified.count; ++i) {
            st = dsu__blob_append_cstr(&b, "  - ");
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, modified.items[i]);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "\n");
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "Extra:\n");
        for (i = 0u; st == DSU_STATUS_SUCCESS && i < extra.count; ++i) {
            st = dsu__blob_append_cstr(&b, "  - ");
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, extra.items[i]);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "\n");
        }
        if (st == DSU_STATUS_SUCCESS && errors.count) st = dsu__blob_append_cstr(&b, "Errors:\n");
        for (i = 0u; st == DSU_STATUS_SUCCESS && i < errors.count; ++i) {
            st = dsu__blob_append_cstr(&b, "  - ");
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, errors.items[i]);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "\n");
        }
    }

    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_to_cstr_take(&b, out_report);

done:
    if (out_summary) {
        *out_summary = sum;
    }
    dsu__blob_free(&b);
    dsu__str_list_free(&missing);
    dsu__str_list_free(&modified);
    dsu__str_list_free(&extra);
    dsu__str_list_free(&errors);
    if (fs) dsu_fs_destroy(ctx, fs);
    dsu__free(roots);
    dsu__free(expected);
    return st;
}

dsu_status_t dsu_report_corruption_assessment(dsu_ctx_t *ctx,
                                             const dsu_state_t *state,
                                             const dsu_log_t *audit_log,
                                             dsu_report_format_t format,
                                             char **out_report) {
    dsu_status_t st;
    dsu_blob_t b;
    dsu__str_list_t issues;
    dsu_u32 ci;
    dsu_u32 fi;
    dsu_u32 root_count;
    char num[32];

    if (!ctx || !state || !out_report) return DSU_STATUS_INVALID_ARGS;
    *out_report = NULL;

    dsu__str_list_init(&issues);
    dsu__blob_init(&b);

    root_count = dsu_state_install_root_count(state);
    if (dsu_state_product_id(state)[0] == '\0') (void)dsu__str_list_push_dup(&issues, "missing product_id");
    if (dsu_state_product_version_installed(state)[0] == '\0') (void)dsu__str_list_push_dup(&issues, "missing product_version_installed");
    if (dsu_state_platform(state)[0] == '\0') (void)dsu__str_list_push_dup(&issues, "missing platform_triple");
    if (root_count == 0u) (void)dsu__str_list_push_dup(&issues, "no install_roots");

    for (ci = 0u; ci < dsu_state_component_count(state); ++ci) {
        const char *cid = dsu_state_component_id(state, ci);
        if (!cid || cid[0] == '\0') {
            (void)dsu__str_list_push_dup(&issues, "component with empty id");
        }
        for (fi = 0u; fi < dsu_state_component_file_count(state, ci); ++fi) {
            dsu_u32 rix = dsu_state_component_file_root_index(state, ci, fi);
            const char *p = dsu_state_component_file_path(state, ci, fi);
            if (rix >= root_count) {
                (void)dsu__str_list_push_dup(&issues, "file references invalid root_index");
                break;
            }
            if (!p || p[0] == '\0') {
                (void)dsu__str_list_push_dup(&issues, "file with empty relative path");
                break;
            }
        }
    }

    if (dsu_state_has_last_audit_log_digest64(state) && !audit_log) {
        (void)dsu__str_list_push_dup(&issues, "state has last_audit_log_digest64 but no audit_log provided");
    }

    if (format == DSU_REPORT_FORMAT_JSON) {
        st = dsu__blob_append_cstr(&b, "{\"issues\":[");
        for (ci = 0u; st == DSU_STATUS_SUCCESS && ci < issues.count; ++ci) {
            if (ci != 0u) st = dsu__blob_put_u8(&b, (dsu_u8)',');
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__json_put_escaped(&b, issues.items[ci]);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "],\"audit_log_present\":");
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, audit_log ? "true" : "false");
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"audit_event_count\":");
        if (st == DSU_STATUS_SUCCESS) {
            sprintf(num, "%lu", (unsigned long)(audit_log ? dsu_log_event_count(audit_log) : 0u));
            st = dsu__blob_append_cstr(&b, num);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"note\":");
        if (st == DSU_STATUS_SUCCESS) st = dsu__json_put_escaped(&b, "Audit log is not authoritative; installed state is authoritative.");
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "}\n");
    } else {
        st = dsu__blob_append_cstr(&b, "Corruption Assessment\n");
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "Issues:\n");
        for (ci = 0u; st == DSU_STATUS_SUCCESS && ci < issues.count; ++ci) {
            st = dsu__blob_append_cstr(&b, "  - ");
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, issues.items[ci]);
            if (st != DSU_STATUS_SUCCESS) break;
            st = dsu__blob_append_cstr(&b, "\n");
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "Audit log present: ");
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, audit_log ? "yes" : "no");
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "\nAudit events: ");
        if (st == DSU_STATUS_SUCCESS) {
            sprintf(num, "%lu", (unsigned long)(audit_log ? dsu_log_event_count(audit_log) : 0u));
            st = dsu__blob_append_cstr(&b, num);
        }
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "\n");
    }

    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_to_cstr_take(&b, out_report);
    dsu__blob_free(&b);
    dsu__str_list_free(&issues);
    return st;
}
