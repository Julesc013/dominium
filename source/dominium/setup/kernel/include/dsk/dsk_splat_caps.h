#ifndef DSK_SPLAT_CAPS_H
#define DSK_SPLAT_CAPS_H

#include "dsk_types.h"

#ifdef __cplusplus
#include <string>
#include <vector>

typedef std::string dsk_splat_id_t;

enum dsk_splat_scope_bits_t {
    DSK_SPLAT_SCOPE_USER = 0x0001u,
    DSK_SPLAT_SCOPE_SYSTEM = 0x0002u,
    DSK_SPLAT_SCOPE_PORTABLE = 0x0004u
};

enum dsk_splat_ui_bits_t {
    DSK_SPLAT_UI_GUI = 0x0001u,
    DSK_SPLAT_UI_TUI = 0x0002u,
    DSK_SPLAT_UI_CLI = 0x0004u
};

enum dsk_splat_cap_bits_t {
    DSK_SPLAT_CAP_ATOMIC_SWAP = 0x0001u,
    DSK_SPLAT_CAP_RESUME = 0x0002u,
    DSK_SPLAT_CAP_PKG_OWNERSHIP = 0x0004u,
    DSK_SPLAT_CAP_PORTABLE_OWNERSHIP = 0x0008u
};

enum dsk_splat_action_bits_t {
    DSK_SPLAT_ACTION_SHORTCUTS = 0x0010u,
    DSK_SPLAT_ACTION_FILE_ASSOC = 0x0020u,
    DSK_SPLAT_ACTION_URL_HANDLERS = 0x0040u,
    DSK_SPLAT_ACTION_CODESIGN_HOOKS = 0x0080u,
    DSK_SPLAT_ACTION_PKGMGR_HOOKS = 0x0100u,
    DSK_SPLAT_ACTION_STEAM_HOOKS = 0x0200u
};

enum dsk_splat_root_convention_t {
    DSK_SPLAT_ROOT_CONVENTION_UNKNOWN = 0u,
    DSK_SPLAT_ROOT_CONVENTION_PORTABLE = 1u,
    DSK_SPLAT_ROOT_CONVENTION_WINDOWS_PROGRAM_FILES = 2u,
    DSK_SPLAT_ROOT_CONVENTION_LINUX_PREFIX = 3u,
    DSK_SPLAT_ROOT_CONVENTION_MACOS_APPLICATIONS = 4u,
    DSK_SPLAT_ROOT_CONVENTION_STEAM_LIBRARY = 5u
};

enum dsk_splat_elevation_required_t {
    DSK_SPLAT_ELEVATION_NEVER = 1u,
    DSK_SPLAT_ELEVATION_OPTIONAL = 2u,
    DSK_SPLAT_ELEVATION_ALWAYS = 3u
};

enum dsk_splat_rollback_semantics_t {
    DSK_SPLAT_ROLLBACK_NONE = 1u,
    DSK_SPLAT_ROLLBACK_PARTIAL = 2u,
    DSK_SPLAT_ROLLBACK_FULL = 3u
};

struct dsk_splat_caps_t {
    std::vector<std::string> supported_platform_triples;
    dsk_u32 supported_scopes;
    dsk_u32 supported_ui_modes;
    dsk_bool supports_atomic_swap;
    dsk_bool supports_resume;
    dsk_bool supports_pkg_ownership;
    dsk_bool supports_portable_ownership;
    dsk_u32 supports_actions;
    dsk_u16 default_root_convention;
    dsk_u16 elevation_required;
    dsk_u16 rollback_semantics;
    dsk_bool is_deprecated;
    std::string notes;
};

DSK_API void dsk_splat_caps_clear(dsk_splat_caps_t *caps);
DSK_API dsk_u32 dsk_splat_caps_to_flags(const dsk_splat_caps_t *caps);
DSK_API dsk_u64 dsk_splat_caps_digest64(const dsk_splat_caps_t *caps);
#endif /* __cplusplus */

#endif /* DSK_SPLAT_CAPS_H */
