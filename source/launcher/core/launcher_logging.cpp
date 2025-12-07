#include "launcher_logging.h"
#include "dom_shared/logging.h"

using namespace dom_shared;

void launcher_log_info(const std::string &msg) { log_info("[launcher] %s", msg.c_str()); }
void launcher_log_warn(const std::string &msg) { log_warn("[launcher] %s", msg.c_str()); }
void launcher_log_error(const std::string &msg) { log_error("[launcher] %s", msg.c_str()); }
