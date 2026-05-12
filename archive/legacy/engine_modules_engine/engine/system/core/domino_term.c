/*
FILE: source/domino/system/core/domino_term.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/core/domino_term
RESPONSIBILITY: Implements `domino_term`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/sys.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct domino_term_context {
    domino_sys_context* sys;
    int                 use_alt;
};

int domino_term_init(domino_sys_context* sys,
                     const domino_term_desc* desc,
                     domino_term_context** out_term)
{
    domino_term_context* term;
    if (!out_term) return -1;
    *out_term = NULL;
    term = (domino_term_context*)malloc(sizeof(domino_term_context));
    if (!term) return -1;
    term->sys = sys;
    term->use_alt = desc ? desc->use_alternate_buffer : 0;
    *out_term = term;
    (void)sys;
    return 0;
}

void domino_term_shutdown(domino_term_context* term)
{
    if (!term) return;
    free(term);
}

int domino_term_write(domino_term_context* term,
                      const char* bytes,
                      size_t len)
{
    size_t written;
    (void)term;
    if (!bytes) return -1;
    written = fwrite(bytes, 1, len, stdout);
    fflush(stdout);
    return (written == len) ? 0 : -1;
}

int domino_term_read_line(domino_term_context* term,
                          char* buf,
                          size_t cap)
{
    (void)term;
    if (!buf || cap == 0) return -1;
    if (fgets(buf, (int)cap, stdin) == NULL) {
        return -1;
    }
    /* strip newline */
    {
        size_t n = strlen(buf);
        if (n > 0 && (buf[n - 1] == '\n' || buf[n - 1] == '\r')) {
            buf[n - 1] = '\0';
            if (n > 1 && buf[n - 2] == '\r') {
                buf[n - 2] = '\0';
            }
        }
    }
    return 0;
}
