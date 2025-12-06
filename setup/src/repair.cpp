#include "dom_setup_cli.h"
#include "dom_setup_install_manifest.h"
#include "dom_setup_paths.h"
#include "dom_setup_fs.h"

#include <cstdio>
#include <string>

static void ensure_layout(const std::string &root)
{
    dom_fs_make_dirs(dom_setup_path_join(root, "bin"));
    dom_fs_make_dirs(dom_setup_path_join(root, "mods"));
    dom_fs_make_dirs(dom_setup_path_join(root, "data"));
    dom_fs_make_dirs(dom_setup_path_join(root, "launcher"));
}

int dom_setup_cmd_repair(const std::string &install_root)
{
    DomInstallManifest manifest;
    std::string err;
    if (!dom_manifest_read(dom_setup_path_join(install_root, "dominium_install.json"), manifest, err)) {
        std::printf("Manifest read failed: %s\n", err.c_str());
        return 1;
    }
    ensure_layout(install_root);

    // Placeholder verification: if placeholder missing, recreate.
    std::string placeholder = dom_setup_path_join(install_root, "README_INSTALL.txt");
    if (!dom_fs_path_exists(placeholder)) {
        FILE *f = std::fopen(placeholder.c_str(), "wb");
        if (f) {
            std::fprintf(f, "Restored placeholder during repair\n");
            std::fclose(f);
        }
    }

    std::printf("Repair completed for %s (%s)\n",
                install_root.c_str(),
                manifest.install_id.c_str());
    return 0;
}
