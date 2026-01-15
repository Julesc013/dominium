/*
FILE: source/dominium/launcher/core/include/launcher_pack_ops.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (ecosystem) / pack_ops
RESPONSIBILITY: Instance-scoped pack install/remove/update/enable operations implemented via the transaction engine (atomic, auditable).
ALLOWED DEPENDENCIES: C++98 standard headers and launcher core instance/tx/audit/pack resolver models; services facade.
FORBIDDEN DEPENDENCIES: OS headers, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; detailed reasons emitted to audit and optionally returned in out_error.
DETERMINISM: No filesystem enumeration ordering; dependency resolution and load-order are deterministic.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_PACK_OPS_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_PACK_OPS_H

#include <string>

extern "C" {
#include "launcher_core_api.h"
}

#include "launcher_instance.h"

namespace dom {
namespace launcher_core {

struct LauncherAuditLog; /* forward-declared; see launcher_audit.h */

/* Installs a pack-like artifact (type pack/mod/runtime) into an instance.
 * Refuses when dependency resolution fails or conflicts are violated.
 */
bool launcher_pack_install_pack_to_instance(const launcher_services_api_v1* services,
                                            const std::string& instance_id,
                                            const LauncherContentEntry& pack_entry,
                                            const std::string& state_root_override,
                                            LauncherInstanceManifest& out_updated_manifest,
                                            LauncherAuditLog* audit,
                                            std::string* out_error);

/* Removes a pack-like entry from an instance.
 * Refuses when the removal would violate required dependencies of remaining enabled packs.
 */
bool launcher_pack_remove_pack_from_instance(const launcher_services_api_v1* services,
                                             const std::string& instance_id,
                                             u32 content_type,
                                             const std::string& pack_id,
                                             const std::string& state_root_override,
                                             LauncherInstanceManifest& out_updated_manifest,
                                             LauncherAuditLog* audit,
                                             std::string* out_error);

/* Updates a pack-like entry to a new version/hash (respects update_policy).
 * `override_prompt`: when non-zero, allows updating entries with update_policy=prompt.
 */
bool launcher_pack_update_pack_in_instance(const launcher_services_api_v1* services,
                                           const std::string& instance_id,
                                           const LauncherContentEntry& new_entry,
                                           const std::string& state_root_override,
                                           u32 override_prompt,
                                           LauncherInstanceManifest& out_updated_manifest,
                                           LauncherAuditLog* audit,
                                           std::string* out_error);

/* Enables/disables a pack-like entry (per-instance only).
 * Refuses when disabling would violate required dependencies.
 */
bool launcher_pack_set_enabled_in_instance(const launcher_services_api_v1* services,
                                           const std::string& instance_id,
                                           u32 content_type,
                                           const std::string& pack_id,
                                           u32 enabled,
                                           const std::string& state_root_override,
                                           LauncherInstanceManifest& out_updated_manifest,
                                           LauncherAuditLog* audit,
                                           std::string* out_error);

/* Sets/clears an explicit load-order override (per instance).
 * `has_override`: 0 clears the override; 1 sets it to `override_value`.
 */
bool launcher_pack_set_order_override_in_instance(const launcher_services_api_v1* services,
                                                  const std::string& instance_id,
                                                  u32 content_type,
                                                  const std::string& pack_id,
                                                  u32 has_override,
                                                  i32 override_value,
                                                  const std::string& state_root_override,
                                                  LauncherInstanceManifest& out_updated_manifest,
                                                  LauncherAuditLog* audit,
                                                  std::string* out_error);

/* Pre-launch validation: deterministic resolution + simulation safety + prelaunch tasks.
 * Intended to be called by the launcher before spawning the game process.
 */
bool launcher_pack_prelaunch_validate_instance(const launcher_services_api_v1* services,
                                               const std::string& instance_id,
                                               const std::string& state_root_override,
                                               LauncherAuditLog* audit,
                                               std::string* out_error);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_PACK_OPS_H */

