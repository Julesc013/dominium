/*
FILE: source/dominium/setup/core/src/platform_iface/dsu_platform_iface.c
MODULE: Dominium Setup
PURPOSE: Platform adapter dispatch + deterministic intent parsing (Plan S-6).
*/
#include "dsu/dsu_platform_iface.h"

#include "../dsu_ctx_internal.h"
#include "../log/dsu_events.h"
#include "../util/dsu_util_internal.h"

#include "dsu_platform_iface_internal.h"

#include <string.h>

#define DSU__INTENT_PREFIX "dsu.intent.v1"

static int dsu__plat_iface_valid(const dsu_platform_iface_t *iface) {
    if (!iface) return 0;
    if (iface->struct_version != DSU_PLATFORM_IFACE_VERSION) return 0;
    if (iface->struct_size < (dsu_u32)sizeof(dsu_platform_iface_t)) return 0;
    return 1;
}

void dsu_platform_intent_init(dsu_platform_intent_t *intent) {
    if (!intent) return;
    memset(intent, 0, sizeof(*intent));
    intent->struct_size = (dsu_u32)sizeof(*intent);
    intent->struct_version = 1u;
}

void dsu_platform_iface_init(dsu_platform_iface_t *iface) {
    if (!iface) return;
    memset(iface, 0, sizeof(*iface));
    iface->struct_size = (dsu_u32)sizeof(*iface);
    iface->struct_version = DSU_PLATFORM_IFACE_VERSION;
}

dsu_status_t dsu_ctx_set_platform_iface(dsu_ctx_t *ctx,
                                        const dsu_platform_iface_t *iface,
                                        void *iface_user) {
    if (!ctx) return DSU_STATUS_INVALID_ARGS;
    if (!iface) {
        dsu_platform_iface_init(&ctx->platform_iface);
        ctx->platform_user = NULL;
        return DSU_STATUS_SUCCESS;
    }
    if (!dsu__plat_iface_valid(iface)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    memcpy(&ctx->platform_iface, iface, sizeof(ctx->platform_iface));
    ctx->platform_user = iface_user;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__plat_missing(void) {
    return DSU_STATUS_INVALID_REQUEST;
}

static int dsu__plat_iface_has_register_handlers(const dsu_platform_iface_t *iface) {
    if (!iface) return 0;
    return iface->plat_register_app_entry ||
           iface->plat_register_file_assoc ||
           iface->plat_register_url_handler ||
           iface->plat_register_uninstall_entry ||
           iface->plat_declare_capability;
}

dsu_status_t plat_request_elevation(dsu_ctx_t *ctx) {
    if (!ctx) return DSU_STATUS_INVALID_ARGS;
    if (!dsu__plat_iface_valid(&ctx->platform_iface)) return DSU_STATUS_INTERNAL_ERROR;
    if (!ctx->platform_iface.plat_request_elevation) return dsu__plat_missing();
    return ctx->platform_iface.plat_request_elevation(ctx->platform_user, ctx);
}

dsu_status_t plat_register_app_entry(dsu_ctx_t *ctx, const dsu_platform_registrations_state_t *state, const dsu_platform_intent_t *intent) {
    if (!ctx || !state || !intent) return DSU_STATUS_INVALID_ARGS;
    if (!dsu__plat_iface_valid(&ctx->platform_iface)) return DSU_STATUS_INTERNAL_ERROR;
    if (!ctx->platform_iface.plat_register_app_entry) return dsu__plat_missing();
    return ctx->platform_iface.plat_register_app_entry(ctx->platform_user, ctx, state, intent);
}

dsu_status_t plat_register_file_assoc(dsu_ctx_t *ctx, const dsu_platform_registrations_state_t *state, const dsu_platform_intent_t *intent) {
    if (!ctx || !state || !intent) return DSU_STATUS_INVALID_ARGS;
    if (!dsu__plat_iface_valid(&ctx->platform_iface)) return DSU_STATUS_INTERNAL_ERROR;
    if (!ctx->platform_iface.plat_register_file_assoc) return dsu__plat_missing();
    return ctx->platform_iface.plat_register_file_assoc(ctx->platform_user, ctx, state, intent);
}

dsu_status_t plat_register_url_handler(dsu_ctx_t *ctx, const dsu_platform_registrations_state_t *state, const dsu_platform_intent_t *intent) {
    if (!ctx || !state || !intent) return DSU_STATUS_INVALID_ARGS;
    if (!dsu__plat_iface_valid(&ctx->platform_iface)) return DSU_STATUS_INTERNAL_ERROR;
    if (!ctx->platform_iface.plat_register_url_handler) return dsu__plat_missing();
    return ctx->platform_iface.plat_register_url_handler(ctx->platform_user, ctx, state, intent);
}

dsu_status_t plat_register_uninstall_entry(dsu_ctx_t *ctx, const dsu_platform_registrations_state_t *state, const dsu_platform_intent_t *intent) {
    if (!ctx || !state || !intent) return DSU_STATUS_INVALID_ARGS;
    if (!dsu__plat_iface_valid(&ctx->platform_iface)) return DSU_STATUS_INTERNAL_ERROR;
    if (!ctx->platform_iface.plat_register_uninstall_entry) return dsu__plat_missing();
    return ctx->platform_iface.plat_register_uninstall_entry(ctx->platform_user, ctx, state, intent);
}

dsu_status_t plat_declare_capability(dsu_ctx_t *ctx, const dsu_platform_registrations_state_t *state, const dsu_platform_intent_t *intent) {
    if (!ctx || !state || !intent) return DSU_STATUS_INVALID_ARGS;
    if (!dsu__plat_iface_valid(&ctx->platform_iface)) return DSU_STATUS_INTERNAL_ERROR;
    if (!ctx->platform_iface.plat_declare_capability) return dsu__plat_missing();
    return ctx->platform_iface.plat_declare_capability(ctx->platform_user, ctx, state, intent);
}

dsu_status_t plat_remove_registrations(dsu_ctx_t *ctx, const dsu_platform_registrations_state_t *state) {
    if (!ctx || !state) return DSU_STATUS_INVALID_ARGS;
    if (!dsu__plat_iface_valid(&ctx->platform_iface)) return DSU_STATUS_INTERNAL_ERROR;
    if (!ctx->platform_iface.plat_remove_registrations) return dsu__plat_missing();
    return ctx->platform_iface.plat_remove_registrations(ctx->platform_user, ctx, state);
}

dsu_status_t plat_atomic_dir_swap(dsu_ctx_t *ctx, const char *src_abs, const char *dst_abs) {
    if (!ctx || !src_abs || !dst_abs) return DSU_STATUS_INVALID_ARGS;
    if (!dsu__plat_iface_valid(&ctx->platform_iface)) return DSU_STATUS_INTERNAL_ERROR;
    if (!ctx->platform_iface.plat_atomic_dir_swap) return dsu__plat_missing();
    return ctx->platform_iface.plat_atomic_dir_swap(ctx->platform_user, ctx, src_abs, dst_abs);
}

dsu_status_t plat_flush_fs(dsu_ctx_t *ctx) {
    if (!ctx) return DSU_STATUS_INVALID_ARGS;
    if (!dsu__plat_iface_valid(&ctx->platform_iface)) return DSU_STATUS_INTERNAL_ERROR;
    if (!ctx->platform_iface.plat_flush_fs) return dsu__plat_missing();
    return ctx->platform_iface.plat_flush_fs(ctx->platform_user, ctx);
}

/* ---------------------------- Intent encoding ---------------------------- */

static int dsu__is_hex(unsigned char c) {
    if (c >= '0' && c <= '9') return 1;
    if (c >= 'a' && c <= 'f') return 1;
    if (c >= 'A' && c <= 'F') return 1;
    return 0;
}

static unsigned char dsu__hex_val(unsigned char c) {
    if (c >= '0' && c <= '9') return (unsigned char)(c - '0');
    if (c >= 'a' && c <= 'f') return (unsigned char)(10u + (c - 'a'));
    if (c >= 'A' && c <= 'F') return (unsigned char)(10u + (c - 'A'));
    return 0u;
}

static int dsu__is_unreserved_byte(unsigned char c) {
    if (c >= 'a' && c <= 'z') return 1;
    if (c >= 'A' && c <= 'Z') return 1;
    if (c >= '0' && c <= '9') return 1;
    if (c == '-' || c == '_' || c == '.' || c == '~') return 1;
    if (c == '/') return 1;
    return 0;
}

static dsu_status_t dsu__pct_encode(const char *in, char **out_ascii) {
    dsu_u32 i;
    dsu_u32 in_len;
    dsu_u32 out_len;
    char *out;
    static const char hex[] = "0123456789ABCDEF";

    if (!out_ascii) return DSU_STATUS_INVALID_ARGS;
    *out_ascii = NULL;
    if (!in) in = "";

    in_len = dsu__strlen(in);
    if (in_len == 0xFFFFFFFFu) return DSU_STATUS_INVALID_ARGS;

    out_len = 0u;
    for (i = 0u; i < in_len; ++i) {
        unsigned char c = (unsigned char)in[i];
        if (dsu__is_unreserved_byte(c)) {
            out_len += 1u;
        } else {
            if (out_len > 0xFFFFFFFFu - 3u) return DSU_STATUS_INTERNAL_ERROR;
            out_len += 3u;
        }
    }

    out = (char *)dsu__malloc(out_len + 1u);
    if (!out) return DSU_STATUS_IO_ERROR;

    out_len = 0u;
    for (i = 0u; i < in_len; ++i) {
        unsigned char c = (unsigned char)in[i];
        if (dsu__is_unreserved_byte(c)) {
            out[out_len++] = (char)c;
        } else {
            out[out_len++] = '%';
            out[out_len++] = hex[(c >> 4) & 0xFu];
            out[out_len++] = hex[c & 0xFu];
        }
    }
    out[out_len] = '\0';
    *out_ascii = out;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__pct_decode(const char *in_ascii, char **out_utf8) {
    dsu_u32 in_len;
    dsu_u32 i;
    dsu_u32 out_len;
    char *out;

    if (!out_utf8) return DSU_STATUS_INVALID_ARGS;
    *out_utf8 = NULL;
    if (!in_ascii) in_ascii = "";

    in_len = dsu__strlen(in_ascii);
    if (in_len == 0xFFFFFFFFu) return DSU_STATUS_INVALID_ARGS;

    out = (char *)dsu__malloc(in_len + 1u);
    if (!out) return DSU_STATUS_IO_ERROR;

    out_len = 0u;
    i = 0u;
    while (i < in_len) {
        unsigned char c = (unsigned char)in_ascii[i++];
        if (c == '%' && i + 1u < in_len) {
            unsigned char a = (unsigned char)in_ascii[i + 0u];
            unsigned char b = (unsigned char)in_ascii[i + 1u];
            if (dsu__is_hex(a) && dsu__is_hex(b)) {
                unsigned char v = (unsigned char)((dsu__hex_val(a) << 4) | dsu__hex_val(b));
                out[out_len++] = (char)v;
                i += 2u;
                continue;
            }
        }
        out[out_len++] = (char)c;
    }
    out[out_len] = '\0';
    *out_utf8 = out;
    return DSU_STATUS_SUCCESS;
}

static const char *dsu__intent_kind_name(dsu_u8 kind) {
    if (kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_APP_ENTRY) return "REGISTER_APP_ENTRY";
    if (kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_FILE_ASSOC) return "REGISTER_FILE_ASSOC";
    if (kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_URL_HANDLER) return "REGISTER_URL_HANDLER";
    if (kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_UNINSTALL_ENTRY) return "REGISTER_UNINSTALL_ENTRY";
    return "DECLARE_CAPABILITY";
}

static dsu_status_t dsu__intent_kind_from_name(const char *s, dsu_u8 *out_kind) {
    if (!s || !out_kind) return DSU_STATUS_INVALID_ARGS;
    *out_kind = 0u;
    if (dsu__streq(s, "REGISTER_APP_ENTRY")) {
        *out_kind = (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_APP_ENTRY;
        return DSU_STATUS_SUCCESS;
    }
    if (dsu__streq(s, "REGISTER_FILE_ASSOC")) {
        *out_kind = (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_FILE_ASSOC;
        return DSU_STATUS_SUCCESS;
    }
    if (dsu__streq(s, "REGISTER_URL_HANDLER")) {
        *out_kind = (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_URL_HANDLER;
        return DSU_STATUS_SUCCESS;
    }
    if (dsu__streq(s, "REGISTER_UNINSTALL_ENTRY")) {
        *out_kind = (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_UNINSTALL_ENTRY;
        return DSU_STATUS_SUCCESS;
    }
    if (dsu__streq(s, "DECLARE_CAPABILITY")) {
        *out_kind = (dsu_u8)DSU_PLATFORM_INTENT_DECLARE_CAPABILITY;
        return DSU_STATUS_SUCCESS;
    }
    return DSU_STATUS_INVALID_REQUEST;
}

static dsu_status_t dsu__blob_append_kv(dsu_blob_t *b, const char *key, const char *val_utf8) {
    dsu_status_t st;
    char *enc = NULL;
    if (!b || !key) return DSU_STATUS_INVALID_ARGS;
    if (!val_utf8) val_utf8 = "";
    st = dsu__blob_append(b, ";", 1u);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append(b, key, dsu__strlen(key));
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append(b, "=", 1u);
    if (st == DSU_STATUS_SUCCESS) st = dsu__pct_encode(val_utf8, &enc);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append(b, enc, dsu__strlen(enc));
    dsu__free(enc);
    return st;
}

dsu_status_t dsu__platform_encode_intent_v1(const dsu_platform_intent_t *intent, char **out_ascii) {
    dsu_blob_t b;
    dsu_status_t st;
    const char *kind_name;

    if (!out_ascii) return DSU_STATUS_INVALID_ARGS;
    *out_ascii = NULL;
    if (!intent || intent->struct_version != 1u) return DSU_STATUS_INVALID_ARGS;

    kind_name = dsu__intent_kind_name(intent->kind);

    dsu__blob_init(&b);
    st = dsu__blob_append(&b, DSU__INTENT_PREFIX, (dsu_u32)sizeof(DSU__INTENT_PREFIX) - 1u);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_kv(&b, "kind", kind_name);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_kv(&b, "app_id", intent->app_id);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_kv(&b, "display_name", intent->display_name);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_kv(&b, "exec_relpath", intent->exec_relpath);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_kv(&b, "arguments", intent->arguments);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_kv(&b, "icon_relpath", intent->icon_relpath);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_kv(&b, "extension", intent->extension);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_kv(&b, "protocol", intent->protocol);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_kv(&b, "marker_relpath", intent->marker_relpath);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_kv(&b, "capability_id", intent->capability_id);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_kv(&b, "capability_value", intent->capability_value);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_kv(&b, "publisher", intent->publisher);

    if (st == DSU_STATUS_SUCCESS) {
        st = dsu__blob_append(&b, "\0", 1u);
    }
    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(&b);
        return st;
    }
    *out_ascii = (char *)b.data;
    return DSU_STATUS_SUCCESS;
}

static const char *dsu__scan_keyval(const char *p, const char **out_key, dsu_u32 *out_key_len, const char **out_val, dsu_u32 *out_val_len) {
    const char *k0;
    const char *eq;
    const char *v0;
    const char *end;
    if (!p || !out_key || !out_key_len || !out_val || !out_val_len) return NULL;
    if (*p == '\0') return NULL;
    if (*p == ';') ++p;
    k0 = p;
    eq = strchr(p, '=');
    if (!eq) return NULL;
    v0 = eq + 1;
    end = strchr(v0, ';');
    if (!end) end = strchr(v0, '\0');
    *out_key = k0;
    *out_key_len = (dsu_u32)(eq - k0);
    *out_val = v0;
    *out_val_len = (dsu_u32)(end - v0);
    return end;
}

static dsu_status_t dsu__dup_substr(const char *s, dsu_u32 n, char **out) {
    char *p;
    if (!out) return DSU_STATUS_INVALID_ARGS;
    *out = NULL;
    p = (char *)dsu__malloc(n + 1u);
    if (!p) return DSU_STATUS_IO_ERROR;
    if (n) memcpy(p, s, (size_t)n);
    p[n] = '\0';
    *out = p;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu__platform_decode_intent_v1(const char *ascii, dsu_platform_intent_t *out_intent) {
    const char *p;
    dsu_u32 prefix_len;
    char *kind_tmp = NULL;
    dsu_u8 kind_u8;
    dsu_status_t st = DSU_STATUS_SUCCESS;

    if (!ascii || !out_intent) return DSU_STATUS_INVALID_ARGS;
    dsu_platform_intent_init(out_intent);

    prefix_len = (dsu_u32)sizeof(DSU__INTENT_PREFIX) - 1u;
    if (strncmp(ascii, DSU__INTENT_PREFIX, (size_t)prefix_len) != 0) {
        return DSU_STATUS_PARSE_ERROR;
    }

    p = ascii + prefix_len;
    while (st == DSU_STATUS_SUCCESS) {
        const char *k;
        const char *v;
        dsu_u32 kn;
        dsu_u32 vn;
        char *kdup = NULL;
        char *vdup = NULL;
        char *vdec = NULL;

        p = dsu__scan_keyval(p, &k, &kn, &v, &vn);
        if (!p) break;

        st = dsu__dup_substr(k, kn, &kdup);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__dup_substr(v, vn, &vdup);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(kdup);
            break;
        }
        st = dsu__pct_decode(vdup, &vdec);
        dsu__free(vdup);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(kdup);
            break;
        }

        if (dsu__streq(kdup, "kind")) {
            dsu__free(kind_tmp);
            kind_tmp = vdec;
            vdec = NULL;
        } else if (dsu__streq(kdup, "app_id")) {
            out_intent->app_id = vdec; vdec = NULL;
        } else if (dsu__streq(kdup, "display_name")) {
            out_intent->display_name = vdec; vdec = NULL;
        } else if (dsu__streq(kdup, "exec_relpath")) {
            out_intent->exec_relpath = vdec; vdec = NULL;
        } else if (dsu__streq(kdup, "arguments")) {
            out_intent->arguments = vdec; vdec = NULL;
        } else if (dsu__streq(kdup, "icon_relpath")) {
            out_intent->icon_relpath = vdec; vdec = NULL;
        } else if (dsu__streq(kdup, "extension")) {
            out_intent->extension = vdec; vdec = NULL;
        } else if (dsu__streq(kdup, "protocol")) {
            out_intent->protocol = vdec; vdec = NULL;
        } else if (dsu__streq(kdup, "marker_relpath")) {
            out_intent->marker_relpath = vdec; vdec = NULL;
        } else if (dsu__streq(kdup, "capability_id")) {
            out_intent->capability_id = vdec; vdec = NULL;
        } else if (dsu__streq(kdup, "capability_value")) {
            out_intent->capability_value = vdec; vdec = NULL;
        } else if (dsu__streq(kdup, "publisher")) {
            out_intent->publisher = vdec; vdec = NULL;
        }

        dsu__free(vdec);
        dsu__free(kdup);
    }

    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(kind_tmp);
        dsu__platform_intent_free_fields(out_intent);
        dsu_platform_intent_init(out_intent);
        return st;
    }

    if (!kind_tmp) {
        dsu__platform_intent_free_fields(out_intent);
        dsu_platform_intent_init(out_intent);
        return DSU_STATUS_PARSE_ERROR;
    }
    st = dsu__intent_kind_from_name(kind_tmp, &kind_u8);
    dsu__free(kind_tmp);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__platform_intent_free_fields(out_intent);
        dsu_platform_intent_init(out_intent);
        return st;
    }
    out_intent->kind = kind_u8;

    /* Normalize NULLs to empty strings for adapter convenience. */
    if (!out_intent->app_id) out_intent->app_id = dsu__strdup("");
    if (!out_intent->display_name) out_intent->display_name = dsu__strdup("");
    if (!out_intent->exec_relpath) out_intent->exec_relpath = dsu__strdup("");
    if (!out_intent->arguments) out_intent->arguments = dsu__strdup("");
    if (!out_intent->icon_relpath) out_intent->icon_relpath = dsu__strdup("");
    if (!out_intent->extension) out_intent->extension = dsu__strdup("");
    if (!out_intent->protocol) out_intent->protocol = dsu__strdup("");
    if (!out_intent->marker_relpath) out_intent->marker_relpath = dsu__strdup("");
    if (!out_intent->capability_id) out_intent->capability_id = dsu__strdup("");
    if (!out_intent->capability_value) out_intent->capability_value = dsu__strdup("");
    if (!out_intent->publisher) out_intent->publisher = dsu__strdup("");

    if (!out_intent->app_id || !out_intent->display_name || !out_intent->exec_relpath ||
        !out_intent->arguments || !out_intent->icon_relpath || !out_intent->extension ||
        !out_intent->protocol || !out_intent->marker_relpath || !out_intent->capability_id ||
        !out_intent->capability_value || !out_intent->publisher) {
        dsu__platform_intent_free_fields(out_intent);
        dsu_platform_intent_init(out_intent);
        return DSU_STATUS_IO_ERROR;
    }

    /* Required-field validation (matches manifest schema; empty values are treated as missing). */
    if (out_intent->kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_APP_ENTRY) {
        if (out_intent->app_id[0] == '\0' || out_intent->display_name[0] == '\0' || out_intent->exec_relpath[0] == '\0') return DSU_STATUS_PARSE_ERROR;
    } else if (out_intent->kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_FILE_ASSOC) {
        if (out_intent->extension[0] == '\0' || out_intent->app_id[0] == '\0') return DSU_STATUS_PARSE_ERROR;
    } else if (out_intent->kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_URL_HANDLER) {
        if (out_intent->protocol[0] == '\0' || out_intent->app_id[0] == '\0') return DSU_STATUS_PARSE_ERROR;
    } else if (out_intent->kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_UNINSTALL_ENTRY) {
        if (out_intent->display_name[0] == '\0') return DSU_STATUS_PARSE_ERROR;
    } else if (out_intent->kind == (dsu_u8)DSU_PLATFORM_INTENT_DECLARE_CAPABILITY) {
        if (out_intent->capability_id[0] == '\0' || out_intent->capability_value[0] == '\0') return DSU_STATUS_PARSE_ERROR;
    }

    return DSU_STATUS_SUCCESS;
}

void dsu__platform_intent_free_fields(dsu_platform_intent_t *intent) {
    if (!intent) return;
    dsu__free((void *)intent->app_id);
    dsu__free((void *)intent->display_name);
    dsu__free((void *)intent->exec_relpath);
    dsu__free((void *)intent->arguments);
    dsu__free((void *)intent->icon_relpath);
    dsu__free((void *)intent->extension);
    dsu__free((void *)intent->protocol);
    dsu__free((void *)intent->marker_relpath);
    dsu__free((void *)intent->capability_id);
    dsu__free((void *)intent->capability_value);
    dsu__free((void *)intent->publisher);

    intent->app_id = NULL;
    intent->display_name = NULL;
    intent->exec_relpath = NULL;
    intent->arguments = NULL;
    intent->icon_relpath = NULL;
    intent->extension = NULL;
    intent->protocol = NULL;
    intent->marker_relpath = NULL;
    intent->capability_id = NULL;
    intent->capability_value = NULL;
    intent->publisher = NULL;
}

/* -------------------------- State -> adapter calls ----------------------- */

static dsu_status_t dsu__build_reg_state(dsu_ctx_t *ctx,
                                        const dsu_state_t *state,
                                        dsu_platform_registrations_state_t *out_rs,
                                        dsu_platform_intent_t **out_intents) {
    dsu_u32 ci;
    dsu_u32 total = 0u;
    dsu_platform_intent_t *intents;
    dsu_u32 w = 0u;
    dsu_status_t st = DSU_STATUS_SUCCESS;

    if (!ctx || !state || !out_rs || !out_intents) return DSU_STATUS_INVALID_ARGS;
    *out_intents = NULL;
    memset(out_rs, 0, sizeof(*out_rs));
    out_rs->struct_size = (dsu_u32)sizeof(*out_rs);
    out_rs->struct_version = 1u;

    for (ci = 0u; ci < dsu_state_component_count(state); ++ci) {
        total += dsu_state_component_registration_count(state, ci);
    }

    intents = (dsu_platform_intent_t *)dsu__malloc(total ? (total * (dsu_u32)sizeof(*intents)) : 1u);
    if (!intents) return DSU_STATUS_IO_ERROR;
    memset(intents, 0, total ? (total * (dsu_u32)sizeof(*intents)) : 1u);

    for (ci = 0u; ci < dsu_state_component_count(state) && st == DSU_STATUS_SUCCESS; ++ci) {
        dsu_u32 ri;
        const char *component_id = dsu_state_component_id(state, ci);
        for (ri = 0u; ri < dsu_state_component_registration_count(state, ci) && st == DSU_STATUS_SUCCESS; ++ri) {
            const char *reg = dsu_state_component_registration(state, ci, ri);
            dsu_platform_intent_t it;
            dsu_platform_intent_init(&it);
            st = dsu__platform_decode_intent_v1(reg, &it);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__platform_intent_free_fields(&it);
                break;
            }
            it.component_id = component_id ? component_id : "";
            intents[w++] = it;
        }
    }

    if (st != DSU_STATUS_SUCCESS) {
        dsu_u32 i;
        for (i = 0u; i < w; ++i) {
            dsu__platform_intent_free_fields(&intents[i]);
        }
        dsu__free(intents);
        return st;
    }

    out_rs->product_id = dsu_state_product_id(state);
    out_rs->product_version = dsu_state_product_version_installed(state);
    out_rs->build_channel = dsu_state_build_channel(state);
    out_rs->platform_triple = dsu_state_platform(state);
    out_rs->scope = (dsu_u8)dsu_state_install_scope(state);
    out_rs->install_root = dsu_state_primary_install_root(state);
    out_rs->intent_count = w;
    out_rs->intents = intents;

    *out_intents = intents;
    return DSU_STATUS_SUCCESS;
}

static void dsu__free_reg_state_intents(dsu_platform_intent_t *intents, dsu_u32 count) {
    dsu_u32 i;
    if (!intents) return;
    for (i = 0u; i < count; ++i) {
        dsu__platform_intent_free_fields(&intents[i]);
    }
    dsu__free(intents);
}

dsu_status_t dsu_platform_register_from_state(dsu_ctx_t *ctx, const dsu_state_t *state) {
    dsu_platform_registrations_state_t rs;
    dsu_platform_intent_t *intents = NULL;
    dsu_u32 i;
    dsu_status_t st;

    if (!ctx || !state) return DSU_STATUS_INVALID_ARGS;
    if (!dsu__plat_iface_valid(&ctx->platform_iface)) return DSU_STATUS_INTERNAL_ERROR;
    if (!dsu__plat_iface_has_register_handlers(&ctx->platform_iface)) return DSU_STATUS_INVALID_REQUEST;

    st = dsu__build_reg_state(ctx, state, &rs, &intents);
    if (st != DSU_STATUS_SUCCESS) return st;

    (void)dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_PLATFORM_REGISTER_START,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_GENERAL,
                      "platform-register start");

    for (i = 0u; i < rs.intent_count; ++i) {
        const dsu_platform_intent_t *it = &rs.intents[i];
        if (it->kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_APP_ENTRY) {
            st = plat_register_app_entry(ctx, &rs, it);
        } else if (it->kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_FILE_ASSOC) {
            st = plat_register_file_assoc(ctx, &rs, it);
        } else if (it->kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_URL_HANDLER) {
            st = plat_register_url_handler(ctx, &rs, it);
        } else if (it->kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_UNINSTALL_ENTRY) {
            st = plat_register_uninstall_entry(ctx, &rs, it);
        } else if (it->kind == (dsu_u8)DSU_PLATFORM_INTENT_DECLARE_CAPABILITY) {
            st = plat_declare_capability(ctx, &rs, it);
        } else {
            st = DSU_STATUS_INVALID_REQUEST;
        }
        if (st != DSU_STATUS_SUCCESS) {
            break;
        }
    }

    dsu__free_reg_state_intents(intents, rs.intent_count);
    rs.intents = NULL;
    rs.intent_count = 0u;

    return st;
}

dsu_status_t dsu_platform_unregister_from_state(dsu_ctx_t *ctx, const dsu_state_t *state) {
    dsu_platform_registrations_state_t rs;
    dsu_platform_intent_t *intents = NULL;
    dsu_status_t st;

    if (!ctx || !state) return DSU_STATUS_INVALID_ARGS;

    st = dsu__build_reg_state(ctx, state, &rs, &intents);
    if (st != DSU_STATUS_SUCCESS) return st;

    (void)dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_PLATFORM_UNREGISTER_START,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_GENERAL,
                      "platform-unregister start");

    st = plat_remove_registrations(ctx, &rs);

    dsu__free_reg_state_intents(intents, rs.intent_count);
    rs.intents = NULL;
    rs.intent_count = 0u;
    return st;
}
