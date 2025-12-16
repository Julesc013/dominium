/*
FILE: include/dominium/_internal/dom_priv/launcher_internal/launcher_process.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/launcher_internal/launcher_process
RESPONSIBILITY: Defines the public contract for `launcher_process` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_LAUNCHER_PROCESS_H
#define DOM_LAUNCHER_PROCESS_H

#include "launcher_context.h"

#include <string>
#include <vector>

/* Constants for `launcher_process`. */
enum DomDisplayMode {
    DOM_DISPLAY_NONE = 0,
    DOM_DISPLAY_CLI  = 1,
    DOM_DISPLAY_TUI  = 2,
    DOM_DISPLAY_GUI  = 3
};

struct Instance {
    std::string instance_id;
    dom_shared::InstallInfo install;
    std::string role;
    DomDisplayMode display_mode;
    std::string universe_path;
    std::string profile_id;
    std::string mods_hash;
    int pid;
    std::string state;
    std::string log_path;
    double start_time_utc;
    double stop_time_utc;
};

struct RuntimeCapabilities {
    std::string binary_id;
    std::string binary_version;
    std::string engine_version;
    std::vector<std::string> roles;
    std::vector<std::string> display_modes;
    std::vector<int> save_versions;
    std::vector<int> content_pack_versions;
};

/* Purpose: Instance start.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
Instance start_instance(const LauncherContext &ctx,
                        const dom_shared::InstallInfo &install,
                        const std::string &role,
                        DomDisplayMode display,
                        const std::string &universe_path,
                        const std::string &profile_id,
                        const std::string &mods_hash);

/* Purpose: Instance stop.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool stop_instance(const std::string &instance_id);
/* Purpose: Instance get.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
Instance *get_instance(const std::string &instance_id);
/* Purpose: Instances list.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
std::vector<Instance> list_instances();
/* Purpose: Capabilities query runtime.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
RuntimeCapabilities query_runtime_capabilities(const dom_shared::InstallInfo &install);

#endif /* DOM_LAUNCHER_PROCESS_H */
