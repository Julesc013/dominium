#include <cstdio>
#include <string>

#include "dom_setup_install_manifest.h"
#include "dom_setup_paths.h"
#include "dom_setup_fs.h"

int main(void)
{
    DomInstallManifest manifest;
    manifest.schema_version = 1;
    manifest.install_id = "test-install";
    manifest.install_type = "portable";
    manifest.platform = dom_manifest_platform_tag();
    manifest.version = "0.1.0-test";
    manifest.created_at = "2025-12-06T00:00:00Z";
    manifest.created_by = "test";

    std::string tmp_root = dom_setup_path_join(dom_setup_get_cwd(), "tests_tmp_manifest");
    dom_fs_make_dirs(tmp_root);
    std::string path = dom_setup_path_join(tmp_root, "dominium_install.json");

    std::string err;
    if (!dom_manifest_write(path, manifest, err)) {
        std::printf("write failed: %s\n", err.c_str());
        return 1;
    }
    DomInstallManifest loaded;
    if (!dom_manifest_read(path, loaded, err)) {
        std::printf("read failed: %s\n", err.c_str());
        return 1;
    }
    if (loaded.install_id != manifest.install_id || loaded.install_type != manifest.install_type) {
        std::printf("roundtrip mismatch\n");
        return 1;
    }
    std::printf("manifest IO test passed\n");
    return 0;
}
