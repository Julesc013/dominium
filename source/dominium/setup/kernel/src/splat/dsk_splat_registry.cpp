#include "dsk/dsk_splat.h"

#include <algorithm>

static void dsk_caps_add_platform(dsk_splat_caps_t *caps, const char *triple) {
    if (!caps || !triple) {
        return;
    }
    caps->supported_platform_triples.push_back(triple);
}

static dsk_splat_caps_t dsk_make_caps(const char *note) {
    dsk_splat_caps_t caps;
    dsk_splat_caps_clear(&caps);
    if (note) {
        caps.notes = note;
    }
    return caps;
}

static void dsk_add_candidate(std::vector<dsk_splat_candidate_t> &out,
                              const char *id,
                              const dsk_splat_caps_t &caps) {
    dsk_splat_candidate_t cand;
    cand.id = id ? id : "";
    cand.caps = caps;
    cand.caps_digest64 = dsk_splat_caps_digest64(&cand.caps);
    out.push_back(cand);
}

static bool dsk_candidate_less(const dsk_splat_candidate_t &a,
                               const dsk_splat_candidate_t &b) {
    return a.id < b.id;
}

void dsk_splat_registry_list(std::vector<dsk_splat_candidate_t> &out) {
    out.clear();

    {
        dsk_splat_caps_t caps = dsk_make_caps("legacy DOS installer");
        dsk_caps_add_platform(&caps, "dos");
        caps.supported_scopes = DSK_SPLAT_SCOPE_PORTABLE;
        caps.supported_ui_modes = DSK_SPLAT_UI_CLI;
        caps.supports_portable_ownership = DSK_TRUE;
        caps.default_root_convention = DSK_SPLAT_ROOT_CONVENTION_PORTABLE;
        caps.rollback_semantics = DSK_SPLAT_ROLLBACK_NONE;
        dsk_add_candidate(out, "splat_dos", caps);
    }
    {
        dsk_splat_caps_t caps = dsk_make_caps("linux deb package manager");
        dsk_caps_add_platform(&caps, "linux_deb");
        caps.supported_scopes = DSK_SPLAT_SCOPE_SYSTEM;
        caps.supported_ui_modes = DSK_SPLAT_UI_TUI | DSK_SPLAT_UI_CLI;
        caps.supports_pkg_ownership = DSK_TRUE;
        caps.supports_actions = DSK_SPLAT_ACTION_PKGMGR_HOOKS;
        caps.default_root_convention = DSK_SPLAT_ROOT_CONVENTION_LINUX_PREFIX;
        caps.elevation_required = DSK_SPLAT_ELEVATION_ALWAYS;
        caps.rollback_semantics = DSK_SPLAT_ROLLBACK_PARTIAL;
        dsk_add_candidate(out, "splat_linux_deb", caps);
    }
    {
        dsk_splat_caps_t caps = dsk_make_caps("linux portable layout");
        dsk_caps_add_platform(&caps, "linux_portable");
        caps.supported_scopes = DSK_SPLAT_SCOPE_PORTABLE;
        caps.supported_ui_modes = DSK_SPLAT_UI_TUI | DSK_SPLAT_UI_CLI;
        caps.supports_atomic_swap = DSK_TRUE;
        caps.supports_resume = DSK_TRUE;
        caps.supports_portable_ownership = DSK_TRUE;
        caps.default_root_convention = DSK_SPLAT_ROOT_CONVENTION_PORTABLE;
        caps.rollback_semantics = DSK_SPLAT_ROLLBACK_FULL;
        dsk_add_candidate(out, "splat_linux_portable", caps);
    }
    {
        dsk_splat_caps_t caps = dsk_make_caps("linux rpm package manager");
        dsk_caps_add_platform(&caps, "linux_rpm");
        caps.supported_scopes = DSK_SPLAT_SCOPE_SYSTEM;
        caps.supported_ui_modes = DSK_SPLAT_UI_TUI | DSK_SPLAT_UI_CLI;
        caps.supports_pkg_ownership = DSK_TRUE;
        caps.supports_actions = DSK_SPLAT_ACTION_PKGMGR_HOOKS;
        caps.default_root_convention = DSK_SPLAT_ROOT_CONVENTION_LINUX_PREFIX;
        caps.elevation_required = DSK_SPLAT_ELEVATION_ALWAYS;
        caps.rollback_semantics = DSK_SPLAT_ROLLBACK_PARTIAL;
        dsk_add_candidate(out, "splat_linux_rpm", caps);
    }
    {
        dsk_splat_caps_t caps = dsk_make_caps("macOS classic legacy");
        dsk_caps_add_platform(&caps, "macos_classic");
        caps.supported_scopes = DSK_SPLAT_SCOPE_SYSTEM;
        caps.supported_ui_modes = DSK_SPLAT_UI_GUI;
        caps.default_root_convention = DSK_SPLAT_ROOT_CONVENTION_MACOS_APPLICATIONS;
        caps.rollback_semantics = DSK_SPLAT_ROLLBACK_NONE;
        dsk_add_candidate(out, "splat_macos_classic", caps);
    }
    {
        dsk_splat_caps_t caps = dsk_make_caps("macOS pkg installer");
        dsk_caps_add_platform(&caps, "macos_pkg");
        caps.supported_scopes = DSK_SPLAT_SCOPE_SYSTEM;
        caps.supported_ui_modes = DSK_SPLAT_UI_GUI | DSK_SPLAT_UI_CLI;
        caps.supports_pkg_ownership = DSK_TRUE;
        caps.supports_actions = DSK_SPLAT_ACTION_CODESIGN_HOOKS | DSK_SPLAT_ACTION_SHORTCUTS;
        caps.default_root_convention = DSK_SPLAT_ROOT_CONVENTION_MACOS_APPLICATIONS;
        caps.elevation_required = DSK_SPLAT_ELEVATION_ALWAYS;
        caps.rollback_semantics = DSK_SPLAT_ROLLBACK_PARTIAL;
        dsk_add_candidate(out, "splat_macos_pkg", caps);
    }
    {
        dsk_splat_caps_t caps = dsk_make_caps("portable archive install");
        dsk_caps_add_platform(&caps, "*");
        caps.supported_scopes = DSK_SPLAT_SCOPE_PORTABLE;
        caps.supported_ui_modes = DSK_SPLAT_UI_GUI | DSK_SPLAT_UI_TUI | DSK_SPLAT_UI_CLI;
        caps.supports_atomic_swap = DSK_TRUE;
        caps.supports_resume = DSK_TRUE;
        caps.supports_portable_ownership = DSK_TRUE;
        caps.default_root_convention = DSK_SPLAT_ROOT_CONVENTION_PORTABLE;
        caps.rollback_semantics = DSK_SPLAT_ROLLBACK_FULL;
        dsk_add_candidate(out, "splat_portable", caps);
    }
    {
        dsk_splat_caps_t caps = dsk_make_caps("steam-managed install");
        dsk_caps_add_platform(&caps, "steam");
        caps.supported_scopes = DSK_SPLAT_SCOPE_USER;
        caps.supported_ui_modes = DSK_SPLAT_UI_GUI | DSK_SPLAT_UI_CLI;
        caps.supports_actions = DSK_SPLAT_ACTION_STEAM_HOOKS;
        caps.default_root_convention = DSK_SPLAT_ROOT_CONVENTION_STEAM_LIBRARY;
        caps.rollback_semantics = DSK_SPLAT_ROLLBACK_PARTIAL;
        dsk_add_candidate(out, "splat_steam", caps);
    }
    {
        dsk_splat_caps_t caps = dsk_make_caps("win16 legacy");
        dsk_caps_add_platform(&caps, "win16_win3x");
        caps.supported_scopes = DSK_SPLAT_SCOPE_PORTABLE;
        caps.supported_ui_modes = DSK_SPLAT_UI_CLI;
        caps.supports_portable_ownership = DSK_TRUE;
        caps.default_root_convention = DSK_SPLAT_ROOT_CONVENTION_WINDOWS_PROGRAM_FILES;
        caps.rollback_semantics = DSK_SPLAT_ROLLBACK_NONE;
        dsk_add_candidate(out, "splat_win16_win3x", caps);
    }
    {
        dsk_splat_caps_t caps = dsk_make_caps("win32 9x legacy");
        dsk_caps_add_platform(&caps, "win32_9x");
        caps.supported_scopes = DSK_SPLAT_SCOPE_USER | DSK_SPLAT_SCOPE_SYSTEM;
        caps.supported_ui_modes = DSK_SPLAT_UI_GUI | DSK_SPLAT_UI_CLI;
        caps.supports_actions = DSK_SPLAT_ACTION_SHORTCUTS;
        caps.default_root_convention = DSK_SPLAT_ROOT_CONVENTION_WINDOWS_PROGRAM_FILES;
        caps.rollback_semantics = DSK_SPLAT_ROLLBACK_NONE;
        dsk_add_candidate(out, "splat_win32_9x", caps);
    }
    {
        dsk_splat_caps_t caps = dsk_make_caps("win32 nt5");
        dsk_caps_add_platform(&caps, "win32_nt5");
        caps.supported_scopes = DSK_SPLAT_SCOPE_USER | DSK_SPLAT_SCOPE_SYSTEM;
        caps.supported_ui_modes = DSK_SPLAT_UI_GUI | DSK_SPLAT_UI_TUI | DSK_SPLAT_UI_CLI;
        caps.supports_actions = DSK_SPLAT_ACTION_SHORTCUTS
                              | DSK_SPLAT_ACTION_FILE_ASSOC
                              | DSK_SPLAT_ACTION_URL_HANDLERS;
        caps.default_root_convention = DSK_SPLAT_ROOT_CONVENTION_WINDOWS_PROGRAM_FILES;
        caps.elevation_required = DSK_SPLAT_ELEVATION_OPTIONAL;
        caps.rollback_semantics = DSK_SPLAT_ROLLBACK_PARTIAL;
        dsk_add_candidate(out, "splat_win32_nt5", caps);
    }

    std::sort(out.begin(), out.end(), dsk_candidate_less);
}

int dsk_splat_registry_find(const std::string &id,
                            dsk_splat_candidate_t *out_candidate) {
    size_t i;
    std::vector<dsk_splat_candidate_t> list;
    dsk_splat_registry_list(list);
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].id == id) {
            if (out_candidate) {
                *out_candidate = list[i];
            }
            return 1;
        }
    }
    return 0;
}

int dsk_splat_registry_contains(const std::string &id) {
    return dsk_splat_registry_find(id, 0);
}
