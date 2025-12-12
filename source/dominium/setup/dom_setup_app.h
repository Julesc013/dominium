#ifndef DOM_SETUP_APP_H
#define DOM_SETUP_APP_H

#include <string>

#include "dom_paths.h"

namespace dom {

struct SetupConfig {
    std::string home;
    std::string action;
    std::string target;
};

class DomSetupApp {
public:
    DomSetupApp();
    ~DomSetupApp();

    bool init_from_cli(const SetupConfig &cfg);
    void run();
    void shutdown();

private:
    bool perform_action(const SetupConfig &cfg);

    Paths m_paths;
};

} // namespace dom

#endif
