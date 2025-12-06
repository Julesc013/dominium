// Lightweight logging helpers for dom_launcher (CLI/TUI/GUI).
#ifndef DOM_LAUNCHER_LOGGING_H
#define DOM_LAUNCHER_LOGGING_H

#include <string>

void launcher_log_info(const std::string &msg);
void launcher_log_error(const std::string &msg);

#endif /* DOM_LAUNCHER_LOGGING_H */
