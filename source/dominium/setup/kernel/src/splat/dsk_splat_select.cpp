#include "dsk/dsk_contracts.h"
#include "dsk/dsk_splat.h"

static void dsk_selection_clear(dsk_splat_selection_t *selection) {
    if (!selection) {
        return;
    }
    selection->candidates.clear();
    selection->rejections.clear();
    selection->selected_id.clear();
    selection->selected_reason = DSK_SPLAT_SELECTED_NONE;
}

static std::string dsk_to_lower(const std::string &s) {
    std::string out = s;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        char c = out[i];
        if (c >= 'A' && c <= 'Z') {
            out[i] = (char)(c - 'A' + 'a');
        }
    }
    return out;
}

static int dsk_is_wildcard(const std::string &value) {
    std::string v = dsk_to_lower(value);
    return v == "*" || v == "any";
}

static int dsk_list_matches(const std::vector<std::string> &values,
                            const std::string &needle) {
    size_t i;
    if (values.empty() || needle.empty()) {
        return 0;
    }
    for (i = 0u; i < values.size(); ++i) {
        if (dsk_is_wildcard(values[i])) {
            return 1;
        }
        if (values[i] == needle) {
            return 1;
        }
    }
    return 0;
}

static int dsk_manifest_allows_target(const dsk_manifest_t &manifest,
                                      const std::string &target) {
    return dsk_list_matches(manifest.supported_targets, target);
}

static int dsk_manifest_allows_splat(const dsk_manifest_t &manifest,
                                     const std::string &id) {
    size_t i;
    if (manifest.allowed_splats.empty()) {
        return 1;
    }
    for (i = 0u; i < manifest.allowed_splats.size(); ++i) {
        if (manifest.allowed_splats[i] == id) {
            return 1;
        }
    }
    return 0;
}

static dsk_u32 dsk_scope_bit(dsk_u16 scope) {
    switch (scope) {
    case DSK_INSTALL_SCOPE_USER: return DSK_SPLAT_SCOPE_USER;
    case DSK_INSTALL_SCOPE_SYSTEM: return DSK_SPLAT_SCOPE_SYSTEM;
    case DSK_INSTALL_SCOPE_PORTABLE: return DSK_SPLAT_SCOPE_PORTABLE;
    default: return 0u;
    }
}

static dsk_u32 dsk_ui_bit(dsk_u16 ui_mode) {
    switch (ui_mode) {
    case DSK_UI_MODE_GUI: return DSK_SPLAT_UI_GUI;
    case DSK_UI_MODE_TUI: return DSK_SPLAT_UI_TUI;
    case DSK_UI_MODE_CLI: return DSK_SPLAT_UI_CLI;
    default: return 0u;
    }
}

static int dsk_caps_supports_platform(const dsk_splat_caps_t &caps,
                                      const std::string &target) {
    return dsk_list_matches(caps.supported_platform_triples, target);
}

static int dsk_caps_supports_scope(const dsk_splat_caps_t &caps, dsk_u16 scope) {
    dsk_u32 bit = dsk_scope_bit(scope);
    return bit != 0u && (caps.supported_scopes & bit) != 0u;
}

static int dsk_caps_supports_ui(const dsk_splat_caps_t &caps, dsk_u16 ui_mode) {
    dsk_u32 bit = dsk_ui_bit(ui_mode);
    return bit != 0u && (caps.supported_ui_modes & bit) != 0u;
}

static int dsk_caps_supports_ownership(const dsk_splat_caps_t &caps,
                                       dsk_u16 ownership_preference) {
    switch (ownership_preference) {
    case DSK_OWNERSHIP_ANY:
        return 1;
    case DSK_OWNERSHIP_PORTABLE:
        return caps.supports_portable_ownership ? 1 : 0;
    case DSK_OWNERSHIP_PKG:
        return caps.supports_pkg_ownership ? 1 : 0;
    case DSK_OWNERSHIP_STEAM:
        return (caps.supports_actions & DSK_SPLAT_ACTION_STEAM_HOOKS) != 0u;
    default:
        return 0;
    }
}

static void dsk_add_rejection(dsk_splat_selection_t *selection,
                              const std::string &id,
                              dsk_u16 code,
                              const char *detail) {
    dsk_splat_rejection_t rej;
    rej.id = id;
    rej.code = code;
    if (detail) {
        rej.detail = detail;
    } else {
        rej.detail.clear();
    }
    selection->rejections.push_back(rej);
}

static dsk_status_t dsk_select_error(dsk_u16 subcode) {
    return dsk_error_make(DSK_DOMAIN_KERNEL,
                          DSK_CODE_VALIDATION_ERROR,
                          subcode,
                          DSK_ERROR_FLAG_USER_ACTIONABLE);
}

dsk_status_t dsk_splat_select(const dsk_manifest_t &manifest,
                              const dsk_request_t &request,
                              dsk_splat_selection_t *out_selection) {
    size_t i;
    dsk_bool has_requested;
    dsk_bool manifest_allows_target;
    dsk_bool selected;

    if (!out_selection) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }

    dsk_selection_clear(out_selection);
    dsk_splat_registry_list(out_selection->candidates);

    has_requested = request.requested_splat_id.empty() ? DSK_FALSE : DSK_TRUE;
    if (has_requested && !dsk_splat_registry_contains(request.requested_splat_id)) {
        for (i = 0u; i < out_selection->candidates.size(); ++i) {
            dsk_add_rejection(out_selection,
                              out_selection->candidates[i].id,
                              DSK_SPLAT_REJECT_REQUESTED_ID_MISMATCH,
                              "requested_splat_id");
        }
        return dsk_select_error(DSK_SUBCODE_SPLAT_NOT_FOUND);
    }

    manifest_allows_target = dsk_manifest_allows_target(manifest, request.target_platform_triple)
                             ? DSK_TRUE
                             : DSK_FALSE;
    selected = DSK_FALSE;

    for (i = 0u; i < out_selection->candidates.size(); ++i) {
        const dsk_splat_candidate_t &cand = out_selection->candidates[i];
        dsk_u32 caps_flags = dsk_splat_caps_to_flags(&cand.caps);

        if (has_requested && cand.id != request.requested_splat_id) {
            dsk_add_rejection(out_selection,
                              cand.id,
                              DSK_SPLAT_REJECT_REQUESTED_ID_MISMATCH,
                              "requested_splat_id");
            continue;
        }
        if (!dsk_caps_supports_platform(cand.caps, request.target_platform_triple)) {
            dsk_add_rejection(out_selection,
                              cand.id,
                              DSK_SPLAT_REJECT_PLATFORM_UNSUPPORTED,
                              "target_platform_triple");
            continue;
        }
        if (!dsk_caps_supports_scope(cand.caps, request.install_scope)) {
            dsk_add_rejection(out_selection,
                              cand.id,
                              DSK_SPLAT_REJECT_SCOPE_UNSUPPORTED,
                              "install_scope");
            continue;
        }
        if (!dsk_caps_supports_ui(cand.caps, request.ui_mode)) {
            dsk_add_rejection(out_selection,
                              cand.id,
                              DSK_SPLAT_REJECT_UI_MODE_UNSUPPORTED,
                              "ui_mode");
            continue;
        }
        if (!dsk_caps_supports_ownership(cand.caps, request.ownership_preference)) {
            dsk_add_rejection(out_selection,
                              cand.id,
                              DSK_SPLAT_REJECT_OWNERSHIP_INCOMPATIBLE,
                              "ownership_preference");
            continue;
        }
        if (!dsk_manifest_allows_splat(manifest, cand.id)) {
            dsk_add_rejection(out_selection,
                              cand.id,
                              DSK_SPLAT_REJECT_MANIFEST_ALLOWLIST,
                              "manifest_allowlist");
            continue;
        }
        if ((request.required_caps & ~caps_flags) != 0u) {
            dsk_add_rejection(out_selection,
                              cand.id,
                              DSK_SPLAT_REJECT_REQUIRED_CAPS_MISSING,
                              "required_caps");
            continue;
        }
        if ((request.prohibited_caps & caps_flags) != 0u) {
            dsk_add_rejection(out_selection,
                              cand.id,
                              DSK_SPLAT_REJECT_PROHIBITED_CAPS_PRESENT,
                              "prohibited_caps");
            continue;
        }
        if (!manifest_allows_target) {
            dsk_add_rejection(out_selection,
                              cand.id,
                              DSK_SPLAT_REJECT_MANIFEST_TARGET_MISMATCH,
                              "manifest_supported_targets");
            continue;
        }

        if (!selected) {
            out_selection->selected_id = cand.id;
            out_selection->selected_reason = has_requested
                                             ? DSK_SPLAT_SELECTED_REQUESTED
                                             : DSK_SPLAT_SELECTED_FIRST_COMPATIBLE;
            selected = DSK_TRUE;
        }
    }

    if (!selected) {
        return dsk_select_error(DSK_SUBCODE_NO_COMPATIBLE_SPLAT);
    }

    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}
