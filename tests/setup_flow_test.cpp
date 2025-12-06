#include <cstdio>
#include <string>

#include "dom_setup_cli.h"
#include "dom_setup_paths.h"
#include "dom_setup_fs.h"

int main(void)
{
    std::string root = dom_setup_path_join(dom_setup_get_cwd(), "tests_tmp_setup_install");
    DomSetupInstallArgs args;
    args.mode = "portable";
    args.target = root;
    args.version = "0.0.test";

    if (dom_setup_cmd_install(args) != 0) {
        std::printf("install command failed\n");
        return 1;
    }
    if (dom_setup_cmd_info(root) != 0) {
        std::printf("info command failed\n");
        return 1;
    }
    if (dom_setup_cmd_repair(root) != 0) {
        std::printf("repair command failed\n");
        return 1;
    }
    // Clean up to avoid leaving temp directories around.
    dom_fs_remove_tree(root);
    std::printf("setup flow test passed\n");
    return 0;
}
