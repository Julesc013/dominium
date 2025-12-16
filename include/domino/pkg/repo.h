/*
FILE: include/domino/pkg/repo.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / pkg/repo
RESPONSIBILITY: Defines the public contract for `repo` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_PKG_REPO_H
#define DOMINO_PKG_REPO_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_product_role {
    DOM_PRODUCT_ROLE_UNKNOWN = 0,
    DOM_PRODUCT_ROLE_GAME,
    DOM_PRODUCT_ROLE_LAUNCHER,
    DOM_PRODUCT_ROLE_SETUP,
    DOM_PRODUCT_ROLE_TOOL
} dom_product_role;

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

/* Resolves DOMINIUM_HOME root; writes a null-terminated path into buffer.
 * Returns D_TRUE on success, D_FALSE on failure.
 */
d_bool dom_repo_get_root(char* buffer, u32 max_len);

/* Milestone 0: load a single primary game product manifest from a fixed path. */
d_bool dom_repo_load_primary_game(dom_product_info* out_info);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_PKG_REPO_H */
