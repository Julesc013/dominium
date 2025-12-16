/*
FILE: source/dominium/setup/dom_setup_app.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/dom_setup_app
RESPONSIBILITY: Defines internal contract for `dom_setup_app`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
