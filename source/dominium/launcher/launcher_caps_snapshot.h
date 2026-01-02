/*
FILE: source/dominium/launcher/launcher_caps_snapshot.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher / caps_snapshot
RESPONSIBILITY: Deterministic capability snapshot model + TLV/text rendering.
ALLOWED DEPENDENCIES: launcher core TLV helpers, Domino caps, and C++98 standard headers.
FORBIDDEN DEPENDENCIES: UI/toolkit headers and non-deterministic data sources.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions required.
DETERMINISM: Stable ordering; no locale or strerror.
*/
#ifndef DOMINIUM_LAUNCHER_CAPS_SNAPSHOT_H
#define DOMINIUM_LAUNCHER_CAPS_SNAPSHOT_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
#include "domino/profile.h"
}

namespace dom {

enum { LAUNCHER_CAPS_TLV_VERSION = 1u };

enum LauncherCapsTlvTag {
    LAUNCHER_CAPS_TLV_TAG_BUILD_ID = 2u,
    LAUNCHER_CAPS_TLV_TAG_GIT_HASH = 3u,
    LAUNCHER_CAPS_TLV_TAG_VERSION_STRING = 4u,
    LAUNCHER_CAPS_TLV_TAG_OS_FAMILY = 5u,
    LAUNCHER_CAPS_TLV_TAG_OS_VERSION_MAJOR = 6u,
    LAUNCHER_CAPS_TLV_TAG_OS_VERSION_MINOR = 7u,
    LAUNCHER_CAPS_TLV_TAG_CPU_ARCH = 8u,
    LAUNCHER_CAPS_TLV_TAG_RAM_CLASS = 9u,
    LAUNCHER_CAPS_TLV_TAG_BACKEND = 10u,
    LAUNCHER_CAPS_TLV_TAG_SELECTED_BACKEND = 11u,
    LAUNCHER_CAPS_TLV_TAG_PROVIDER_NET = 12u,
    LAUNCHER_CAPS_TLV_TAG_PROVIDER_TRUST = 13u,
    LAUNCHER_CAPS_TLV_TAG_PROVIDER_KEYCHAIN = 14u,
    LAUNCHER_CAPS_TLV_TAG_PROVIDER_CONTENT = 15u,
    LAUNCHER_CAPS_TLV_TAG_SUPPORTS_STDOUT_CAPTURE = 16u,
    LAUNCHER_CAPS_TLV_TAG_SUPPORTS_FILE_PICKER = 17u,
    LAUNCHER_CAPS_TLV_TAG_SUPPORTS_OPEN_FOLDER = 18u,
    LAUNCHER_CAPS_TLV_TAG_SUPPORTS_TLS = 19u,
    LAUNCHER_CAPS_TLV_TAG_FS_PERM_MODEL = 20u,
    LAUNCHER_CAPS_TLV_TAG_MAX_PATH_LEN = 21u
};

enum LauncherCapsBackendTlvTag {
    LAUNCHER_CAPS_BACKEND_TLV_TAG_SUBSYS_ID = 1u,
    LAUNCHER_CAPS_BACKEND_TLV_TAG_SUBSYS_NAME = 2u,
    LAUNCHER_CAPS_BACKEND_TLV_TAG_BACKEND_NAME = 3u,
    LAUNCHER_CAPS_BACKEND_TLV_TAG_DET_GRADE = 4u,
    LAUNCHER_CAPS_BACKEND_TLV_TAG_PERF_CLASS = 5u,
    LAUNCHER_CAPS_BACKEND_TLV_TAG_PRIORITY = 6u
};

enum LauncherCapsSelectionTlvTag {
    LAUNCHER_CAPS_SEL_TLV_TAG_SUBSYS_ID = 1u,
    LAUNCHER_CAPS_SEL_TLV_TAG_SUBSYS_NAME = 2u,
    LAUNCHER_CAPS_SEL_TLV_TAG_BACKEND_NAME = 3u,
    LAUNCHER_CAPS_SEL_TLV_TAG_DET_GRADE = 4u,
    LAUNCHER_CAPS_SEL_TLV_TAG_PERF_CLASS = 5u,
    LAUNCHER_CAPS_SEL_TLV_TAG_PRIORITY = 6u,
    LAUNCHER_CAPS_SEL_TLV_TAG_OVERRIDE = 7u
};

enum LauncherCapsFsPermModel {
    LAUNCHER_CAPS_FS_PERM_UNKNOWN = 0u,
    LAUNCHER_CAPS_FS_PERM_USER = 1u,
    LAUNCHER_CAPS_FS_PERM_SYSTEM = 2u,
    LAUNCHER_CAPS_FS_PERM_MIXED = 3u
};

enum LauncherCapsRamClass {
    LAUNCHER_CAPS_RAM_UNKNOWN = 0u,
    LAUNCHER_CAPS_RAM_LT_4GB = 1u,
    LAUNCHER_CAPS_RAM_4_8GB = 2u,
    LAUNCHER_CAPS_RAM_8_16GB = 3u,
    LAUNCHER_CAPS_RAM_16_32GB = 4u,
    LAUNCHER_CAPS_RAM_32GB_PLUS = 5u
};

struct LauncherCapsBackend {
    u32 subsystem_id;
    std::string subsystem_name;
    std::string backend_name;
    u32 determinism;
    u32 perf_class;
    u32 priority;

    LauncherCapsBackend();
};

struct LauncherCapsSelection {
    u32 subsystem_id;
    std::string subsystem_name;
    std::string backend_name;
    u32 determinism;
    u32 perf_class;
    u32 priority;
    u32 chosen_by_override;

    LauncherCapsSelection();
};

struct LauncherCapsSnapshot {
    u32 schema_version;
    std::string version_string;
    std::string build_id;
    std::string git_hash;

    u32 os_family;
    u32 os_version_major;
    u32 os_version_minor;
    u32 cpu_arch;
    u32 ram_class;

    u32 provider_net;
    u32 provider_trust;
    u32 provider_keychain;
    u32 provider_content;

    u32 supports_stdout_capture;
    u32 supports_file_picker;
    u32 supports_open_folder;
    u32 supports_tls;
    u32 fs_perm_model;
    u32 max_path_len;

    std::vector<LauncherCapsBackend> backends;
    std::vector<LauncherCapsSelection> selections;

    LauncherCapsSnapshot();
};

bool launcher_caps_snapshot_build(const dom_profile* profile,
                                  LauncherCapsSnapshot& out_snapshot,
                                  std::string& out_error);

bool launcher_caps_snapshot_to_tlv_bytes(const LauncherCapsSnapshot& snapshot,
                                         std::vector<unsigned char>& out_bytes);

std::string launcher_caps_snapshot_to_text(const LauncherCapsSnapshot& snapshot);

bool launcher_caps_snapshot_write_tlv(const LauncherCapsSnapshot& snapshot,
                                      const std::string& path,
                                      std::string& out_error);

bool launcher_caps_snapshot_write_text(const LauncherCapsSnapshot& snapshot,
                                       const std::string& path,
                                       std::string& out_error);

} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CAPS_SNAPSHOT_H */
