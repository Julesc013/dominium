/*
FILE: source/dominium/setup/core/src/manifest/dsu_manifest.c
MODULE: Dominium Setup
PURPOSE: Baseline manifest parser for Plan S-1 (strict INI-like format).
*/
#include "../../include/dsu/dsu_manifest.h"
#include "../../include/dsu/dsu_log.h"

#include "../dsu_ctx_internal.h"
#include "../log/dsu_events.h"
#include "../util/dsu_util_internal.h"

#include <string.h>

struct dsu_manifest {
    char *product_id;
    char *version;
    char *install_root;
    dsu_u32 component_count;
    char **components;
};

static char *dsu__trim(char *s) {
    char *end;
    unsigned char c;
    if (!s) {
        return s;
    }
    while ((c = (unsigned char)*s) != 0u) {
        if (c != ' ' && c != '\t') {
            break;
        }
        ++s;
    }
    end = s + strlen(s);
    while (end > s) {
        c = (unsigned char)end[-1];
        if (c != ' ' && c != '\t') {
            break;
        }
        end[-1] = '\0';
        --end;
    }
    return s;
}

static int dsu__is_comment_or_empty(const char *s) {
    unsigned char c;
    if (!s) {
        return 1;
    }
    while ((c = (unsigned char)*s) != 0u) {
        if (c == ' ' || c == '\t' || c == '\r' || c == '\n') {
            ++s;
            continue;
        }
        if (c == '#' || c == ';') {
            return 1;
        }
        return 0;
    }
    return 1;
}

static dsu_status_t dsu__parse_string_value(const char *value, char **out_str) {
    const char *p;
    const char *q;
    dsu_u32 n;
    char *out;

    if (!value || !out_str) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_str = NULL;

    p = value;
    while (*p == ' ' || *p == '\t') {
        ++p;
    }
    if (*p == '"') {
        ++p;
        q = p;
        while (*q && *q != '"') {
            unsigned char c = (unsigned char)*q;
            if (c < 0x20u || c > 0x7Eu) {
                return DSU_STATUS_PARSE_ERROR;
            }
            ++q;
        }
        if (*q != '"') {
            return DSU_STATUS_PARSE_ERROR;
        }
        n = (dsu_u32)(q - p);
        ++q;
        while (*q == ' ' || *q == '\t') {
            ++q;
        }
        if (*q != '\0') {
            return DSU_STATUS_PARSE_ERROR;
        }
        out = (char *)dsu__malloc(n + 1u);
        if (!out) {
            return DSU_STATUS_IO_ERROR;
        }
        if (n) {
            memcpy(out, p, (size_t)n);
        }
        out[n] = '\0';
        *out_str = out;
        return DSU_STATUS_SUCCESS;
    }

    /* Unquoted token (no spaces). */
    q = p;
    while (*q) {
        unsigned char c = (unsigned char)*q;
        if (c < 0x21u || c > 0x7Eu) {
            return DSU_STATUS_PARSE_ERROR;
        }
        ++q;
    }
    if (q == p) {
        return DSU_STATUS_PARSE_ERROR;
    }
    n = (dsu_u32)(q - p);
    out = (char *)dsu__malloc(n + 1u);
    if (!out) {
        return DSU_STATUS_IO_ERROR;
    }
    memcpy(out, p, (size_t)n);
    out[n] = '\0';
    *out_str = out;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__parse_components_value(const char *value,
                                               char ***out_components,
                                               dsu_u32 *out_count) {
    const char *p;
    dsu_u32 cap;
    dsu_u32 count;
    char **items;
    dsu_status_t st;

    if (!value || !out_components || !out_count) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_components = NULL;
    *out_count = 0u;

    p = value;
    while (*p == ' ' || *p == '\t') {
        ++p;
    }
    if (*p != '[') {
        return DSU_STATUS_PARSE_ERROR;
    }
    ++p;

    cap = 4u;
    count = 0u;
    items = (char **)dsu__malloc(cap * (dsu_u32)sizeof(*items));
    if (!items) {
        return DSU_STATUS_IO_ERROR;
    }
    memset(items, 0, (size_t)cap * sizeof(*items));

    for (;;) {
        const char *item_start;
        const char *item_end;
        char *tmp;
        dsu_u32 n;

        while (*p == ' ' || *p == '\t') {
            ++p;
        }
        if (*p == ']') {
            ++p;
            break;
        }

        if (*p == '"') {
            ++p;
            item_start = p;
            while (*p && *p != '"') {
                unsigned char c = (unsigned char)*p;
                if (c < 0x20u || c > 0x7Eu) {
                    st = DSU_STATUS_PARSE_ERROR;
                    goto fail;
                }
                ++p;
            }
            if (*p != '"') {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            item_end = p;
            ++p;
        } else {
            item_start = p;
            while (*p && *p != ',' && *p != ']') {
                unsigned char c = (unsigned char)*p;
                if (c < 0x21u || c > 0x7Eu) {
                    st = DSU_STATUS_PARSE_ERROR;
                    goto fail;
                }
                ++p;
            }
            item_end = p;
        }

        while (item_end > item_start && (item_end[-1] == ' ' || item_end[-1] == '\t')) {
            --item_end;
        }
        if (item_end == item_start) {
            st = DSU_STATUS_PARSE_ERROR;
            goto fail;
        }

        n = (dsu_u32)(item_end - item_start);
        tmp = (char *)dsu__malloc(n + 1u);
        if (!tmp) {
            st = DSU_STATUS_IO_ERROR;
            goto fail;
        }
        memcpy(tmp, item_start, (size_t)n);
        tmp[n] = '\0';

        st = dsu__ascii_to_lower_inplace(tmp);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(tmp);
            goto fail;
        }
        if (!dsu__is_ascii_id(tmp)) {
            dsu__free(tmp);
            st = DSU_STATUS_PARSE_ERROR;
            goto fail;
        }

        if (count == cap) {
            dsu_u32 new_cap = cap * 2u;
            char **new_items;
            if (new_cap < cap) {
                dsu__free(tmp);
                st = DSU_STATUS_INTERNAL_ERROR;
                goto fail;
            }
            new_items = (char **)dsu__realloc(items, new_cap * (dsu_u32)sizeof(*items));
            if (!new_items) {
                dsu__free(tmp);
                st = DSU_STATUS_IO_ERROR;
                goto fail;
            }
            memset(new_items + cap, 0, (size_t)(new_cap - cap) * sizeof(*new_items));
            items = new_items;
            cap = new_cap;
        }

        items[count++] = tmp;

        while (*p == ' ' || *p == '\t') {
            ++p;
        }
        if (*p == ',') {
            ++p;
            continue;
        }
        if (*p == ']') {
            ++p;
            break;
        }
        st = DSU_STATUS_PARSE_ERROR;
        goto fail;
    }

    while (*p == ' ' || *p == '\t') {
        ++p;
    }
    if (*p != '\0') {
        st = DSU_STATUS_PARSE_ERROR;
        goto fail;
    }

    *out_components = items;
    *out_count = count;
    return DSU_STATUS_SUCCESS;

fail:
    if (items) {
        dsu_u32 i;
        for (i = 0u; i < count; ++i) {
            dsu__free(items[i]);
        }
        dsu__free(items);
    }
    return st;
}

static void dsu__manifest_free(dsu_manifest_t *m) {
    dsu_u32 i;
    if (!m) {
        return;
    }
    dsu__free(m->product_id);
    dsu__free(m->version);
    dsu__free(m->install_root);
    for (i = 0u; i < m->component_count; ++i) {
        dsu__free(m->components[i]);
    }
    dsu__free(m->components);
    m->components = NULL;
    m->component_count = 0u;
}

dsu_status_t dsu_manifest_load_file(dsu_ctx_t *ctx,
                                   const char *path,
                                   dsu_manifest_t **out_manifest) {
    dsu_u8 *bytes;
    dsu_u32 len;
    char *text;
    dsu_u32 i;
    dsu_manifest_t *m;
    dsu_status_t st;

    char *product_id = NULL;
    char *version = NULL;
    char *install_root = NULL;
    char **components = NULL;
    dsu_u32 component_count = 0u;

    if (!ctx || !path || !out_manifest) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_manifest = NULL;

    st = dsu__fs_read_all(&ctx->config, path, &bytes, &len);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    /* Ensure text has no NULs and is terminated. */
    for (i = 0u; i < len; ++i) {
        if (bytes[i] == 0u) {
            dsu__free(bytes);
            return DSU_STATUS_PARSE_ERROR;
        }
    }
    text = (char *)dsu__malloc(len + 1u);
    if (!text) {
        dsu__free(bytes);
        return DSU_STATUS_IO_ERROR;
    }
    if (len) {
        memcpy(text, bytes, (size_t)len);
    }
    text[len] = '\0';
    dsu__free(bytes);

    /* Parse by lines. */
    {
        char *p = text;
        while (*p) {
            char *line = p;
            char *eq;
            char *key;
            char *val;

            while (*p && *p != '\n' && *p != '\r') {
                ++p;
            }
            if (*p == '\r') {
                *p++ = '\0';
                if (*p == '\n') {
                    ++p;
                }
            } else if (*p == '\n') {
                *p++ = '\0';
            }

            line = dsu__trim(line);
            if (dsu__is_comment_or_empty(line)) {
                continue;
            }

            eq = strchr(line, '=');
            if (!eq) {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
            *eq = '\0';
            key = dsu__trim(line);
            val = dsu__trim(eq + 1);

            if (dsu__streq(key, "product_id")) {
                if (product_id) {
                    st = DSU_STATUS_PARSE_ERROR;
                    goto fail;
                }
                st = dsu__parse_string_value(val, &product_id);
                if (st != DSU_STATUS_SUCCESS) {
                    goto fail;
                }
                st = dsu__ascii_to_lower_inplace(product_id);
                if (st != DSU_STATUS_SUCCESS || !dsu__is_ascii_id(product_id)) {
                    st = DSU_STATUS_PARSE_ERROR;
                    goto fail;
                }
            } else if (dsu__streq(key, "version")) {
                if (version) {
                    st = DSU_STATUS_PARSE_ERROR;
                    goto fail;
                }
                st = dsu__parse_string_value(val, &version);
                if (st != DSU_STATUS_SUCCESS) {
                    goto fail;
                }
                if (!dsu__is_ascii_printable(version)) {
                    st = DSU_STATUS_PARSE_ERROR;
                    goto fail;
                }
            } else if (dsu__streq(key, "install_root")) {
                if (install_root) {
                    st = DSU_STATUS_PARSE_ERROR;
                    goto fail;
                }
                st = dsu__parse_string_value(val, &install_root);
                if (st != DSU_STATUS_SUCCESS) {
                    goto fail;
                }
                if (!dsu__is_ascii_printable(install_root)) {
                    st = DSU_STATUS_PARSE_ERROR;
                    goto fail;
                }
            } else if (dsu__streq(key, "components")) {
                if (components) {
                    st = DSU_STATUS_PARSE_ERROR;
                    goto fail;
                }
                st = dsu__parse_components_value(val, &components, &component_count);
                if (st != DSU_STATUS_SUCCESS) {
                    goto fail;
                }
            } else {
                st = DSU_STATUS_PARSE_ERROR;
                goto fail;
            }
        }
    }

    dsu__free(text);
    text = NULL;

    if (!product_id || !version || !install_root || !components || component_count == 0u) {
        st = DSU_STATUS_PARSE_ERROR;
        goto fail;
    }

    /* Canonicalize components: sort + unique. */
    dsu__sort_str_ptrs(components, component_count);
    {
        dsu_u32 w = 0u;
        dsu_u32 r;
        for (r = 0u; r < component_count; ++r) {
            if (w == 0u || dsu__strcmp_bytes(components[w - 1u], components[r]) != 0) {
                components[w++] = components[r];
            } else {
                dsu__free(components[r]);
            }
        }
        component_count = w;
    }

    m = (dsu_manifest_t *)dsu__malloc((dsu_u32)sizeof(*m));
    if (!m) {
        st = DSU_STATUS_IO_ERROR;
        goto fail;
    }
    memset(m, 0, sizeof(*m));
    m->product_id = product_id;
    m->version = version;
    m->install_root = install_root;
    m->components = components;
    m->component_count = component_count;

    (void)dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_MANIFEST_LOADED,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_MANIFEST,
                      "manifest loaded");

    *out_manifest = m;
    return DSU_STATUS_SUCCESS;

fail:
    dsu__free(text);
    dsu__free(product_id);
    dsu__free(version);
    dsu__free(install_root);
    if (components) {
        dsu_u32 j;
        for (j = 0u; j < component_count; ++j) {
            dsu__free(components[j]);
        }
        dsu__free(components);
    }
    return st;
}

void dsu_manifest_destroy(dsu_ctx_t *ctx, dsu_manifest_t *manifest) {
    (void)ctx;
    if (!manifest) {
        return;
    }
    dsu__manifest_free(manifest);
    dsu__free(manifest);
}

const char *dsu_manifest_product_id(const dsu_manifest_t *manifest) {
    if (!manifest || !manifest->product_id) {
        return "";
    }
    return manifest->product_id;
}

const char *dsu_manifest_version(const dsu_manifest_t *manifest) {
    if (!manifest || !manifest->version) {
        return "";
    }
    return manifest->version;
}

const char *dsu_manifest_install_root(const dsu_manifest_t *manifest) {
    if (!manifest || !manifest->install_root) {
        return "";
    }
    return manifest->install_root;
}

dsu_u32 dsu_manifest_component_count(const dsu_manifest_t *manifest) {
    if (!manifest) {
        return 0u;
    }
    return manifest->component_count;
}

const char *dsu_manifest_component_id(const dsu_manifest_t *manifest, dsu_u32 index) {
    if (!manifest || index >= manifest->component_count) {
        return NULL;
    }
    return manifest->components[index];
}

