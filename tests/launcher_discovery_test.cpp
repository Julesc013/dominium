#include <cstdio>
#include <string>
#include <vector>
#include <sys/stat.h>
#ifdef _WIN32
#include <direct.h>
#endif

#include "launcher_discovery.h"
#include "launcher_context.h"
#include "dom_shared/manifest_install.h"
#include "dom_shared/os_paths.h"
#include "dom_shared/uuid.h"
#include "dom_shared/logging.h"

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
    bool ok = false;
    std::string err;
    write_install_manifest(info, ok, err);
    return ok;
}

int main(void)
{
    std::string tmp_root = os_path_join(os_get_default_portable_install_root(), "tests_tmp_launcher_discovery");
    create_fake_install(tmp_root, "launcher-test");

    std::vector<InstallInfo> installs = discover_installs(get_launcher_context());
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
