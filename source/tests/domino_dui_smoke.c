/*
FILE: source/tests/domino_dui_smoke.c
MODULE: Tests
RESPONSIBILITY: DUI backend smoke test (native/dgfx/null) via the capability registry.
*/
#include <stdio.h>
#include <string.h>

#include "domino/caps.h"
#include "domino/profile.h"
#include "domino/io/container.h"
#include "domino/sys.h"

#include "dui/dui_api_v1.h"

static int tlv_write_u32(unsigned char* dst, u32 cap, u32* io_off, u32 tag, u32 v)
{
    unsigned char le[4];
    dtlv_le_write_u32(le, v);
    return dtlv_tlv_write(dst, cap, io_off, tag, le, 4u);
}

static int tlv_write_u64(unsigned char* dst, u32 cap, u32* io_off, u32 tag, u64 v)
{
    unsigned char le[8];
    dtlv_le_write_u32(le + 0u, (u32)(v & 0xffffffffu));
    dtlv_le_write_u32(le + 4u, (u32)((v >> 32u) & 0xffffffffu));
    return dtlv_tlv_write(dst, cap, io_off, tag, le, 8u);
}

static int tlv_write_raw(unsigned char* dst, u32 cap, u32* io_off, u32 tag, const void* payload, u32 payload_len)
{
    return dtlv_tlv_write(dst, cap, io_off, tag, payload, payload_len);
}

static int tlv_write_cstr(unsigned char* dst, u32 cap, u32* io_off, u32 tag, const char* s)
{
    const u32 n = (u32)((s && s[0]) ? strlen(s) : 0u);
    return dtlv_tlv_write(dst, cap, io_off, tag, (s ? s : ""), n);
}

static int schema_emit_node(unsigned char* dst,
                            u32 cap,
                            u32* io_off,
                            u32 id,
                            u32 kind,
                            const char* text,
                            u32 action_id,
                            u32 bind_id,
                            u32 flags,
                            u64 required_caps,
                            const unsigned char* children,
                            u32 children_len)
{
    unsigned char payload[512];
    u32 poff = 0u;
    if (!dst || !io_off) {
        return -1;
    }
    if (tlv_write_u32(payload, (u32)sizeof(payload), &poff, DUI_TLV_ID_U32, id) != 0) return -1;
    if (tlv_write_u32(payload, (u32)sizeof(payload), &poff, DUI_TLV_KIND_U32, kind) != 0) return -1;
    if (text && text[0]) {
        if (tlv_write_cstr(payload, (u32)sizeof(payload), &poff, DUI_TLV_TEXT_UTF8, text) != 0) return -1;
    }
    if (action_id != 0u) {
        if (tlv_write_u32(payload, (u32)sizeof(payload), &poff, DUI_TLV_ACTION_U32, action_id) != 0) return -1;
    }
    if (bind_id != 0u) {
        if (tlv_write_u32(payload, (u32)sizeof(payload), &poff, DUI_TLV_BIND_U32, bind_id) != 0) return -1;
    }
    if (flags != 0u) {
        if (tlv_write_u32(payload, (u32)sizeof(payload), &poff, DUI_TLV_FLAGS_U32, flags) != 0) return -1;
    }
    if (required_caps != 0u) {
        if (tlv_write_u64(payload, (u32)sizeof(payload), &poff, DUI_TLV_REQUIRED_CAPS_U64, required_caps) != 0) return -1;
    }
    if (children && children_len != 0u) {
        if (tlv_write_raw(payload, (u32)sizeof(payload), &poff, DUI_TLV_CHILDREN_V1, children, children_len) != 0) return -1;
    }
    return tlv_write_raw(dst, cap, io_off, DUI_TLV_NODE_V1, payload, poff);
}

static int build_smoke_schema(unsigned char* out_buf, u32 cap, u32* out_len)
{
    unsigned char children[2048];
    unsigned char form[2048];
    unsigned char schema[2048];
    u32 child_off = 0u;
    u32 form_off = 0u;
    u32 schema_off = 0u;
    u32 out_off = 0u;

    if (!out_buf || !out_len) {
        return -1;
    }
    *out_len = 0u;

    if (schema_emit_node(children, (u32)sizeof(children), &child_off,
                         10u, (u32)DUI_NODE_LABEL, "Smoke Label",
                         0u, 0u, 0u, (u64)DUI_CAP_LABEL, 0, 0u) != 0) return -1;
    if (schema_emit_node(children, (u32)sizeof(children), &child_off,
                         11u, (u32)DUI_NODE_BUTTON, "Smoke Button",
                         1u, 0u, DUI_NODE_FLAG_FOCUSABLE, (u64)DUI_CAP_BUTTON, 0, 0u) != 0) return -1;
    if (schema_emit_node(children, (u32)sizeof(children), &child_off,
                         12u, (u32)DUI_NODE_CHECKBOX, "Smoke Checkbox",
                         0u, 12u, DUI_NODE_FLAG_FOCUSABLE, (u64)DUI_CAP_CHECKBOX, 0, 0u) != 0) return -1;
    if (schema_emit_node(children, (u32)sizeof(children), &child_off,
                         13u, (u32)DUI_NODE_TEXT_FIELD, 0,
                         0u, 13u, DUI_NODE_FLAG_FOCUSABLE, (u64)DUI_CAP_TEXT_FIELD, 0, 0u) != 0) return -1;
    if (schema_emit_node(children, (u32)sizeof(children), &child_off,
                         14u, (u32)DUI_NODE_PROGRESS, 0,
                         0u, 14u, 0u, (u64)DUI_CAP_PROGRESS, 0, 0u) != 0) return -1;
    if (schema_emit_node(children, (u32)sizeof(children), &child_off,
                         15u, (u32)DUI_NODE_LIST, 0,
                         0u, 15u, (u32)(DUI_NODE_FLAG_FOCUSABLE | DUI_NODE_FLAG_FLEX), (u64)DUI_CAP_LIST, 0, 0u) != 0) return -1;

    {
        unsigned char root_payload[512];
        u32 roff = 0u;
        if (tlv_write_u32(root_payload, (u32)sizeof(root_payload), &roff, DUI_TLV_ID_U32, 1u) != 0) return -1;
        if (tlv_write_u32(root_payload, (u32)sizeof(root_payload), &roff, DUI_TLV_KIND_U32, (u32)DUI_NODE_COLUMN) != 0) return -1;
        if (tlv_write_u64(root_payload, (u32)sizeof(root_payload), &roff, DUI_TLV_REQUIRED_CAPS_U64, (u64)DUI_CAP_LAYOUT_COLUMN) != 0) return -1;
        if (tlv_write_raw(root_payload, (u32)sizeof(root_payload), &roff, DUI_TLV_CHILDREN_V1, children, child_off) != 0) return -1;
        if (tlv_write_raw(form, (u32)sizeof(form), &form_off, DUI_TLV_NODE_V1, root_payload, roff) != 0) return -1;
    }

    if (tlv_write_raw(schema, (u32)sizeof(schema), &schema_off, DUI_TLV_FORM_V1, form, form_off) != 0) return -1;
    if (tlv_write_raw(out_buf, cap, &out_off, DUI_TLV_SCHEMA_V1, schema, schema_off) != 0) return -1;

    *out_len = out_off;
    return 0;
}

static int state_emit_text(unsigned char* dst, u32 cap, u32* io_off, u32 bind_id, const char* s)
{
    unsigned char payload[512];
    u32 poff = 0u;
    if (!dst || !io_off) {
        return -1;
    }
    if (tlv_write_u32(payload, (u32)sizeof(payload), &poff, DUI_TLV_BIND_U32, bind_id) != 0) return -1;
    if (tlv_write_u32(payload, (u32)sizeof(payload), &poff, DUI_TLV_VALUE_TYPE_U32, (u32)DUI_VALUE_TEXT) != 0) return -1;
    if (tlv_write_cstr(payload, (u32)sizeof(payload), &poff, DUI_TLV_VALUE_UTF8, s ? s : "") != 0) return -1;
    return tlv_write_raw(dst, cap, io_off, DUI_TLV_VALUE_V1, payload, poff);
}

static int state_emit_u32(unsigned char* dst, u32 cap, u32* io_off, u32 bind_id, u32 v)
{
    unsigned char payload[256];
    u32 poff = 0u;
    if (!dst || !io_off) {
        return -1;
    }
    if (tlv_write_u32(payload, (u32)sizeof(payload), &poff, DUI_TLV_BIND_U32, bind_id) != 0) return -1;
    if (tlv_write_u32(payload, (u32)sizeof(payload), &poff, DUI_TLV_VALUE_TYPE_U32, (u32)DUI_VALUE_U32) != 0) return -1;
    if (tlv_write_u32(payload, (u32)sizeof(payload), &poff, DUI_TLV_VALUE_U32, v) != 0) return -1;
    return tlv_write_raw(dst, cap, io_off, DUI_TLV_VALUE_V1, payload, poff);
}

static int state_emit_list(unsigned char* dst, u32 cap, u32* io_off, u32 bind_id)
{
    unsigned char list_payload[1024];
    unsigned char value_payload[2048];
    u32 loff = 0u;
    u32 voff = 0u;
    unsigned char item_payload[256];
    u32 ioff;

    if (!dst || !io_off) {
        return -1;
    }
    if (tlv_write_u32(list_payload, (u32)sizeof(list_payload), &loff, DUI_TLV_LIST_SELECTED_U32, 1002u) != 0) return -1;

    ioff = 0u;
    if (tlv_write_u32(item_payload, (u32)sizeof(item_payload), &ioff, DUI_TLV_ITEM_ID_U32, 1001u) != 0) return -1;
    if (tlv_write_cstr(item_payload, (u32)sizeof(item_payload), &ioff, DUI_TLV_ITEM_TEXT_UTF8, "Item A") != 0) return -1;
    if (tlv_write_raw(list_payload, (u32)sizeof(list_payload), &loff, DUI_TLV_LIST_ITEM_V1, item_payload, ioff) != 0) return -1;

    ioff = 0u;
    if (tlv_write_u32(item_payload, (u32)sizeof(item_payload), &ioff, DUI_TLV_ITEM_ID_U32, 1002u) != 0) return -1;
    if (tlv_write_cstr(item_payload, (u32)sizeof(item_payload), &ioff, DUI_TLV_ITEM_TEXT_UTF8, "Item B") != 0) return -1;
    if (tlv_write_raw(list_payload, (u32)sizeof(list_payload), &loff, DUI_TLV_LIST_ITEM_V1, item_payload, ioff) != 0) return -1;

    ioff = 0u;
    if (tlv_write_u32(item_payload, (u32)sizeof(item_payload), &ioff, DUI_TLV_ITEM_ID_U32, 1003u) != 0) return -1;
    if (tlv_write_cstr(item_payload, (u32)sizeof(item_payload), &ioff, DUI_TLV_ITEM_TEXT_UTF8, "Item C") != 0) return -1;
    if (tlv_write_raw(list_payload, (u32)sizeof(list_payload), &loff, DUI_TLV_LIST_ITEM_V1, item_payload, ioff) != 0) return -1;

    if (tlv_write_u32(value_payload, (u32)sizeof(value_payload), &voff, DUI_TLV_BIND_U32, bind_id) != 0) return -1;
    if (tlv_write_u32(value_payload, (u32)sizeof(value_payload), &voff, DUI_TLV_VALUE_TYPE_U32, (u32)DUI_VALUE_LIST) != 0) return -1;
    if (tlv_write_raw(value_payload, (u32)sizeof(value_payload), &voff, DUI_TLV_LIST_V1, list_payload, loff) != 0) return -1;

    return tlv_write_raw(dst, cap, io_off, DUI_TLV_VALUE_V1, value_payload, voff);
}

static int build_smoke_state(unsigned char* out_buf, u32 cap, u32* out_len)
{
    unsigned char inner[4096];
    u32 inner_off = 0u;
    u32 out_off = 0u;

    if (!out_buf || !out_len) {
        return -1;
    }
    *out_len = 0u;

    if (state_emit_text(inner, (u32)sizeof(inner), &inner_off, 10u, "Label: ok") != 0) return -1;
    if (state_emit_text(inner, (u32)sizeof(inner), &inner_off, 13u, "Text") != 0) return -1;
    if (state_emit_u32(inner, (u32)sizeof(inner), &inner_off, 12u, 1u) != 0) return -1;
    if (state_emit_u32(inner, (u32)sizeof(inner), &inner_off, 14u, 500u) != 0) return -1;
    if (state_emit_list(inner, (u32)sizeof(inner), &inner_off, 15u) != 0) return -1;

    if (tlv_write_raw(out_buf, cap, &out_off, DUI_TLV_STATE_V1, inner, inner_off) != 0) return -1;
    *out_len = out_off;
    return 0;
}

static int copy_cstr_bounded(char* dst, size_t cap, const char* src)
{
    size_t n;
    if (!dst || cap == 0u) {
        return 0;
    }
    if (!src) {
        dst[0] = '\0';
        return 1;
    }
    n = strlen(src);
    if (n >= cap) {
        return 0;
    }
    memcpy(dst, src, n);
    dst[n] = '\0';
    return 1;
}

static const dui_api_v1* get_dui_api_for_backend(const char* backend_name)
{
    dom_profile profile;
    dom_hw_caps hw;
    dom_selection sel;
    dom_backend_desc desc;
    dom_caps_result rc;
    u32 i;
    u32 count;
    const char* chosen = "";

    (void)dom_caps_register_builtin_backends();
    (void)dom_caps_finalize_registry();

    memset(&profile, 0, sizeof(profile));
    profile.abi_version = DOM_PROFILE_ABI_VERSION;
    profile.struct_size = (u32)sizeof(dom_profile);
    profile.kind = DOM_PROFILE_BASELINE;
    profile.lockstep_strict = 0u;
    profile.override_count = 0u;
    profile.feature_count = 0u;

    if (backend_name && backend_name[0]) {
        profile.override_count = 1u;
        (void)copy_cstr_bounded(profile.overrides[0].subsystem_key, sizeof(profile.overrides[0].subsystem_key), "ui");
        (void)copy_cstr_bounded(profile.overrides[0].backend_name, sizeof(profile.overrides[0].backend_name), backend_name);
    }

    memset(&hw, 0, sizeof(hw));
    hw.abi_version = DOM_CAPS_ABI_VERSION;
    hw.struct_size = (u32)sizeof(hw);
    (void)dom_hw_caps_probe_host(&hw);

    memset(&sel, 0, sizeof(sel));
    sel.abi_version = DOM_CAPS_ABI_VERSION;
    sel.struct_size = (u32)sizeof(sel);
    rc = dom_caps_select(&profile, &hw, &sel);
    if (rc != DOM_CAPS_OK) {
        return (const dui_api_v1*)0;
    }

    for (i = 0u; i < sel.entry_count; ++i) {
        if (sel.entries[i].subsystem_id == DOM_SUBSYS_DUI) {
            chosen = sel.entries[i].backend_name ? sel.entries[i].backend_name : "";
            break;
        }
    }
    if (!chosen || !chosen[0]) {
        return (const dui_api_v1*)0;
    }

    count = dom_caps_backend_count();
    for (i = 0u; i < count; ++i) {
        if (dom_caps_backend_get(i, &desc) != DOM_CAPS_OK) {
            continue;
        }
        if (desc.subsystem_id != DOM_SUBSYS_DUI) {
            continue;
        }
        if (!desc.backend_name || strcmp(desc.backend_name, chosen) != 0) {
            continue;
        }
        if (!desc.get_api) {
            return (const dui_api_v1*)0;
        }
        return (const dui_api_v1*)desc.get_api(DUI_API_ABI_VERSION);
    }
    return (const dui_api_v1*)0;
}

static int wait_for_quit(const dui_api_v1* api, dui_context* ctx, u32 max_pumps)
{
    u32 i;
    dui_event_v1 ev;
    if (!api || !ctx) {
        return 0;
    }
    memset(&ev, 0, sizeof(ev));
    for (i = 0u; i < max_pumps; ++i) {
        (void)api->pump(ctx);
        while (api->poll_event(ctx, &ev) > 0) {
            if (ev.type == (u32)DUI_EVENT_QUIT) {
                return 1;
            }
            memset(&ev, 0, sizeof(ev));
        }
        dsys_sleep_ms(1);
    }
    return 0;
}

int main(int argc, char** argv)
{
    const char* backend = (argc >= 2) ? argv[1] : "null";
    const dui_api_v1* api;
    dui_context* ctx = (dui_context*)0;
    dui_window* win = (dui_window*)0;
    dui_window_desc_v1 wdesc;
    unsigned char schema[2048];
    u32 schema_len = 0u;
    unsigned char state[4096];
    u32 state_len = 0u;
    u32 flags = 0u;

    api = get_dui_api_for_backend(backend);
    if (!api) {
        fprintf(stderr, "dui_smoke: failed to resolve backend '%s'\n", backend ? backend : "(null)");
        return 2;
    }

    if (strcmp(backend, "dgfx") == 0) {
        flags |= DUI_WINDOW_FLAG_HEADLESS;
    }

    if (api->create_context(&ctx) != DUI_OK || !ctx) {
        fprintf(stderr, "dui_smoke: create_context failed (%s)\n", backend);
        return 3;
    }

    memset(&wdesc, 0, sizeof(wdesc));
    wdesc.abi_version = DUI_API_ABI_VERSION;
    wdesc.struct_size = (u32)sizeof(wdesc);
    wdesc.title = "DUI Smoke";
    wdesc.width = 640;
    wdesc.height = 480;
    wdesc.flags = flags;

    if (api->create_window(ctx, &wdesc, &win) != DUI_OK || !win) {
        fprintf(stderr, "dui_smoke: create_window failed (%s)\n", backend);
        api->destroy_context(ctx);
        return 4;
    }

    if (build_smoke_schema(schema, (u32)sizeof(schema), &schema_len) != 0) {
        fprintf(stderr, "dui_smoke: build schema failed\n");
        api->destroy_window(win);
        api->destroy_context(ctx);
        return 5;
    }
    if (build_smoke_state(state, (u32)sizeof(state), &state_len) != 0) {
        fprintf(stderr, "dui_smoke: build state failed\n");
        api->destroy_window(win);
        api->destroy_context(ctx);
        return 6;
    }

    if (api->set_schema_tlv(win, schema, schema_len) != DUI_OK) {
        fprintf(stderr, "dui_smoke: set_schema_tlv failed\n");
        api->destroy_window(win);
        api->destroy_context(ctx);
        return 7;
    }
    if (api->set_state_tlv(win, state, state_len) != DUI_OK) {
        fprintf(stderr, "dui_smoke: set_state_tlv failed\n");
        api->destroy_window(win);
        api->destroy_context(ctx);
        return 8;
    }

    (void)api->render(win);
    (void)api->pump(ctx);
    (void)api->render(win);

    (void)api->request_quit(ctx);
    if (!wait_for_quit(api, ctx, 200u)) {
        fprintf(stderr, "dui_smoke: did not observe quit event\n");
        api->destroy_window(win);
        api->destroy_context(ctx);
        return 9;
    }

    api->destroy_window(win);
    api->destroy_context(ctx);
    return 0;
}

