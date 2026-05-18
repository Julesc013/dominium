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

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_shared_string {
    const char* data;
    size_t size;
} dom_shared_string;

typedef struct dom_shared_string_list {
    const dom_shared_string* items;
    size_t count;
} dom_shared_string_list;

dom_shared_string os_get_executable_path(void);       // full path to this executable
dom_shared_string os_get_executable_directory(void);  // directory containing this executable

dom_shared_string os_get_platform_id(void);           // "win_nt" | "linux" | "mac"

// Default install roots for different modes
dom_shared_string os_get_default_per_user_install_root(void);
/* Purpose: Root os get default system install.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
dom_shared_string os_get_default_system_install_root(void);
dom_shared_string os_get_default_portable_install_root(void); // usually current dir

// Data roots for launcher and game
dom_shared_string os_get_per_user_launcher_data_root(void);
/* Purpose: Root os get per user game data.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
dom_shared_string os_get_per_user_game_data_root(void);

// Default install root search locations for discovery
dom_shared_string_list os_get_default_install_roots(void);

/* Purpose: Exists os ensure directory.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
int os_ensure_directory_exists(const char* path);
/* Purpose: Exists os file.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
int os_file_exists(const char* path);
/* Purpose: Exists os directory.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
int os_directory_exists(const char* path);

// Join path segments with platform-appropriate separators
dom_shared_string os_path_join(const char* a, const char* b);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif
