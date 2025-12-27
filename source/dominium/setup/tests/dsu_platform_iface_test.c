/*
FILE: source/dominium/setup/tests/dsu_platform_iface_test.c
MODULE: Dominium Setup
PURPOSE: Plan S-9 platform interface idempotency test.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dsu/dsu_callbacks.h"
#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"
#include "dsu/dsu_manifest.h"
#include "dsu/dsu_plan.h"
#include "dsu/dsu_platform_iface.h"
#include "dsu/dsu_resolve.h"
#include "dsu/dsu_state.h"

#include "../core/src/state/dsu_state_internal.h"

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
#define T_ACTION 0x0052u
#define T_ACTION_VER 0x0053u
#define T_ACTION_KIND 0x0054u
#define T_ACTION_APP_ID 0x0055u
#define T_ACTION_DISPLAY_NAME 0x0056u
#define T_ACTION_EXEC_RELPATH 0x0057u
#define T_ACTION_ARGUMENTS 0x0058u
#define T_ACTION_ICON_RELPATH 0x0059u
#define T_ACTION_EXTENSION 0x005Au
#define T_ACTION_PROTOCOL 0x005Bu
#define T_ACTION_MARKER_RELPATH 0x005Cu
#define T_ACTION_CAPABILITY_ID 0x005Du
#define T_ACTION_CAPABILITY_VALUE 0x005Eu
#define T_ACTION_PUBLISHER 0x005Fu

typedef struct action_spec_t {
    dsu_u8 kind;
    const char *app_id;
    const char *display_name;
    const char *exec_relpath;
    const char *arguments;
    const char *icon_relpath;
    const char *extension;
    const char *protocol;
    const char *marker_relpath;
    const char *capability_id;
    const char *capability_value;
    const char *publisher;
} action_spec_t;

typedef struct component_spec_t {
    const char *id;
    const char *version;
    dsu_u8 kind;
    dsu_u32 flags;
    const action_spec_t *actions;
    dsu_u32 action_count;
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

static int build_action_container(buf_t *out_act, const action_spec_t *a) {
    if (!out_act || !a) return 0;
    memset(out_act, 0, sizeof(*out_act));
    if (!buf_put_tlv_u32(out_act, T_ACTION_VER, 1ul)) return 0;
    if (!buf_put_tlv_u8(out_act, T_ACTION_KIND, a->kind)) return 0;
    if (a->app_id && !buf_put_tlv_str(out_act, T_ACTION_APP_ID, a->app_id)) return 0;
    if (a->display_name && !buf_put_tlv_str(out_act, T_ACTION_DISPLAY_NAME, a->display_name)) return 0;
    if (a->exec_relpath && !buf_put_tlv_str(out_act, T_ACTION_EXEC_RELPATH, a->exec_relpath)) return 0;
    if (a->arguments && !buf_put_tlv_str(out_act, T_ACTION_ARGUMENTS, a->arguments)) return 0;
    if (a->icon_relpath && !buf_put_tlv_str(out_act, T_ACTION_ICON_RELPATH, a->icon_relpath)) return 0;
    if (a->extension && !buf_put_tlv_str(out_act, T_ACTION_EXTENSION, a->extension)) return 0;
    if (a->protocol && !buf_put_tlv_str(out_act, T_ACTION_PROTOCOL, a->protocol)) return 0;
    if (a->marker_relpath && !buf_put_tlv_str(out_act, T_ACTION_MARKER_RELPATH, a->marker_relpath)) return 0;
    if (a->capability_id && !buf_put_tlv_str(out_act, T_ACTION_CAPABILITY_ID, a->capability_id)) return 0;
    if (a->capability_value && !buf_put_tlv_str(out_act, T_ACTION_CAPABILITY_VALUE, a->capability_value)) return 0;
    if (a->publisher && !buf_put_tlv_str(out_act, T_ACTION_PUBLISHER, a->publisher)) return 0;
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
    for (i = 0u; i < c->action_count; ++i) {
        buf_t act;
        if (!build_action_container(&act, &c->actions[i])) return 0;
        if (!buf_put_tlv(out_comp, T_ACTION, act.data, act.len)) {
            buf_free(&act);
            return 0;
        }
        buf_free(&act);
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

typedef struct plat_mock_t {
    unsigned char *seq;
    unsigned int seq_len;
    unsigned int seq_cap;
    unsigned int remove_calls;
} plat_mock_t;

static void plat_mock_reset_seq(plat_mock_t *m, unsigned char *seq, unsigned int cap) {
    if (!m) return;
    m->seq = seq;
    m->seq_len = 0u;
    m->seq_cap = cap;
}

static dsu_status_t plat_mock_push(plat_mock_t *m, const dsu_platform_intent_t *intent) {
    if (!m || !intent) return DSU_STATUS_INVALID_ARGS;
    if (m->seq && m->seq_len < m->seq_cap) {
        m->seq[m->seq_len++] = intent->kind;
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t mock_register_app_entry(void *user,
                                           dsu_ctx_t *ctx,
                                           const dsu_platform_registrations_state_t *state,
                                           const dsu_platform_intent_t *intent) {
    (void)ctx;
    (void)state;
    return plat_mock_push((plat_mock_t *)user, intent);
}

static dsu_status_t mock_register_file_assoc(void *user,
                                            dsu_ctx_t *ctx,
                                            const dsu_platform_registrations_state_t *state,
                                            const dsu_platform_intent_t *intent) {
    (void)ctx;
    (void)state;
    return plat_mock_push((plat_mock_t *)user, intent);
}

static dsu_status_t mock_register_url_handler(void *user,
                                             dsu_ctx_t *ctx,
                                             const dsu_platform_registrations_state_t *state,
                                             const dsu_platform_intent_t *intent) {
    (void)ctx;
    (void)state;
    return plat_mock_push((plat_mock_t *)user, intent);
}

static dsu_status_t mock_register_uninstall_entry(void *user,
                                                 dsu_ctx_t *ctx,
                                                 const dsu_platform_registrations_state_t *state,
                                                 const dsu_platform_intent_t *intent) {
    (void)ctx;
    (void)state;
    return plat_mock_push((plat_mock_t *)user, intent);
}

static dsu_status_t mock_declare_capability(void *user,
                                           dsu_ctx_t *ctx,
                                           const dsu_platform_registrations_state_t *state,
                                           const dsu_platform_intent_t *intent) {
    (void)ctx;
    (void)state;
    return plat_mock_push((plat_mock_t *)user, intent);
}

static dsu_status_t mock_remove_registrations(void *user,
                                             dsu_ctx_t *ctx,
                                             const dsu_platform_registrations_state_t *state) {
    plat_mock_t *m = (plat_mock_t *)user;
    (void)ctx;
    (void)state;
    if (!m) return DSU_STATUS_INVALID_ARGS;
    m->remove_calls += 1u;
    return DSU_STATUS_SUCCESS;
}

static int test_platform_iface_idempotent_register_unregister(void) {
    const char *mf_path = "dsu_test_platform_iface.dsumanifest";
    buf_t mf_bytes;
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *m = NULL;
    dsu_resolve_result_t *r = NULL;
    dsu_plan_t *plan = NULL;
    dsu_state_t *state = NULL;
    dsu_status_t st;
    int ok = 1;
    dsu_platform_iface_t iface;
    plat_mock_t mock;
    unsigned char seq_a[8];
    unsigned char seq_b[8];
    unsigned int expected = 0u;
    dsu_u32 i;

    const char *const platform_targets[] = {"any-any"};
    install_root_spec_t ir[1];
    action_spec_t actions[3];
    component_spec_t comps[1];
    manifest_spec_t spec;

    memset(&mf_bytes, 0, sizeof(mf_bytes));
    memset(&ir, 0, sizeof(ir));
    memset(&actions, 0, sizeof(actions));
    memset(&comps, 0, sizeof(comps));
    memset(&spec, 0, sizeof(spec));
    memset(&mock, 0, sizeof(mock));

    ir[0].scope = (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    ir[0].platform = "any-any";
    ir[0].path = "install/platform_iface";

    actions[0].kind = (dsu_u8)DSU_MANIFEST_ACTION_REGISTER_APP_ENTRY;
    actions[0].app_id = "dominium.app";
    actions[0].display_name = "Dominium";
    actions[0].exec_relpath = "bin/dominium.exe";
    actions[0].publisher = "Dominium Project";

    actions[1].kind = (dsu_u8)DSU_MANIFEST_ACTION_REGISTER_URL_HANDLER;
    actions[1].app_id = "dominium.app";
    actions[1].protocol = "dominium";

    actions[2].kind = (dsu_u8)DSU_MANIFEST_ACTION_DECLARE_CAPABILITY;
    actions[2].capability_id = "cap.sample";
    actions[2].capability_value = "present";

    comps[0].id = "core";
    comps[0].version = "1.0.0";
    comps[0].kind = (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_OTHER;
    comps[0].flags = 0u;
    comps[0].actions = actions;
    comps[0].action_count = 3u;

    spec.product_id = "dominium";
    spec.product_version = "1.0.0";
    spec.build_channel = "stable";
    spec.platform_targets = platform_targets;
    spec.platform_target_count = 1u;
    spec.install_roots = ir;
    spec.install_root_count = 1u;
    spec.components = comps;
    spec.component_count = 1u;

    ok &= expect(build_manifest_file(&mf_bytes, &spec), "build manifest bytes");
    ok &= expect(write_bytes_file(mf_path, mf_bytes.data, mf_bytes.len), "write manifest");
    buf_free(&mf_bytes);
    if (!ok) goto done;

    ctx = create_ctx_deterministic();
    ok &= expect(ctx != NULL, "ctx create");
    if (!ok) goto done;

    st = dsu_manifest_load_file(ctx, mf_path, &m);
    ok &= expect(st == DSU_STATUS_SUCCESS && m != NULL, "manifest load");
    if (!ok) goto done;

    {
        const char *const requested[] = {"core"};
        dsu_resolve_request_t req;
        dsu_resolve_request_init(&req);
        req.operation = DSU_RESOLVE_OPERATION_INSTALL;
        req.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        req.requested_components = requested;
        req.requested_component_count = 1u;
        st = dsu_resolve_components(ctx, m, NULL, &req, &r);
    }
    ok &= expect(st == DSU_STATUS_SUCCESS && r != NULL, "resolve manifest");
    if (!ok) goto done;

    st = dsu_plan_build(ctx, m, mf_path, r, 0x1111222233334444ULL, &plan);
    ok &= expect(st == DSU_STATUS_SUCCESS && plan != NULL, "plan build");
    if (!ok) goto done;

    st = dsu__state_build_from_plan(ctx, plan, NULL, 0u, 0u, 0u, &state);
    ok &= expect(st == DSU_STATUS_SUCCESS && state != NULL, "state build");
    if (!ok) goto done;

    for (i = 0u; i < dsu_state_component_count(state); ++i) {
        expected += (unsigned int)dsu_state_component_registration_count(state, i);
    }
    ok &= expect(expected > 0u, "registrations present");
    if (!ok) goto done;

    dsu_platform_iface_init(&iface);
    iface.plat_register_app_entry = mock_register_app_entry;
    iface.plat_register_file_assoc = mock_register_file_assoc;
    iface.plat_register_url_handler = mock_register_url_handler;
    iface.plat_register_uninstall_entry = mock_register_uninstall_entry;
    iface.plat_declare_capability = mock_declare_capability;
    iface.plat_remove_registrations = mock_remove_registrations;

    st = dsu_ctx_set_platform_iface(ctx, &iface, &mock);
    ok &= expect(st == DSU_STATUS_SUCCESS, "set platform iface");
    if (!ok) goto done;

    plat_mock_reset_seq(&mock, seq_a, (unsigned int)(sizeof(seq_a) / sizeof(seq_a[0])));
    st = dsu_platform_register_from_state(ctx, state);
    ok &= expect(st == DSU_STATUS_SUCCESS, "register pass A");
    ok &= expect(mock.seq_len == expected, "register count A");
    if (!ok) goto done;

    plat_mock_reset_seq(&mock, seq_b, (unsigned int)(sizeof(seq_b) / sizeof(seq_b[0])));
    st = dsu_platform_register_from_state(ctx, state);
    ok &= expect(st == DSU_STATUS_SUCCESS, "register pass B");
    ok &= expect(mock.seq_len == expected, "register count B");
    ok &= expect(memcmp(seq_a, seq_b, expected) == 0, "register sequence deterministic");
    if (!ok) goto done;

    st = dsu_platform_unregister_from_state(ctx, state);
    ok &= expect(st == DSU_STATUS_SUCCESS, "unregister pass A");
    st = dsu_platform_unregister_from_state(ctx, state);
    ok &= expect(st == DSU_STATUS_SUCCESS, "unregister pass B");
    ok &= expect(mock.remove_calls == 2u, "unregister calls");

done:
    if (state) dsu_state_destroy(ctx, state);
    if (plan) dsu_plan_destroy(ctx, plan);
    if (r) dsu_resolve_result_destroy(ctx, r);
    if (m) dsu_manifest_destroy(ctx, m);
    if (ctx) dsu_ctx_destroy(ctx);
    remove(mf_path);
    return ok;
}

int main(void) {
    int ok = 1;
    ok &= test_platform_iface_idempotent_register_unregister();
    return ok ? 0 : 1;
}
