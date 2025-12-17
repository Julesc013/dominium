/*
FILE: source/tests/launcher_ui_backend_swap_test.c
MODULE: Tests
RESPONSIBILITY: Final acceptance check: swapping UI backend must not affect non-UI backend selection when gfx is fixed.
*/
#include <stdio.h>
#include <string.h>

#include "domino/caps.h"
#include "domino/profile.h"

static int str_ieq(const char* a, const char* b)
{
    size_t i;
    size_t la, lb;
    if (!a || !b) return 0;
    la = strlen(a);
    lb = strlen(b);
    if (la != lb) return 0;
    for (i = 0u; i < la; ++i) {
        char ca = a[i];
        char cb = b[i];
        if (ca >= 'A' && ca <= 'Z') ca = (char)(ca - 'A' + 'a');
        if (cb >= 'A' && cb <= 'Z') cb = (char)(cb - 'A' + 'a');
        if (ca != cb) return 0;
    }
    return 1;
}

static void copy_cstr_bounded(char* dst, size_t cap, const char* src)
{
    size_t n;
    if (!dst || cap == 0u) return;
    if (!src) {
        dst[0] = '\0';
        return;
    }
    n = strlen(src);
    if (n >= cap) n = cap - 1u;
    memcpy(dst, src, n);
    dst[n] = '\0';
}

static int backend_exists(dom_subsystem_id subsys, const char* backend)
{
    u32 i, count;
    dom_backend_desc desc;
    if (!backend || !backend[0]) return 0;
    count = dom_caps_backend_count();
    memset(&desc, 0, sizeof(desc));
    for (i = 0u; i < count; ++i) {
        if (dom_caps_backend_get(i, &desc) != DOM_CAPS_OK) continue;
        if (desc.subsystem_id != subsys) continue;
        if (!desc.backend_name) continue;
        if (str_ieq(desc.backend_name, backend)) return 1;
    }
    return 0;
}

static const char* selection_backend(const dom_selection* sel, dom_subsystem_id subsys)
{
    u32 i;
    if (!sel) return "";
    for (i = 0u; i < sel->entry_count; ++i) {
        const dom_selection_entry* e = &sel->entries[i];
        if (e->subsystem_id == subsys) {
            return e->backend_name ? e->backend_name : "";
        }
    }
    return "";
}

static void set_override(dom_profile* p, const char* key, const char* backend)
{
    if (!p || !key || !backend) return;
    if (p->override_count >= DOM_PROFILE_MAX_OVERRIDES) return;
    copy_cstr_bounded(p->overrides[p->override_count].subsystem_key, sizeof(p->overrides[p->override_count].subsystem_key), key);
    copy_cstr_bounded(p->overrides[p->override_count].backend_name, sizeof(p->overrides[p->override_count].backend_name), backend);
    p->override_count += 1u;
}

static int select_with(dom_hw_caps* hw, const dom_profile* p, dom_selection* out_sel)
{
    dom_caps_result r;
    memset(out_sel, 0, sizeof(*out_sel));
    out_sel->abi_version = DOM_CAPS_ABI_VERSION;
    out_sel->struct_size = (u32)sizeof(*out_sel);
    r = dom_caps_select(p, hw, out_sel);
    return (r == DOM_CAPS_OK) ? 0 : 1;
}

int main(void)
{
    dom_hw_caps hw;
    const char* gfx_backend;
    dom_profile base;
    dom_profile p_a;
    dom_profile p_b;
    dom_profile p_c;
    dom_selection sel_a;
    dom_selection sel_b;
    dom_selection sel_c;
    const char* dsys_a;
    const char* dsys_b;
    const char* dgfx_a;
    const char* dgfx_b;

    (void)dom_caps_register_builtin_backends();
    (void)dom_caps_finalize_registry();

    memset(&hw, 0, sizeof(hw));
    hw.abi_version = DOM_CAPS_ABI_VERSION;
    hw.struct_size = (u32)sizeof(hw);
    (void)dom_hw_caps_probe_host(&hw);

    gfx_backend = backend_exists(DOM_SUBSYS_DGFX, "soft") ? "soft" : (backend_exists(DOM_SUBSYS_DGFX, "null") ? "null" : "");
    if (!gfx_backend[0]) {
        fprintf(stderr, "ui_backend_swap: no supported DGFX backends found (expected soft and/or null)\n");
        return 2;
    }

    memset(&base, 0, sizeof(base));
    base.abi_version = DOM_PROFILE_ABI_VERSION;
    base.struct_size = (u32)sizeof(base);
    base.kind = DOM_PROFILE_BASELINE;
    base.lockstep_strict = 0u;
    base.override_count = 0u;
    base.feature_count = 0u;

    /* Profile A: ui=dgfx (when available), gfx fixed. */
    p_a = base;
    set_override(&p_a, "gfx", gfx_backend);
    if (backend_exists(DOM_SUBSYS_DUI, "dgfx")) {
        set_override(&p_a, "ui", "dgfx");
    } else {
        /* Fallback: compare null vs native-only environment. */
        set_override(&p_a, "ui", "null");
    }

    /* Profile B: ui=null, gfx fixed. */
    p_b = base;
    set_override(&p_b, "gfx", gfx_backend);
    if (backend_exists(DOM_SUBSYS_DUI, "null")) {
        set_override(&p_b, "ui", "null");
    }

    if (select_with(&hw, &p_a, &sel_a) != 0 || select_with(&hw, &p_b, &sel_b) != 0) {
        fprintf(stderr, "ui_backend_swap: selection failed\n");
        return 3;
    }

    dsys_a = selection_backend(&sel_a, DOM_SUBSYS_DSYS);
    dsys_b = selection_backend(&sel_b, DOM_SUBSYS_DSYS);
    dgfx_a = selection_backend(&sel_a, DOM_SUBSYS_DGFX);
    dgfx_b = selection_backend(&sel_b, DOM_SUBSYS_DGFX);

    if (!str_ieq(dsys_a, dsys_b)) {
        fprintf(stderr, "ui_backend_swap: DSYS changed across UI backends (%s vs %s)\n", dsys_a, dsys_b);
        return 4;
    }
    if (!str_ieq(dgfx_a, dgfx_b)) {
        fprintf(stderr, "ui_backend_swap: DGFX changed across UI backends (%s vs %s)\n", dgfx_a, dgfx_b);
        return 5;
    }

#if defined(_WIN32) || defined(_WIN64)
    /* On Windows, also validate explicit native UI backend when present (win32). */
    if (backend_exists(DOM_SUBSYS_DUI, "win32")) {
        p_c = base;
        set_override(&p_c, "gfx", gfx_backend);
        set_override(&p_c, "ui", "win32");
        if (select_with(&hw, &p_c, &sel_c) != 0) {
            fprintf(stderr, "ui_backend_swap: selection failed for ui=win32\n");
            return 6;
        }
        if (!str_ieq(selection_backend(&sel_c, DOM_SUBSYS_DSYS), dsys_a)) {
            fprintf(stderr, "ui_backend_swap: DSYS changed across ui=win32\n");
            return 7;
        }
        if (!str_ieq(selection_backend(&sel_c, DOM_SUBSYS_DGFX), dgfx_a)) {
            fprintf(stderr, "ui_backend_swap: DGFX changed across ui=win32\n");
            return 8;
        }
    }
#endif

    printf("launcher_ui_backend_swap_test: OK\n");
    return 0;
}

