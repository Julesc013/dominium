// dom_main runtime application entry helpers.
#ifndef DOM_MAIN_RUNTIME_APP_H
#define DOM_MAIN_RUNTIME_APP_H

#include <string>

struct RuntimeConfig {
    std::string role;          /* client | server | tool */
    std::string display;       /* none | cli | tui | gui | auto */
    std::string universe_path;
    std::string launcher_session_id;
    std::string launcher_instance_id;
    std::string launcher_integration; /* auto | off */
};

int runtime_print_version();
int runtime_print_capabilities();
int runtime_run(const RuntimeConfig &cfg);

#endif /* DOM_MAIN_RUNTIME_APP_H */
