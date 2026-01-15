/*
FILE: include/dominium/_internal/dom_priv/dom_shared/os_paths.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/dom_shared/os_paths
RESPONSIBILITY: Defines the public contract for `os_paths` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SHARED_OS_PATHS_H
#define DOM_SHARED_OS_PATHS_H

#include <string>
#include <vector>

namespace dom_shared {

std::string os_get_executable_path();       // full path to this executable
std::string os_get_executable_directory();  // directory containing this executable

std::string os_get_platform_id();           // "win_nt" | "linux" | "mac"

// Default install roots for different modes
std::string os_get_default_per_user_install_root();
/* Purpose: Root os get default system install.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
std::string os_get_default_system_install_root();
std::string os_get_default_portable_install_root(); // usually current dir

// Data roots for launcher and game
std::string os_get_per_user_launcher_data_root();
/* Purpose: Root os get per user game data.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
std::string os_get_per_user_game_data_root();

// Default install root search locations for discovery
std::vector<std::string> os_get_default_install_roots();

/* Purpose: Exists os ensure directory.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool os_ensure_directory_exists(const std::string& path);
/* Purpose: Exists os file.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool os_file_exists(const std::string& path);
/* Purpose: Exists os directory.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool os_directory_exists(const std::string& path);

// Join path segments with platform-appropriate separators
std::string os_path_join(const std::string& a, const std::string& b);

} // namespace dom_shared

#endif
