#ifndef DOM_SHARED_LOGGING_H
#define DOM_SHARED_LOGGING_H

#include <string>

namespace dom_shared {

enum LogLevel {
    LOG_TRACE,
    LOG_DEBUG,
    LOG_INFO,
    LOG_WARN,
    LOG_ERROR
};

void log_set_min_level(LogLevel level);
void log_set_output_file(const std::string& path); // optional; stdout by default

void log_trace(const char* fmt, ...);
void log_debug(const char* fmt, ...);
void log_info(const char* fmt, ...);
void log_warn(const char* fmt, ...);
void log_error(const char* fmt, ...);

} // namespace dom_shared

#endif
