/*
FILE: source/domino/system/plat/null/dom_plat_term_stub.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/null/dom_plat_term_stub
RESPONSIBILITY: Implements `dom_plat_term_stub`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dominium/dom_plat_term.h"

#include <stdio.h>

static int term_attach(void) { return 0; }
static void term_detach(void) { }
static int term_write(const char* s, size_t n)
{
    return (int)fwrite(s, 1, n, stdout);
}
static int term_read_line(char* buf, size_t cap)
{
    if (!buf || cap == 0) return -1;
    if (!fgets(buf, (int)cap, stdin)) return -1;
    return 0;
}
static int term_enter_alt(void) { return 0; }
static void term_leave_alt(void) { }
static void term_set_cursor(int x, int y) { (void)x; (void)y; }
static void term_set_attr(uint32_t attr_flags) { (void)attr_flags; }

static const struct dom_term_vtable g_term_stub = {
    DOM_TERM_API_VERSION,
    term_attach,
    term_detach,
    term_write,
    term_read_line,
    term_enter_alt,
    term_leave_alt,
    term_set_cursor,
    term_set_attr
};

const struct dom_term_vtable* dom_plat_term_probe(const struct dom_sys_vtable* sys)
{
    (void)sys;
    return &g_term_stub;
}
