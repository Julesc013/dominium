/*
FILE: source/dominium/setup/core/src/resolve/dsu_resolve.c
MODULE: Dominium Setup
PURPOSE: Deterministic component resolution engine (Plan S-3).
*/
#include "../../include/dsu/dsu_resolve.h"
#include "../../include/dsu/dsu_log.h"
#include "../../include/dsu/dsu_fs.h"

#include "../dsu_ctx_internal.h"
#include "../fs/dsu_platform_iface.h"
#include "../log/dsu_events.h"
#include "../util/dsu_util_internal.h"

#include <string.h>

typedef struct dsu__resolve_log_event_t {
    dsu_u8 code;
    char *a;
    char *b;
} dsu__resolve_log_event_t;

typedef struct dsu__resolved_component_t {
    char *id;
    char *version;
    dsu_u8 source;
    dsu_u8 action;
    dsu_u16 reserved16;
} dsu__resolved_component_t;

struct dsu_resolve_result {
    dsu_u32 struct_version;

    dsu_u8 operation;
    dsu_u8 scope;
    dsu_u8 reserved8[2];

    char *platform;
    char *product_id;
    char *product_version;
    char *install_root;

    dsu_u64 manifest_digest64;
    dsu_u64 resolved_digest64;

    dsu_u32 component_count;
    dsu__resolved_component_t *components;

    dsu_u32 log_count;
    dsu_u32 log_cap;
    dsu__resolve_log_event_t *log_events;
};

typedef struct dsu__graph_dep_t {
    dsu_u32 target_index; /* 0xFFFFFFFFu => not in manifest */
    const char *target_id;
    dsu_u8 constraint_kind;
    const char *constraint_version;
} dsu__graph_dep_t;

typedef struct dsu__graph_node_t {
    const char *id;
    const char *version;
    dsu_u8 kind;
    dsu_u32 flags;

    dsu_u32 dep_count;
    dsu__graph_dep_t *deps;
} dsu__graph_node_t;

typedef struct dsu__graph_t {
    dsu_u32 node_count;
    dsu__graph_node_t *nodes;
} dsu__graph_t;

typedef struct dsu__pin_rule_t {
    char *component_id;
    char *version;
} dsu__pin_rule_t;

static void dsu__resolve_log_event_free(dsu__resolve_log_event_t *e) {
    if (!e) {
        return;
    }
    dsu__free(e->a);
    dsu__free(e->b);
    e->a = NULL;
    e->b = NULL;
}

static void dsu__resolve_result_free(dsu_resolve_result_t *r) {
    dsu_u32 i;
    if (!r) {
        return;
    }
    dsu__free(r->platform);
    dsu__free(r->product_id);
    dsu__free(r->product_version);
    dsu__free(r->install_root);

    for (i = 0u; i < r->component_count; ++i) {
        dsu__free(r->components[i].id);
        dsu__free(r->components[i].version);
    }
    dsu__free(r->components);
    r->components = NULL;
    r->component_count = 0u;

    for (i = 0u; i < r->log_count; ++i) {
        dsu__resolve_log_event_free(&r->log_events[i]);
    }
    dsu__free(r->log_events);
    r->log_events = NULL;
    r->log_count = 0u;
    r->log_cap = 0u;
}

static dsu_status_t dsu__log_push(dsu_resolve_result_t *r,
                                 dsu_u8 code,
                                 const char *a,
                                 const char *b) {
    dsu_u32 count;
    dsu_u32 cap;
    dsu__resolve_log_event_t *p;
    dsu__resolve_log_event_t *e;

    if (!r) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (!a) a = "";
    if (!b) b = "";

    count = r->log_count;
    cap = r->log_cap;
    if (count == cap) {
        dsu_u32 new_cap = (cap == 0u) ? 8u : (cap * 2u);
        p = (dsu__resolve_log_event_t *)dsu__realloc(r->log_events,
                                                     new_cap * (dsu_u32)sizeof(*p));
        if (!p) {
            return DSU_STATUS_IO_ERROR;
        }
        r->log_events = p;
        r->log_cap = new_cap;
    }

    e = &r->log_events[count];
    memset(e, 0, sizeof(*e));
    e->code = code;
    e->a = dsu__strdup(a);
    e->b = dsu__strdup(b);
    if (!e->a || !e->b) {
        dsu__resolve_log_event_free(e);
        return DSU_STATUS_IO_ERROR;
    }
    r->log_count = count + 1u;
    return DSU_STATUS_SUCCESS;
}

void dsu_resolve_request_init(dsu_resolve_request_t *req) {
    if (!req) {
        return;
    }
    memset(req, 0, sizeof(*req));
    req->struct_size = (dsu_u32)sizeof(*req);
    req->struct_version = 2u;
    req->operation = DSU_RESOLVE_OPERATION_INSTALL;
    req->scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    req->allow_prerelease = DSU_FALSE;
    req->install_roots = NULL;
    req->install_root_count = 0u;
}

static dsu_status_t dsu__dup_lower_ascii_id(const char *s, char **out) {
    dsu_status_t st;
    char *t;
    if (!out) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out = NULL;
    if (!s || s[0] == '\0') {
        return DSU_STATUS_INVALID_REQUEST;
    }
    t = dsu__strdup(s);
    if (!t) {
        return DSU_STATUS_IO_ERROR;
    }
    st = dsu__ascii_to_lower_inplace(t);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(t);
        return DSU_STATUS_INVALID_REQUEST;
    }
    if (!dsu__is_ascii_id(t)) {
        dsu__free(t);
        return DSU_STATUS_INVALID_REQUEST;
    }
    *out = t;
    return DSU_STATUS_SUCCESS;
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

static dsu_status_t dsu__normalize_id_list(const char *const *in_items,
                                          dsu_u32 in_count,
                                          char ***out_items,
                                          dsu_u32 *out_count) {
    dsu_u32 i;
    char **tmp;
    dsu_u32 w;

    if (!out_items || !out_count) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_items = NULL;
    *out_count = 0u;
    if (in_count == 0u) {
        return DSU_STATUS_SUCCESS;
    }
    if (!in_items) {
        return DSU_STATUS_INVALID_ARGS;
    }

    tmp = (char **)dsu__malloc(in_count * (dsu_u32)sizeof(*tmp));
    if (!tmp) {
        return DSU_STATUS_IO_ERROR;
    }
    memset(tmp, 0, (size_t)in_count * sizeof(*tmp));

    for (i = 0u; i < in_count; ++i) {
        dsu_status_t st = dsu__dup_lower_ascii_id(in_items[i], &tmp[i]);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free_str_list(tmp, in_count);
            return st;
        }
    }

    dsu__sort_str_ptrs(tmp, in_count);

    /* De-dup in place (stable). */
    w = 0u;
    for (i = 0u; i < in_count; ++i) {
        if (w == 0u || dsu__strcmp_bytes(tmp[w - 1u], tmp[i]) != 0) {
            tmp[w++] = tmp[i];
        } else {
            dsu__free(tmp[i]);
        }
    }

    *out_items = tmp;
    *out_count = w;
    return DSU_STATUS_SUCCESS;
}

static dsu_bool dsu__sorted_str_list_contains(char *const *items, dsu_u32 count, const char *id) {
    dsu_u32 lo;
    dsu_u32 hi;

    if (!items || count == 0u || !id) {
        return DSU_FALSE;
    }

    lo = 0u;
    hi = count;
    while (lo < hi) {
        dsu_u32 mid = lo + ((hi - lo) / 2u);
        int c = dsu__strcmp_bytes(items[mid], id);
        if (c == 0) {
            return DSU_TRUE;
        }
        if (c < 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return DSU_FALSE;
}

static dsu_status_t dsu__find_component_index(const dsu_manifest_t *manifest,
                                             const char *component_id,
                                             dsu_u32 *out_index) {
    dsu_u32 lo;
    dsu_u32 hi;
    dsu_u32 count;

    if (!out_index) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_index = 0u;
    if (!manifest || !component_id || component_id[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }

    count = dsu_manifest_component_count(manifest);
    lo = 0u;
    hi = count;
    while (lo < hi) {
        dsu_u32 mid = lo + ((hi - lo) / 2u);
        const char *mid_id = dsu_manifest_component_id(manifest, mid);
        int c = dsu__strcmp_bytes(mid_id ? mid_id : "", component_id);
        if (c == 0) {
            *out_index = mid;
            return DSU_STATUS_SUCCESS;
        }
        if (c < 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return DSU_STATUS_MISSING_COMPONENT;
}

static const char *dsu__state_find_component_version(const dsu_state_t *state, const char *component_id) {
    dsu_u32 lo;
    dsu_u32 hi;
    dsu_u32 count;

    if (!state || !component_id || component_id[0] == '\0') {
        return NULL;
    }

    count = dsu_state_component_count(state);
    lo = 0u;
    hi = count;
    while (lo < hi) {
        dsu_u32 mid = lo + ((hi - lo) / 2u);
        const char *mid_id = dsu_state_component_id(state, mid);
        int c = dsu__strcmp_bytes(mid_id ? mid_id : "", component_id);
        if (c == 0) {
            return dsu_state_component_version(state, mid);
        }
        if (c < 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return NULL;
}

static void dsu__graph_free(dsu__graph_t *g) {
    dsu_u32 i;
    if (!g) {
        return;
    }
    for (i = 0u; i < g->node_count; ++i) {
        dsu__free(g->nodes[i].deps);
        g->nodes[i].deps = NULL;
        g->nodes[i].dep_count = 0u;
    }
    dsu__free(g->nodes);
    g->nodes = NULL;
    g->node_count = 0u;
}

static dsu_status_t dsu__graph_build(const dsu_manifest_t *manifest, dsu__graph_t *out_g) {
    dsu_u32 i;
    dsu_u32 n;
    dsu__graph_t g;

    if (!manifest || !out_g) {
        return DSU_STATUS_INVALID_ARGS;
    }
    memset(&g, 0, sizeof(g));

    n = dsu_manifest_component_count(manifest);
    g.node_count = n;
    g.nodes = (dsu__graph_node_t *)dsu__malloc(n * (dsu_u32)sizeof(*g.nodes));
    if (!g.nodes && n != 0u) {
        return DSU_STATUS_IO_ERROR;
    }
    if (n != 0u) {
        memset(g.nodes, 0, (size_t)n * sizeof(*g.nodes));
    }

    for (i = 0u; i < n; ++i) {
        dsu__graph_node_t *node = &g.nodes[i];
        dsu_u32 dep_count = dsu_manifest_component_dependency_count(manifest, i);
        dsu_u32 j;

        node->id = dsu_manifest_component_id(manifest, i);
        node->version = dsu_manifest_component_version(manifest, i);
        node->kind = (dsu_u8)dsu_manifest_component_kind(manifest, i);
        node->flags = dsu_manifest_component_flags(manifest, i);

        node->dep_count = dep_count;
        node->deps = (dsu__graph_dep_t *)dsu__malloc(dep_count * (dsu_u32)sizeof(*node->deps));
        if (!node->deps && dep_count != 0u) {
            dsu__graph_free(&g);
            return DSU_STATUS_IO_ERROR;
        }
        if (dep_count != 0u) {
            memset(node->deps, 0, (size_t)dep_count * sizeof(*node->deps));
        }

        for (j = 0u; j < dep_count; ++j) {
            dsu__graph_dep_t *d = &node->deps[j];
            const char *dep_id = dsu_manifest_component_dependency_id(manifest, i, j);
            dsu_status_t st;
            dsu_u32 dep_index = 0u;

            d->target_id = dep_id ? dep_id : "";
            d->constraint_kind = (dsu_u8)dsu_manifest_component_dependency_constraint_kind(manifest, i, j);
            d->constraint_version = dsu_manifest_component_dependency_constraint_version(manifest, i, j);

            st = dsu__find_component_index(manifest, d->target_id, &dep_index);
            if (st == DSU_STATUS_SUCCESS) {
                d->target_index = dep_index;
            } else {
                d->target_index = 0xFFFFFFFFu;
            }
        }
    }

    *out_g = g;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__parse_u32_dec(const char **io_p, dsu_u32 *out_v) {
    const char *p;
    dsu_u32 v;
    dsu_u32 digits;

    if (!io_p || !out_v) {
        return DSU_STATUS_INVALID_ARGS;
    }
    p = *io_p;
    v = 0u;
    digits = 0u;
    while (*p >= '0' && *p <= '9') {
        dsu_u32 d = (dsu_u32)(*p - '0');
        if (v > (0xFFFFFFFFu / 10u)) {
            return DSU_STATUS_PARSE_ERROR;
        }
        v *= 10u;
        if (v > 0xFFFFFFFFu - d) {
            return DSU_STATUS_PARSE_ERROR;
        }
        v += d;
        ++p;
        ++digits;
    }
    if (digits == 0u) {
        return DSU_STATUS_PARSE_ERROR;
    }
    *io_p = p;
    *out_v = v;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__semverish_split(const char *s,
                                        dsu_u32 *out_major,
                                        dsu_u32 *out_minor,
                                        dsu_u32 *out_patch,
                                        const char **out_suffix) {
    const char *p;
    dsu_u32 major;
    dsu_u32 minor;
    dsu_u32 patch;
    dsu_status_t st;

    if (!s || !out_major || !out_minor || !out_patch || !out_suffix) {
        return DSU_STATUS_INVALID_ARGS;
    }

    p = s;
    st = dsu__parse_u32_dec(&p, &major);
    if (st != DSU_STATUS_SUCCESS || *p != '.') {
        return DSU_STATUS_PARSE_ERROR;
    }
    ++p;
    st = dsu__parse_u32_dec(&p, &minor);
    if (st != DSU_STATUS_SUCCESS || *p != '.') {
        return DSU_STATUS_PARSE_ERROR;
    }
    ++p;
    st = dsu__parse_u32_dec(&p, &patch);
    if (st != DSU_STATUS_SUCCESS) {
        return DSU_STATUS_PARSE_ERROR;
    }

    if (*p == '\0') {
        *out_suffix = NULL;
    } else if (*p == '-') {
        ++p;
        if (*p == '\0') {
            return DSU_STATUS_PARSE_ERROR;
        }
        *out_suffix = p;
    } else {
        return DSU_STATUS_PARSE_ERROR;
    }

    *out_major = major;
    *out_minor = minor;
    *out_patch = patch;
    return DSU_STATUS_SUCCESS;
}

static int dsu__semverish_cmp(const char *a, const char *b) {
    dsu_u32 a_major, a_minor, a_patch;
    dsu_u32 b_major, b_minor, b_patch;
    const char *a_suf;
    const char *b_suf;
    if (!a) a = "";
    if (!b) b = "";
    if (dsu__semverish_split(a, &a_major, &a_minor, &a_patch, &a_suf) != DSU_STATUS_SUCCESS) {
        return dsu__strcmp_bytes(a, b);
    }
    if (dsu__semverish_split(b, &b_major, &b_minor, &b_patch, &b_suf) != DSU_STATUS_SUCCESS) {
        return dsu__strcmp_bytes(a, b);
    }

    if (a_major != b_major) return (a_major < b_major) ? -1 : 1;
    if (a_minor != b_minor) return (a_minor < b_minor) ? -1 : 1;
    if (a_patch != b_patch) return (a_patch < b_patch) ? -1 : 1;

    if (!a_suf && !b_suf) return 0;
    if (!a_suf && b_suf) return 1;  /* release > prerelease */
    if (a_suf && !b_suf) return -1; /* prerelease < release */
    return dsu__strcmp_bytes(a_suf, b_suf);
}

static dsu_bool dsu__has_prerelease_suffix(const char *v) {
    const char *p;
    if (!v) {
        return DSU_FALSE;
    }
    p = v;
    while (*p) {
        if (*p == '-') {
            return DSU_TRUE;
        }
        ++p;
    }
    return DSU_FALSE;
}

static dsu_bool dsu__satisfies_constraint(const char *candidate_version,
                                         dsu_u8 kind,
                                         const char *constraint_version) {
    if (!candidate_version) candidate_version = "";
    if (!constraint_version) constraint_version = "";

    switch ((dsu_manifest_version_constraint_kind_t)kind) {
        case DSU_MANIFEST_VERSION_CONSTRAINT_ANY:
            return DSU_TRUE;
        case DSU_MANIFEST_VERSION_CONSTRAINT_EXACT:
            return (dsu__strcmp_bytes(candidate_version, constraint_version) == 0) ? DSU_TRUE : DSU_FALSE;
        case DSU_MANIFEST_VERSION_CONSTRAINT_AT_LEAST:
            return (dsu__semverish_cmp(candidate_version, constraint_version) >= 0) ? DSU_TRUE : DSU_FALSE;
        default:
            return DSU_FALSE;
    }
}

static void dsu__pins_free(dsu__pin_rule_t *pins, dsu_u32 count) {
    dsu_u32 i;
    if (!pins) {
        return;
    }
    for (i = 0u; i < count; ++i) {
        dsu__free(pins[i].component_id);
        dsu__free(pins[i].version);
        pins[i].component_id = NULL;
        pins[i].version = NULL;
    }
    dsu__free(pins);
}

static int dsu__pin_cmp(const dsu__pin_rule_t *a, const dsu__pin_rule_t *b) {
    return dsu__strcmp_bytes(a ? a->component_id : NULL, b ? b->component_id : NULL);
}

static void dsu__sort_pins(dsu__pin_rule_t *pins, dsu_u32 count) {
    dsu_u32 i;
    if (!pins || count < 2u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dsu__pin_rule_t key = pins[i];
        dsu_u32 j = i;
        while (j > 0u && dsu__pin_cmp(&pins[j - 1u], &key) > 0) {
            pins[j] = pins[j - 1u];
            --j;
        }
        pins[j] = key;
    }
}

static dsu_status_t dsu__normalize_pins(const dsu_resolve_pin_t *in_pins,
                                       dsu_u32 in_count,
                                       dsu__pin_rule_t **out_pins,
                                       dsu_u32 *out_count) {
    dsu_u32 i;
    dsu__pin_rule_t *pins;

    if (!out_pins || !out_count) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_pins = NULL;
    *out_count = 0u;
    if (in_count == 0u) {
        return DSU_STATUS_SUCCESS;
    }
    if (!in_pins) {
        return DSU_STATUS_INVALID_ARGS;
    }

    pins = (dsu__pin_rule_t *)dsu__malloc(in_count * (dsu_u32)sizeof(*pins));
    if (!pins) {
        return DSU_STATUS_IO_ERROR;
    }
    memset(pins, 0, (size_t)in_count * sizeof(*pins));

    for (i = 0u; i < in_count; ++i) {
        const char *id = in_pins[i].component_id;
        const char *ver = in_pins[i].version;
        dsu_u32 maj, min, pat;
        const char *suf;
        dsu_status_t st;

        st = dsu__dup_lower_ascii_id(id, &pins[i].component_id);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__pins_free(pins, in_count);
            return st;
        }
        if (!ver || ver[0] == '\0') {
            dsu__pins_free(pins, in_count);
            return DSU_STATUS_INVALID_REQUEST;
        }
        pins[i].version = dsu__strdup(ver);
        if (!pins[i].version) {
            dsu__pins_free(pins, in_count);
            return DSU_STATUS_IO_ERROR;
        }
        st = dsu__semverish_split(pins[i].version, &maj, &min, &pat, &suf);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__pins_free(pins, in_count);
            return DSU_STATUS_INVALID_REQUEST;
        }
    }

    dsu__sort_pins(pins, in_count);
    for (i = 1u; i < in_count; ++i) {
        if (dsu__strcmp_bytes(pins[i - 1u].component_id, pins[i].component_id) == 0) {
            dsu__pins_free(pins, in_count);
            return DSU_STATUS_INVALID_REQUEST;
        }
    }

    *out_pins = pins;
    *out_count = in_count;
    return DSU_STATUS_SUCCESS;
}

static const char *dsu__pin_find(const dsu__pin_rule_t *pins, dsu_u32 count, const char *component_id) {
    dsu_u32 lo;
    dsu_u32 hi;
    if (!pins || count == 0u || !component_id) {
        return NULL;
    }
    lo = 0u;
    hi = count;
    while (lo < hi) {
        dsu_u32 mid = lo + ((hi - lo) / 2u);
        int c = dsu__strcmp_bytes(pins[mid].component_id, component_id);
        if (c == 0) {
            return pins[mid].version;
        }
        if (c < 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return NULL;
}

static const char *dsu__select_platform(const dsu_manifest_t *manifest,
                                       const dsu_resolve_request_t *req,
                                       dsu_status_t *out_st) {
    dsu_u32 count;
    const char *p;
    if (out_st) {
        *out_st = DSU_STATUS_SUCCESS;
    }

    if (!manifest || !req) {
        if (out_st) *out_st = DSU_STATUS_INVALID_ARGS;
        return NULL;
    }

    if (req->target_platform && req->target_platform[0] != '\0') {
        return req->target_platform;
    }

    count = dsu_manifest_platform_target_count(manifest);
    if (count == 1u) {
        p = dsu_manifest_platform_target(manifest, 0u);
        return p ? p : "";
    }
    if (out_st) {
        *out_st = DSU_STATUS_INVALID_REQUEST;
    }
    return NULL;
}

static dsu_status_t dsu__platform_supported(const dsu_manifest_t *manifest, const char *plat) {
    dsu_u32 count;
    dsu_u32 lo;
    dsu_u32 hi;

    if (!manifest || !plat || plat[0] == '\0') {
        return DSU_STATUS_PLATFORM_INCOMPATIBLE;
    }

    count = dsu_manifest_platform_target_count(manifest);
    if (count == 0u) {
        return DSU_STATUS_PLATFORM_INCOMPATIBLE;
    }

    lo = 0u;
    hi = count;
    while (lo < hi) {
        dsu_u32 mid = lo + ((hi - lo) / 2u);
        const char *m = dsu_manifest_platform_target(manifest, mid);
        int c = dsu__strcmp_bytes(m ? m : "", plat);
        if (c == 0) {
            return DSU_STATUS_SUCCESS;
        }
        if (c < 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return DSU_STATUS_PLATFORM_INCOMPATIBLE;
}

static dsu_bool dsu__is_abs_path_like(const char *p) {
    if (!p || p[0] == '\0') {
        return DSU_FALSE;
    }
    if (p[0] == '/' || p[0] == '\\') {
        return DSU_TRUE;
    }
    if ((p[0] == '/' && p[1] == '/') || (p[0] == '\\' && p[1] == '\\')) {
        return DSU_TRUE;
    }
    if (((p[0] >= 'A' && p[0] <= 'Z') || (p[0] >= 'a' && p[0] <= 'z')) && p[1] == ':' &&
        (p[2] == '/' || p[2] == '\\')) {
        return DSU_TRUE;
    }
    return DSU_FALSE;
}

static dsu_status_t dsu__canon_install_root(const char *path_in, char *path_out, dsu_u32 path_out_cap) {
    dsu_status_t st;
    if (!path_in || !path_out || path_out_cap == 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (dsu__is_abs_path_like(path_in)) {
        return dsu_fs_path_canonicalize(path_in, path_out, path_out_cap);
    }
    {
        char cwd[1024];
        st = dsu_platform_get_cwd(cwd, (dsu_u32)sizeof(cwd));
        if (st != DSU_STATUS_SUCCESS) {
            return st;
        }
        return dsu_fs_path_join(cwd, path_in, path_out, path_out_cap);
    }
}

static dsu_status_t dsu__select_install_root(const dsu_manifest_t *manifest,
                                            dsu_u8 scope,
                                            const char *plat,
                                            const char *const *roots,
                                            dsu_u32 root_count,
                                            const char **out_path) {
    dsu_u32 i;
    dsu_u32 count;
    const char *found;
    dsu_u32 found_count;

    if (!out_path) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_path = NULL;
    if (!manifest || !plat || plat[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (root_count > 1u) {
        return DSU_STATUS_INVALID_REQUEST;
    }

    count = dsu_manifest_install_root_count(manifest);
    found = NULL;
    found_count = 0u;
    for (i = 0u; i < count; ++i) {
        dsu_manifest_install_scope_t s = dsu_manifest_install_root_scope(manifest, i);
        const char *p = dsu_manifest_install_root_platform(manifest, i);
        const char *path = dsu_manifest_install_root_path(manifest, i);
        if ((dsu_u8)s != scope) {
            continue;
        }
        if (!p || dsu__strcmp_bytes(p, plat) != 0) {
            continue;
        }
        if (root_count == 1u) {
            const char *want = roots ? roots[0] : NULL;
            if (!want || want[0] == '\0') {
                return DSU_STATUS_INVALID_REQUEST;
            }
            if (path) {
                if (dsu__strcmp_bytes(path, want) == 0) {
                    found = path;
                    ++found_count;
                } else {
                    char want_abs[1024];
                    char path_abs[1024];
                    dsu_status_t st_want = dsu__canon_install_root(want, want_abs, (dsu_u32)sizeof(want_abs));
                    dsu_status_t st_path = dsu__canon_install_root(path, path_abs, (dsu_u32)sizeof(path_abs));
                    if (st_want == DSU_STATUS_SUCCESS && st_path == DSU_STATUS_SUCCESS &&
                        dsu__strcmp_bytes(want_abs, path_abs) == 0) {
                        found = path;
                        ++found_count;
                    }
                }
            }
        } else {
            found = path ? path : "";
            ++found_count;
        }
    }

    if (found_count == 0u) {
        return (root_count == 0u) ? DSU_STATUS_PLATFORM_INCOMPATIBLE : DSU_STATUS_INVALID_REQUEST;
    }
    if (found_count != 1u) {
        return DSU_STATUS_INVALID_REQUEST;
    }
    *out_path = found;
    return DSU_STATUS_SUCCESS;
}

static dsu_u8 dsu__source_priority(dsu_u8 s) {
    switch ((dsu_resolve_source_t)s) {
        case DSU_RESOLVE_SOURCE_USER: return 3u;
        case DSU_RESOLVE_SOURCE_DEFAULT: return 2u;
        case DSU_RESOLVE_SOURCE_DEPENDENCY: return 1u;
        case DSU_RESOLVE_SOURCE_INSTALLED: return 0u;
        default: return 0u;
    }
}

static void dsu__select_with_source(dsu_u32 idx, dsu_u8 src, dsu_u8 *selected, dsu_u8 *sources) {
    if (!selected || !sources) {
        return;
    }
    if (!selected[idx]) {
        selected[idx] = 1u;
        sources[idx] = src;
        return;
    }
    if (dsu__source_priority(src) > dsu__source_priority(sources[idx])) {
        sources[idx] = src;
    }
}

static dsu_status_t dsu__finalize_success(dsu_resolve_result_t *r,
                                         const dsu__graph_t *g,
                                         const dsu_u8 *selected,
                                         const dsu_u8 *sources,
                                         const dsu_u8 *actions) {
    dsu_u32 i;
    dsu_u32 count;
    dsu_u64 h;
    dsu_u8 sep = 0u;

    if (!r || !g || !selected || !sources) {
        return DSU_STATUS_INVALID_ARGS;
    }

    count = 0u;
    for (i = 0u; i < g->node_count; ++i) {
        if (selected[i]) {
            ++count;
        }
    }

    r->components = (dsu__resolved_component_t *)dsu__malloc(count * (dsu_u32)sizeof(*r->components));
    if (!r->components && count != 0u) {
        return DSU_STATUS_IO_ERROR;
    }
    if (count != 0u) {
        memset(r->components, 0, (size_t)count * sizeof(*r->components));
    }

    h = dsu_digest64_init();
    h = dsu_digest64_update(h, r->platform ? r->platform : "", dsu__strlen(r->platform ? r->platform : ""));
    h = dsu_digest64_update(h, &sep, 1u);
    h = dsu_digest64_update(h, &r->scope, 1u);
    h = dsu_digest64_update(h, &sep, 1u);

    r->component_count = 0u;
    for (i = 0u; i < g->node_count; ++i) {
        const dsu__graph_node_t *node;
        const char *id;
        const char *ver;
        dsu__resolved_component_t *c;
        if (!selected[i]) {
            continue;
        }
        node = &g->nodes[i];
        id = node->id ? node->id : "";
        ver = node->version ? node->version : "";

        c = &r->components[r->component_count++];
        c->id = dsu__strdup(id);
        c->version = dsu__strdup(ver);
        c->source = sources[i];
        c->action = actions ? actions[i] : (dsu_u8)DSU_RESOLVE_COMPONENT_ACTION_NONE;
        c->reserved16 = 0u;
        if (!c->id || !c->version) {
            return DSU_STATUS_IO_ERROR;
        }

        h = dsu_digest64_update(h, id, dsu__strlen(id));
        h = dsu_digest64_update(h, &sep, 1u);
        h = dsu_digest64_update(h, ver, dsu__strlen(ver));
        h = dsu_digest64_update(h, &sep, 1u);
    }

    r->resolved_digest64 = h;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_resolve_components(dsu_ctx_t *ctx,
                                   const dsu_manifest_t *manifest,
                                   const dsu_state_t *installed_state,
                                   const dsu_resolve_request_t *request,
                                   dsu_resolve_result_t **out_result) {
    dsu_status_t st = DSU_STATUS_SUCCESS;
    dsu_resolve_result_t *r = NULL;
    dsu__graph_t g;

    char **requested = NULL;
    dsu_u32 requested_count = 0u;
    char **excluded = NULL;
    dsu_u32 excluded_count = 0u;
    dsu__pin_rule_t *pins = NULL;
    dsu_u32 pin_count = 0u;

    dsu_u8 *selected = NULL;
    dsu_u8 *sources = NULL;
    dsu_u8 *actions = NULL;

    char *plat_norm = NULL;
    const char *plat = NULL;
    const char *install_root = NULL;
    dsu_u32 i;

    memset(&g, 0, sizeof(g));

    if (!ctx || !manifest || !request || !out_result) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_result = NULL;

    if (request->struct_version < 1u || request->struct_size < (dsu_u32)sizeof(*request)) {
        return DSU_STATUS_INVALID_REQUEST;
    }
    if (request->scope > DSU_MANIFEST_INSTALL_SCOPE_SYSTEM) {
        return DSU_STATUS_INVALID_REQUEST;
    }
    if (request->operation > DSU_RESOLVE_OPERATION_UNINSTALL) {
        return DSU_STATUS_INVALID_REQUEST;
    }

    r = (dsu_resolve_result_t *)dsu__malloc((dsu_u32)sizeof(*r));
    if (!r) {
        return DSU_STATUS_IO_ERROR;
    }
    memset(r, 0, sizeof(*r));
    r->struct_version = 1u;
    r->operation = (dsu_u8)request->operation;
    r->scope = (dsu_u8)request->scope;
    r->manifest_digest64 = dsu_manifest_content_digest64(manifest);

    r->product_id = dsu__strdup(dsu_manifest_product_id(manifest));
    r->product_version = dsu__strdup(dsu_manifest_product_version(manifest));
    if (!r->product_id || !r->product_version) {
        st = DSU_STATUS_IO_ERROR;
        goto fail_destroy;
    }

    st = dsu__graph_build(manifest, &g);
    if (st != DSU_STATUS_SUCCESS) {
        goto fail_destroy;
    }

    st = dsu__normalize_id_list(request->requested_components,
                                request->requested_component_count,
                                &requested,
                                &requested_count);
    if (st != DSU_STATUS_SUCCESS) {
        goto fail_destroy;
    }
    st = dsu__normalize_id_list(request->excluded_components,
                                request->excluded_component_count,
                                &excluded,
                                &excluded_count);
    if (st != DSU_STATUS_SUCCESS) {
        goto fail_destroy;
    }
    st = dsu__normalize_pins(request->pins, request->pin_count, &pins, &pin_count);
    if (st != DSU_STATUS_SUCCESS) {
        goto fail_destroy;
    }

    /* Reject overlaps between requested and excluded. */
    for (i = 0u; i < requested_count; ++i) {
        if (dsu__sorted_str_list_contains(excluded, excluded_count, requested[i])) {
            (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_SEED_USER, requested[i], "excluded");
            st = DSU_STATUS_INVALID_REQUEST;
            goto fail_result;
        }
    }

    /* Pin targets must exist in the manifest. */
    for (i = 0u; i < pin_count; ++i) {
        dsu_u32 idx = 0u;
        if (dsu__find_component_index(manifest, pins[i].component_id, &idx) != DSU_STATUS_SUCCESS) {
            (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_SEED_USER, pins[i].component_id, "pin_missing");
            st = DSU_STATUS_INVALID_REQUEST;
            goto fail_result;
        }
    }

    selected = (dsu_u8 *)dsu__malloc(g.node_count);
    sources = (dsu_u8 *)dsu__malloc(g.node_count);
    actions = (dsu_u8 *)dsu__malloc(g.node_count);
    if ((!selected || !sources || !actions) && g.node_count != 0u) {
        st = DSU_STATUS_IO_ERROR;
        goto fail_destroy;
    }
    if (g.node_count != 0u) {
        memset(selected, 0, (size_t)g.node_count);
        memset(sources, 0, (size_t)g.node_count);
        memset(actions, 0, (size_t)g.node_count);
    }

    /* Phase 1 — Seed selection */
    for (i = 0u; i < requested_count; ++i) {
        dsu_u32 idx = 0u;
        if (dsu__find_component_index(manifest, requested[i], &idx) != DSU_STATUS_SUCCESS) {
            (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_SEED_USER, requested[i], "missing");
            st = DSU_STATUS_MISSING_COMPONENT;
            goto fail_result;
        }
        dsu__select_with_source(idx, (dsu_u8)DSU_RESOLVE_SOURCE_USER, selected, sources);
        (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_SEED_USER, requested[i], "");
    }

    /* Default selection applies only when the user did not explicitly specify components. */
    if (requested_count == 0u) {
        for (i = 0u; i < g.node_count; ++i) {
            const dsu__graph_node_t *node = &g.nodes[i];
            const char *id = node->id ? node->id : "";
            if ((node->flags & DSU_MANIFEST_COMPONENT_FLAG_DEFAULT_SELECTED) == 0u) {
                continue;
            }
            if (dsu__sorted_str_list_contains(excluded, excluded_count, id)) {
                continue;
            }
            if (!selected[i]) {
                dsu__select_with_source(i, (dsu_u8)DSU_RESOLVE_SOURCE_DEFAULT, selected, sources);
                (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_SEED_DEFAULT, id, "");
            }
        }
    }

    /* Ensure non-empty selection. */
    {
        dsu_u32 any = 0u;
        for (i = 0u; i < g.node_count; ++i) {
            if (selected[i]) {
                any = 1u;
                break;
            }
        }
        if (!any) {
            (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_SEED_DEFAULT, "selection", "empty");
            st = DSU_STATUS_INVALID_REQUEST;
            goto fail_result;
        }
    }

    /* Phase 2 — Dependency closure */
    {
        dsu_u32 changed = 1u;
        while (changed) {
            changed = 0u;
            for (i = 0u; i < g.node_count; ++i) {
                const dsu__graph_node_t *node;
                dsu_u32 j;
                if (!selected[i]) {
                    continue;
                }
                node = &g.nodes[i];
                for (j = 0u; j < node->dep_count; ++j) {
                    const dsu__graph_dep_t *d = &node->deps[j];
                    dsu_u32 dep_idx = d->target_index;
                    const char *from_id = node->id ? node->id : "";
                    const char *dep_id = d->target_id ? d->target_id : "";
                    const char *dep_ver;

                    if (dep_idx == 0xFFFFFFFFu) {
                        (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_ADD_DEPENDENCY, from_id, dep_id);
                        st = DSU_STATUS_UNSATISFIED_DEPENDENCY;
                        goto fail_result;
                    }
                    if (dsu__sorted_str_list_contains(excluded, excluded_count, dep_id)) {
                        (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_ADD_DEPENDENCY, from_id, dep_id);
                        st = DSU_STATUS_UNSATISFIED_DEPENDENCY;
                        goto fail_result;
                    }

                    dep_ver = g.nodes[dep_idx].version;
                    if (!dsu__satisfies_constraint(dep_ver, d->constraint_kind, d->constraint_version)) {
                        (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_ADD_DEPENDENCY, dep_id, "version_conflict");
                        st = DSU_STATUS_VERSION_CONFLICT;
                        goto fail_result;
                    }

                    if (!selected[dep_idx]) {
                        dsu__select_with_source(dep_idx, (dsu_u8)DSU_RESOLVE_SOURCE_DEPENDENCY, selected, sources);
                        (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_ADD_DEPENDENCY, from_id, dep_id);
                        changed = 1u;
                    }
                }
            }
        }
    }

    if (!request->allow_prerelease) {
        for (i = 0u; i < g.node_count; ++i) {
            if (selected[i] && dsu__has_prerelease_suffix(g.nodes[i].version)) {
                (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_ADD_DEPENDENCY, g.nodes[i].id, "prerelease");
                st = DSU_STATUS_VERSION_CONFLICT;
                goto fail_result;
            }
        }
    }

    for (i = 0u; i < g.node_count; ++i) {
        const char *pin_ver;
        const char *id;
        if (!selected[i]) {
            continue;
        }
        id = g.nodes[i].id ? g.nodes[i].id : "";
        pin_ver = dsu__pin_find(pins, pin_count, id);
        if (pin_ver && dsu__strcmp_bytes(g.nodes[i].version, pin_ver) != 0) {
            (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_ADD_DEPENDENCY, id, "pinned_mismatch");
            st = DSU_STATUS_VERSION_CONFLICT;
            goto fail_result;
        }
    }

    /* Phase 3 — Conflict detection */
    for (i = 0u; i < g.node_count; ++i) {
        dsu_u32 ccount;
        dsu_u32 j;
        const char *id;
        if (!selected[i]) {
            continue;
        }
        id = g.nodes[i].id ? g.nodes[i].id : "";
        ccount = dsu_manifest_component_conflict_count(manifest, i);
        for (j = 0u; j < ccount; ++j) {
            const char *cid = dsu_manifest_component_conflict_id(manifest, i, j);
            dsu_u32 cidx = 0u;
            if (!cid) {
                continue;
            }
            if (dsu__find_component_index(manifest, cid, &cidx) != DSU_STATUS_SUCCESS) {
                continue;
            }
            if (selected[cidx]) {
                (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_CONFLICT, id, cid);
                st = DSU_STATUS_EXPLICIT_CONFLICT;
                goto fail_result;
            }
        }
    }

    /* Phase 4 — Platform filtering (enforced by target platform + selected install root). */
    plat = dsu__select_platform(manifest, request, &st);
    if (st != DSU_STATUS_SUCCESS || !plat || plat[0] == '\0') {
        (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_PLATFORM_FILTER, "platform", "missing");
        st = (st != DSU_STATUS_SUCCESS) ? st : DSU_STATUS_INVALID_REQUEST;
        goto fail_result;
    }
    if (request->target_platform && request->target_platform[0] != '\0') {
        plat_norm = dsu__strdup(plat);
        if (!plat_norm) {
            st = DSU_STATUS_IO_ERROR;
            goto fail_destroy;
        }
        if (dsu__ascii_to_lower_inplace(plat_norm) != DSU_STATUS_SUCCESS || !dsu__is_ascii_printable(plat_norm)) {
            (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_PLATFORM_FILTER, "platform", "invalid");
            st = DSU_STATUS_INVALID_REQUEST;
            goto fail_result;
        }
        plat = plat_norm;
    }
    st = dsu__platform_supported(manifest, plat);
    if (st != DSU_STATUS_SUCCESS) {
        (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_PLATFORM_FILTER, "platform", plat);
        goto fail_result;
    }
    r->platform = dsu__strdup(plat);
    if (!r->platform) {
        st = DSU_STATUS_IO_ERROR;
        goto fail_destroy;
    }

    /* Phase 5 — Installed-state reconciliation */
    if (!installed_state) {
        if (request->operation != DSU_RESOLVE_OPERATION_INSTALL) {
            (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_RECONCILE_INSTALLED, "installed_state", "required");
            st = DSU_STATUS_INVALID_REQUEST;
            goto fail_result;
        }
    } else {
        if (dsu__strcmp_bytes(dsu_state_product_id(installed_state), r->product_id) != 0) {
            (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_RECONCILE_INSTALLED, "product_id", "mismatch");
            st = DSU_STATUS_INVALID_REQUEST;
            goto fail_result;
        }
        if ((dsu_u8)dsu_state_scope(installed_state) != r->scope) {
            (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_RECONCILE_INSTALLED, "scope", "mismatch");
            st = DSU_STATUS_INVALID_REQUEST;
            goto fail_result;
        }
        if (dsu__strcmp_bytes(dsu_state_platform(installed_state), r->platform) != 0) {
            (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_RECONCILE_INSTALLED, "platform", "mismatch");
            st = DSU_STATUS_PLATFORM_INCOMPATIBLE;
            goto fail_result;
        }
    }

    /* Install root selection (validated against manifest and state). */
    {
        const char *state_root = installed_state ? dsu_state_install_root(installed_state) : NULL;
        if (request->operation == DSU_RESOLVE_OPERATION_REPAIR ||
            request->operation == DSU_RESOLVE_OPERATION_UNINSTALL) {
            if (request->install_root_count == 0u) {
                const char *roots_tmp[1];
                if (!state_root || state_root[0] == '\0') {
                    (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_RECONCILE_INSTALLED, "install_root", "missing");
                    st = DSU_STATUS_INVALID_REQUEST;
                    goto fail_result;
                }
                roots_tmp[0] = state_root;
                st = dsu__select_install_root(manifest,
                                              (dsu_u8)request->scope,
                                              plat,
                                              roots_tmp,
                                              1u,
                                              &install_root);
            } else {
                st = dsu__select_install_root(manifest,
                                              (dsu_u8)request->scope,
                                              plat,
                                              request->install_roots,
                                              request->install_root_count,
                                              &install_root);
            }
        } else {
            if (request->install_root_count == 0u && state_root && state_root[0] != '\0') {
                const char *roots_tmp[1];
                roots_tmp[0] = state_root;
                st = dsu__select_install_root(manifest,
                                              (dsu_u8)request->scope,
                                              plat,
                                              roots_tmp,
                                              1u,
                                              &install_root);
            } else {
                st = dsu__select_install_root(manifest,
                                              (dsu_u8)request->scope,
                                              plat,
                                              request->install_roots,
                                              request->install_root_count,
                                              &install_root);
            }
        }
        if (st != DSU_STATUS_SUCCESS || !install_root) {
            (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_PLATFORM_FILTER, "install_root", plat);
            st = (st != DSU_STATUS_SUCCESS) ? st : DSU_STATUS_PLATFORM_INCOMPATIBLE;
            goto fail_result;
        }
        if (state_root && state_root[0] != '\0') {
            if (dsu__strcmp_bytes(state_root, install_root) != 0) {
                char state_abs[1024];
                char install_abs[1024];
                dsu_status_t st_state = dsu__canon_install_root(state_root, state_abs, (dsu_u32)sizeof(state_abs));
                dsu_status_t st_install = dsu__canon_install_root(install_root, install_abs, (dsu_u32)sizeof(install_abs));
                if (st_state != DSU_STATUS_SUCCESS ||
                    st_install != DSU_STATUS_SUCCESS ||
                    dsu__strcmp_bytes(state_abs, install_abs) != 0) {
                    (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_RECONCILE_INSTALLED, "install_root", "mismatch");
                    st = DSU_STATUS_INVALID_REQUEST;
                    goto fail_result;
                }
            }
        }
        r->install_root = dsu__strdup(install_root);
        if (!r->install_root) {
            st = DSU_STATUS_IO_ERROR;
            goto fail_destroy;
        }
    }

    switch (request->operation) {
        case DSU_RESOLVE_OPERATION_INSTALL:
            for (i = 0u; i < g.node_count; ++i) {
                if (!selected[i]) continue;
                if (installed_state) {
                    const char *iv = dsu__state_find_component_version(installed_state, g.nodes[i].id ? g.nodes[i].id : "");
                    if (iv) {
                        (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_RECONCILE_INSTALLED, g.nodes[i].id, "already_installed");
                        st = DSU_STATUS_INVALID_REQUEST;
                        goto fail_result;
                    }
                }
                actions[i] = (dsu_u8)DSU_RESOLVE_COMPONENT_ACTION_INSTALL;
            }
            break;

        case DSU_RESOLVE_OPERATION_UPGRADE:
            if (!installed_state) {
                (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_RECONCILE_INSTALLED, "installed_state", "required");
                st = DSU_STATUS_INVALID_REQUEST;
                goto fail_result;
            }
            for (i = 0u; i < g.node_count; ++i) {
                const char *id;
                const char *mv;
                const char *iv;
                int cmp;
                if (!selected[i]) continue;
                id = g.nodes[i].id ? g.nodes[i].id : "";
                mv = g.nodes[i].version ? g.nodes[i].version : "";
                iv = dsu__state_find_component_version(installed_state, id);
                if (!iv) {
                    (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_RECONCILE_INSTALLED, id, "not_installed");
                    st = DSU_STATUS_INVALID_REQUEST;
                    goto fail_result;
                }
                cmp = dsu__semverish_cmp(mv, iv);
                if (cmp < 0) {
                    (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_RECONCILE_INSTALLED, id, "illegal_downgrade");
                    st = DSU_STATUS_ILLEGAL_DOWNGRADE;
                    goto fail_result;
                } else if (cmp == 0) {
                    actions[i] = (dsu_u8)DSU_RESOLVE_COMPONENT_ACTION_NONE;
                } else {
                    actions[i] = (dsu_u8)DSU_RESOLVE_COMPONENT_ACTION_UPGRADE;
                }
            }
            break;

        case DSU_RESOLVE_OPERATION_REPAIR:
            if (!installed_state) {
                (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_RECONCILE_INSTALLED, "installed_state", "required");
                st = DSU_STATUS_INVALID_REQUEST;
                goto fail_result;
            }
            for (i = 0u; i < g.node_count; ++i) {
                const char *id;
                const char *mv;
                const char *iv;
                int cmp;
                if (!selected[i]) continue;
                id = g.nodes[i].id ? g.nodes[i].id : "";
                mv = g.nodes[i].version ? g.nodes[i].version : "";
                iv = dsu__state_find_component_version(installed_state, id);
                if (!iv) {
                    (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_RECONCILE_INSTALLED, id, "not_installed");
                    st = DSU_STATUS_INVALID_REQUEST;
                    goto fail_result;
                }
                cmp = dsu__semverish_cmp(mv, iv);
                if (cmp != 0) {
                    (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_RECONCILE_INSTALLED, id, "version_mismatch");
                    st = DSU_STATUS_INVALID_REQUEST;
                    goto fail_result;
                }
                actions[i] = (dsu_u8)DSU_RESOLVE_COMPONENT_ACTION_REPAIR;
            }
            break;

        case DSU_RESOLVE_OPERATION_UNINSTALL:
            if (!installed_state) {
                (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_RECONCILE_INSTALLED, "installed_state", "required");
                st = DSU_STATUS_INVALID_REQUEST;
                goto fail_result;
            }
            for (i = 0u; i < g.node_count; ++i) {
                const char *id;
                const char *iv;
                if (!selected[i]) continue;
                id = g.nodes[i].id ? g.nodes[i].id : "";
                iv = dsu__state_find_component_version(installed_state, id);
                if (!iv) {
                    selected[i] = 0u;
                    sources[i] = 0u;
                    actions[i] = (dsu_u8)DSU_RESOLVE_COMPONENT_ACTION_NONE;
                    (void)dsu__log_push(r, (dsu_u8)DSU_RESOLVE_LOG_RECONCILE_INSTALLED, id, "not_installed");
                    continue;
                }
                actions[i] = (dsu_u8)DSU_RESOLVE_COMPONENT_ACTION_UNINSTALL;
            }
            break;

        default:
            st = DSU_STATUS_INVALID_REQUEST;
            goto fail_result;
    }

    /* Phase 6 — Canonical ordering + digest */
    st = dsu__finalize_success(r, &g, selected, sources, actions);
    if (st != DSU_STATUS_SUCCESS) {
        goto fail_destroy;
    }

    (void)dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_RESOLVE_COMPLETE,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_RESOLVE,
                      "resolve complete");

    *out_result = r;
    dsu__free(plat_norm);
    dsu__free(selected);
    dsu__free(sources);
    dsu__free(actions);
    dsu__free_str_list(requested, requested_count);
    dsu__free_str_list(excluded, excluded_count);
    dsu__pins_free(pins, pin_count);
    dsu__graph_free(&g);
    return DSU_STATUS_SUCCESS;

fail_result:
    *out_result = r;
    dsu__free(plat_norm);
    dsu__free(selected);
    dsu__free(sources);
    dsu__free(actions);
    dsu__free_str_list(requested, requested_count);
    dsu__free_str_list(excluded, excluded_count);
    dsu__pins_free(pins, pin_count);
    dsu__graph_free(&g);
    return st;

fail_destroy:
    dsu__free(plat_norm);
    dsu__free(selected);
    dsu__free(sources);
    dsu__free(actions);
    dsu__free_str_list(requested, requested_count);
    dsu__free_str_list(excluded, excluded_count);
    dsu__pins_free(pins, pin_count);
    dsu__graph_free(&g);
    if (r) {
        dsu_resolve_result_destroy(ctx, r);
    }
    return st;
}

void dsu_resolve_result_destroy(dsu_ctx_t *ctx, dsu_resolve_result_t *result) {
    (void)ctx;
    if (!result) {
        return;
    }
    dsu__resolve_result_free(result);
    dsu__free(result);
}

dsu_resolve_operation_t dsu_resolve_result_operation(const dsu_resolve_result_t *result) {
    if (!result) {
        return DSU_RESOLVE_OPERATION_INSTALL;
    }
    return (dsu_resolve_operation_t)result->operation;
}

dsu_manifest_install_scope_t dsu_resolve_result_scope(const dsu_resolve_result_t *result) {
    if (!result) {
        return DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    }
    return (dsu_manifest_install_scope_t)result->scope;
}

const char *dsu_resolve_result_platform(const dsu_resolve_result_t *result) {
    if (!result || !result->platform) {
        return "";
    }
    return result->platform;
}

const char *dsu_resolve_result_product_id(const dsu_resolve_result_t *result) {
    if (!result || !result->product_id) {
        return "";
    }
    return result->product_id;
}

const char *dsu_resolve_result_product_version(const dsu_resolve_result_t *result) {
    if (!result || !result->product_version) {
        return "";
    }
    return result->product_version;
}

const char *dsu_resolve_result_install_root(const dsu_resolve_result_t *result) {
    if (!result || !result->install_root) {
        return "";
    }
    return result->install_root;
}

dsu_u64 dsu_resolve_result_manifest_digest64(const dsu_resolve_result_t *result) {
    if (!result) {
        return (dsu_u64)0u;
    }
    return result->manifest_digest64;
}

dsu_u64 dsu_resolve_result_resolved_digest64(const dsu_resolve_result_t *result) {
    if (!result) {
        return (dsu_u64)0u;
    }
    return result->resolved_digest64;
}

dsu_u32 dsu_resolve_result_component_count(const dsu_resolve_result_t *result) {
    if (!result) {
        return 0u;
    }
    return result->component_count;
}

const char *dsu_resolve_result_component_id(const dsu_resolve_result_t *result, dsu_u32 index) {
    if (!result || index >= result->component_count) {
        return NULL;
    }
    return result->components[index].id;
}

const char *dsu_resolve_result_component_version(const dsu_resolve_result_t *result, dsu_u32 index) {
    if (!result || index >= result->component_count) {
        return NULL;
    }
    return result->components[index].version;
}

dsu_resolve_source_t dsu_resolve_result_component_source(const dsu_resolve_result_t *result, dsu_u32 index) {
    if (!result || index >= result->component_count) {
        return DSU_RESOLVE_SOURCE_DEPENDENCY;
    }
    return (dsu_resolve_source_t)result->components[index].source;
}

dsu_resolve_component_action_t dsu_resolve_result_component_action(const dsu_resolve_result_t *result, dsu_u32 index) {
    if (!result || index >= result->component_count) {
        return DSU_RESOLVE_COMPONENT_ACTION_NONE;
    }
    return (dsu_resolve_component_action_t)result->components[index].action;
}

dsu_u32 dsu_resolve_result_log_count(const dsu_resolve_result_t *result) {
    if (!result) {
        return 0u;
    }
    return result->log_count;
}

dsu_resolve_log_code_t dsu_resolve_result_log_code(const dsu_resolve_result_t *result, dsu_u32 index) {
    if (!result || index >= result->log_count) {
        return DSU_RESOLVE_LOG_SEED_USER;
    }
    return (dsu_resolve_log_code_t)result->log_events[index].code;
}

const char *dsu_resolve_result_log_a(const dsu_resolve_result_t *result, dsu_u32 index) {
    if (!result || index >= result->log_count) {
        return NULL;
    }
    return result->log_events[index].a;
}

const char *dsu_resolve_result_log_b(const dsu_resolve_result_t *result, dsu_u32 index) {
    if (!result || index >= result->log_count) {
        return NULL;
    }
    return result->log_events[index].b;
}
