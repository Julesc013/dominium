/*
FILE: source/dominium/launcher/core/include/launcher_instance_artifact_ops.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / instance_artifact_ops
RESPONSIBILITY: Install/update/remove/verify/repair/rollback operations implemented via the instance transaction engine (no in-place mutation).
ALLOWED DEPENDENCIES: C++98 standard headers and `include/domino/**` base types; launcher core instance/tx/audit models.
FORBIDDEN DEPENDENCIES: OS headers, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions required.
DETERMINISM: All outputs are deterministic given explicit inputs and injected services (FS/time); no filesystem enumeration ordering is relied upon.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_ARTIFACT_OPS_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_ARTIFACT_OPS_H

#include <string>

extern "C" {
#include "launcher_core_api.h"
}

#include "launcher_instance.h"

namespace dom {
namespace launcher_core {

struct LauncherAuditLog; /* forward-declared; see launcher_audit.h */

bool launcher_instance_install_artifact_to_instance(const launcher_services_api_v1* services,
                                                    const std::string& instance_id,
                                                    const LauncherContentEntry& artifact_entry,
                                                    const std::string& state_root_override,
                                                    LauncherInstanceManifest& out_updated_manifest,
                                                    LauncherAuditLog* audit);

bool launcher_instance_update_artifact_in_instance(const launcher_services_api_v1* services,
                                                   const std::string& instance_id,
                                                   const LauncherContentEntry& new_entry,
                                                   const std::string& state_root_override,
                                                   u32 override_prompt,
                                                   LauncherInstanceManifest& out_updated_manifest,
                                                   LauncherAuditLog* audit);

bool launcher_instance_remove_artifact_from_instance(const launcher_services_api_v1* services,
                                                     const std::string& instance_id,
                                                     u32 content_type,
                                                     const std::string& content_id,
                                                     const std::string& state_root_override,
                                                     LauncherInstanceManifest& out_updated_manifest,
                                                     LauncherAuditLog* audit);

bool launcher_instance_verify_or_repair(const launcher_services_api_v1* services,
                                        const std::string& instance_id,
                                        const std::string& state_root_override,
                                        u32 repair_mode,
                                        LauncherInstanceManifest& out_updated_manifest,
                                        LauncherAuditLog* audit);

bool launcher_instance_rollback_to_known_good(const launcher_services_api_v1* services,
                                              const std::string& instance_id,
                                              const std::string& state_root_override,
                                              const std::string& cause,
                                              u64 source_tx_id,
                                              LauncherInstanceManifest& out_restored_manifest,
                                              LauncherAuditLog* audit);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_ARTIFACT_OPS_H */

