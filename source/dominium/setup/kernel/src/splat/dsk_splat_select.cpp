#include "dsk/dsk_contracts.h"
#include "dsk/dsk_splat.h"

#include "dominium/core_caps.h"
#include "dominium/core_solver.h"

#include <cstring>

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

struct dsk_solver_component_t {
    core_solver_component_desc desc;
    std::vector<core_cap_entry> provides;
};

static core_cap_entry dsk_make_bool_cap(u32 key_id, dsk_bool ok) {
    core_cap_entry e;
    std::memset(&e, 0, sizeof(e));
    e.key_id = key_id;
    e.type = (u8)CORE_CAP_BOOL;
    e.v.bool_value = ok ? 1u : 0u;
    return e;
}

static core_solver_constraint dsk_make_require_bool(u32 key_id) {
    core_solver_constraint c;
    std::memset(&c, 0, sizeof(c));
    c.key_id = key_id;
    c.op = (u8)CORE_SOLVER_OP_EQ;
    c.type = (u8)CORE_CAP_BOOL;
    c.value.bool_value = 1u;
    return c;
}

static dsk_u16 dsk_reject_code_from_key(u32 key_id) {
    switch (key_id) {
    case CORE_CAP_KEY_SETUP_TARGET_OK: return DSK_SPLAT_REJECT_PLATFORM_UNSUPPORTED;
    case CORE_CAP_KEY_SETUP_SCOPE_OK: return DSK_SPLAT_REJECT_SCOPE_UNSUPPORTED;
    case CORE_CAP_KEY_SETUP_UI_OK: return DSK_SPLAT_REJECT_UI_MODE_UNSUPPORTED;
    case CORE_CAP_KEY_SETUP_OWNERSHIP_OK: return DSK_SPLAT_REJECT_OWNERSHIP_INCOMPATIBLE;
    case CORE_CAP_KEY_SETUP_MANIFEST_ALLOWLIST_OK: return DSK_SPLAT_REJECT_MANIFEST_ALLOWLIST;
    case CORE_CAP_KEY_SETUP_REQUIRED_CAPS_OK: return DSK_SPLAT_REJECT_REQUIRED_CAPS_MISSING;
    case CORE_CAP_KEY_SETUP_PROHIBITED_CAPS_OK: return DSK_SPLAT_REJECT_PROHIBITED_CAPS_PRESENT;
    case CORE_CAP_KEY_SETUP_MANIFEST_TARGET_OK: return DSK_SPLAT_REJECT_MANIFEST_TARGET_MISMATCH;
    default:
        break;
    }
    return DSK_SPLAT_REJECT_NONE;
}

static const char* dsk_reject_detail_from_code(dsk_u16 code) {
    switch (code) {
    case DSK_SPLAT_REJECT_REQUESTED_ID_MISMATCH: return "requested_splat_id";
    case DSK_SPLAT_REJECT_PLATFORM_UNSUPPORTED: return "target_platform_triple";
    case DSK_SPLAT_REJECT_SCOPE_UNSUPPORTED: return "install_scope";
    case DSK_SPLAT_REJECT_UI_MODE_UNSUPPORTED: return "ui_mode";
    case DSK_SPLAT_REJECT_OWNERSHIP_INCOMPATIBLE: return "ownership_preference";
    case DSK_SPLAT_REJECT_MANIFEST_ALLOWLIST: return "manifest_allowlist";
    case DSK_SPLAT_REJECT_REQUIRED_CAPS_MISSING: return "required_caps";
    case DSK_SPLAT_REJECT_PROHIBITED_CAPS_PRESENT: return "prohibited_caps";
    case DSK_SPLAT_REJECT_MANIFEST_TARGET_MISMATCH: return "manifest_supported_targets";
    default:
        break;
    }
    return "";
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
    core_caps host_caps;
    std::vector<core_solver_constraint> requires;
    std::vector<dsk_solver_component_t> components;
    std::vector<core_solver_component_desc> comp_descs;
    core_solver_category_desc category;
    core_solver_override override_sel;
    core_solver_desc desc;
    core_solver_result result;
    dsk_status_t status;

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
                              dsk_reject_detail_from_code(DSK_SPLAT_REJECT_REQUESTED_ID_MISMATCH));
        }
        return dsk_select_error(DSK_SUBCODE_SPLAT_NOT_FOUND);
    }

    manifest_allows_target = dsk_manifest_allows_target(manifest, request.target_platform_triple)
                             ? DSK_TRUE
                             : DSK_FALSE;

    core_caps_clear(&host_caps);
    (void)core_caps_set_bool(&host_caps, CORE_CAP_KEY_SETUP_MANIFEST_TARGET_OK, manifest_allows_target ? 1u : 0u);

    requires.clear();
    requires.push_back(dsk_make_require_bool(CORE_CAP_KEY_SETUP_TARGET_OK));
    requires.push_back(dsk_make_require_bool(CORE_CAP_KEY_SETUP_SCOPE_OK));
    requires.push_back(dsk_make_require_bool(CORE_CAP_KEY_SETUP_UI_OK));
    requires.push_back(dsk_make_require_bool(CORE_CAP_KEY_SETUP_OWNERSHIP_OK));
    requires.push_back(dsk_make_require_bool(CORE_CAP_KEY_SETUP_MANIFEST_ALLOWLIST_OK));
    requires.push_back(dsk_make_require_bool(CORE_CAP_KEY_SETUP_REQUIRED_CAPS_OK));
    requires.push_back(dsk_make_require_bool(CORE_CAP_KEY_SETUP_PROHIBITED_CAPS_OK));
    requires.push_back(dsk_make_require_bool(CORE_CAP_KEY_SETUP_MANIFEST_TARGET_OK));

    components.clear();
    comp_descs.clear();
    components.reserve(out_selection->candidates.size());
    comp_descs.reserve(out_selection->candidates.size());

    for (i = 0u; i < out_selection->candidates.size(); ++i) {
        const dsk_splat_candidate_t &cand = out_selection->candidates[i];
        dsk_u32 caps_flags = dsk_splat_caps_to_flags(&cand.caps);
        const dsk_bool target_ok = dsk_caps_supports_platform(cand.caps, request.target_platform_triple) ? DSK_TRUE : DSK_FALSE;
        const dsk_bool scope_ok = dsk_caps_supports_scope(cand.caps, request.install_scope) ? DSK_TRUE : DSK_FALSE;
        const dsk_bool ui_ok = dsk_caps_supports_ui(cand.caps, request.ui_mode) ? DSK_TRUE : DSK_FALSE;
        const dsk_bool ownership_ok = dsk_caps_supports_ownership(cand.caps, request.ownership_preference) ? DSK_TRUE : DSK_FALSE;
        const dsk_bool allowlist_ok = dsk_manifest_allows_splat(manifest, cand.id) ? DSK_TRUE : DSK_FALSE;
        const dsk_bool required_ok = ((request.required_caps & ~caps_flags) == 0u) ? DSK_TRUE : DSK_FALSE;
        const dsk_bool prohibited_ok = ((request.prohibited_caps & caps_flags) == 0u) ? DSK_TRUE : DSK_FALSE;

        dsk_solver_component_t comp;
        std::memset(&comp.desc, 0, sizeof(comp.desc));
        comp.desc.component_id = cand.id.c_str();
        comp.desc.category_id = CORE_SOLVER_CAT_PLATFORM;
        comp.desc.priority = 0u;

        comp.provides.push_back(dsk_make_bool_cap(CORE_CAP_KEY_SETUP_TARGET_OK, target_ok));
        comp.provides.push_back(dsk_make_bool_cap(CORE_CAP_KEY_SETUP_SCOPE_OK, scope_ok));
        comp.provides.push_back(dsk_make_bool_cap(CORE_CAP_KEY_SETUP_UI_OK, ui_ok));
        comp.provides.push_back(dsk_make_bool_cap(CORE_CAP_KEY_SETUP_OWNERSHIP_OK, ownership_ok));
        comp.provides.push_back(dsk_make_bool_cap(CORE_CAP_KEY_SETUP_MANIFEST_ALLOWLIST_OK, allowlist_ok));
        comp.provides.push_back(dsk_make_bool_cap(CORE_CAP_KEY_SETUP_REQUIRED_CAPS_OK, required_ok));
        comp.provides.push_back(dsk_make_bool_cap(CORE_CAP_KEY_SETUP_PROHIBITED_CAPS_OK, prohibited_ok));

        comp.desc.provides = (const core_cap_entry *)0;
        comp.desc.provides_count = 0u;
        comp.desc.requires = (const core_solver_constraint *)0;
        comp.desc.requires_count = 0u;
        comp.desc.forbids = (const core_solver_constraint *)0;
        comp.desc.forbids_count = 0u;
        comp.desc.prefers = (const core_solver_constraint *)0;
        comp.desc.prefers_count = 0u;
        comp.desc.conflicts = (const char * const *)0;
        comp.desc.conflicts_count = 0u;

        components.push_back(comp);
    }

    comp_descs.clear();
    comp_descs.reserve(components.size());
    for (i = 0u; i < components.size(); ++i) {
        dsk_solver_component_t &comp = components[i];
        comp.desc.provides = comp.provides.empty() ? (const core_cap_entry *)0 : &comp.provides[0];
        comp.desc.provides_count = (u32)comp.provides.size();
        comp_descs.push_back(comp.desc);
    }

    category.category_id = CORE_SOLVER_CAT_PLATFORM;
    category.required = 1u;

    std::memset(&desc, 0, sizeof(desc));
    desc.categories = &category;
    desc.category_count = 1u;
    desc.components = comp_descs.empty() ? (const core_solver_component_desc *)0 : &comp_descs[0];
    desc.component_count = (u32)comp_descs.size();
    desc.host_caps = &host_caps;
    desc.profile_requires = requires.empty() ? (const core_solver_constraint *)0 : &requires[0];
    desc.profile_requires_count = (u32)requires.size();
    desc.profile_forbids = (const core_solver_constraint *)0;
    desc.profile_forbids_count = 0u;
    desc.score_fn = 0;
    desc.score_user = 0;

    if (has_requested) {
        override_sel.category_id = CORE_SOLVER_CAT_PLATFORM;
        override_sel.component_id = request.requested_splat_id.c_str();
        desc.overrides = &override_sel;
        desc.override_count = 1u;
    } else {
        desc.overrides = (const core_solver_override *)0;
        desc.override_count = 0u;
    }

    core_solver_result_clear(&result);
    (void)core_solver_select(&desc, &result);

    for (i = 0u; i < result.rejected_count; ++i) {
        const core_solver_reject &rj = result.rejected[i];
        dsk_u16 code = DSK_SPLAT_REJECT_NONE;
        const char *detail = "";

        if (rj.reason == CORE_SOLVER_REJECT_OVERRIDE_MISMATCH) {
            code = DSK_SPLAT_REJECT_REQUESTED_ID_MISMATCH;
        } else if (rj.reason == CORE_SOLVER_REJECT_CONSTRAINT) {
            code = dsk_reject_code_from_key(rj.constraint.key_id);
        } else {
            code = DSK_SPLAT_REJECT_NONE;
        }

        detail = dsk_reject_detail_from_code(code);
        if (code != DSK_SPLAT_REJECT_NONE) {
            dsk_add_rejection(out_selection, rj.component_id, code, detail);
        }
    }

    if (result.ok == 0u || result.selected_count == 0u) {
        if (has_requested && result.fail_reason == CORE_SOLVER_FAIL_OVERRIDE_NOT_FOUND) {
            status = dsk_select_error(DSK_SUBCODE_SPLAT_NOT_FOUND);
        } else {
            status = dsk_select_error(DSK_SUBCODE_NO_COMPATIBLE_SPLAT);
        }
        return status;
    }

    out_selection->selected_id = result.selected[0].component_id;
    out_selection->selected_reason = (has_requested && result.selected[0].reason == CORE_SOLVER_SELECT_OVERRIDE)
                                     ? DSK_SPLAT_SELECTED_REQUESTED
                                     : DSK_SPLAT_SELECTED_FIRST_COMPATIBLE;

    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}
