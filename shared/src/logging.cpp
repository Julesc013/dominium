#include "dom_shared/logging.h"

#include <ctime>
#include <iostream>

static std::string timestamp_now()
{
    char buf[64];
    std::time_t t = std::time(0);
    std::tm tmv;
#ifdef _WIN32
    localtime_s(&tmv, &t);
#else
    localtime_r(&t, &tmv);
#endif
    std::strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", &tmv);
    return std::string(buf);
}

static void log_common(const char *level, const std::string &msg, std::ostream &os)
{
    os << "[" << timestamp_now() << "][" << level << "] " << msg << std::endl;
}

void log_info(const std::string &msg)
{
    log_common("INFO", msg, std::cout);
}

void log_warn(const std::string &msg)
{
    log_common("WARN", msg, std::cout);
}

void log_error(const std::string &msg)
{
    log_common("ERROR", msg, std::cerr);
}
