#include <cstdio>
#include <string>
#include <sys/stat.h>
#ifdef _WIN32
#include <direct.h>
#endif

#include "dom_shared/manifest_install.h"
#include "dom_shared/os_paths.h"

int main(void)
{
    InstallInfo info;
    info.install_id = "test-install";
    info.install_type = "portable";
    info.platform = os_get_platform_id();
    info.version = "0.1.0-test";
    info.root_path = os_get_default_portable_install_root() + "/tests_tmp_manifest";

    bool ok = false;
    std::string err;
    /* ensure directory exists */
#ifdef _WIN32
    _mkdir(info.root_path.c_str());
#else
    mkdir(info.root_path.c_str(), 0755);
#endif

    write_install_manifest(info, ok, err);
    if (!ok) {
        std::printf("write failed: %s\n", err.c_str());
        return 1;
    }
    InstallInfo loaded = parse_install_manifest(info.root_path, ok, err);
    if (!ok) {
        std::printf("read failed: %s\n", err.c_str());
        return 1;
    }
    if (loaded.install_id != info.install_id || loaded.install_type != info.install_type) {
        std::printf("roundtrip mismatch\n");
        return 1;
    }
    std::printf("manifest IO test passed\n");
    return 0;
}
