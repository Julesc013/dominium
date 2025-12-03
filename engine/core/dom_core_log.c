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
