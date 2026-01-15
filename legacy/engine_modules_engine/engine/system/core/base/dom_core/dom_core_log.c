/*
FILE: source/domino/system/core/base/dom_core/dom_core_log.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/core/base/dom_core/dom_core_log
RESPONSIBILITY: Implements `dom_core_log`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_core_log.h"
#include <stdarg.h>
#include <stdio.h>

static DomLogSinkFn g_sink = 0;
static void *g_sink_ud = 0;

void dom_log_init(DomLogSinkFn sink, void *user_data)
{
    g_sink = sink;
    g_sink_ud = user_data;
}

void dom_log_shutdown(void)
{
    g_sink = 0;
    g_sink_ud = 0;
}

void dom_log_message(DomLogLevel level, const char *file, int line, const char *fmt, ...)
{
    char buffer[256];
    (void)level;
    (void)file;
    (void)line;

    if (!fmt) return;

    {
        va_list args;
        va_start(args, fmt);
        vsnprintf(buffer, sizeof(buffer), fmt, args);
        va_end(args);
    }

    if (g_sink) {
        g_sink(level, file, line, buffer, g_sink_ud);
    } else {
        fprintf(stderr, "%s\n", buffer);
    }
}
