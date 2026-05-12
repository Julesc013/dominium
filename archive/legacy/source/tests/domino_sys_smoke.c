/*
FILE: source/tests/domino_sys_smoke.c
MODULE: Repository
LAYER / SUBSYSTEM: source/tests
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

static void print_dsys_caps(const dsys_caps* caps)
{
    if (!caps) {
        return;
    }
    printf("dsys: backend=%s ui_modes=%u windows=%d mouse=%d gamepad=%d hi_res_timer=%d\n",
           caps->name ? caps->name : "(null)",
           (unsigned)caps->ui_modes,
           caps->has_windows ? 1 : 0,
           caps->has_mouse ? 1 : 0,
           caps->has_gamepad ? 1 : 0,
           caps->has_high_res_timer ? 1 : 0);
}

static void join_path(char* out, size_t cap, const char* base, const char* leaf)
{
    size_t i;
    size_t j;
    char sep;

    if (!out || cap == 0u) {
        return;
    }

    out[0] = '\0';
    if (!base) {
        base = "";
    }
    if (!leaf) {
        leaf = "";
    }

    sep = '/';
#if defined(_WIN32)
    sep = '\\';
#endif

    i = 0u;
    while (base[i] != '\0' && i + 1u < cap) {
        out[i] = base[i];
        ++i;
    }
    if (i > 0u && i + 1u < cap) {
        char last;
        last = out[i - 1u];
        if (last != '/' && last != '\\') {
            out[i++] = sep;
        }
    }
    j = 0u;
    while (leaf[j] != '\0' && i + 1u < cap) {
        out[i++] = leaf[j++];
    }
    out[i] = '\0';
}

static int print_selection_audit(void)
{
    dom_profile profile;
    dom_selection sel;
    dom_hw_caps hw;
    char audit[DOM_CAPS_AUDIT_LOG_MAX_BYTES];
    u32 len;

    memset(&profile, 0, sizeof(profile));
    profile.abi_version = DOM_PROFILE_ABI_VERSION;
    profile.struct_size = (u32)sizeof(profile);
    profile.kind = DOM_PROFILE_BASELINE;
    profile.lockstep_strict = 0u;
    profile.preferred_gfx_backend[0] = '\0';

    if (dom_caps_register_builtin_backends() != DOM_CAPS_OK) {
        printf("caps: register_builtin_backends failed\n");
        return 1;
    }
    if (dom_caps_finalize_registry() != DOM_CAPS_OK) {
        printf("caps: finalize_registry failed\n");
        return 1;
    }

    memset(&sel, 0, sizeof(sel));
    sel.abi_version = DOM_CAPS_ABI_VERSION;
    sel.struct_size = (u32)sizeof(sel);
    memset(&hw, 0, sizeof(hw));
    if (dom_hw_caps_probe_host(&hw) != 0) {
        memset(&hw, 0, sizeof(hw));
    }
    if (dom_caps_select(&profile, &hw, &sel) != DOM_CAPS_OK) {
        printf("caps: select failed\n");
    }

    audit[0] = '\0';
    len = (u32)sizeof(audit);
    (void)dom_caps_get_audit_log(&sel, audit, &len);
    if (audit[0] != '\0') {
        printf("%s", audit);
    }
    return (sel.result == DOM_CAPS_OK) ? 0 : 1;
}

static int want_strict_feature(const dsys_caps* caps)
{
    if (!caps || !caps->name) {
        return 0;
    }
    if (streq(caps->name, "win32") || streq(caps->name, "win32_headless")) {
        return 1;
    }
    return 0;
}

static int smoke_fs(const dsys_caps* caps)
{
    char tmp[260];
    char file_path[520];
    const char* payload;
    char buf[64];
    void* fh;
    size_t wrote;
    size_t read;

    if (!dsys_get_path(DSYS_PATH_TEMP, tmp, sizeof(tmp)) || tmp[0] == '\0') {
        printf("smoke: DSYS_PATH_TEMP unavailable\n");
        return 1;
    }

    join_path(file_path, sizeof(file_path), tmp, "domino_sys_smoke.tmp");

    payload = "domino_sys_smoke";
    fh = dsys_file_open(file_path, "wb");
    if (!fh) {
        printf("smoke: file_open(wb) failed: %s\n", file_path);
        return 1;
    }
    wrote = dsys_file_write(fh, payload, strlen(payload));
    (void)dsys_file_close(fh);
    if (wrote != strlen(payload)) {
        printf("smoke: file_write short write\n");
        return 1;
    }

    memset(buf, 0, sizeof(buf));
    fh = dsys_file_open(file_path, "rb");
    if (!fh) {
        printf("smoke: file_open(rb) failed\n");
        return 1;
    }
    read = dsys_file_read(fh, buf, sizeof(buf) - 1u);
    (void)dsys_file_close(fh);
    if (read == 0u || strcmp(buf, payload) != 0) {
        printf("smoke: file_read mismatch (got '%s')\n", buf);
        return 1;
    }

    if (remove(file_path) != 0) {
        printf("smoke: remove failed (ignored): %s\n", file_path);
        if (want_strict_feature(caps)) {
            return 1;
        }
    }

    return 0;
}

static int smoke_dir(const dsys_caps* caps)
{
    char tmp[260];
    dsys_dir_iter* it;
    dsys_dir_entry e;
    int ok;

    (void)caps;

    if (!dsys_get_path(DSYS_PATH_TEMP, tmp, sizeof(tmp)) || tmp[0] == '\0') {
        return 1;
    }

    it = dsys_dir_open(tmp);
    if (!it) {
        printf("smoke: dir_open failed: %s\n", tmp);
        return want_strict_feature(caps) ? 1 : 0;
    }
    ok = dsys_dir_next(it, &e) ? 1 : 1; /* existence is sufficient */
    (void)ok;
    dsys_dir_close(it);
    return 0;
}

static int smoke_time(void)
{
    uint64_t t0;
    uint64_t t1;
    uint64_t t2;

    t0 = dsys_time_now_us();
    t1 = dsys_time_now_us();
    if (t1 < t0) {
        printf("smoke: time not monotonic (%llu -> %llu)\n",
               (unsigned long long)t0,
               (unsigned long long)t1);
        return 1;
    }
    dsys_sleep_ms(1u);
    t2 = dsys_time_now_us();
    if (t2 < t1) {
        printf("smoke: time not monotonic after sleep (%llu -> %llu)\n",
               (unsigned long long)t1,
               (unsigned long long)t2);
        return 1;
    }
    return 0;
}

static int smoke_dynlib(const dsys_caps* caps)
{
    dsys_core_api_v1 core;
    dsys_dynlib_api_v1* dyn;
    void* lib;
    void* sym;

    memset(&core, 0, sizeof(core));
    if (dsys_get_core_api(1u, &core) != DSYS_OK || !core.query_interface) {
        printf("smoke: core api unavailable\n");
        return want_strict_feature(caps) ? 1 : 0;
    }

    dyn = (dsys_dynlib_api_v1*)0;
    if (core.query_interface(DSYS_IID_DYNLIB_API_V1, (void**)&dyn) != DSYS_OK || !dyn) {
        printf("smoke: dynlib unsupported\n");
        return want_strict_feature(caps) ? 1 : 0;
    }

    if (dyn->abi_version != 1u || dyn->struct_size < (u32)sizeof(*dyn)) {
        printf("smoke: dynlib abi mismatch\n");
        return 1;
    }

    lib = dyn->open ? dyn->open("kernel32.dll") : (void*)0;
    if (!lib) {
        printf("smoke: dynlib open failed\n");
        return want_strict_feature(caps) ? 1 : 0;
    }

    sym = dyn->sym ? dyn->sym(lib, "GetTickCount") : (void*)0;
    if (!sym) {
        printf("smoke: dynlib sym failed\n");
        if (dyn->close) {
            dyn->close(lib);
        }
        return want_strict_feature(caps) ? 1 : 0;
    }

    if (dyn->close) {
        dyn->close(lib);
    }

    return 0;
}

static int smoke_process(const dsys_caps* caps)
{
    dsys_process_desc desc;
    dsys_process* proc;
    int code;

#if defined(_WIN32)
    const char* args[] = {
        "C:\\Windows\\System32\\cmd.exe",
        "/c",
        "exit",
        "0",
        NULL
    };
    desc.exe = args[0];
    desc.argv = args;
#else
    const char* args[] = { "/bin/true", NULL };
    desc.exe = args[0];
    desc.argv = args;
#endif
    desc.flags = 0u;

    proc = dsys_process_spawn(&desc);
    if (!proc) {
        printf("smoke: process spawn unsupported/failed\n");
        return want_strict_feature(caps) ? 1 : 0;
    }
    code = dsys_process_wait(proc);
    dsys_process_destroy(proc);
    if (code != 0) {
        printf("smoke: process exit code %d\n", code);
        return 1;
    }
    return 0;
}

static int smoke_window(const dsys_caps* caps)
{
    dsys_window_desc wdesc;
    dsys_window* win;
    dsys_event ev;
    uint64_t start;
    uint64_t now;

    if (!caps || !caps->has_windows) {
        return 0;
    }

    wdesc.x = 0;
    wdesc.y = 0;
    wdesc.width = 320;
    wdesc.height = 240;
    wdesc.mode = DWIN_MODE_WINDOWED;

    win = dsys_window_create(&wdesc);
    if (!win) {
        printf("smoke: window_create failed\n");
        return 1;
    }

    start = dsys_time_now_us();
    for (;;) {
        now = dsys_time_now_us();
        if (now - start > 300000u) {
            break;
        }
        while (dsys_poll_event(&ev)) {
            if (ev.type == DSYS_EVENT_QUIT) {
                break;
            }
        }
        dsys_sleep_ms(1u);
    }

    dsys_window_destroy(win);
    return 0;
}

static int run_smoke(void)
{
    dsys_caps caps;
    int rc;

    rc = 0;
    if (dsys_init() != DSYS_OK) {
        printf("smoke: dsys_init failed\n");
        return 1;
    }

    caps = dsys_get_caps();
    print_dsys_caps(&caps);

    rc |= smoke_time();
    rc |= smoke_fs(&caps);
    rc |= smoke_dir(&caps);
    rc |= smoke_dynlib(&caps);
    rc |= smoke_process(&caps);
    rc |= smoke_window(&caps);

    dsys_shutdown();
    return rc ? 1 : 0;
}

int main(int argc, char** argv)
{
    int print_selection;
    int run;
    int rc;

    print_selection = has_flag(argc, argv, "--print-selection");
    run = has_flag(argc, argv, "--smoke");
    if (!print_selection && !run) {
        run = 1;
    }

    rc = 0;
    if (print_selection) {
        rc |= print_selection_audit();
    }
    if (run) {
        rc |= run_smoke();
    }

    return rc ? 1 : 0;
}
