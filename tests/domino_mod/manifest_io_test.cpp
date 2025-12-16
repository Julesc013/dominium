/*
FILE: tests/domino_mod/manifest_io_test.cpp
MODULE: Repository
LAYER / SUBSYSTEM: tests/domino_mod
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <cstdio>
#include <string>
#include <sys/stat.h>
#ifdef _WIN32
#include <direct.h>
#endif

#include "dom_shared/manifest_install.h"
#include "dom_shared/os_paths.h"

using namespace dom_shared;

int main(void)
{
    InstallInfo info;
    info.install_id = "test-install";
    info.install_type = "portable";
    info.platform = os_get_platform_id();
    info.version = "0.1.0-test";
    info.root_path = os_get_default_portable_install_root() + "/tests_tmp_manifest";

    /* ensure directory exists */
#ifdef _WIN32
    _mkdir(info.root_path.c_str());
#else
    mkdir(info.root_path.c_str(), 0755);
#endif

    if (!write_install_manifest(info)) {
        std::printf("write failed\n");
        return 1;
    }
    InstallInfo loaded;
    if (!parse_install_manifest(info.root_path, loaded)) {
        std::printf("read failed\n");
        return 1;
    }
    if (loaded.install_id != info.install_id || loaded.install_type != info.install_type) {
        std::printf("roundtrip mismatch\n");
        return 1;
    }
    std::printf("manifest IO test passed\n");
    return 0;
}
