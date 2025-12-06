#include <cstdio>
#include <string>
#include <vector>

#include "launcher_discovery.h"
#include "dom_setup_install_manifest.h"
#include "dom_setup_paths.h"
#include "dom_setup_fs.h"

static bool create_fake_install(const std::string &root, const std::string &install_id)
{
    dom_fs_make_dirs(root);
    DomInstallManifest manifest;
    manifest.schema_version = 1;
    manifest.install_id = install_id;
    manifest.install_type = "portable";
    manifest.platform = dom_manifest_platform_tag();
    manifest.version = "0.0.test";
    manifest.created_at = "2025-12-06T00:00:00Z";
    manifest.created_by = "test";
    std::string err;
    return dom_manifest_write(dom_setup_path_join(root, "dominium_install.json"), manifest, err);
}

int main(void)
{
    std::string tmp_root = dom_setup_path_join(dom_setup_get_cwd(), "tests_tmp_launcher_discovery");
    create_fake_install(tmp_root, "launcher-test");

    std::vector<LauncherInstall> installs;
    if (!launcher_discover_installs(installs)) {
        std::printf("discovery failed\n");
        return 1;
    }
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
