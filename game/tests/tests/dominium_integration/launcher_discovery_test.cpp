/*
FILE: tests/dominium_integration/launcher_discovery_test.cpp
MODULE: Repository
LAYER / SUBSYSTEM: tests/dominium_integration
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <cstdio>
#include <string>
#include <vector>
#include <sys/stat.h>
#ifdef _WIN32
#include <direct.h>
#endif

#include "dom_launcher/launcher_discovery.h"
#include "dom_launcher/launcher_context.h"
#include "dom_launcher/launcher_state.h"
#include "dom_shared/manifest_install.h"
#include "dom_shared/os_paths.h"
#include "dom_shared/uuid.h"
#include "dom_shared/logging.h"

using namespace dom_shared;
using namespace dom_launcher;

static bool create_fake_install(const std::string &root, const std::string &install_id)
{
    /* best-effort directory creation */
#ifdef _WIN32
    _mkdir(root.c_str());
#else
    mkdir(root.c_str(), 0755);
#endif
    InstallInfo info;
    info.install_id = install_id;
    info.install_type = "portable";
    info.platform = os_get_platform_id();
    info.version = "0.0.test";
    info.root_path = root;
    return write_install_manifest(info);
}

int main(void)
{
    std::string tmp_root = os_path_join(os_get_default_portable_install_root(), "tests_tmp_launcher_discovery");
    create_fake_install(tmp_root, "launcher-test");

    state_initialize();
    LauncherState& state = get_state();
    state.db.manual_install_paths.push_back(tmp_root);

    std::vector<InstallInfo> installs = discover_installs(state);
    bool found = false;
    for (size_t i = 0; i < installs.size(); ++i) {
        if (installs[i].install_id == "launcher-test") {
            found = true;
            break;
        }
    }
    if (!found) {
        std::printf("fake install not discovered\n");
        return 1;
    }
    std::printf("launcher discovery test passed\n");
    return 0;
}
