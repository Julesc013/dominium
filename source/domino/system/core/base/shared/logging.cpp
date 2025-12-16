/*
FILE: source/domino/system/core/base/shared/logging.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/core/base/shared/logging
RESPONSIBILITY: Implements `logging`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_shared/logging.h"

#include <cstdio>
#include <cstdarg>
#include <ctime>
#include <string>

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#endif

namespace dom_shared {

static LogLevel g_min_level = LOG_INFO;
static FILE* g_log_file = stdout;
static long g_lock = 0;

static void lock_log()
{
#ifdef _WIN32
    while (InterlockedCompareExchange(&g_lock, 1, 0) != 0) {
        Sleep(0);
    }
#else
    while (__sync_val_compare_and_swap(&g_lock, 0, 1) != 0) {
        /* spin */ ;
    }
#endif
}

static void unlock_log()
{
#ifdef _WIN32
    InterlockedExchange(&g_lock, 0);
#else
    __sync_val_compare_and_swap(&g_lock, 1, 0);
#endif
}

static const char* level_to_str(LogLevel lvl)
{
    switch (lvl) {
    case LOG_TRACE: return "TRACE";
    case LOG_DEBUG: return "DEBUG";
    case LOG_INFO:  return "INFO";
    case LOG_WARN:  return "WARN";
    case LOG_ERROR: return "ERROR";
    }
    return "INFO";
}

void log_set_min_level(LogLevel level)
{
    g_min_level = level;
}

void log_set_output_file(const std::string& path)
{
    lock_log();
    if (g_log_file && g_log_file != stdout) {
        std::fclose(g_log_file);
        g_log_file = stdout;
    }
    if (!path.empty()) {
        FILE* f = std::fopen(path.c_str(), "a");
        if (f) {
            g_log_file = f;
        }
    }
    unlock_log();
}

static void log_emit(LogLevel lvl, const char* fmt, va_list ap)
{
    if (lvl < g_min_level) return;

    char msg_buf[1024];
#ifdef _WIN32
    int n = _vsnprintf(msg_buf, sizeof(msg_buf) - 1, fmt, ap);
#else
    int n = vsnprintf(msg_buf, sizeof(msg_buf), fmt, ap);
#endif
    if (n < 0) {
        return;
    }
    msg_buf[sizeof(msg_buf) - 1] = '\0';

    std::time_t t = std::time(0);
#ifdef _WIN32
    std::tm tmv;
    localtime_s(&tmv, &t);
#else
    std::tm tmv;
    localtime_r(&t, &tmv);
#endif
    char ts_buf[64];
    std::strftime(ts_buf, sizeof(ts_buf), "%Y-%m-%d %H:%M:%S", &tmv);

    lock_log();
    std::fprintf(g_log_file ? g_log_file : stdout, "[%s][%s] %s\n", ts_buf, level_to_str(lvl), msg_buf);
    std::fflush(g_log_file ? g_log_file : stdout);
    unlock_log();
}

void log_trace(const char* fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    log_emit(LOG_TRACE, fmt, ap);
    va_end(ap);
}

void log_debug(const char* fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    log_emit(LOG_DEBUG, fmt, ap);
    va_end(ap);
}

void log_info(const char* fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    log_emit(LOG_INFO, fmt, ap);
    va_end(ap);
}

void log_warn(const char* fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    log_emit(LOG_WARN, fmt, ap);
    va_end(ap);
}

void log_error(const char* fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    log_emit(LOG_ERROR, fmt, ap);
    va_end(ap);
}

} // namespace dom_shared
