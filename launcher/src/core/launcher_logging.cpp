#include "launcher_logging.h"
#include "dom_shared/logging.h"

void launcher_log_info(const std::string &msg) { log_info("[launcher] " + msg); }
void launcher_log_warn(const std::string &msg) { log_warn("[launcher] " + msg); }
void launcher_log_error(const std::string &msg) { log_error("[launcher] " + msg); }
