#include "dominium/dom_core.h"

#include <stdio.h>

void dom_log(enum dom_log_level lvl, const char* category, const char* msg)
{
    const char* lvl_str = "INFO";
    switch (lvl) {
    case DOM_LOG_DEBUG: lvl_str = "DEBUG"; break;
    case DOM_LOG_INFO:  lvl_str = "INFO"; break;
    case DOM_LOG_WARN:  lvl_str = "WARN"; break;
    case DOM_LOG_ERROR: lvl_str = "ERROR"; break;
    default: break;
    }
    if (!category) category = "core";
    if (!msg) msg = "";
    printf("[%s] %s: %s\n", lvl_str, category, msg);
}
