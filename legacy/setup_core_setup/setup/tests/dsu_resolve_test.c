/*
FILE: source/dominium/setup/tests/dsu_resolve_test.c
MODULE: Dominium Setup
PURPOSE: Plan S-3 resolver tests (selection, closure, conflicts, platform, state reconciliation, determinism).
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dsu/dsu_callbacks.h"
#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"
#include "dsu/dsu_fs.h"
#include "dsu/dsu_manifest.h"
#include "dsu/dsu_resolve.h"
#include "dsu/dsu_state.h"

#include "../core/src/fs/dsu_platform_iface.h"

typedef struct buf_t {
    unsigned char *data;
    unsigned long len;
    unsigned long cap;
} buf_t;

static void buf_free(buf_t *b) {
    if (!b) return;
    free(b->data);
    b->data = NULL;
    b->len = 0ul;
    b->cap = 0ul;
}

static int buf_reserve(buf_t *b, unsigned long add) {
    unsigned long need;
    unsigned long new_cap;
    unsigned char *p;
    if (!b) return 0;
    if (add == 0ul) return 1;
    need = b->len + add;
    if (need < b->len) return 0;
    if (need <= b->cap) return 1;
    new_cap = (b->cap == 0ul) ? 256ul : b->cap;
    while (new_cap < need) {
        if (new_cap > 0x7FFFFFFFul) {
            new_cap = need;
            break;
        }
        new_cap *= 2ul;
    }
    p = (unsigned char *)realloc(b->data, (size_t)new_cap);
    if (!p) return 0;
    b->data = p;
    b->cap = new_cap;
    return 1;
}

static int buf_append(buf_t *b, const void *bytes, unsigned long n) {
    if (!b) return 0;
    if (n == 0ul) return 1;
    if (!bytes) return 0;
    if (!buf_reserve(b, n)) return 0;
    memcpy(b->data + b->len, bytes, (size_t)n);
    b->len += n;
    return 1;
}

static int buf_put_u8(buf_t *b, unsigned char v) {
    return buf_append(b, &v, 1ul);
}

static int buf_put_u16le(buf_t *b, unsigned short v) {
    unsigned char tmp[2];
    tmp[0] = (unsigned char)(v & 0xFFu);
    tmp[1] = (unsigned char)((v >> 8) & 0xFFu);
    return buf_append(b, tmp, 2ul);
}

static int buf_put_u32le(buf_t *b, unsigned long v) {
    unsigned char tmp[4];
    tmp[0] = (unsigned char)(v & 0xFFul);
    tmp[1] = (unsigned char)((v >> 8) & 0xFFul);
    tmp[2] = (unsigned char)((v >> 16) & 0xFFul);
    tmp[3] = (unsigned char)((v >> 24) & 0xFFul);
    return buf_append(b, tmp, 4ul);
}

static int buf_put_tlv(buf_t *b, unsigned short type, const void *payload, unsigned long payload_len) {
    if (!buf_put_u16le(b, type)) return 0;
    if (!buf_put_u32le(b, payload_len)) return 0;
    return buf_append(b, payload, payload_len);
}

static int buf_put_tlv_u32(buf_t *b, unsigned short type, unsigned long v) {
    unsigned char tmp[4];
    tmp[0] = (unsigned char)(v & 0xFFul);
    tmp[1] = (unsigned char)((v >> 8) & 0xFFul);
    tmp[2] = (unsigned char)((v >> 16) & 0xFFul);
    tmp[3] = (unsigned char)((v >> 24) & 0xFFul);
    return buf_put_tlv(b, type, tmp, 4ul);
}

static int buf_put_tlv_u8(buf_t *b, unsigned short type, unsigned char v) {
    return buf_put_tlv(b, type, &v, 1ul);
}

static int buf_put_tlv_str(buf_t *b, unsigned short type, const char *s) {
    unsigned long n;
    if (!s) s = "";
    n = (unsigned long)strlen(s);
    return buf_put_tlv(b, type, s, n);
}

static unsigned long header_checksum32_base(const unsigned char hdr[20]) {
    unsigned long sum = 0ul;
    unsigned long i;
    for (i = 0ul; i < 16ul; ++i) {
        sum += (unsigned long)hdr[i];
    }
    return sum;
}

static int wrap_file(buf_t *out_file, const unsigned char magic[4], unsigned short version, const buf_t *payload) {
    unsigned char hdr[20];
    unsigned long checksum;
    if (!out_file || !magic || !payload) return 0;
    memset(out_file, 0, sizeof(*out_file));
    memset(hdr, 0, sizeof(hdr));
    hdr[0] = magic[0];
    hdr[1] = magic[1];
    hdr[2] = magic[2];
    hdr[3] = magic[3];
    hdr[4] = (unsigned char)(version & 0xFFu);
    hdr[5] = (unsigned char)((version >> 8) & 0xFFu);
    hdr[6] = 0xFEu;
    hdr[7] = 0xFFu;
    hdr[8] = 20u;
    hdr[9] = 0u;
    hdr[10] = 0u;
    hdr[11] = 0u;
    hdr[12] = (unsigned char)(payload->len & 0xFFul);
    hdr[13] = (unsigned char)((payload->len >> 8) & 0xFFul);
    hdr[14] = (unsigned char)((payload->len >> 16) & 0xFFul);
    hdr[15] = (unsigned char)((payload->len >> 24) & 0xFFul);
    checksum = header_checksum32_base(hdr);
    hdr[16] = (unsigned char)(checksum & 0xFFul);
    hdr[17] = (unsigned char)((checksum >> 8) & 0xFFul);
    hdr[18] = (unsigned char)((checksum >> 16) & 0xFFul);
    hdr[19] = (unsigned char)((checksum >> 24) & 0xFFul);
    if (!buf_append(out_file, hdr, 20ul)) return 0;
    if (!buf_append(out_file, payload->data, payload->len)) return 0;
    return 1;
}

static int write_bytes_file(const char *path, const unsigned char *bytes, unsigned long len) {
    FILE *f;
    size_t n;
    if (!path || (!bytes && len != 0ul)) return 0;
    f = fopen(path, "wb");
    if (!f) return 0;
    n = (size_t)len;
    if (n != 0u) {
        if (fwrite(bytes, 1u, n, f) != n) {
            fclose(f);
            return 0;
        }
    }
    if (fclose(f) != 0) return 0;
    return 1;
}

static int expect(int cond, const char *msg) {
    if (!cond) {
        fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
        return 0;
    }
    return 1;
}

static dsu_ctx_t *create_ctx_deterministic(void) {
    dsu_config_t cfg;
    dsu_callbacks_t cbs;
    dsu_ctx_t *ctx = NULL;
    dsu_status_t st;
    dsu_config_init(&cfg);
    dsu_callbacks_init(&cbs);
    cfg.flags |= DSU_CONFIG_FLAG_DETERMINISTIC;
    st = dsu_ctx_create(&cfg, &cbs, NULL, &ctx);
    if (st != DSU_STATUS_SUCCESS) {
        return NULL;
    }
    return ctx;
}

static int bytes_equal(const unsigned char *a, unsigned long a_len, const unsigned char *b, unsigned long b_len) {
    if (a_len != b_len) return 0;
    if (a_len == 0ul) return 1;
    if (!a || !b) return 0;
    return memcmp(a, b, (size_t)a_len) == 0;
}

static int buf_put_cstr(buf_t *b, const char *s) {
    if (!s) s = "";
    return buf_append(b, s, (unsigned long)strlen(s));
}

static int buf_put_u64_dec(buf_t *b, dsu_u64 v) {
    char tmp[32];
    unsigned int n = 0u;
    unsigned int i;
    if (!b) return 0;
    if (v == (dsu_u64)0u) {
        tmp[n++] = '0';
    } else {
        while (v != (dsu_u64)0u && n < (unsigned int)(sizeof(tmp) / sizeof(tmp[0]))) {
            unsigned int digit = (unsigned int)(v % (dsu_u64)10u);
            tmp[n++] = (char)('0' + digit);
            v /= (dsu_u64)10u;
        }
    }
    for (i = 0u; i < n; ++i) {
        char c = tmp[n - 1u - i];
        if (!buf_append(b, &c, 1ul)) return 0;
    }
    return 1;
}

static int buf_put_u32_dec(buf_t *b, dsu_u32 v) {
    return buf_put_u64_dec(b, (dsu_u64)v);
}

/* Manifest TLVs (docs/setup/MANIFEST_SCHEMA.md) */
#define T_MANIFEST_ROOT 0x0001u
#define T_ROOT_VER 0x0002u
#define T_PRODUCT_ID 0x0010u
#define T_PRODUCT_VER 0x0011u
#define T_BUILD_CHANNEL 0x0012u
#define T_PLATFORM_TARGET 0x0020u
#define T_INSTALL_ROOT 0x0030u
#define T_IR_VER 0x0031u
#define T_IR_SCOPE 0x0032u
#define T_IR_PLATFORM 0x0033u
#define T_IR_PATH 0x0034u
#define T_COMPONENT 0x0040u
#define T_C_VER 0x0041u
#define T_C_ID 0x0042u
#define T_C_VERSTR 0x0043u
#define T_C_KIND 0x0044u
#define T_C_FLAGS 0x0045u
#define T_DEPENDENCY 0x0046u
#define T_DEP_VER 0x0047u
#define T_DEP_ID 0x0048u
#define T_DEP_KIND 0x0049u
#define T_DEP_CONSTRAINT_VER 0x004Au
#define T_CONFLICT 0x004Bu

typedef struct dep_spec_t {
    const char *id;
    dsu_u8 constraint_kind;
    const char *constraint_version;
} dep_spec_t;

typedef struct component_spec_t {
    const char *id;
    const char *version;
    dsu_u8 kind;
    dsu_u32 flags;
    const dep_spec_t *deps;
    dsu_u32 dep_count;
    const char *const *conflicts;
    dsu_u32 conflict_count;
} component_spec_t;

typedef struct install_root_spec_t {
    dsu_u8 scope;
    const char *platform;
    const char *path;
} install_root_spec_t;

typedef struct manifest_spec_t {
    const char *product_id;
    const char *product_version;
    const char *build_channel;
    const char *const *platform_targets;
    dsu_u32 platform_target_count;
    const install_root_spec_t *install_roots;
    dsu_u32 install_root_count;
    const component_spec_t *components;
    dsu_u32 component_count;
} manifest_spec_t;

static int build_install_root_container(buf_t *out_ir, const install_root_spec_t *ir) {
    if (!out_ir || !ir) return 0;
    memset(out_ir, 0, sizeof(*out_ir));
    if (!buf_put_tlv_u32(out_ir, T_IR_VER, 1ul)) return 0;
    if (!buf_put_tlv_u8(out_ir, T_IR_SCOPE, (unsigned char)ir->scope)) return 0;
    if (!buf_put_tlv_str(out_ir, T_IR_PLATFORM, ir->platform)) return 0;
    if (!buf_put_tlv_str(out_ir, T_IR_PATH, ir->path)) return 0;
    return 1;
}

static int build_dependency_container(buf_t *out_dep, const dep_spec_t *d) {
    if (!out_dep || !d) return 0;
    memset(out_dep, 0, sizeof(*out_dep));
    if (!buf_put_tlv_u32(out_dep, T_DEP_VER, 1ul)) return 0;
    if (!buf_put_tlv_str(out_dep, T_DEP_ID, d->id)) return 0;
    if (!buf_put_tlv_u8(out_dep, T_DEP_KIND, (unsigned char)d->constraint_kind)) return 0;
    if (d->constraint_kind != (dsu_u8)DSU_MANIFEST_VERSION_CONSTRAINT_ANY) {
        if (!buf_put_tlv_str(out_dep, T_DEP_CONSTRAINT_VER, d->constraint_version ? d->constraint_version : "")) return 0;
    }
    return 1;
}

static int build_component_container(buf_t *out_comp, const component_spec_t *c) {
    dsu_u32 i;
    if (!out_comp || !c) return 0;
    memset(out_comp, 0, sizeof(*out_comp));
    if (!buf_put_tlv_u32(out_comp, T_C_VER, 1ul)) return 0;
    if (!buf_put_tlv_str(out_comp, T_C_ID, c->id)) return 0;
    if (c->version && c->version[0] != '\0') {
        if (!buf_put_tlv_str(out_comp, T_C_VERSTR, c->version)) return 0;
    }
    if (!buf_put_tlv_u8(out_comp, T_C_KIND, (unsigned char)c->kind)) return 0;
    if (!buf_put_tlv_u32(out_comp, T_C_FLAGS, (unsigned long)c->flags)) return 0;

    for (i = 0u; i < c->dep_count; ++i) {
        buf_t dep;
        if (!build_dependency_container(&dep, &c->deps[i])) return 0;
        if (!buf_put_tlv(out_comp, T_DEPENDENCY, dep.data, dep.len)) {
            buf_free(&dep);
            return 0;
        }
        buf_free(&dep);
    }
    for (i = 0u; i < c->conflict_count; ++i) {
        if (!buf_put_tlv_str(out_comp, T_CONFLICT, c->conflicts[i])) return 0;
    }
    return 1;
}

static int build_manifest_file(buf_t *out_file, const manifest_spec_t *spec) {
    dsu_u32 i;
    buf_t root;
    buf_t payload;
    buf_t cb;
    buf_t irb;
    static const unsigned char magic[4] = {'D', 'S', 'U', 'M'};

    if (!out_file || !spec) return 0;
    memset(out_file, 0, sizeof(*out_file));
    memset(&root, 0, sizeof(root));
    memset(&payload, 0, sizeof(payload));
    memset(&cb, 0, sizeof(cb));
    memset(&irb, 0, sizeof(irb));

    if (!buf_put_tlv_u32(&root, T_ROOT_VER, 1ul)) goto fail;
    if (!buf_put_tlv_str(&root, T_PRODUCT_ID, spec->product_id)) goto fail;
    if (!buf_put_tlv_str(&root, T_PRODUCT_VER, spec->product_version)) goto fail;
    if (!buf_put_tlv_str(&root, T_BUILD_CHANNEL, spec->build_channel ? spec->build_channel : "stable")) goto fail;

    for (i = 0u; i < spec->platform_target_count; ++i) {
        if (!buf_put_tlv_str(&root, T_PLATFORM_TARGET, spec->platform_targets[i])) goto fail;
    }
    for (i = 0u; i < spec->install_root_count; ++i) {
        if (!build_install_root_container(&irb, &spec->install_roots[i])) goto fail;
        if (!buf_put_tlv(&root, T_INSTALL_ROOT, irb.data, irb.len)) {
            buf_free(&irb);
            goto fail;
        }
        buf_free(&irb);
    }
    for (i = 0u; i < spec->component_count; ++i) {
        if (!build_component_container(&cb, &spec->components[i])) goto fail;
        if (!buf_put_tlv(&root, T_COMPONENT, cb.data, cb.len)) {
            buf_free(&cb);
            goto fail;
        }
        buf_free(&cb);
    }

    if (!buf_put_tlv(&payload, T_MANIFEST_ROOT, root.data, root.len)) goto fail;
    if (!wrap_file(out_file, magic, (unsigned short)DSU_MANIFEST_FORMAT_VERSION, &payload)) goto fail;
    buf_free(&root);
    buf_free(&payload);
    return 1;

fail:
    buf_free(&cb);
    buf_free(&irb);
    buf_free(&root);
    buf_free(&payload);
    buf_free(out_file);
    return 0;
}

/* State TLVs (core/src/state/dsu_state.c) */
#define S_T_ROOT 0x0001u
#define S_T_ROOT_VER 0x0002u
#define S_T_PRODUCT_ID 0x0010u
#define S_T_PRODUCT_VER 0x0011u
#define S_T_PLATFORM 0x0020u
#define S_T_SCOPE 0x0021u
#define S_T_INSTALL_ROOT 0x0022u
#define S_T_COMPONENT 0x0040u
#define S_T_C_VER 0x0041u
#define S_T_C_ID 0x0042u
#define S_T_C_VERSTR 0x0043u

typedef struct state_component_spec_t {
    const char *id;
    const char *version;
} state_component_spec_t;

typedef struct state_spec_t {
    const char *product_id;
    const char *product_version;
    const char *platform;
    dsu_u8 scope;
    const char *install_root;
    const state_component_spec_t *components;
    dsu_u32 component_count;
} state_spec_t;

static int is_abs_path_like(const char *p) {
    if (!p) return 0;
    if (p[0] == '/' || p[0] == '\\') return 1;
    if ((p[0] == '/' && p[1] == '/') || (p[0] == '\\' && p[1] == '\\')) return 1;
    if (((p[0] >= 'A' && p[0] <= 'Z') || (p[0] >= 'a' && p[0] <= 'z')) && p[1] == ':' && (p[2] == '/' || p[2] == '\\')) return 1;
    return 0;
}

static int build_state_component_container(buf_t *out_comp, const state_component_spec_t *c) {
    if (!out_comp || !c) return 0;
    memset(out_comp, 0, sizeof(*out_comp));
    if (!buf_put_tlv_u32(out_comp, S_T_C_VER, 1ul)) return 0;
    if (!buf_put_tlv_str(out_comp, S_T_C_ID, c->id)) return 0;
    if (!buf_put_tlv_str(out_comp, S_T_C_VERSTR, c->version ? c->version : "")) return 0;
    return 1;
}

static int build_state_file(buf_t *out_file, const state_spec_t *spec) {
    dsu_u32 i;
    dsu_status_t st;
    const char *install_root_in;
    char install_root_abs[1024];
    buf_t root;
    buf_t payload;
    buf_t cb;
    static const unsigned char magic[4] = {'D', 'S', 'U', 'S'};

    if (!out_file || !spec) return 0;
    memset(out_file, 0, sizeof(*out_file));
    memset(&root, 0, sizeof(root));
    memset(&payload, 0, sizeof(payload));
    memset(&cb, 0, sizeof(cb));

    if (!buf_put_tlv_u32(&root, S_T_ROOT_VER, 1ul)) goto fail;
    if (!buf_put_tlv_str(&root, S_T_PRODUCT_ID, spec->product_id)) goto fail;
    if (!buf_put_tlv_str(&root, S_T_PRODUCT_VER, spec->product_version)) goto fail;
    if (!buf_put_tlv_str(&root, S_T_PLATFORM, spec->platform)) goto fail;
    if (!buf_put_tlv_u8(&root, S_T_SCOPE, (unsigned char)spec->scope)) goto fail;
    install_root_in = spec->install_root ? spec->install_root : "";
    if (install_root_in[0] == '\0') goto fail;
    if (is_abs_path_like(install_root_in)) {
        st = dsu_fs_path_canonicalize(install_root_in, install_root_abs, (dsu_u32)sizeof(install_root_abs));
        if (st != DSU_STATUS_SUCCESS) goto fail;
    } else {
        char cwd[1024];
        st = dsu_platform_get_cwd(cwd, (dsu_u32)sizeof(cwd));
        if (st != DSU_STATUS_SUCCESS) goto fail;
        st = dsu_fs_path_join(cwd, install_root_in, install_root_abs, (dsu_u32)sizeof(install_root_abs));
        if (st != DSU_STATUS_SUCCESS) goto fail;
    }
    if (!buf_put_tlv_str(&root, S_T_INSTALL_ROOT, install_root_abs)) goto fail;

    for (i = 0u; i < spec->component_count; ++i) {
        if (!build_state_component_container(&cb, &spec->components[i])) goto fail;
        if (!buf_put_tlv(&root, S_T_COMPONENT, cb.data, cb.len)) {
            buf_free(&cb);
            goto fail;
        }
        buf_free(&cb);
    }

    if (!buf_put_tlv(&payload, S_T_ROOT, root.data, root.len)) goto fail;
    if (!wrap_file(out_file, magic, 1u, &payload)) goto fail;

    buf_free(&root);
    buf_free(&payload);
    return 1;

fail:
    buf_free(&cb);
    buf_free(&root);
    buf_free(&payload);
    buf_free(out_file);
    return 0;
}

static int serialize_resolved(const dsu_resolve_result_t *r, buf_t *out) {
    dsu_u32 i;
    dsu_u32 n;
    const char *s;
    const char *v;
    if (!r || !out) return 0;
    memset(out, 0, sizeof(*out));

    if (!buf_put_cstr(out, "platform=")) return 0;
    if (!buf_put_cstr(out, dsu_resolve_result_platform(r))) return 0;
    if (!buf_put_cstr(out, "\n")) return 0;

    if (!buf_put_cstr(out, "scope=")) return 0;
    if (!buf_put_u32_dec(out, (dsu_u32)dsu_resolve_result_scope(r))) return 0;
    if (!buf_put_cstr(out, "\n")) return 0;

    if (!buf_put_cstr(out, "operation=")) return 0;
    if (!buf_put_u32_dec(out, (dsu_u32)dsu_resolve_result_operation(r))) return 0;
    if (!buf_put_cstr(out, "\n")) return 0;

    if (!buf_put_cstr(out, "manifest_digest64=")) return 0;
    if (!buf_put_u64_dec(out, dsu_resolve_result_manifest_digest64(r))) return 0;
    if (!buf_put_cstr(out, "\n")) return 0;

    if (!buf_put_cstr(out, "resolved_digest64=")) return 0;
    if (!buf_put_u64_dec(out, dsu_resolve_result_resolved_digest64(r))) return 0;
    if (!buf_put_cstr(out, "\n")) return 0;

    if (!buf_put_cstr(out, "components:\n")) return 0;
    n = dsu_resolve_result_component_count(r);
    for (i = 0u; i < n; ++i) {
        s = dsu_resolve_result_component_id(r, i);
        v = dsu_resolve_result_component_version(r, i);
        if (!s) s = "";
        if (!v) v = "";
        if (!buf_put_cstr(out, s)) return 0;
        if (!buf_put_cstr(out, "@")) return 0;
        if (!buf_put_cstr(out, v)) return 0;
        if (!buf_put_cstr(out, "|")) return 0;
        if (!buf_put_u32_dec(out, (dsu_u32)dsu_resolve_result_component_source(r, i))) return 0;
        if (!buf_put_cstr(out, "|")) return 0;
        if (!buf_put_u32_dec(out, (dsu_u32)dsu_resolve_result_component_action(r, i))) return 0;
        if (!buf_put_cstr(out, "\n")) return 0;
    }

    if (!buf_put_cstr(out, "log:\n")) return 0;
    n = dsu_resolve_result_log_count(r);
    for (i = 0u; i < n; ++i) {
        if (!buf_put_u32_dec(out, (dsu_u32)dsu_resolve_result_log_code(r, i))) return 0;
        if (!buf_put_cstr(out, "|")) return 0;
        s = dsu_resolve_result_log_a(r, i);
        v = dsu_resolve_result_log_b(r, i);
        if (!s) s = "";
        if (!v) v = "";
        if (!buf_put_cstr(out, s)) return 0;
        if (!buf_put_cstr(out, "|")) return 0;
        if (!buf_put_cstr(out, v)) return 0;
        if (!buf_put_cstr(out, "\n")) return 0;
    }
    return 1;
}

static int test_default_only(void) {
    const char *mf_path = "dsu_test_resolve_default.dsumanifest";
    buf_t mf_bytes;
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *m = NULL;
    dsu_resolve_result_t *r = NULL;
    dsu_status_t st;
    int ok = 1;

    const char *const platform_targets[] = {"any-any"};
    install_root_spec_t ir[1];
    component_spec_t comps[2];
    manifest_spec_t spec;

    memset(&mf_bytes, 0, sizeof(mf_bytes));
    memset(&ir, 0, sizeof(ir));
    memset(&comps, 0, sizeof(comps));
    memset(&spec, 0, sizeof(spec));

    ir[0].scope = (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    ir[0].platform = "any-any";
    ir[0].path = "install/dominium";

    comps[0].id = "core";
    comps[0].version = NULL;
    comps[0].kind = (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_RUNTIME;
    comps[0].flags = (dsu_u32)DSU_MANIFEST_COMPONENT_FLAG_DEFAULT_SELECTED;
    comps[0].deps = NULL;
    comps[0].dep_count = 0u;
    comps[0].conflicts = NULL;
    comps[0].conflict_count = 0u;

    comps[1].id = "tools";
    comps[1].version = NULL;
    comps[1].kind = (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_TOOLS;
    comps[1].flags = (dsu_u32)DSU_MANIFEST_COMPONENT_FLAG_DEFAULT_SELECTED;
    comps[1].deps = NULL;
    comps[1].dep_count = 0u;
    comps[1].conflicts = NULL;
    comps[1].conflict_count = 0u;

    spec.product_id = "dominium";
    spec.product_version = "1.0.0";
    spec.build_channel = "stable";
    spec.platform_targets = platform_targets;
    spec.platform_target_count = 1u;
    spec.install_roots = ir;
    spec.install_root_count = 1u;
    spec.components = comps;
    spec.component_count = 2u;

    ok &= expect(build_manifest_file(&mf_bytes, &spec), "build manifest bytes (default-only)");
    ok &= expect(write_bytes_file(mf_path, mf_bytes.data, mf_bytes.len), "write manifest (default-only)");
    buf_free(&mf_bytes);
    if (!ok) goto done;

    ctx = create_ctx_deterministic();
    ok &= expect(ctx != NULL, "ctx create (default-only)");
    if (!ok) goto done;

    st = dsu_manifest_load_file(ctx, mf_path, &m);
    ok &= expect(st == DSU_STATUS_SUCCESS && m != NULL, "manifest load (default-only)");
    if (!ok) goto done;

    {
        dsu_resolve_request_t req;
        dsu_resolve_request_init(&req);
        req.operation = DSU_RESOLVE_OPERATION_INSTALL;
        req.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        st = dsu_resolve_components(ctx, m, NULL, &req, &r);
    }
    ok &= expect(st == DSU_STATUS_SUCCESS && r != NULL, "resolve (default-only)");
    ok &= expect(dsu_resolve_result_component_count(r) == 2u, "component_count==2 (default-only)");
    ok &= expect(strcmp(dsu_resolve_result_component_id(r, 0u), "core") == 0, "component[0]==core (default-only)");
    ok &= expect(strcmp(dsu_resolve_result_component_id(r, 1u), "tools") == 0, "component[1]==tools (default-only)");
    ok &= expect(dsu_resolve_result_component_source(r, 0u) == DSU_RESOLVE_SOURCE_DEFAULT, "source core default");
    ok &= expect(dsu_resolve_result_component_source(r, 1u) == DSU_RESOLVE_SOURCE_DEFAULT, "source tools default");
    ok &= expect(dsu_resolve_result_component_action(r, 0u) == DSU_RESOLVE_COMPONENT_ACTION_INSTALL, "action core install");
    ok &= expect(dsu_resolve_result_component_action(r, 1u) == DSU_RESOLVE_COMPONENT_ACTION_INSTALL, "action tools install");
    ok &= expect(strcmp(dsu_resolve_result_component_version(r, 0u), "1.0.0") == 0, "core version inherits product");

done:
    if (r) dsu_resolve_result_destroy(ctx, r);
    if (m) dsu_manifest_destroy(ctx, m);
    if (ctx) dsu_ctx_destroy(ctx);
    remove(mf_path);
    return ok;
}

static int test_explicit_selection_and_exclude(void) {
    const char *mf_path = "dsu_test_resolve_explicit.dsumanifest";
    buf_t mf_bytes;
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *m = NULL;
    dsu_resolve_result_t *r = NULL;
    dsu_status_t st;
    int ok = 1;

    const char *const platform_targets[] = {"any-any"};
    install_root_spec_t ir[1];
    component_spec_t comps[2];
    manifest_spec_t spec;

    memset(&mf_bytes, 0, sizeof(mf_bytes));
    memset(&ir, 0, sizeof(ir));
    memset(&comps, 0, sizeof(comps));
    memset(&spec, 0, sizeof(spec));

    ir[0].scope = (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    ir[0].platform = "any-any";
    ir[0].path = "install/dominium";

    comps[0].id = "core";
    comps[0].version = NULL;
    comps[0].kind = (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_RUNTIME;
    comps[0].flags = (dsu_u32)DSU_MANIFEST_COMPONENT_FLAG_DEFAULT_SELECTED;

    comps[1].id = "extras";
    comps[1].version = NULL;
    comps[1].kind = (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_OTHER;
    comps[1].flags = 0u;

    spec.product_id = "dominium";
    spec.product_version = "1.0.0";
    spec.build_channel = "stable";
    spec.platform_targets = platform_targets;
    spec.platform_target_count = 1u;
    spec.install_roots = ir;
    spec.install_root_count = 1u;
    spec.components = comps;
    spec.component_count = 2u;

    ok &= expect(build_manifest_file(&mf_bytes, &spec), "build manifest bytes (explicit)");
    ok &= expect(write_bytes_file(mf_path, mf_bytes.data, mf_bytes.len), "write manifest (explicit)");
    buf_free(&mf_bytes);
    if (!ok) goto done;

    ctx = create_ctx_deterministic();
    ok &= expect(ctx != NULL, "ctx create (explicit)");
    if (!ok) goto done;

    st = dsu_manifest_load_file(ctx, mf_path, &m);
    ok &= expect(st == DSU_STATUS_SUCCESS && m != NULL, "manifest load (explicit)");
    if (!ok) goto done;

    {
        const char *const requested[] = {"extras"};
        const char *const excluded[] = {"core"};
        dsu_resolve_request_t req;
        dsu_resolve_request_init(&req);
        req.operation = DSU_RESOLVE_OPERATION_INSTALL;
        req.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        req.requested_components = requested;
        req.requested_component_count = 1u;
        req.excluded_components = excluded;
        req.excluded_component_count = 1u;
        st = dsu_resolve_components(ctx, m, NULL, &req, &r);
    }
    ok &= expect(st == DSU_STATUS_SUCCESS && r != NULL, "resolve (explicit)");
    ok &= expect(dsu_resolve_result_component_count(r) == 1u, "component_count==1 (explicit)");
    ok &= expect(strcmp(dsu_resolve_result_component_id(r, 0u), "extras") == 0, "component[0]==extras (explicit)");
    ok &= expect(dsu_resolve_result_component_source(r, 0u) == DSU_RESOLVE_SOURCE_USER, "source extras user");

done:
    if (r) dsu_resolve_result_destroy(ctx, r);
    if (m) dsu_manifest_destroy(ctx, m);
    if (ctx) dsu_ctx_destroy(ctx);
    remove(mf_path);
    return ok;
}

static int test_dependency_closure(void) {
    const char *mf_path = "dsu_test_resolve_deps.dsumanifest";
    buf_t mf_bytes;
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *m = NULL;
    dsu_resolve_result_t *r = NULL;
    dsu_status_t st;
    int ok = 1;

    const char *const platform_targets[] = {"any-any"};
    install_root_spec_t ir[1];
    dep_spec_t deps_a[1];
    component_spec_t comps[2];
    manifest_spec_t spec;

    memset(&mf_bytes, 0, sizeof(mf_bytes));
    memset(&ir, 0, sizeof(ir));
    memset(&deps_a, 0, sizeof(deps_a));
    memset(&comps, 0, sizeof(comps));
    memset(&spec, 0, sizeof(spec));

    ir[0].scope = (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    ir[0].platform = "any-any";
    ir[0].path = "install/dominium";

    deps_a[0].id = "b";
    deps_a[0].constraint_kind = (dsu_u8)DSU_MANIFEST_VERSION_CONSTRAINT_ANY;
    deps_a[0].constraint_version = NULL;

    comps[0].id = "a";
    comps[0].kind = (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_OTHER;
    comps[0].flags = 0u;
    comps[0].deps = deps_a;
    comps[0].dep_count = 1u;

    comps[1].id = "b";
    comps[1].kind = (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_OTHER;
    comps[1].flags = 0u;

    spec.product_id = "dominium";
    spec.product_version = "1.0.0";
    spec.build_channel = "stable";
    spec.platform_targets = platform_targets;
    spec.platform_target_count = 1u;
    spec.install_roots = ir;
    spec.install_root_count = 1u;
    spec.components = comps;
    spec.component_count = 2u;

    ok &= expect(build_manifest_file(&mf_bytes, &spec), "build manifest bytes (deps)");
    ok &= expect(write_bytes_file(mf_path, mf_bytes.data, mf_bytes.len), "write manifest (deps)");
    buf_free(&mf_bytes);
    if (!ok) goto done;

    ctx = create_ctx_deterministic();
    ok &= expect(ctx != NULL, "ctx create (deps)");
    if (!ok) goto done;

    st = dsu_manifest_load_file(ctx, mf_path, &m);
    ok &= expect(st == DSU_STATUS_SUCCESS && m != NULL, "manifest load (deps)");
    if (!ok) goto done;

    {
        const char *const requested[] = {"a"};
        dsu_resolve_request_t req;
        dsu_resolve_request_init(&req);
        req.operation = DSU_RESOLVE_OPERATION_INSTALL;
        req.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        req.requested_components = requested;
        req.requested_component_count = 1u;
        st = dsu_resolve_components(ctx, m, NULL, &req, &r);
    }
    ok &= expect(st == DSU_STATUS_SUCCESS && r != NULL, "resolve (deps)");
    ok &= expect(dsu_resolve_result_component_count(r) == 2u, "component_count==2 (deps)");
    ok &= expect(strcmp(dsu_resolve_result_component_id(r, 0u), "a") == 0, "component[0]==a (deps)");
    ok &= expect(strcmp(dsu_resolve_result_component_id(r, 1u), "b") == 0, "component[1]==b (deps)");
    ok &= expect(dsu_resolve_result_component_source(r, 0u) == DSU_RESOLVE_SOURCE_USER, "source a user");
    ok &= expect(dsu_resolve_result_component_source(r, 1u) == DSU_RESOLVE_SOURCE_DEPENDENCY, "source b dependency");

done:
    if (r) dsu_resolve_result_destroy(ctx, r);
    if (m) dsu_manifest_destroy(ctx, m);
    if (ctx) dsu_ctx_destroy(ctx);
    remove(mf_path);
    return ok;
}

static int test_conflict_detection(void) {
    const char *mf_path = "dsu_test_resolve_conflict.dsumanifest";
    buf_t mf_bytes;
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *m = NULL;
    dsu_resolve_result_t *r = NULL;
    dsu_status_t st;
    int ok = 1;

    const char *const platform_targets[] = {"any-any"};
    install_root_spec_t ir[1];
    const char *const conflicts_a[] = {"b"};
    component_spec_t comps[2];
    manifest_spec_t spec;

    memset(&mf_bytes, 0, sizeof(mf_bytes));
    memset(&ir, 0, sizeof(ir));
    memset(&comps, 0, sizeof(comps));
    memset(&spec, 0, sizeof(spec));

    ir[0].scope = (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    ir[0].platform = "any-any";
    ir[0].path = "install/dominium";

    comps[0].id = "a";
    comps[0].kind = (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_OTHER;
    comps[0].flags = 0u;
    comps[0].conflicts = conflicts_a;
    comps[0].conflict_count = 1u;

    comps[1].id = "b";
    comps[1].kind = (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_OTHER;
    comps[1].flags = 0u;

    spec.product_id = "dominium";
    spec.product_version = "1.0.0";
    spec.build_channel = "stable";
    spec.platform_targets = platform_targets;
    spec.platform_target_count = 1u;
    spec.install_roots = ir;
    spec.install_root_count = 1u;
    spec.components = comps;
    spec.component_count = 2u;

    ok &= expect(build_manifest_file(&mf_bytes, &spec), "build manifest bytes (conflict)");
    ok &= expect(write_bytes_file(mf_path, mf_bytes.data, mf_bytes.len), "write manifest (conflict)");
    buf_free(&mf_bytes);
    if (!ok) goto done;

    ctx = create_ctx_deterministic();
    ok &= expect(ctx != NULL, "ctx create (conflict)");
    if (!ok) goto done;

    st = dsu_manifest_load_file(ctx, mf_path, &m);
    ok &= expect(st == DSU_STATUS_SUCCESS && m != NULL, "manifest load (conflict)");
    if (!ok) goto done;

    {
        const char *const requested[] = {"a", "b"};
        dsu_resolve_request_t req;
        dsu_resolve_request_init(&req);
        req.operation = DSU_RESOLVE_OPERATION_INSTALL;
        req.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        req.requested_components = requested;
        req.requested_component_count = 2u;
        st = dsu_resolve_components(ctx, m, NULL, &req, &r);
    }
    ok &= expect(st == DSU_STATUS_EXPLICIT_CONFLICT, "explicit conflict detected");

done:
    if (r) dsu_resolve_result_destroy(ctx, r);
    if (m) dsu_manifest_destroy(ctx, m);
    if (ctx) dsu_ctx_destroy(ctx);
    remove(mf_path);
    return ok;
}

static int test_platform_ambiguity_failure(void) {
    const char *mf_path = "dsu_test_resolve_platform_ambig.dsumanifest";
    buf_t mf_bytes;
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *m = NULL;
    dsu_resolve_result_t *r = NULL;
    dsu_status_t st;
    int ok = 1;

    const char *const platform_targets[] = {"any-any", "linux-x64"};
    install_root_spec_t ir[2];
    component_spec_t comps[1];
    manifest_spec_t spec;

    memset(&mf_bytes, 0, sizeof(mf_bytes));
    memset(&ir, 0, sizeof(ir));
    memset(&comps, 0, sizeof(comps));
    memset(&spec, 0, sizeof(spec));

    ir[0].scope = (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    ir[0].platform = "any-any";
    ir[0].path = "install/dominium";
    ir[1].scope = (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    ir[1].platform = "linux-x64";
    ir[1].path = "install/dominium";

    comps[0].id = "core";
    comps[0].kind = (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_OTHER;
    comps[0].flags = (dsu_u32)DSU_MANIFEST_COMPONENT_FLAG_DEFAULT_SELECTED;

    spec.product_id = "dominium";
    spec.product_version = "1.0.0";
    spec.build_channel = "stable";
    spec.platform_targets = platform_targets;
    spec.platform_target_count = 2u;
    spec.install_roots = ir;
    spec.install_root_count = 2u;
    spec.components = comps;
    spec.component_count = 1u;

    ok &= expect(build_manifest_file(&mf_bytes, &spec), "build manifest bytes (platform ambiguity)");
    ok &= expect(write_bytes_file(mf_path, mf_bytes.data, mf_bytes.len), "write manifest (platform ambiguity)");
    buf_free(&mf_bytes);
    if (!ok) goto done;

    ctx = create_ctx_deterministic();
    ok &= expect(ctx != NULL, "ctx create (platform ambiguity)");
    if (!ok) goto done;

    st = dsu_manifest_load_file(ctx, mf_path, &m);
    ok &= expect(st == DSU_STATUS_SUCCESS && m != NULL, "manifest load (platform ambiguity)");
    if (!ok) goto done;

    {
        dsu_resolve_request_t req;
        dsu_resolve_request_init(&req);
        req.operation = DSU_RESOLVE_OPERATION_INSTALL;
        req.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        req.target_platform = NULL;
        st = dsu_resolve_components(ctx, m, NULL, &req, &r);
    }
    ok &= expect(st == DSU_STATUS_INVALID_REQUEST, "ambiguous platform rejected");

done:
    if (r) dsu_resolve_result_destroy(ctx, r);
    if (m) dsu_manifest_destroy(ctx, m);
    if (ctx) dsu_ctx_destroy(ctx);
    remove(mf_path);
    return ok;
}

static int test_platform_missing_install_root_failure(void) {
    const char *mf_path = "dsu_test_resolve_platform_root.dsumanifest";
    buf_t mf_bytes;
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *m = NULL;
    dsu_resolve_result_t *r = NULL;
    dsu_status_t st;
    int ok = 1;

    const char *const platform_targets[] = {"any-any"};
    install_root_spec_t ir[1];
    component_spec_t comps[1];
    manifest_spec_t spec;

    memset(&mf_bytes, 0, sizeof(mf_bytes));
    memset(&ir, 0, sizeof(ir));
    memset(&comps, 0, sizeof(comps));
    memset(&spec, 0, sizeof(spec));

    ir[0].scope = (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    ir[0].platform = "any-any";
    ir[0].path = "install/dominium";

    comps[0].id = "core";
    comps[0].kind = (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_OTHER;
    comps[0].flags = (dsu_u32)DSU_MANIFEST_COMPONENT_FLAG_DEFAULT_SELECTED;

    spec.product_id = "dominium";
    spec.product_version = "1.0.0";
    spec.build_channel = "stable";
    spec.platform_targets = platform_targets;
    spec.platform_target_count = 1u;
    spec.install_roots = ir;
    spec.install_root_count = 1u;
    spec.components = comps;
    spec.component_count = 1u;

    ok &= expect(build_manifest_file(&mf_bytes, &spec), "build manifest bytes (missing install root)");
    ok &= expect(write_bytes_file(mf_path, mf_bytes.data, mf_bytes.len), "write manifest (missing install root)");
    buf_free(&mf_bytes);
    if (!ok) goto done;

    ctx = create_ctx_deterministic();
    ok &= expect(ctx != NULL, "ctx create (missing install root)");
    if (!ok) goto done;

    st = dsu_manifest_load_file(ctx, mf_path, &m);
    ok &= expect(st == DSU_STATUS_SUCCESS && m != NULL, "manifest load (missing install root)");
    if (!ok) goto done;

    {
        dsu_resolve_request_t req;
        dsu_resolve_request_init(&req);
        req.operation = DSU_RESOLVE_OPERATION_INSTALL;
        req.scope = DSU_MANIFEST_INSTALL_SCOPE_USER;
        st = dsu_resolve_components(ctx, m, NULL, &req, &r);
    }
    ok &= expect(st == DSU_STATUS_PLATFORM_INCOMPATIBLE, "missing install root rejected");

done:
    if (r) dsu_resolve_result_destroy(ctx, r);
    if (m) dsu_manifest_destroy(ctx, m);
    if (ctx) dsu_ctx_destroy(ctx);
    remove(mf_path);
    return ok;
}

static int test_upgrade_monotonicity(void) {
    const char *mf_path = "dsu_test_resolve_upgrade.dsumanifest";
    const char *st_path = "dsu_test_resolve_upgrade.dsustate";
    buf_t mf_bytes;
    buf_t st_bytes;
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *m = NULL;
    dsu_state_t *s = NULL;
    dsu_resolve_result_t *r = NULL;
    dsu_status_t st;
    int ok = 1;

    const char *const platform_targets[] = {"any-any"};
    install_root_spec_t ir[1];
    component_spec_t comps[1];
    manifest_spec_t mspec;
    state_component_spec_t sc[1];
    state_spec_t sspec;

    memset(&mf_bytes, 0, sizeof(mf_bytes));
    memset(&st_bytes, 0, sizeof(st_bytes));
    memset(&ir, 0, sizeof(ir));
    memset(&comps, 0, sizeof(comps));
    memset(&mspec, 0, sizeof(mspec));
    memset(&sc, 0, sizeof(sc));
    memset(&sspec, 0, sizeof(sspec));

    ir[0].scope = (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    ir[0].platform = "any-any";
    ir[0].path = "install/dominium";

    comps[0].id = "core";
    comps[0].version = "2.0.0";
    comps[0].kind = (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_OTHER;
    comps[0].flags = 0u;

    mspec.product_id = "dominium";
    mspec.product_version = "2.0.0";
    mspec.build_channel = "stable";
    mspec.platform_targets = platform_targets;
    mspec.platform_target_count = 1u;
    mspec.install_roots = ir;
    mspec.install_root_count = 1u;
    mspec.components = comps;
    mspec.component_count = 1u;

    sc[0].id = "core";
    sc[0].version = "1.0.0";
    sspec.product_id = "dominium";
    sspec.product_version = "1.0.0";
    sspec.platform = "any-any";
    sspec.scope = (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    sspec.install_root = "install/dominium";
    sspec.components = sc;
    sspec.component_count = 1u;

    ok &= expect(build_manifest_file(&mf_bytes, &mspec), "build manifest bytes (upgrade)");
    ok &= expect(write_bytes_file(mf_path, mf_bytes.data, mf_bytes.len), "write manifest (upgrade)");
    buf_free(&mf_bytes);
    ok &= expect(build_state_file(&st_bytes, &sspec), "build state bytes (upgrade)");
    ok &= expect(write_bytes_file(st_path, st_bytes.data, st_bytes.len), "write state (upgrade)");
    buf_free(&st_bytes);
    if (!ok) goto done;

    ctx = create_ctx_deterministic();
    ok &= expect(ctx != NULL, "ctx create (upgrade)");
    if (!ok) goto done;

    st = dsu_manifest_load_file(ctx, mf_path, &m);
    ok &= expect(st == DSU_STATUS_SUCCESS && m != NULL, "manifest load (upgrade)");
    if (!ok) goto done;
    st = dsu_state_load_file(ctx, st_path, &s);
    ok &= expect(st == DSU_STATUS_SUCCESS && s != NULL, "state load (upgrade)");
    if (!ok) goto done;

    {
        const char *const requested[] = {"core"};
        dsu_resolve_request_t req;
        dsu_resolve_request_init(&req);
        req.operation = DSU_RESOLVE_OPERATION_UPGRADE;
        req.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        req.requested_components = requested;
        req.requested_component_count = 1u;
        st = dsu_resolve_components(ctx, m, s, &req, &r);
    }
    ok &= expect(st == DSU_STATUS_SUCCESS && r != NULL, "resolve upgrade");
    ok &= expect(dsu_resolve_result_component_count(r) == 1u, "upgrade component_count==1");
    ok &= expect(dsu_resolve_result_component_action(r, 0u) == DSU_RESOLVE_COMPONENT_ACTION_UPGRADE, "upgrade action==UPGRADE");

done:
    if (r) dsu_resolve_result_destroy(ctx, r);
    if (s) dsu_state_destroy(ctx, s);
    if (m) dsu_manifest_destroy(ctx, m);
    if (ctx) dsu_ctx_destroy(ctx);
    remove(mf_path);
    remove(st_path);
    return ok;
}

static int test_illegal_downgrade(void) {
    const char *mf_path = "dsu_test_resolve_downgrade.dsumanifest";
    const char *st_path = "dsu_test_resolve_downgrade.dsustate";
    buf_t mf_bytes;
    buf_t st_bytes;
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *m = NULL;
    dsu_state_t *s = NULL;
    dsu_resolve_result_t *r = NULL;
    dsu_status_t st;
    int ok = 1;

    const char *const platform_targets[] = {"any-any"};
    install_root_spec_t ir[1];
    component_spec_t comps[1];
    manifest_spec_t mspec;
    state_component_spec_t sc[1];
    state_spec_t sspec;

    memset(&mf_bytes, 0, sizeof(mf_bytes));
    memset(&st_bytes, 0, sizeof(st_bytes));
    memset(&ir, 0, sizeof(ir));
    memset(&comps, 0, sizeof(comps));
    memset(&mspec, 0, sizeof(mspec));
    memset(&sc, 0, sizeof(sc));
    memset(&sspec, 0, sizeof(sspec));

    ir[0].scope = (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    ir[0].platform = "any-any";
    ir[0].path = "install/dominium";

    comps[0].id = "core";
    comps[0].version = "1.0.0";
    comps[0].kind = (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_OTHER;
    comps[0].flags = 0u;

    mspec.product_id = "dominium";
    mspec.product_version = "1.0.0";
    mspec.build_channel = "stable";
    mspec.platform_targets = platform_targets;
    mspec.platform_target_count = 1u;
    mspec.install_roots = ir;
    mspec.install_root_count = 1u;
    mspec.components = comps;
    mspec.component_count = 1u;

    sc[0].id = "core";
    sc[0].version = "2.0.0";
    sspec.product_id = "dominium";
    sspec.product_version = "2.0.0";
    sspec.platform = "any-any";
    sspec.scope = (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    sspec.install_root = "install/dominium";
    sspec.components = sc;
    sspec.component_count = 1u;

    ok &= expect(build_manifest_file(&mf_bytes, &mspec), "build manifest bytes (downgrade)");
    ok &= expect(write_bytes_file(mf_path, mf_bytes.data, mf_bytes.len), "write manifest (downgrade)");
    buf_free(&mf_bytes);
    ok &= expect(build_state_file(&st_bytes, &sspec), "build state bytes (downgrade)");
    ok &= expect(write_bytes_file(st_path, st_bytes.data, st_bytes.len), "write state (downgrade)");
    buf_free(&st_bytes);
    if (!ok) goto done;

    ctx = create_ctx_deterministic();
    ok &= expect(ctx != NULL, "ctx create (downgrade)");
    if (!ok) goto done;

    st = dsu_manifest_load_file(ctx, mf_path, &m);
    ok &= expect(st == DSU_STATUS_SUCCESS && m != NULL, "manifest load (downgrade)");
    if (!ok) goto done;
    st = dsu_state_load_file(ctx, st_path, &s);
    ok &= expect(st == DSU_STATUS_SUCCESS && s != NULL, "state load (downgrade)");
    if (!ok) goto done;

    {
        const char *const requested[] = {"core"};
        dsu_resolve_request_t req;
        dsu_resolve_request_init(&req);
        req.operation = DSU_RESOLVE_OPERATION_UPGRADE;
        req.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        req.requested_components = requested;
        req.requested_component_count = 1u;
        st = dsu_resolve_components(ctx, m, s, &req, &r);
    }
    ok &= expect(st == DSU_STATUS_ILLEGAL_DOWNGRADE, "illegal downgrade rejected");

done:
    if (r) dsu_resolve_result_destroy(ctx, r);
    if (s) dsu_state_destroy(ctx, s);
    if (m) dsu_manifest_destroy(ctx, m);
    if (ctx) dsu_ctx_destroy(ctx);
    remove(mf_path);
    remove(st_path);
    return ok;
}

static int test_deterministic_serialization(void) {
    const char *mf_path = "dsu_test_resolve_det.dsumanifest";
    buf_t mf_bytes;
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *m = NULL;
    dsu_resolve_result_t *r1 = NULL;
    dsu_resolve_result_t *r2 = NULL;
    dsu_status_t st;
    buf_t s1;
    buf_t s2;
    int ok = 1;

    const char *const platform_targets[] = {"any-any"};
    install_root_spec_t ir[1];
    component_spec_t comps[2];
    manifest_spec_t spec;

    memset(&mf_bytes, 0, sizeof(mf_bytes));
    memset(&s1, 0, sizeof(s1));
    memset(&s2, 0, sizeof(s2));
    memset(&ir, 0, sizeof(ir));
    memset(&comps, 0, sizeof(comps));
    memset(&spec, 0, sizeof(spec));

    ir[0].scope = (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    ir[0].platform = "any-any";
    ir[0].path = "install/dominium";

    comps[0].id = "core";
    comps[0].kind = (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_OTHER;
    comps[0].flags = 0u;
    comps[1].id = "data";
    comps[1].kind = (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_OTHER;
    comps[1].flags = 0u;

    spec.product_id = "dominium";
    spec.product_version = "1.0.0";
    spec.build_channel = "stable";
    spec.platform_targets = platform_targets;
    spec.platform_target_count = 1u;
    spec.install_roots = ir;
    spec.install_root_count = 1u;
    spec.components = comps;
    spec.component_count = 2u;

    ok &= expect(build_manifest_file(&mf_bytes, &spec), "build manifest bytes (det)");
    ok &= expect(write_bytes_file(mf_path, mf_bytes.data, mf_bytes.len), "write manifest (det)");
    buf_free(&mf_bytes);
    if (!ok) goto done;

    ctx = create_ctx_deterministic();
    ok &= expect(ctx != NULL, "ctx create (det)");
    if (!ok) goto done;

    st = dsu_manifest_load_file(ctx, mf_path, &m);
    ok &= expect(st == DSU_STATUS_SUCCESS && m != NULL, "manifest load (det)");
    if (!ok) goto done;

    {
        const char *const requested[] = {"data", "core"};
        dsu_resolve_request_t req;
        dsu_resolve_request_init(&req);
        req.operation = DSU_RESOLVE_OPERATION_INSTALL;
        req.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        req.requested_components = requested;
        req.requested_component_count = 2u;
        st = dsu_resolve_components(ctx, m, NULL, &req, &r1);
    }
    ok &= expect(st == DSU_STATUS_SUCCESS && r1 != NULL, "resolve A (det)");
    if (!ok) goto done;
    ok &= expect(serialize_resolved(r1, &s1), "serialize A (det)");
    if (!ok) goto done;

    {
        const char *const requested[] = {"data", "core"};
        dsu_resolve_request_t req;
        dsu_resolve_request_init(&req);
        req.operation = DSU_RESOLVE_OPERATION_INSTALL;
        req.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        req.requested_components = requested;
        req.requested_component_count = 2u;
        st = dsu_resolve_components(ctx, m, NULL, &req, &r2);
    }
    ok &= expect(st == DSU_STATUS_SUCCESS && r2 != NULL, "resolve B (det)");
    if (!ok) goto done;
    ok &= expect(serialize_resolved(r2, &s2), "serialize B (det)");
    if (!ok) goto done;

    ok &= expect(bytes_equal(s1.data, s1.len, s2.data, s2.len), "resolved serialization deterministic");
    ok &= expect(dsu_resolve_result_component_count(r1) == 2u, "component_count==2 (det)");
    ok &= expect(strcmp(dsu_resolve_result_component_id(r1, 0u), "core") == 0, "component[0]==core (det)");
    ok &= expect(strcmp(dsu_resolve_result_component_id(r1, 1u), "data") == 0, "component[1]==data (det)");

done:
    buf_free(&s1);
    buf_free(&s2);
    if (r2) dsu_resolve_result_destroy(ctx, r2);
    if (r1) dsu_resolve_result_destroy(ctx, r1);
    if (m) dsu_manifest_destroy(ctx, m);
    if (ctx) dsu_ctx_destroy(ctx);
    remove(mf_path);
    return ok;
}

int main(void) {
    int ok = 1;
    ok &= test_default_only();
    ok &= test_explicit_selection_and_exclude();
    ok &= test_dependency_closure();
    ok &= test_conflict_detection();
    ok &= test_platform_ambiguity_failure();
    ok &= test_platform_missing_install_root_failure();
    ok &= test_upgrade_monotonicity();
    ok &= test_illegal_downgrade();
    ok &= test_deterministic_serialization();
    return ok ? 0 : 1;
}
