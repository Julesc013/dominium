/*
FILE: include/domino/pkg/repo.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / pkg/repo
RESPONSIBILITY: Defines the public contract for `repo` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_PKG_REPO_H
#define DOMINO_PKG_REPO_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Purpose: Role of a product binary in the repository.
 *
 * Notes:
 * - The current JSON parser maps string tokens to these values (e.g., `"game"` -> `DOM_PRODUCT_ROLE_GAME`).
 */
typedef enum dom_product_role {
    DOM_PRODUCT_ROLE_UNKNOWN = 0,
    DOM_PRODUCT_ROLE_GAME,
    DOM_PRODUCT_ROLE_LAUNCHER,
    DOM_PRODUCT_ROLE_SETUP,
    DOM_PRODUCT_ROLE_TOOL
} dom_product_role;

/* Purpose: OS family discriminator used by repository manifests and layout selection.
 *
 * Notes:
 * - This is a manifest/packaging classification and is distinct from `DomOSFamily` in `domino/platform.h`.
 */
typedef enum dom_os_family {
    DOM_OS_UNKNOWN = 0,
    DOM_OS_WINNT,
    DOM_OS_WIN9X,
    DOM_OS_WIN3X,
    DOM_OS_DOS,
    DOM_OS_MAC_CLASSIC,
    DOM_OS_MAC_CARBON,
    DOM_OS_MAC_COCOA,
    DOM_OS_POSIX,
    DOM_OS_SDL,
    DOM_OS_WEB,
    DOM_OS_CPM
} dom_os_family;

/* Purpose: CPU/VM architecture discriminator used by repository manifests and layout selection. */
typedef enum dom_arch {
    DOM_ARCH_UNKNOWN = 0,
    DOM_ARCH_X86_16,
    DOM_ARCH_X86_32,
    DOM_ARCH_X86_64,
    DOM_ARCH_ARM_32,
    DOM_ARCH_ARM_64,
    DOM_ARCH_M68K_32,
    DOM_ARCH_PPC_32,
    DOM_ARCH_PPC_64,
    DOM_ARCH_Z80_8,
    DOM_ARCH_WASM_32,
    DOM_ARCH_WASM_64
} dom_arch;

/* Purpose: Compatibility version tuple advertised by a product.
 *
 * Each field is a protocol/data-format version used for compatibility checks between products
 * (launcher, game, tools) and stored artifacts (saves, packs, replays).
 */
typedef struct dom_compat_profile {
    u16 save_format_version;
    u16 pack_format_version;
    u16 net_protocol_version;
    u16 replay_format_version;
    u16 launcher_proto_version;
    u16 tools_proto_version;
} dom_compat_profile;

#define DOM_PRODUCT_ID_MAX  32
#define DOM_VERSION_STR_MAX 32
#define DOM_EXEC_PATH_MAX   256

/* Purpose: Product descriptor loaded from a repository product manifest (POD).
 *
 * Fields:
 * - `product_id`: Manifest `product_id` string.
 * - `role`: Parsed `role` classification (see `dom_product_role`).
 * - `product_version` / `core_version`: String versions as represented in the manifest.
 * - `os_family` / `arch`: Parsed platform classification for the build.
 * - `exec_rel_path`: Relative executable path as represented in the manifest.
 * - `compat`: Compatibility version tuple.
 *
 * ABI/layout:
 * - String members are fixed-size, NUL-terminated buffers.
 */
typedef struct dom_product_info {
    char             product_id[DOM_PRODUCT_ID_MAX];
    dom_product_role role;
    char             product_version[DOM_VERSION_STR_MAX];
    char             core_version[DOM_VERSION_STR_MAX];
    dom_os_family    os_family;
    dom_arch         arch;
    char             exec_rel_path[DOM_EXEC_PATH_MAX];
    dom_compat_profile compat;
} dom_product_info;

/* Purpose: Resolve the repository root directory for the current process.
 *
 * Parameters:
 * - `buffer`: Output buffer receiving a NUL-terminated path (non-NULL).
 * - `max_len`: Capacity of `buffer` in bytes (must be > 0).
 *
 * Returns:
 * - `D_TRUE` on success.
 * - `D_FALSE` if arguments are invalid or the resolved path does not fit.
 *
 * Notes:
 * - Current behavior uses the `DOMINIUM_HOME` environment variable when set, otherwise `"."`.
 */
d_bool dom_repo_get_root(char* buffer, u32 max_len);

/* Purpose: Load the primary game product descriptor from a fixed, milestone-0 repository path.
 *
 * Parameters:
 * - `out_info`: Output product info (non-NULL).
 *
 * Returns:
 * - `D_TRUE` on success.
 * - `D_FALSE` on failure (missing files/keys or parse failure).
 *
 * Notes:
 * - This is a placeholder implementation with hard-coded path components and a minimal JSON extractor.
 * - The current path uses forward slashes and assumes a fixed platform directory.
 */
d_bool dom_repo_load_primary_game(dom_product_info* out_info);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_PKG_REPO_H */
