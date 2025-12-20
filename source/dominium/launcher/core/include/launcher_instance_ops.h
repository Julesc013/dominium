/*
FILE: source/dominium/launcher/core/include/launcher_instance_ops.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / instance_ops
RESPONSIBILITY: Instance root operations (create/clone/template/delete/state markers) with staging/previous semantics and audit emission.
ALLOWED DEPENDENCIES: C++98 standard headers and `include/domino/**` base types; launcher core service facade types.
FORBIDDEN DEPENDENCIES: OS headers, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions required.
DETERMINISM: All outputs are deterministic given explicit inputs and injected services (FS/time); no filesystem enumeration ordering is relied upon.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_OPS_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_OPS_H

#include <string>

extern "C" {
#include "launcher_core_api.h"
}

#include "launcher_instance.h"

namespace dom {
namespace launcher_core {

struct LauncherAuditLog; /* forward-declared; see launcher_audit.h */

struct LauncherInstancePaths {
    std::string state_root;
    std::string instances_root;
    std::string instance_root;

    std::string manifest_path;

    std::string config_root;
    std::string config_file_path; /* config/config.tlv */

    std::string saves_root;
    std::string mods_root;
    std::string content_root;
    std::string cache_root;
    std::string logs_root;
    std::string staging_root;
    std::string staging_manifest_path; /* staging/manifest.tlv */
    std::string previous_root;

    LauncherInstancePaths();
};

LauncherInstancePaths launcher_instance_paths_make(const std::string& state_root,
                                                   const std::string& instance_id);

/* Root layout helpers. */
bool launcher_instance_ensure_root_layout(const launcher_services_api_v1* services,
                                          const LauncherInstancePaths& paths);

/* Instance lifecycle operations (no in-place mutation of live instances; uses staging/previous).
 * `state_root_override`: when non-empty, overrides FS get_path(LAUNCHER_FS_PATH_STATE).
 * `audit`: optional; when provided, operation emits deterministic audit reasons.
 */

bool launcher_instance_create_instance(const launcher_services_api_v1* services,
                                       const LauncherInstanceManifest& desired_manifest,
                                       const std::string& state_root_override,
                                       LauncherInstanceManifest& out_created_manifest,
                                       LauncherAuditLog* audit);

bool launcher_instance_delete_instance(const launcher_services_api_v1* services,
                                       const std::string& instance_id,
                                       const std::string& state_root_override,
                                       LauncherAuditLog* audit);

bool launcher_instance_clone_instance(const launcher_services_api_v1* services,
                                      const std::string& source_instance_id,
                                      const std::string& new_instance_id,
                                      const std::string& state_root_override,
                                      LauncherInstanceManifest& out_created_manifest,
                                      LauncherAuditLog* audit);

bool launcher_instance_template_instance(const launcher_services_api_v1* services,
                                         const std::string& source_instance_id,
                                         const std::string& new_instance_id,
                                         const std::string& state_root_override,
                                         LauncherInstanceManifest& out_created_manifest,
                                         LauncherAuditLog* audit);

bool launcher_instance_mark_known_good(const launcher_services_api_v1* services,
                                       const std::string& instance_id,
                                       const std::string& state_root_override,
                                       LauncherInstanceManifest& out_updated_manifest,
                                       LauncherAuditLog* audit);

bool launcher_instance_mark_broken(const launcher_services_api_v1* services,
                                   const std::string& instance_id,
                                   const std::string& state_root_override,
                                   LauncherInstanceManifest& out_updated_manifest,
                                   LauncherAuditLog* audit);

enum LauncherInstanceExportMode {
    LAUNCHER_INSTANCE_EXPORT_DEFINITION_ONLY = 1u,
    LAUNCHER_INSTANCE_EXPORT_FULL_BUNDLE = 2u
};

enum LauncherInstanceImportMode {
    LAUNCHER_INSTANCE_IMPORT_DEFINITION_ONLY = 1u,
    LAUNCHER_INSTANCE_IMPORT_FULL_BUNDLE = 2u
};

bool launcher_instance_export_instance(const launcher_services_api_v1* services,
                                       const std::string& instance_id,
                                       const std::string& export_root,
                                       const std::string& state_root_override,
                                       u32 export_mode,
                                       LauncherAuditLog* audit);

bool launcher_instance_import_instance(const launcher_services_api_v1* services,
                                       const std::string& import_root,
                                       const std::string& new_instance_id,
                                       const std::string& state_root_override,
                                       u32 import_mode,
                                       u32 safe_mode,
                                       LauncherInstanceManifest& out_created_manifest,
                                       LauncherAuditLog* audit);

/* Lightweight helpers used by tests and higher layers. */
bool launcher_instance_load_manifest(const launcher_services_api_v1* services,
                                     const std::string& instance_id,
                                     const std::string& state_root_override,
                                     LauncherInstanceManifest& out_manifest);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_OPS_H */
