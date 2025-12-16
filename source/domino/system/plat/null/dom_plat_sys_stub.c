/*
FILE: source/domino/system/plat/null/dom_plat_sys_stub.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/null/dom_plat_sys_stub
RESPONSIBILITY: Implements `dom_plat_sys_stub`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dominium/dom_plat_sys.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static int sys_init(void) { return 0; }
static void sys_shutdown(void) { }

static int copy_str(const char* src, char* buf, size_t cap)
{
    size_t n;
    if (!buf || cap == 0) return -1;
    if (!src) {
        buf[0] = '\0';
        return 0;
    }
    n = strlen(src);
    if (n >= cap) n = cap - 1;
    memcpy(buf, src, n);
    buf[n] = '\0';
    return 0;
}

static int get_program_root(char* buf, size_t cap)  { return copy_str(".", buf, cap); }
static int get_data_root(char* buf, size_t cap)     { return copy_str("./data", buf, cap); }
static int get_state_root(char* buf, size_t cap)    { return copy_str("./state", buf, cap); }

static int fs_mkdir_p(const char* path)
{
    /* Stub: success without creating directories */
    (void)path;
    return 0;
}

static int fs_exists(const char* path)
{
    FILE* f = fopen(path, "rb");
    if (f) { fclose(f); return 1; }
    return 0;
}

static int fs_remove(const char* path)
{
    return remove(path);
}

static int spawn_process(const char* path, char* const argv[], int flags, int* out_exit_code)
{
    (void)path; (void)argv; (void)flags;
    if (out_exit_code) *out_exit_code = -1;
    return -1; /* TODO: implement platform process spawn */
}

static uint64_t ticks(void)
{
    return (uint64_t)clock();
}

static double seconds(void)
{
    return (double)clock() / (double)CLOCKS_PER_SEC;
}

static const struct dom_sys_vtable g_sys_stub = {
    DOM_SYS_API_VERSION,
    sys_init,
    sys_shutdown,
    get_program_root,
    get_data_root,
    get_state_root,
    fs_mkdir_p,
    fs_exists,
    fs_remove,
    spawn_process,
    ticks,
    seconds
};

const struct dom_sys_vtable* dom_plat_sys_choose_best(void)
{
    return &g_sys_stub;
}
