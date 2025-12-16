/*
FILE: tests/domino_gfx/dgfx_demo.c
MODULE: Repository
LAYER / SUBSYSTEM: tests/domino_gfx
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/sys.h"
#include "domino/gfx.h"
#include "domino/caps.h"
#include "domino/profile.h"

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

static int streq(const char* a, const char* b)
{
    if (!a || !b) {
        return 0;
    }
    return strcmp(a, b) == 0;
}

static int starts_with(const char* s, const char* prefix)
{
    size_t i;
    if (!s || !prefix) {
        return 0;
    }
    for (i = 0u; prefix[i] != '\0'; ++i) {
        if (s[i] != prefix[i]) {
            return 0;
        }
    }
    return 1;
}

static const char* get_opt_value(int argc, char** argv, const char* key)
{
    int i;
    size_t klen;

    if (!key || !key[0]) {
        return (const char*)0;
    }

    klen = strlen(key);
    for (i = 1; i < argc; ++i) {
        const char* a = argv[i];
        if (!a) {
            continue;
        }
        if (streq(a, key)) {
            if (i + 1 < argc) {
                return argv[i + 1];
            }
            return (const char*)0;
        }
        if (starts_with(a, key) && a[klen] == '=') {
            return a + klen + 1u;
        }
    }
    return (const char*)0;
}

static int has_flag(int argc, char** argv, const char* flag)
{
    int i;
    for (i = 1; i < argc; ++i) {
        if (streq(argv[i], flag)) {
            return 1;
        }
    }
    return 0;
}

static int parse_int(const char* s, int* out)
{
    char* endp;
    long v;

    if (!s || !s[0] || !out) {
        return 0;
    }

    endp = (char*)0;
    v = strtol(s, &endp, 10);
    if (!endp || endp == s || *endp != '\0') {
        return 0;
    }
    *out = (int)v;
    return 1;
}

static void profile_init(dom_profile* p)
{
    if (!p) {
        return;
    }
    memset(p, 0, sizeof(*p));
    p->abi_version = DOM_PROFILE_ABI_VERSION;
    p->struct_size = (u32)sizeof(*p);
    p->kind = DOM_PROFILE_BASELINE;
    p->lockstep_strict = 0u;
    p->preferred_gfx_backend[0] = '\0';
}

static int profile_apply_kind(dom_profile* p, const char* s)
{
    if (!p || !s || !s[0]) {
        return 1;
    }
    if (streq(s, "baseline")) {
        p->kind = DOM_PROFILE_BASELINE;
        return 1;
    }
    if (streq(s, "compat")) {
        p->kind = DOM_PROFILE_COMPAT;
        return 1;
    }
    if (streq(s, "perf")) {
        p->kind = DOM_PROFILE_PERF;
        return 1;
    }
    return 0;
}

static int profile_apply_gfx(dom_profile* p, const char* s)
{
    size_t n;
    if (!p) {
        return 0;
    }
    if (!s || !s[0] || streq(s, "auto")) {
        p->preferred_gfx_backend[0] = '\0';
        return 1;
    }
    n = strlen(s);
    if (n >= (size_t)DOM_PROFILE_BACKEND_NAME_MAX) {
        n = (size_t)DOM_PROFILE_BACKEND_NAME_MAX - 1u;
    }
    memcpy(p->preferred_gfx_backend, s, n);
    p->preferred_gfx_backend[n] = '\0';
    return 1;
}

static const dom_selection_entry* selection_find(const dom_selection* sel, dom_subsystem_id id)
{
    u32 i;
    if (!sel) {
        return (const dom_selection_entry*)0;
    }
    for (i = 0u; i < sel->entry_count; ++i) {
        if (sel->entries[i].subsystem_id == id) {
            return &sel->entries[i];
        }
    }
    return (const dom_selection_entry*)0;
}

static int dgfx_backend_from_name(const char* name, dgfx_backend_t* out)
{
    if (!name || !out) {
        return 0;
    }
    if (streq(name, "soft")) {
        *out = DGFX_BACKEND_SOFT;
        return 1;
    }
    if (streq(name, "dx9")) {
        *out = DGFX_BACKEND_DX9;
        return 1;
    }
    if (streq(name, "null")) {
        *out = DGFX_BACKEND_NULL;
        return 1;
    }
    return 0;
}

static int caps_init_and_select(const dom_profile* profile, dom_selection* out_sel, char* out_audit, u32 audit_cap)
{
    dom_hw_caps hw;
    u32 len;

    if (!profile || !out_sel || !out_audit || audit_cap == 0u) {
        return 0;
    }

    if (dom_caps_register_builtin_backends() != DOM_CAPS_OK) {
        printf("caps: register_builtin_backends failed\n");
        return 0;
    }
    if (dom_caps_finalize_registry() != DOM_CAPS_OK) {
        printf("caps: finalize_registry failed\n");
        return 0;
    }

    memset(out_sel, 0, sizeof(*out_sel));
    out_sel->abi_version = DOM_CAPS_ABI_VERSION;
    out_sel->struct_size = (u32)sizeof(*out_sel);

    memset(&hw, 0, sizeof(hw));
    if (dom_hw_caps_probe_host(&hw) != 0) {
        memset(&hw, 0, sizeof(hw));
    }
    (void)dom_caps_select(profile, &hw, out_sel);

    out_audit[0] = '\0';
    len = audit_cap;
    (void)dom_caps_get_audit_log(out_sel, out_audit, &len);
    return 1;
}

static void emit_demo_scene(dgfx_cmd_buffer* cmd, int w, int h, int frame_index)
{
    u32 clear_rgba;
    dgfx_viewport_t vp;
    dgfx_sprite_t sprites[3];
    dgfx_line_segment_t lines[2];
    dgfx_text_draw_t text;
    int x;
    int y;

    if (!cmd) {
        return;
    }

    clear_rgba = 0xff202020u;
    (void)dgfx_cmd_emit(cmd, DGFX_CMD_CLEAR, &clear_rgba, (u16)sizeof(clear_rgba));

    vp.x = 0;
    vp.y = 0;
    vp.w = (i32)w;
    vp.h = (i32)h;
    (void)dgfx_cmd_emit(cmd, DGFX_CMD_SET_VIEWPORT, &vp, (u16)sizeof(vp));

    if (w <= 0) w = 1;
    if (h <= 0) h = 1;

    x = (frame_index * 3) % w;
    y = (frame_index * 2) % h;
    x = x - 32;
    y = y - 16;

    sprites[0].x = (i32)x;
    sprites[0].y = (i32)y;
    sprites[0].w = 64;
    sprites[0].h = 32;
    sprites[0].color_rgba = 0xffcc3333u;

    sprites[1].x = (i32)(w - x - 64);
    sprites[1].y = (i32)y;
    sprites[1].w = 64;
    sprites[1].h = 32;
    sprites[1].color_rgba = 0xff33cc33u;

    sprites[2].x = (i32)(w / 2 - 16);
    sprites[2].y = (i32)((frame_index * 4) % h) - 16;
    sprites[2].w = 32;
    sprites[2].h = 32;
    sprites[2].color_rgba = 0xff3366ccu;

    (void)dgfx_cmd_emit(cmd, DGFX_CMD_DRAW_SPRITES, sprites, (u16)sizeof(sprites));

    lines[0].x0 = 0;
    lines[0].y0 = 0;
    lines[0].x1 = w - 1;
    lines[0].y1 = h - 1;
    lines[0].color_rgba = 0xffffffffu;
    lines[0].thickness = 1;

    lines[1].x0 = w - 1;
    lines[1].y0 = 0;
    lines[1].x1 = 0;
    lines[1].y1 = h - 1;
    lines[1].color_rgba = 0xffcccc00u;
    lines[1].thickness = 1;

    (void)dgfx_cmd_emit(cmd, DGFX_CMD_DRAW_LINES, lines, (u16)sizeof(lines));

    text.x = 8;
    text.y = 8;
    text.color_rgba = 0xffffffffu;
    text.utf8_text = "dgfx_demo";
    (void)dgfx_cmd_emit(cmd, DGFX_CMD_DRAW_TEXT, &text, (u16)sizeof(text));
}

int main(int argc, char** argv)
{
    const char* gfx_override;
    const char* profile_str;
    const char* frames_str;
    const char* lockstep_str;
    int print_selection;
    int frames;
    u32 lockstep_strict;

    dom_profile profile;
    dom_selection sel;
    char audit[DOM_CAPS_AUDIT_LOG_MAX_BYTES];

    const dom_selection_entry* gfx_sel;
    dgfx_backend_t gfx_backend;

    dsys_window_desc wdesc;
    dsys_window* win;
    dsys_event ev;
    void* hwnd;

    dgfx_desc gfx_desc;
    int32_t w;
    int32_t h;
    int frame;
    int quit;

    gfx_override = get_opt_value(argc, argv, "--gfx");
    profile_str = get_opt_value(argc, argv, "--profile");
    frames_str = get_opt_value(argc, argv, "--frames");
    lockstep_str = get_opt_value(argc, argv, "--lockstep-strict");
    print_selection = has_flag(argc, argv, "--print-selection");

    frames = 120;
    if (frames_str && frames_str[0]) {
        if (!parse_int(frames_str, &frames) || frames < 0) {
            printf("dgfx_demo: bad --frames value\n");
            return 1;
        }
    }

    lockstep_strict = 0u;
    if (lockstep_str && lockstep_str[0]) {
        int v;
        if (!parse_int(lockstep_str, &v) || (v != 0 && v != 1)) {
            printf("dgfx_demo: bad --lockstep-strict value\n");
            return 1;
        }
        lockstep_strict = (u32)v;
    }

    profile_init(&profile);
    profile.lockstep_strict = lockstep_strict;
    if (!profile_apply_kind(&profile, profile_str)) {
        printf("dgfx_demo: unknown --profile (use compat|baseline|perf)\n");
        return 1;
    }
    if (!profile_apply_gfx(&profile, gfx_override)) {
        printf("dgfx_demo: bad --gfx\n");
        return 1;
    }

    if (!caps_init_and_select(&profile, &sel, audit, (u32)sizeof(audit))) {
        return 1;
    }

    if (print_selection && audit[0] != '\0') {
        printf("%s", audit);
    }

    if (sel.result != DOM_CAPS_OK) {
        printf("dgfx_demo: selection failed (reason=%d)\n", (int)sel.fail_reason);
        return 1;
    }

    gfx_sel = selection_find(&sel, DOM_SUBSYS_DGFX);
    if (!gfx_sel || !gfx_sel->backend_name) {
        printf("dgfx_demo: selection missing dgfx\n");
        return 1;
    }

    if (!dgfx_backend_from_name(gfx_sel->backend_name, &gfx_backend)) {
        printf("dgfx_demo: dgfx backend unsupported by demo: %s\n", gfx_sel->backend_name);
        return 1;
    }

    if (dsys_init() != DSYS_OK) {
        printf("dgfx_demo: dsys_init failed\n");
        return 1;
    }

    wdesc.x = 0;
    wdesc.y = 0;
    wdesc.width = 640;
    wdesc.height = 360;
    wdesc.mode = DWIN_MODE_WINDOWED;

    win = dsys_window_create(&wdesc);
    if (!win) {
        printf("dgfx_demo: window_create failed\n");
        dsys_shutdown();
        return 1;
    }

    hwnd = dsys_window_get_native_handle(win);

    memset(&gfx_desc, 0, sizeof(gfx_desc));
    gfx_desc.backend = gfx_backend;
    gfx_desc.native_window = hwnd;
    gfx_desc.width = wdesc.width;
    gfx_desc.height = wdesc.height;
    gfx_desc.fullscreen = 0;
    gfx_desc.vsync = 0;
    gfx_desc.window = (void*)win;

    if (!dgfx_init(&gfx_desc)) {
        printf("dgfx_demo: dgfx_init failed (backend=%s)\n", gfx_sel->backend_name);
        dsys_window_destroy(win);
        dsys_shutdown();
        return 1;
    }

    printf("dgfx_demo: selected_gfx=%s det=%d frames=%d\n",
           gfx_sel->backend_name,
           (int)gfx_sel->determinism,
           frames);

    quit = 0;
    for (frame = 0; frame < frames && !quit; ++frame) {
        dgfx_cmd_buffer* cmd;
        dsys_window_get_size(win, &w, &h);

        while (dsys_poll_event(&ev)) {
            if (ev.type == DSYS_EVENT_QUIT) {
                quit = 1;
                break;
            }
            if (ev.type == DSYS_EVENT_KEY_DOWN && ev.payload.key.key == 27) {
                quit = 1;
                break;
            }
        }

        cmd = dgfx_get_frame_cmd_buffer();
        dgfx_cmd_buffer_reset(cmd);
        emit_demo_scene(cmd, (int)w, (int)h, frame);
        dgfx_execute(cmd);
        dgfx_end_frame();
    }

    dgfx_shutdown();
    dsys_window_destroy(win);
    dsys_shutdown();
    return 0;
}
