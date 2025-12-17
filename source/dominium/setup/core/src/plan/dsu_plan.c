/*
FILE: source/dominium/setup/core/src/plan/dsu_plan.c
MODULE: Dominium Setup
PURPOSE: Plan builder and deterministic dsuplan (de)serialization.
*/
#include "../../include/dsu/dsu_plan.h"
#include "../../include/dsu/dsu_log.h"

#include "../dsu_ctx_internal.h"
#include "../log/dsu_events.h"
#include "../util/dsu_util_internal.h"

#include <string.h>

#define DSU_PLAN_MAGIC_0 'D'
#define DSU_PLAN_MAGIC_1 'S'
#define DSU_PLAN_MAGIC_2 'U'
#define DSU_PLAN_MAGIC_3 'P'
#define DSU_PLAN_FORMAT_VERSION 3u

typedef struct dsu_plan_step_t {
    dsu_plan_step_kind_t kind;
    char *arg;
} dsu_plan_step_t;

struct dsu_plan {
    dsu_u32 flags;
    dsu_u32 id_hash32;
    dsu_u64 id_hash64;
    dsu_u64 manifest_digest64;
    dsu_u64 resolved_digest64;
    dsu_u8 operation;
    dsu_u8 scope;
    dsu_u8 reserved8[2];
    char *product_id;
    char *version;
    char *install_root;
    dsu_u32 component_count;
    char **components;
    dsu_u32 step_count;
    dsu_plan_step_t *steps;
};

static void dsu__plan_free(dsu_plan_t *p) {
    dsu_u32 i;
    if (!p) {
        return;
    }
    dsu__free(p->product_id);
    dsu__free(p->version);
    dsu__free(p->install_root);
    for (i = 0u; i < p->component_count; ++i) {
        dsu__free(p->components[i]);
    }
    dsu__free(p->components);
    for (i = 0u; i < p->step_count; ++i) {
        dsu__free(p->steps[i].arg);
    }
    dsu__free(p->steps);
    p->components = NULL;
    p->steps = NULL;
    p->component_count = 0u;
    p->step_count = 0u;
}

static void dsu__u64_to_le_bytes(dsu_u64 v, dsu_u8 out[8]) {
    out[0] = (dsu_u8)(v & 0xFFu);
    out[1] = (dsu_u8)((v >> 8) & 0xFFu);
    out[2] = (dsu_u8)((v >> 16) & 0xFFu);
    out[3] = (dsu_u8)((v >> 24) & 0xFFu);
    out[4] = (dsu_u8)((v >> 32) & 0xFFu);
    out[5] = (dsu_u8)((v >> 40) & 0xFFu);
    out[6] = (dsu_u8)((v >> 48) & 0xFFu);
    out[7] = (dsu_u8)((v >> 56) & 0xFFu);
}

static void dsu__plan_compute_ids(dsu_plan_t *p) {
    dsu_u32 h32;
    dsu_u64 h64;
    dsu_u32 i;
    dsu_u8 sep;
    dsu_u8 tmp8[8];
    if (!p) {
        return;
    }

    h32 = dsu_digest32_init();
    h64 = dsu_digest64_init();
    sep = 0u;

    dsu__u64_to_le_bytes(p->manifest_digest64, tmp8);
    h32 = dsu_digest32_update(h32, tmp8, 8u);
    h32 = dsu_digest32_update(h32, &sep, 1u);
    h64 = dsu_digest64_update(h64, tmp8, 8u);
    h64 = dsu_digest64_update(h64, &sep, 1u);

    dsu__u64_to_le_bytes(p->resolved_digest64, tmp8);
    h32 = dsu_digest32_update(h32, tmp8, 8u);
    h32 = dsu_digest32_update(h32, &sep, 1u);
    h64 = dsu_digest64_update(h64, tmp8, 8u);
    h64 = dsu_digest64_update(h64, &sep, 1u);

    h32 = dsu_digest32_update(h32, &p->operation, 1u);
    h32 = dsu_digest32_update(h32, &sep, 1u);
    h32 = dsu_digest32_update(h32, &p->scope, 1u);
    h32 = dsu_digest32_update(h32, &sep, 1u);

    h64 = dsu_digest64_update(h64, &p->operation, 1u);
    h64 = dsu_digest64_update(h64, &sep, 1u);
    h64 = dsu_digest64_update(h64, &p->scope, 1u);
    h64 = dsu_digest64_update(h64, &sep, 1u);

    h32 = dsu_digest32_update(h32, p->product_id, dsu__strlen(p->product_id));
    h32 = dsu_digest32_update(h32, &sep, 1u);
    h32 = dsu_digest32_update(h32, p->version, dsu__strlen(p->version));
    h32 = dsu_digest32_update(h32, &sep, 1u);
    h32 = dsu_digest32_update(h32, p->install_root, dsu__strlen(p->install_root));
    h32 = dsu_digest32_update(h32, &sep, 1u);

    h64 = dsu_digest64_update(h64, p->product_id, dsu__strlen(p->product_id));
    h64 = dsu_digest64_update(h64, &sep, 1u);
    h64 = dsu_digest64_update(h64, p->version, dsu__strlen(p->version));
    h64 = dsu_digest64_update(h64, &sep, 1u);
    h64 = dsu_digest64_update(h64, p->install_root, dsu__strlen(p->install_root));
    h64 = dsu_digest64_update(h64, &sep, 1u);

    for (i = 0u; i < p->component_count; ++i) {
        const char *c = p->components[i] ? p->components[i] : "";
        h32 = dsu_digest32_update(h32, c, dsu__strlen(c));
        h32 = dsu_digest32_update(h32, &sep, 1u);
        h64 = dsu_digest64_update(h64, c, dsu__strlen(c));
        h64 = dsu_digest64_update(h64, &sep, 1u);
    }
    for (i = 0u; i < p->step_count; ++i) {
        const dsu_plan_step_t *s = &p->steps[i];
        const char *a = s->arg ? s->arg : "";
        dsu_u8 kind_u8 = (dsu_u8)s->kind;
        h32 = dsu_digest32_update(h32, &kind_u8, 1u);
        h32 = dsu_digest32_update(h32, a, dsu__strlen(a));
        h32 = dsu_digest32_update(h32, &sep, 1u);
        h64 = dsu_digest64_update(h64, &kind_u8, 1u);
        h64 = dsu_digest64_update(h64, a, dsu__strlen(a));
        h64 = dsu_digest64_update(h64, &sep, 1u);
    }

    p->id_hash32 = h32;
    p->id_hash64 = h64;
}

dsu_status_t dsu_plan_build(dsu_ctx_t *ctx,
                           const dsu_resolve_result_t *resolved,
                           dsu_plan_t **out_plan) {
    dsu_plan_t *p;
    dsu_u32 resolved_count;
    dsu_u32 apply_count;
    dsu_u32 step_count;
    dsu_u32 i;

    if (!ctx || !resolved || !out_plan) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_plan = NULL;

    resolved_count = dsu_resolve_result_component_count(resolved);
    apply_count = 0u;
    for (i = 0u; i < resolved_count; ++i) {
        dsu_resolve_component_action_t a = dsu_resolve_result_component_action(resolved, i);
        if (a != DSU_RESOLVE_COMPONENT_ACTION_NONE) {
            ++apply_count;
        }
    }
    step_count = 1u + apply_count + 2u;

    p = (dsu_plan_t *)dsu__malloc((dsu_u32)sizeof(*p));
    if (!p) {
        return DSU_STATUS_IO_ERROR;
    }
    memset(p, 0, sizeof(*p));
    p->flags = ctx->config.flags;
    p->manifest_digest64 = dsu_resolve_result_manifest_digest64(resolved);
    p->resolved_digest64 = dsu_resolve_result_resolved_digest64(resolved);
    p->operation = (dsu_u8)dsu_resolve_result_operation(resolved);
    p->scope = (dsu_u8)dsu_resolve_result_scope(resolved);
    p->reserved8[0] = 0u;
    p->reserved8[1] = 0u;

    p->product_id = dsu__strdup(dsu_resolve_result_product_id(resolved));
    p->version = dsu__strdup(dsu_resolve_result_product_version(resolved));
    p->install_root = dsu__strdup(dsu_resolve_result_install_root(resolved));
    if (!p->product_id || !p->version || !p->install_root) {
        dsu_plan_destroy(ctx, p);
        return DSU_STATUS_IO_ERROR;
    }

    p->components = (char **)dsu__malloc(apply_count * (dsu_u32)sizeof(*p->components));
    if (!p->components && apply_count != 0u) {
        dsu_plan_destroy(ctx, p);
        return DSU_STATUS_IO_ERROR;
    }
    if (apply_count != 0u) {
        memset(p->components, 0, (size_t)apply_count * sizeof(*p->components));
    }
    p->component_count = 0u;
    for (i = 0u; i < resolved_count; ++i) {
        dsu_resolve_component_action_t a = dsu_resolve_result_component_action(resolved, i);
        const char *id;
        if (a == DSU_RESOLVE_COMPONENT_ACTION_NONE) {
            continue;
        }
        id = dsu_resolve_result_component_id(resolved, i);
        p->components[p->component_count] = dsu__strdup(id ? id : "");
        if (!p->components[p->component_count]) {
            dsu_plan_destroy(ctx, p);
            return DSU_STATUS_IO_ERROR;
        }
        ++p->component_count;
    }

    p->steps = (dsu_plan_step_t *)dsu__malloc(step_count * (dsu_u32)sizeof(*p->steps));
    if (!p->steps) {
        dsu_plan_destroy(ctx, p);
        return DSU_STATUS_IO_ERROR;
    }
    memset(p->steps, 0, (size_t)step_count * sizeof(*p->steps));

    p->steps[0].kind = DSU_PLAN_STEP_DECLARE_INSTALL_ROOT;
    p->steps[0].arg = dsu__strdup(p->install_root);
    if (!p->steps[0].arg) {
        dsu_plan_destroy(ctx, p);
        return DSU_STATUS_IO_ERROR;
    }
    {
        dsu_u32 w = 0u;
        for (i = 0u; i < resolved_count; ++i) {
            dsu_resolve_component_action_t a = dsu_resolve_result_component_action(resolved, i);
            const char *id = dsu_resolve_result_component_id(resolved, i);
            dsu_plan_step_kind_t kind = DSU_PLAN_STEP_INSTALL_COMPONENT;
            if (a == DSU_RESOLVE_COMPONENT_ACTION_NONE) {
                continue;
            }
            if (a == DSU_RESOLVE_COMPONENT_ACTION_UPGRADE) {
                kind = DSU_PLAN_STEP_UPGRADE_COMPONENT;
            } else if (a == DSU_RESOLVE_COMPONENT_ACTION_REPAIR) {
                kind = DSU_PLAN_STEP_REPAIR_COMPONENT;
            } else if (a == DSU_RESOLVE_COMPONENT_ACTION_UNINSTALL) {
                kind = DSU_PLAN_STEP_UNINSTALL_COMPONENT;
            } else {
                kind = DSU_PLAN_STEP_INSTALL_COMPONENT;
            }
            p->steps[1u + w].kind = kind;
            p->steps[1u + w].arg = dsu__strdup(id ? id : "");
            if (!p->steps[1u + w].arg) {
                dsu_plan_destroy(ctx, p);
                return DSU_STATUS_IO_ERROR;
            }
            ++w;
        }
    }
    p->steps[1u + apply_count].kind = DSU_PLAN_STEP_WRITE_STATE;
    p->steps[1u + apply_count].arg = NULL;
    p->steps[2u + apply_count].kind = DSU_PLAN_STEP_WRITE_LOG;
    p->steps[2u + apply_count].arg = NULL;
    p->step_count = step_count;

    dsu__plan_compute_ids(p);

    (void)dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_PLAN_BUILT,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_PLAN,
                      "plan built");

    *out_plan = p;
    return DSU_STATUS_SUCCESS;
}

void dsu_plan_destroy(dsu_ctx_t *ctx, dsu_plan_t *plan) {
    (void)ctx;
    if (!plan) {
        return;
    }
    dsu__plan_free(plan);
    dsu__free(plan);
}

dsu_u32 dsu_plan_id_hash32(const dsu_plan_t *plan) {
    if (!plan) {
        return 0u;
    }
    return plan->id_hash32;
}

dsu_u64 dsu_plan_id_hash64(const dsu_plan_t *plan) {
    if (!plan) {
        return (dsu_u64)0u;
    }
    return plan->id_hash64;
}

const char *dsu_plan_product_id(const dsu_plan_t *plan) {
    if (!plan || !plan->product_id) {
        return "";
    }
    return plan->product_id;
}

const char *dsu_plan_version(const dsu_plan_t *plan) {
    if (!plan || !plan->version) {
        return "";
    }
    return plan->version;
}

const char *dsu_plan_install_root(const dsu_plan_t *plan) {
    if (!plan || !plan->install_root) {
        return "";
    }
    return plan->install_root;
}

dsu_u32 dsu_plan_component_count(const dsu_plan_t *plan) {
    if (!plan) {
        return 0u;
    }
    return plan->component_count;
}

const char *dsu_plan_component_id(const dsu_plan_t *plan, dsu_u32 index) {
    if (!plan || index >= plan->component_count) {
        return NULL;
    }
    return plan->components[index];
}

dsu_u32 dsu_plan_step_count(const dsu_plan_t *plan) {
    if (!plan) {
        return 0u;
    }
    return plan->step_count;
}

dsu_plan_step_kind_t dsu_plan_step_kind(const dsu_plan_t *plan, dsu_u32 index) {
    if (!plan || index >= plan->step_count) {
        return (dsu_plan_step_kind_t)0;
    }
    return plan->steps[index].kind;
}

const char *dsu_plan_step_arg(const dsu_plan_t *plan, dsu_u32 index) {
    if (!plan || index >= plan->step_count) {
        return NULL;
    }
    return plan->steps[index].arg;
}

dsu_status_t dsu_plan_write_file(dsu_ctx_t *ctx, const dsu_plan_t *plan, const char *path) {
    dsu_blob_t payload;
    dsu_blob_t file_bytes;
    dsu_u8 magic[4];
    dsu_u32 i;
    dsu_status_t st;

    if (!ctx || !plan || !path) {
        return DSU_STATUS_INVALID_ARGS;
    }

    dsu__blob_init(&payload);
    dsu__blob_init(&file_bytes);

    st = dsu__blob_put_u32le(&payload, plan->flags);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u32le(&payload, plan->id_hash32);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u64le(&payload, plan->id_hash64);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u64le(&payload, plan->manifest_digest64);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u64le(&payload, plan->resolved_digest64);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u8(&payload, plan->operation);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u8(&payload, plan->scope);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u16le(&payload, 0u);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u32le(&payload, dsu__strlen(plan->product_id));
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u32le(&payload, dsu__strlen(plan->version));
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u32le(&payload, dsu__strlen(plan->install_root));
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u32le(&payload, plan->component_count);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u32le(&payload, plan->step_count);

    if (st == DSU_STATUS_SUCCESS && dsu__strlen(plan->product_id)) {
        st = dsu__blob_append(&payload, plan->product_id, dsu__strlen(plan->product_id));
    }
    if (st == DSU_STATUS_SUCCESS && dsu__strlen(plan->version)) {
        st = dsu__blob_append(&payload, plan->version, dsu__strlen(plan->version));
    }
    if (st == DSU_STATUS_SUCCESS && dsu__strlen(plan->install_root)) {
        st = dsu__blob_append(&payload, plan->install_root, dsu__strlen(plan->install_root));
    }

    for (i = 0u; st == DSU_STATUS_SUCCESS && i < plan->component_count; ++i) {
        dsu_u32 n = dsu__strlen(plan->components[i]);
        st = dsu__blob_put_u32le(&payload, n);
        if (st != DSU_STATUS_SUCCESS) break;
        if (n) {
            st = dsu__blob_append(&payload, plan->components[i], n);
            if (st != DSU_STATUS_SUCCESS) break;
        }
    }

    for (i = 0u; st == DSU_STATUS_SUCCESS && i < plan->step_count; ++i) {
        const dsu_plan_step_t *s = &plan->steps[i];
        const char *arg = s->arg ? s->arg : "";
        dsu_u32 arg_len = dsu__strlen(arg);
        st = dsu__blob_put_u8(&payload, (dsu_u8)s->kind);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_put_u8(&payload, 0u);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_put_u16le(&payload, 0u);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_put_u32le(&payload, arg_len);
        if (st != DSU_STATUS_SUCCESS) break;
        if (arg_len) {
            st = dsu__blob_append(&payload, arg, arg_len);
            if (st != DSU_STATUS_SUCCESS) break;
        }
    }

    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(&payload);
        dsu__blob_free(&file_bytes);
        return st;
    }

    magic[0] = (dsu_u8)DSU_PLAN_MAGIC_0;
    magic[1] = (dsu_u8)DSU_PLAN_MAGIC_1;
    magic[2] = (dsu_u8)DSU_PLAN_MAGIC_2;
    magic[3] = (dsu_u8)DSU_PLAN_MAGIC_3;

    st = dsu__file_wrap_payload(magic, (dsu_u16)DSU_PLAN_FORMAT_VERSION, payload.data, payload.size, &file_bytes);
    dsu__blob_free(&payload);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(&file_bytes);
        return st;
    }

    st = dsu__fs_write_all(path, file_bytes.data, file_bytes.size);
    dsu__blob_free(&file_bytes);

    if (st == DSU_STATUS_SUCCESS) {
        (void)dsu_log_emit(ctx,
                          dsu_ctx_get_audit_log(ctx),
                          DSU_EVENT_PLAN_WRITTEN,
                          (dsu_u8)DSU_LOG_SEVERITY_INFO,
                          (dsu_u8)DSU_LOG_CATEGORY_PLAN,
                          "plan written");
    }
    return st;
}

static dsu_status_t dsu__read_string_alloc(const dsu_u8 *buf,
                                          dsu_u32 len,
                                          dsu_u32 *io_off,
                                          dsu_u32 n,
                                          char **out_str) {
    char *s;
    dsu_u32 i;
    if (!out_str) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_str = NULL;
    if (n == 0u) {
        s = (char *)dsu__malloc(1u);
        if (!s) {
            return DSU_STATUS_IO_ERROR;
        }
        s[0] = '\0';
        *out_str = s;
        return DSU_STATUS_SUCCESS;
    }
    if (len - *io_off < n) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    s = (char *)dsu__malloc(n + 1u);
    if (!s) {
        return DSU_STATUS_IO_ERROR;
    }
    memcpy(s, buf + *io_off, (size_t)n);
    s[n] = '\0';
    for (i = 0u; i < n; ++i) {
        if (((unsigned char *)s)[i] == 0u) {
            dsu__free(s);
            return DSU_STATUS_INTEGRITY_ERROR;
        }
    }
    *io_off += n;
    *out_str = s;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_plan_read_file(dsu_ctx_t *ctx, const char *path, dsu_plan_t **out_plan) {
    dsu_u8 *file_bytes;
    dsu_u32 file_len;
    dsu_u8 magic[4];
    const dsu_u8 *payload;
    dsu_u32 payload_len;
    dsu_u32 off;
    dsu_status_t st;
    dsu_plan_t *p;
    dsu_u32 product_len;
    dsu_u32 version_len;
    dsu_u32 root_len;
    dsu_u16 reserved16;
    dsu_u32 i;

    if (!ctx || !path || !out_plan) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_plan = NULL;

    st = dsu__fs_read_all(&ctx->config, path, &file_bytes, &file_len);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    magic[0] = (dsu_u8)DSU_PLAN_MAGIC_0;
    magic[1] = (dsu_u8)DSU_PLAN_MAGIC_1;
    magic[2] = (dsu_u8)DSU_PLAN_MAGIC_2;
    magic[3] = (dsu_u8)DSU_PLAN_MAGIC_3;

    st = dsu__file_unwrap_payload(file_bytes,
                                  file_len,
                                  magic,
                                  (dsu_u16)DSU_PLAN_FORMAT_VERSION,
                                  &payload,
                                  &payload_len);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(file_bytes);
        return st;
    }

    p = (dsu_plan_t *)dsu__malloc((dsu_u32)sizeof(*p));
    if (!p) {
        dsu__free(file_bytes);
        return DSU_STATUS_IO_ERROR;
    }
    memset(p, 0, sizeof(*p));

    off = 0u;
    st = dsu__read_u32le(payload, payload_len, &off, &p->flags);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u32le(payload, payload_len, &off, &p->id_hash32);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u64le(payload, payload_len, &off, &p->id_hash64);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u64le(payload, payload_len, &off, &p->manifest_digest64);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u64le(payload, payload_len, &off, &p->resolved_digest64);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u8(payload, payload_len, &off, &p->operation);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u8(payload, payload_len, &off, &p->scope);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u16le(payload, payload_len, &off, &reserved16);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u32le(payload, payload_len, &off, &product_len);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u32le(payload, payload_len, &off, &version_len);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u32le(payload, payload_len, &off, &root_len);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u32le(payload, payload_len, &off, &p->component_count);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u32le(payload, payload_len, &off, &p->step_count);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(file_bytes);
        dsu_plan_destroy(ctx, p);
        return st;
    }
    (void)reserved16;

    st = dsu__read_string_alloc(payload, payload_len, &off, product_len, &p->product_id);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_string_alloc(payload, payload_len, &off, version_len, &p->version);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_string_alloc(payload, payload_len, &off, root_len, &p->install_root);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(file_bytes);
        dsu_plan_destroy(ctx, p);
        return st;
    }

    p->components = (char **)dsu__malloc(p->component_count * (dsu_u32)sizeof(*p->components));
    if (!p->components && p->component_count != 0u) {
        dsu__free(file_bytes);
        dsu_plan_destroy(ctx, p);
        return DSU_STATUS_IO_ERROR;
    }
    if (p->component_count != 0u) {
        memset(p->components, 0, (size_t)p->component_count * sizeof(*p->components));
    }
    for (i = 0u; i < p->component_count; ++i) {
        dsu_u32 n;
        st = dsu__read_u32le(payload, payload_len, &off, &n);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_string_alloc(payload, payload_len, &off, n, &p->components[i]);
        if (st != DSU_STATUS_SUCCESS) break;
    }
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(file_bytes);
        dsu_plan_destroy(ctx, p);
        return st;
    }

    p->steps = (dsu_plan_step_t *)dsu__malloc(p->step_count * (dsu_u32)sizeof(*p->steps));
    if (!p->steps && p->step_count != 0u) {
        dsu__free(file_bytes);
        dsu_plan_destroy(ctx, p);
        return DSU_STATUS_IO_ERROR;
    }
    if (p->step_count != 0u) {
        memset(p->steps, 0, (size_t)p->step_count * sizeof(*p->steps));
    }
    for (i = 0u; i < p->step_count; ++i) {
        dsu_u8 kind;
        dsu_u8 reserved8;
        dsu_u16 reserved16;
        dsu_u32 arg_len;
        st = dsu__read_u8(payload, payload_len, &off, &kind);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_u8(payload, payload_len, &off, &reserved8);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_u16le(payload, payload_len, &off, &reserved16);
        if (st != DSU_STATUS_SUCCESS) break;
        (void)reserved8;
        (void)reserved16;
        st = dsu__read_u32le(payload, payload_len, &off, &arg_len);
        if (st != DSU_STATUS_SUCCESS) break;
        p->steps[i].kind = (dsu_plan_step_kind_t)kind;
        st = dsu__read_string_alloc(payload, payload_len, &off, arg_len, &p->steps[i].arg);
        if (st != DSU_STATUS_SUCCESS) break;
        if (p->steps[i].arg && p->steps[i].arg[0] == '\0') {
            dsu__free(p->steps[i].arg);
            p->steps[i].arg = NULL;
        }
    }
    dsu__free(file_bytes);
    if (st != DSU_STATUS_SUCCESS) {
        dsu_plan_destroy(ctx, p);
        return st;
    }

    (void)dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_PLAN_LOADED,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_PLAN,
                      "plan loaded");

    *out_plan = p;
    return DSU_STATUS_SUCCESS;
}
