#include "dsk/dsk_api.h"
#include "dsk/dsk_audit.h"
#include "dsk/dsk_contracts.h"
#include "dsk/dsk_digest.h"
#include "dsk/dsk_error.h"
#include "dsk/dsk_plan.h"
#include "dsk/dsk_resume.h"
#include "dsk/dsk_jobs.h"
#include "dsk/dsk_splat.h"
#include "dss/dss_services.h"

#include "args_parse.h"
#include "dominium/core_audit.h"
#include "json_writer.h"
#include "request_builder.h"

#include <algorithm>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

struct dsk_mem_sink_t {
    std::vector<dsk_u8> data;
};

static dsk_status_t dsk_mem_sink_write(void *user, const dsk_u8 *data, dsk_u32 len) {
    dsk_mem_sink_t *sink = reinterpret_cast<dsk_mem_sink_t *>(user);
    if (!sink) {
        return dsk_error_make(DSK_DOMAIN_FRONTEND, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    if (len && !data) {
        return dsk_error_make(DSK_DOMAIN_FRONTEND, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    sink->data.insert(sink->data.end(), data, data + len);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static int load_file(const dss_fs_api_t *fs, const char *path, std::vector<dsk_u8> &out) {
    dss_error_t st;
    if (!fs || !fs->read_file_bytes) {
        return 0;
    }
    st = fs->read_file_bytes(fs->ctx, path, &out);
    return dss_error_is_ok(st);
}

static int write_file(const dss_fs_api_t *fs,
                      const char *path,
                      const std::vector<dsk_u8> &data) {
    dss_error_t st;
    if (!fs || !fs->write_file_bytes_atomic) {
        return 0;
    }
    st = fs->write_file_bytes_atomic(fs->ctx,
                                     path,
                                     data.empty() ? 0 : &data[0],
                                     (dss_u32)data.size());
    return dss_error_is_ok(st);
}

static const char *op_to_string(dsk_u16 op) {
    switch (op) {
    case DSK_OPERATION_INSTALL: return "install";
    case DSK_OPERATION_UPGRADE: return "upgrade";
    case DSK_OPERATION_REPAIR: return "repair";
    case DSK_OPERATION_UNINSTALL: return "uninstall";
    case DSK_OPERATION_VERIFY: return "verify";
    case DSK_OPERATION_STATUS: return "status";
    default: return "unknown";
    }
}

static const char *scope_to_string(dsk_u16 scope) {
    switch (scope) {
    case DSK_INSTALL_SCOPE_USER: return "user";
    case DSK_INSTALL_SCOPE_SYSTEM: return "system";
    case DSK_INSTALL_SCOPE_PORTABLE: return "portable";
    default: return "unknown";
    }
}

static const char *ui_mode_to_string(dsk_u16 mode) {
    switch (mode) {
    case DSK_UI_MODE_GUI: return "gui";
    case DSK_UI_MODE_TUI: return "tui";
    case DSK_UI_MODE_CLI: return "cli";
    default: return "unknown";
    }
}

static const char *ownership_to_string(dsk_u16 value) {
    switch (value) {
    case DSK_OWNERSHIP_PORTABLE: return "portable";
    case DSK_OWNERSHIP_PKG: return "pkg";
    case DSK_OWNERSHIP_STEAM: return "steam";
    case DSK_OWNERSHIP_ANY: return "any";
    default: return "unknown";
    }
}

static const char *root_convention_to_string(dsk_u16 value) {
    switch (value) {
    case DSK_SPLAT_ROOT_CONVENTION_PORTABLE: return "portable";
    case DSK_SPLAT_ROOT_CONVENTION_WINDOWS_PROGRAM_FILES: return "windows_program_files";
    case DSK_SPLAT_ROOT_CONVENTION_LINUX_PREFIX: return "linux_prefix";
    case DSK_SPLAT_ROOT_CONVENTION_MACOS_APPLICATIONS: return "macos_applications";
    case DSK_SPLAT_ROOT_CONVENTION_STEAM_LIBRARY: return "steam_library";
    default: return "unknown";
    }
}

static const char *elevation_to_string(dsk_u16 value) {
    switch (value) {
    case DSK_SPLAT_ELEVATION_NEVER: return "never";
    case DSK_SPLAT_ELEVATION_OPTIONAL: return "optional";
    case DSK_SPLAT_ELEVATION_ALWAYS: return "always";
    default: return "unknown";
    }
}

static const char *rollback_to_string(dsk_u16 value) {
    switch (value) {
    case DSK_SPLAT_ROLLBACK_NONE: return "none";
    case DSK_SPLAT_ROLLBACK_PARTIAL: return "partial";
    case DSK_SPLAT_ROLLBACK_FULL: return "full";
    default: return "unknown";
    }
}

static const char *selected_reason_to_string(dsk_u16 value) {
    switch (value) {
    case DSK_SPLAT_SELECTED_REQUESTED: return "requested_id";
    case DSK_SPLAT_SELECTED_FIRST_COMPATIBLE: return "first_compatible";
    default: return "none";
    }
}

struct dsk_cli_artifacts_t {
    const char *manifest;
    const char *request;
    const char *plan;
    const char *state;
    const char *audit;
    const char *journal;
    const char *txn_journal;
};

struct dsk_cli_digests_t {
    dsk_bool has_manifest;
    dsk_bool has_request;
    dsk_bool has_plan;
    dsk_bool has_state;
    dsk_bool has_audit;
    dsk_u64 manifest;
    dsk_u64 request;
    dsk_u64 plan;
    dsk_u64 state;
    dsk_u64 audit;
};

static dsk_cli_artifacts_t dsk_cli_artifacts_empty(void) {
    dsk_cli_artifacts_t artifacts;
    artifacts.manifest = "";
    artifacts.request = "";
    artifacts.plan = "";
    artifacts.state = "";
    artifacts.audit = "";
    artifacts.journal = "";
    artifacts.txn_journal = "";
    return artifacts;
}

static dsk_cli_digests_t dsk_cli_digests_empty(void) {
    dsk_cli_digests_t digests;
    digests.has_manifest = DSK_FALSE;
    digests.has_request = DSK_FALSE;
    digests.has_plan = DSK_FALSE;
    digests.has_state = DSK_FALSE;
    digests.has_audit = DSK_FALSE;
    digests.manifest = 0u;
    digests.request = 0u;
    digests.plan = 0u;
    digests.state = 0u;
    digests.audit = 0u;
    return digests;
}

static void dsk_json_write_error(dsk_json_writer_t *writer, dsk_status_t status) {
    dsk_u32 subcode = dom::core_audit::err_subcode(status);
    dsk_json_begin_object(writer);
    dsk_json_key(writer, "domain");
    dsk_json_u32(writer, status.domain);
    dsk_json_key(writer, "code");
    dsk_json_u32(writer, status.code);
    dsk_json_key(writer, "subcode");
    dsk_json_u32(writer, subcode);
    dsk_json_key(writer, "flags");
    dsk_json_u32(writer, status.flags);
    dsk_json_key(writer, "msg_id");
    dsk_json_u32(writer, status.msg_id);
    dsk_json_key(writer, "label");
    dsk_json_string(writer, dsk_error_to_string_stable(status));
    dsk_json_end_object(writer);
}

static void dsk_json_write_artifacts(dsk_json_writer_t *writer,
                                     const dsk_cli_artifacts_t &artifacts) {
    dsk_json_begin_object(writer);
    dsk_json_key(writer, "manifest");
    dsk_json_string(writer, artifacts.manifest ? artifacts.manifest : "");
    dsk_json_key(writer, "request");
    dsk_json_string(writer, artifacts.request ? artifacts.request : "");
    dsk_json_key(writer, "plan");
    dsk_json_string(writer, artifacts.plan ? artifacts.plan : "");
    dsk_json_key(writer, "state");
    dsk_json_string(writer, artifacts.state ? artifacts.state : "");
    dsk_json_key(writer, "audit");
    dsk_json_string(writer, artifacts.audit ? artifacts.audit : "");
    dsk_json_key(writer, "journal");
    dsk_json_string(writer, artifacts.journal ? artifacts.journal : "");
    dsk_json_key(writer, "txn_journal");
    dsk_json_string(writer, artifacts.txn_journal ? artifacts.txn_journal : "");
    dsk_json_end_object(writer);
}

static void dsk_json_write_digest_or_empty(dsk_json_writer_t *writer,
                                           dsk_bool has_value,
                                           dsk_u64 value) {
    if (has_value) {
        dsk_json_u64_hex(writer, value);
    } else {
        dsk_json_string(writer, "");
    }
}

static void dsk_json_write_digests(dsk_json_writer_t *writer,
                                   const dsk_cli_digests_t &digests) {
    dsk_json_begin_object(writer);
    dsk_json_key(writer, "manifest");
    dsk_json_write_digest_or_empty(writer, digests.has_manifest, digests.manifest);
    dsk_json_key(writer, "request");
    dsk_json_write_digest_or_empty(writer, digests.has_request, digests.request);
    dsk_json_key(writer, "plan");
    dsk_json_write_digest_or_empty(writer, digests.has_plan, digests.plan);
    dsk_json_key(writer, "state");
    dsk_json_write_digest_or_empty(writer, digests.has_state, digests.state);
    dsk_json_key(writer, "audit");
    dsk_json_write_digest_or_empty(writer, digests.has_audit, digests.audit);
    dsk_json_end_object(writer);
}

static void dsk_json_write_string_list_sorted(dsk_json_writer_t *writer,
                                              const std::vector<std::string> &values) {
    std::vector<std::string> sorted = values;
    size_t i;
    std::sort(sorted.begin(), sorted.end());
    dsk_json_begin_array(writer);
    for (i = 0u; i < sorted.size(); ++i) {
        dsk_json_string(writer, sorted[i].c_str());
    }
    dsk_json_end_array(writer);
}

static void dsk_json_write_scopes(dsk_json_writer_t *writer, dsk_u32 scopes) {
    dsk_json_begin_array(writer);
    if (scopes & DSK_SPLAT_SCOPE_USER) {
        dsk_json_string(writer, "user");
    }
    if (scopes & DSK_SPLAT_SCOPE_SYSTEM) {
        dsk_json_string(writer, "system");
    }
    if (scopes & DSK_SPLAT_SCOPE_PORTABLE) {
        dsk_json_string(writer, "portable");
    }
    dsk_json_end_array(writer);
}

static void dsk_json_write_ui_modes(dsk_json_writer_t *writer, dsk_u32 modes) {
    dsk_json_begin_array(writer);
    if (modes & DSK_SPLAT_UI_GUI) {
        dsk_json_string(writer, "gui");
    }
    if (modes & DSK_SPLAT_UI_TUI) {
        dsk_json_string(writer, "tui");
    }
    if (modes & DSK_SPLAT_UI_CLI) {
        dsk_json_string(writer, "cli");
    }
    dsk_json_end_array(writer);
}

static void dsk_json_write_actions(dsk_json_writer_t *writer, dsk_u32 actions) {
    dsk_json_begin_array(writer);
    if (actions & DSK_SPLAT_ACTION_SHORTCUTS) {
        dsk_json_string(writer, "shortcuts");
    }
    if (actions & DSK_SPLAT_ACTION_FILE_ASSOC) {
        dsk_json_string(writer, "file_assoc");
    }
    if (actions & DSK_SPLAT_ACTION_URL_HANDLERS) {
        dsk_json_string(writer, "url_handlers");
    }
    if (actions & DSK_SPLAT_ACTION_CODESIGN_HOOKS) {
        dsk_json_string(writer, "codesign_hooks");
    }
    if (actions & DSK_SPLAT_ACTION_PKGMGR_HOOKS) {
        dsk_json_string(writer, "pkgmgr_hooks");
    }
    if (actions & DSK_SPLAT_ACTION_STEAM_HOOKS) {
        dsk_json_string(writer, "steam_hooks");
    }
    dsk_json_end_array(writer);
}

static void dsk_json_write_caps(dsk_json_writer_t *writer, const dsk_splat_caps_t &caps) {
    dsk_json_begin_object(writer);
    dsk_json_key(writer, "supported_platform_triples");
    dsk_json_write_string_list_sorted(writer, caps.supported_platform_triples);
    dsk_json_key(writer, "supported_scopes");
    dsk_json_write_scopes(writer, caps.supported_scopes);
    dsk_json_key(writer, "supported_ui_modes");
    dsk_json_write_ui_modes(writer, caps.supported_ui_modes);
    dsk_json_key(writer, "supports_atomic_swap");
    dsk_json_bool(writer, caps.supports_atomic_swap);
    dsk_json_key(writer, "supports_resume");
    dsk_json_bool(writer, caps.supports_resume);
    dsk_json_key(writer, "supports_pkg_ownership");
    dsk_json_bool(writer, caps.supports_pkg_ownership);
    dsk_json_key(writer, "supports_portable_ownership");
    dsk_json_bool(writer, caps.supports_portable_ownership);
    dsk_json_key(writer, "supports_actions");
    dsk_json_write_actions(writer, caps.supports_actions);
    dsk_json_key(writer, "default_root_convention");
    dsk_json_string(writer, root_convention_to_string(caps.default_root_convention));
    dsk_json_key(writer, "elevation_required");
    dsk_json_string(writer, elevation_to_string(caps.elevation_required));
    dsk_json_key(writer, "rollback_semantics");
    dsk_json_string(writer, rollback_to_string(caps.rollback_semantics));
    dsk_json_key(writer, "notes");
    dsk_json_string(writer, caps.notes.c_str());
    dsk_json_end_object(writer);
}

static bool dsk_candidate_less(const dsk_splat_candidate_t &a,
                               const dsk_splat_candidate_t &b) {
    return a.id < b.id;
}

static bool dsk_rejection_less(const dsk_splat_rejection_t &a,
                               const dsk_splat_rejection_t &b) {
    if (a.id != b.id) {
        return a.id < b.id;
    }
    return a.code < b.code;
}

static void dsk_json_write_splat_registry(dsk_json_writer_t *writer,
                                          const std::vector<dsk_splat_candidate_t> &splats) {
    std::vector<dsk_splat_candidate_t> sorted = splats;
    size_t i;
    std::sort(sorted.begin(), sorted.end(), dsk_candidate_less);
    dsk_json_begin_array(writer);
    for (i = 0u; i < sorted.size(); ++i) {
        dsk_json_begin_object(writer);
        dsk_json_key(writer, "id");
        dsk_json_string(writer, sorted[i].id.c_str());
        dsk_json_key(writer, "caps_digest64");
        dsk_json_u64_hex(writer, sorted[i].caps_digest64);
        dsk_json_key(writer, "caps");
        dsk_json_write_caps(writer, sorted[i].caps);
        dsk_json_end_object(writer);
    }
    dsk_json_end_array(writer);
}

static void dsk_json_write_selection(dsk_json_writer_t *writer,
                                     const dsk_splat_selection_t &selection,
                                     dsk_status_t status) {
    std::vector<dsk_splat_candidate_t> candidates = selection.candidates;
    std::vector<dsk_splat_rejection_t> rejections = selection.rejections;
    size_t i;
    (void)status;
    std::sort(candidates.begin(), candidates.end(), dsk_candidate_less);
    std::sort(rejections.begin(), rejections.end(), dsk_rejection_less);

    dsk_json_begin_object(writer);
    dsk_json_key(writer, "status");
    dsk_json_string(writer, dsk_error_is_ok(status) ? "ok" : "error");
    dsk_json_key(writer, "selected_splat");
    dsk_json_string(writer, selection.selected_id.c_str());
    dsk_json_key(writer, "selected_reason");
    dsk_json_u32(writer, selection.selected_reason);
    dsk_json_key(writer, "selected_reason_label");
    dsk_json_string(writer, selected_reason_to_string(selection.selected_reason));
    dsk_json_key(writer, "candidates");
    dsk_json_begin_array(writer);
    for (i = 0u; i < candidates.size(); ++i) {
        dsk_json_begin_object(writer);
        dsk_json_key(writer, "id");
        dsk_json_string(writer, candidates[i].id.c_str());
        dsk_json_key(writer, "caps_digest64");
        dsk_json_u64_hex(writer, candidates[i].caps_digest64);
        dsk_json_end_object(writer);
    }
    dsk_json_end_array(writer);
    dsk_json_key(writer, "rejections");
    dsk_json_begin_array(writer);
    for (i = 0u; i < rejections.size(); ++i) {
        dsk_json_begin_object(writer);
        dsk_json_key(writer, "id");
        dsk_json_string(writer, rejections[i].id.c_str());
        dsk_json_key(writer, "code");
        dsk_json_u32(writer, rejections[i].code);
        if (!rejections[i].detail.empty()) {
            dsk_json_key(writer, "detail");
            dsk_json_string(writer, rejections[i].detail.c_str());
        }
        dsk_json_end_object(writer);
    }
    dsk_json_end_array(writer);
    dsk_json_end_object(writer);
}

static void dsk_json_write_audit_summary(dsk_json_writer_t *writer,
                                         const dsk_audit_t &audit) {
    dsk_json_begin_object(writer);
    dsk_json_key(writer, "operation");
    dsk_json_string(writer, op_to_string(audit.operation));
    dsk_json_key(writer, "selected_splat");
    dsk_json_string(writer, audit.selected_splat.c_str());
    dsk_json_key(writer, "manifest_digest64");
    dsk_json_u64_hex(writer, audit.manifest_digest64);
    dsk_json_key(writer, "request_digest64");
    dsk_json_u64_hex(writer, audit.request_digest64);
    dsk_json_key(writer, "plan_digest64");
    dsk_json_u64_hex(writer, audit.plan_digest64);
    dsk_json_end_object(writer);
}

static void dsk_json_write_status_summary(dsk_json_writer_t *writer,
                                          const dsk_job_journal_t &journal) {
    size_t i;
    dsk_u32 pending = 0u;
    dsk_u32 in_progress = 0u;
    dsk_u32 complete = 0u;
    dsk_u32 failed = 0u;
    const char *state = "unknown";
    for (i = 0u; i < journal.checkpoints.size(); ++i) {
        dsk_u16 st = journal.checkpoints[i].status;
        if (st == DSK_JOB_STATUS_PENDING) {
            ++pending;
        } else if (st == DSK_JOB_STATUS_IN_PROGRESS) {
            ++in_progress;
        } else if (st == DSK_JOB_STATUS_COMPLETE || st == DSK_JOB_STATUS_SKIPPED) {
            ++complete;
        } else if (st == DSK_JOB_STATUS_FAILED) {
            ++failed;
        }
    }
    if (failed > 0u) {
        state = "failed";
    } else if (in_progress > 0u) {
        state = "in_progress";
    } else if (pending > 0u) {
        state = "pending";
    } else {
        state = "complete";
    }

    dsk_json_begin_object(writer);
    dsk_json_key(writer, "state");
    dsk_json_string(writer, state);
    dsk_json_key(writer, "pending");
    dsk_json_u32(writer, pending);
    dsk_json_key(writer, "in_progress");
    dsk_json_u32(writer, in_progress);
    dsk_json_key(writer, "complete");
    dsk_json_u32(writer, complete);
    dsk_json_key(writer, "failed");
    dsk_json_u32(writer, failed);
    dsk_json_key(writer, "last_error");
    dsk_json_write_error(writer, journal.last_error);
    dsk_json_end_object(writer);
}

static void dsk_json_write_state_summary(dsk_json_writer_t *writer,
                                         const dsk_installed_state_t &state) {
    dsk_json_begin_object(writer);
    dsk_json_key(writer, "product_id");
    dsk_json_string(writer, state.product_id.c_str());
    dsk_json_key(writer, "installed_version");
    dsk_json_string(writer, state.installed_version.c_str());
    dsk_json_key(writer, "selected_splat");
    dsk_json_string(writer, state.selected_splat.c_str());
    dsk_json_key(writer, "install_scope");
    dsk_json_string(writer, scope_to_string(state.install_scope));
    dsk_json_key(writer, "install_root");
    dsk_json_string(writer, state.install_root.c_str());
    dsk_json_key(writer, "ownership");
    dsk_json_string(writer, ownership_to_string(state.ownership));
    dsk_json_end_object(writer);
}

static bool dsk_resolved_less(const dsk_resolved_component_t &a,
                              const dsk_resolved_component_t &b) {
    return a.component_id < b.component_id;
}

static void dsk_json_write_resolved_set(dsk_json_writer_t *writer,
                                        const dsk_plan_t &plan) {
    std::vector<dsk_resolved_component_t> comps = plan.resolved_components;
    size_t i;
    std::sort(comps.begin(), comps.end(), dsk_resolved_less);
    dsk_json_begin_object(writer);
    dsk_json_key(writer, "resolved_set_digest64");
    dsk_json_u64_hex(writer, plan.resolved_set_digest64);
    dsk_json_key(writer, "components");
    dsk_json_begin_array(writer);
    for (i = 0u; i < comps.size(); ++i) {
        dsk_json_begin_object(writer);
        dsk_json_key(writer, "component_id");
        dsk_json_string(writer, comps[i].component_id.c_str());
        dsk_json_key(writer, "component_version");
        dsk_json_string(writer, comps[i].component_version.c_str());
        dsk_json_key(writer, "kind");
        dsk_json_string(writer, comps[i].kind.c_str());
        dsk_json_key(writer, "source");
        dsk_json_u32(writer, comps[i].source);
        dsk_json_end_object(writer);
    }
    dsk_json_end_array(writer);
    dsk_json_end_object(writer);
}

static void dsk_json_write_plan_summary(dsk_json_writer_t *writer,
                                        const dsk_plan_t &plan) {
    dsk_json_begin_object(writer);
    dsk_json_key(writer, "product_id");
    dsk_json_string(writer, plan.product_id.c_str());
    dsk_json_key(writer, "product_version");
    dsk_json_string(writer, plan.product_version.c_str());
    dsk_json_key(writer, "selected_splat_id");
    dsk_json_string(writer, plan.selected_splat_id.c_str());
    dsk_json_key(writer, "operation");
    dsk_json_string(writer, op_to_string(plan.operation));
    dsk_json_key(writer, "install_scope");
    dsk_json_string(writer, scope_to_string(plan.install_scope));
    dsk_json_key(writer, "payload_root");
    dsk_json_string(writer, plan.payload_root.c_str());
    dsk_json_key(writer, "plan_digest64");
    dsk_json_u64_hex(writer, plan.plan_digest64);
    dsk_json_key(writer, "resolved_set_digest64");
    dsk_json_u64_hex(writer, plan.resolved_set_digest64);
    dsk_json_end_object(writer);
}

static dsk_status_t dsk_json_write_plan_payload(dsk_json_writer_t *writer,
                                                const dsk_plan_t &plan) {
    std::string json;
    dsk_status_t st = dsk_plan_dump_json(&plan, &json);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    dsk_json_raw(writer, json.c_str());
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static void dsk_cli_json_begin(dsk_json_writer_t *writer,
                               const char *command,
                               dsk_status_t status,
                               int exit_code,
                               const dsk_cli_artifacts_t &artifacts,
                               const dsk_cli_digests_t &digests) {
    dsk_json_begin_object(writer);
    dsk_json_key(writer, "schema_version");
    dsk_json_string(writer, "setup2-cli-1");
    dsk_json_key(writer, "command");
    dsk_json_string(writer, command ? command : "");
    dsk_json_key(writer, "status");
    dsk_json_string(writer, dsk_error_is_ok(status) ? "ok" : "error");
    dsk_json_key(writer, "status_code");
    dsk_json_u32(writer, (dsk_u32)exit_code);
    dsk_json_key(writer, "artifacts");
    dsk_json_write_artifacts(writer, artifacts);
    dsk_json_key(writer, "digests");
    dsk_json_write_digests(writer, digests);
    dsk_json_key(writer, "details");
    dsk_json_begin_object(writer);
}

static void dsk_cli_json_end(dsk_json_writer_t *writer) {
    dsk_json_end_object(writer);
    dsk_json_end_object(writer);
}

static dsk_bool dsk_cli_parse_bool_option(const dsk_args_view_t *args,
                                          const char *name,
                                          dsk_bool default_value) {
    const char *value;
    dsk_bool parsed = default_value;
    if (!args || !name) {
        return default_value;
    }
    value = dsk_args_get_value(args, name);
    if (!value) {
        return default_value;
    }
    if (dsk_args_parse_bool(value, &parsed)) {
        return parsed;
    }
    return default_value;
}

static dsk_bool dsk_cli_is_json_requested(const dsk_args_view_t *args) {
    const char *format;
    if (!args) {
        return DSK_FALSE;
    }
    if (dsk_args_has_flag(args, "--json")) {
        return DSK_TRUE;
    }
    format = dsk_args_get_value(args, "--format");
    if (!format) {
        return DSK_FALSE;
    }
    return std::strcmp(format, "json") == 0;
}

static dsk_bool dsk_digest_from_bytes(const std::vector<dsk_u8> &bytes,
                                      dsk_u64 *out_digest) {
    if (!out_digest || bytes.empty()) {
        return DSK_FALSE;
    }
    *out_digest = dsk_digest64_bytes(&bytes[0], (dsk_u32)bytes.size());
    return DSK_TRUE;
}

static bool dsk_template_less(const dsk_layout_template_t &a,
                              const dsk_layout_template_t &b) {
    return a.template_id < b.template_id;
}

static bool dsk_component_less_by_id(const dsk_manifest_component_t &a,
                                     const dsk_manifest_component_t &b) {
    return a.component_id < b.component_id;
}

static bool dsk_artifact_less_by_id(const dsk_artifact_t &a, const dsk_artifact_t &b) {
    return a.artifact_id < b.artifact_id;
}

static void dsk_json_write_manifest(dsk_json_writer_t *writer,
                                    const dsk_manifest_t &manifest) {
    std::vector<dsk_layout_template_t> templates = manifest.layout_templates;
    std::vector<dsk_manifest_component_t> components = manifest.components;
    size_t i;

    std::sort(templates.begin(), templates.end(), dsk_template_less);
    std::sort(components.begin(), components.end(), dsk_component_less_by_id);

    dsk_json_begin_object(writer);
    dsk_json_key(writer, "product_id");
    dsk_json_string(writer, manifest.product_id.c_str());
    dsk_json_key(writer, "version");
    dsk_json_string(writer, manifest.version.c_str());
    dsk_json_key(writer, "build_id");
    dsk_json_string(writer, manifest.build_id.c_str());
    dsk_json_key(writer, "supported_targets");
    dsk_json_write_string_list_sorted(writer, manifest.supported_targets);
    dsk_json_key(writer, "allowed_splats");
    dsk_json_write_string_list_sorted(writer, manifest.allowed_splats);
    dsk_json_key(writer, "layout_templates");
    dsk_json_begin_array(writer);
    for (i = 0u; i < templates.size(); ++i) {
        dsk_json_begin_object(writer);
        dsk_json_key(writer, "template_id");
        dsk_json_string(writer, templates[i].template_id.c_str());
        dsk_json_key(writer, "target_root");
        dsk_json_string(writer, templates[i].target_root.c_str());
        dsk_json_key(writer, "path_prefix");
        dsk_json_string(writer, templates[i].path_prefix.c_str());
        dsk_json_end_object(writer);
    }
    dsk_json_end_array(writer);
    dsk_json_key(writer, "components");
    dsk_json_begin_array(writer);
    for (i = 0u; i < components.size(); ++i) {
        dsk_manifest_component_t comp = components[i];
        std::vector<std::string> deps = comp.deps;
        std::vector<std::string> conflicts = comp.conflicts;
        std::vector<std::string> targets = comp.supported_targets;
        std::vector<dsk_artifact_t> artifacts = comp.artifacts;
        size_t j;

        std::sort(deps.begin(), deps.end());
        std::sort(conflicts.begin(), conflicts.end());
        std::sort(targets.begin(), targets.end());
        std::sort(artifacts.begin(), artifacts.end(), dsk_artifact_less_by_id);

        dsk_json_begin_object(writer);
        dsk_json_key(writer, "component_id");
        dsk_json_string(writer, comp.component_id.c_str());
        dsk_json_key(writer, "component_version");
        dsk_json_string(writer, comp.component_version.c_str());
        dsk_json_key(writer, "kind");
        dsk_json_string(writer, comp.kind.c_str());
        dsk_json_key(writer, "default_selected");
        dsk_json_bool(writer, comp.default_selected);
        dsk_json_key(writer, "deps");
        dsk_json_begin_array(writer);
        for (j = 0u; j < deps.size(); ++j) {
            dsk_json_string(writer, deps[j].c_str());
        }
        dsk_json_end_array(writer);
        dsk_json_key(writer, "conflicts");
        dsk_json_begin_array(writer);
        for (j = 0u; j < conflicts.size(); ++j) {
            dsk_json_string(writer, conflicts[j].c_str());
        }
        dsk_json_end_array(writer);
        dsk_json_key(writer, "supported_targets");
        dsk_json_begin_array(writer);
        for (j = 0u; j < targets.size(); ++j) {
            dsk_json_string(writer, targets[j].c_str());
        }
        dsk_json_end_array(writer);
        dsk_json_key(writer, "artifacts");
        dsk_json_begin_array(writer);
        for (j = 0u; j < artifacts.size(); ++j) {
            dsk_json_begin_object(writer);
            dsk_json_key(writer, "artifact_id");
            dsk_json_string(writer, artifacts[j].artifact_id.c_str());
            dsk_json_key(writer, "source_path");
            dsk_json_string(writer, artifacts[j].source_path.c_str());
            dsk_json_key(writer, "size");
            dsk_json_u64(writer, artifacts[j].size);
            dsk_json_key(writer, "digest64");
            dsk_json_u64_hex(writer, artifacts[j].digest64);
            dsk_json_key(writer, "layout_template_id");
            dsk_json_string(writer, artifacts[j].layout_template_id.c_str());
            dsk_json_key(writer, "hash");
            dsk_json_string(writer, artifacts[j].hash.c_str());
            dsk_json_end_object(writer);
        }
        dsk_json_end_array(writer);
        dsk_json_end_object(writer);
    }
    dsk_json_end_array(writer);
    dsk_json_end_object(writer);
}

static void dsk_json_write_request(dsk_json_writer_t *writer,
                                   const dsk_request_t &request) {
    dsk_json_begin_object(writer);
    dsk_json_key(writer, "operation");
    dsk_json_string(writer, op_to_string(request.operation));
    dsk_json_key(writer, "install_scope");
    dsk_json_string(writer, scope_to_string(request.install_scope));
    dsk_json_key(writer, "ui_mode");
    dsk_json_string(writer, ui_mode_to_string(request.ui_mode));
    dsk_json_key(writer, "policy_flags");
    dsk_json_u32(writer, request.policy_flags);
    dsk_json_key(writer, "target_platform_triple");
    dsk_json_string(writer, request.target_platform_triple.c_str());
    dsk_json_key(writer, "preferred_install_root");
    dsk_json_string(writer, request.preferred_install_root.c_str());
    dsk_json_key(writer, "payload_root");
    dsk_json_string(writer, request.payload_root.c_str());
    dsk_json_key(writer, "requested_splat_id");
    dsk_json_string(writer, request.requested_splat_id.c_str());
    dsk_json_key(writer, "required_caps");
    dsk_json_u32(writer, request.required_caps);
    dsk_json_key(writer, "prohibited_caps");
    dsk_json_u32(writer, request.prohibited_caps);
    dsk_json_key(writer, "ownership_preference");
    dsk_json_string(writer, ownership_to_string(request.ownership_preference));
    dsk_json_key(writer, "requested_components");
    dsk_json_write_string_list_sorted(writer, request.requested_components);
    dsk_json_key(writer, "excluded_components");
    dsk_json_write_string_list_sorted(writer, request.excluded_components);
    dsk_json_end_object(writer);
}

static void print_usage(void) {
    std::printf("dominium-setup2 manifest validate --in <file> [--json]\n");
    std::printf("dominium-setup2 manifest dump --in <file> --out <file> --format json [--json]\n");
    std::printf("dominium-setup2 request validate --in <file> [--json]\n");
    std::printf("dominium-setup2 request dump --in <file> --out <file> --format json [--json]\n");
    std::printf("dominium-setup2 request make --manifest <file> --op <install|upgrade|repair|uninstall|verify|status>\n");
    std::printf("  --scope <user|system|portable> --ui-mode <cli|tui|gui>\n");
    std::printf("  [--components <csv>] [--exclude <csv>] [--root <path>] --out-request <file>\n");
    std::printf("  [--deterministic 0|1] [--json]\n");
    std::printf("dominium-setup2 plan --manifest <file> --request <file> --out-plan <file> [--json]\n");
    std::printf("dominium-setup2 resolve --manifest <file> --request <file> [--json]\n");
    std::printf("dominium-setup2 dump-plan --plan <file> [--json]\n");
    std::printf("dominium-setup2 apply --plan <file> [--out-state <file>] [--out-audit <file>] [--out-journal <file>] [--dry-run] [--json]\n");
    std::printf("dominium-setup2 resume --journal <file> [--out-state <file>] [--out-audit <file>] [--json]\n");
    std::printf("dominium-setup2 rollback --journal <file> [--out-audit <file>] [--json]\n");
    std::printf("dominium-setup2 status --journal <file> [--json]\n");
    std::printf("dominium-setup2 verify --state <file> [--format json|txt] [--json]\n");
    std::printf("dominium-setup2 uninstall-preview --state <file> [--components <csv>] [--format json|txt] [--json]\n");
    std::printf("dominium-setup2 dump-splats [--json]\n");
    std::printf("dominium-setup2 select-splat --manifest <file> --request <file> [--json]\n");
    std::printf("options: --use-fake-services <sandbox_root>\n");
}

static const char *get_arg_value(int argc, char **argv, const char *name) {
    int i;
    for (i = 2; i < argc - 1; ++i) {
        if (std::strcmp(argv[i], name) == 0) {
            return argv[i + 1];
        }
    }
    return 0;
}

static int finish(dss_services_t *services, int code) {
    if (services) {
        dss_services_shutdown(services);
    }
    return code;
}

int main(int argc, char **argv) {
    dss_services_t services;
    dss_services_config_t services_cfg;
    dss_error_t services_st;
    const char *fake_root = get_arg_value(argc, argv, "--use-fake-services");

    if (argc < 2) {
        print_usage();
        return 1;
    }

    dss_services_config_init(&services_cfg);
    if (fake_root) {
        services_cfg.sandbox_root = fake_root;
        services_st = dss_services_init_fake(&services_cfg, &services);
    } else {
        services_st = dss_services_init_real(&services);
    }
    if (!dss_error_is_ok(services_st)) {
        std::fprintf(stderr, "error: failed to init services\n");
        return 1;
    }

    if (std::strcmp(argv[1], "manifest") == 0) {
        if (argc < 3) {
            print_usage();
            return finish(&services, 1);
        }
        dsk_args_view_t args;
        dsk_args_view_init(&args, argc, argv, 3);
        if (std::strcmp(argv[2], "validate") == 0) {
            const char *path = dsk_args_get_value(&args, "--in");
            dsk_bool json = dsk_cli_is_json_requested(&args);
            std::vector<dsk_u8> bytes;
            dsk_manifest_t manifest;
            dsk_status_t st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
            if (!path) {
                st = dsk_error_make(DSK_DOMAIN_FRONTEND,
                                    DSK_CODE_INVALID_ARGS,
                                    DSK_SUBCODE_MISSING_FIELD,
                                    DSK_ERROR_FLAG_USER_ACTIONABLE);
            } else if (!load_file(&services.fs, path, bytes)) {
                st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                    DSK_CODE_IO_ERROR,
                                    DSK_SUBCODE_NONE,
                                    0u);
            } else {
                st = dsk_manifest_parse(&bytes[0], (dsk_u32)bytes.size(), &manifest);
            }
            if (json) {
                dsk_cli_artifacts_t artifacts = dsk_cli_artifacts_empty();
                dsk_cli_digests_t digests = dsk_cli_digests_empty();
                dsk_json_writer_t writer;
                artifacts.manifest = path ? path : "";
                digests.has_manifest = dsk_digest_from_bytes(bytes, &digests.manifest);
                dsk_json_writer_init(&writer);
                dsk_cli_json_begin(&writer,
                                   "manifest validate",
                                   st,
                                   dsk_error_to_exit_code(st),
                                   artifacts,
                                   digests);
                dsk_json_key(&writer, "error");
                dsk_json_write_error(&writer, st);
                dsk_json_key(&writer, "valid");
                dsk_json_bool(&writer, dsk_error_is_ok(st));
                dsk_cli_json_end(&writer);
                std::printf("%s\n", dsk_json_writer_str(&writer).c_str());
            } else if (dsk_error_is_ok(st)) {
                std::printf("ok\n");
            } else {
                std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
            }
            return finish(&services, dsk_error_to_exit_code(st));
        }
        if (std::strcmp(argv[2], "dump") == 0) {
            const char *path = dsk_args_get_value(&args, "--in");
            const char *out_path = dsk_args_get_value(&args, "--out");
            const char *format = dsk_args_get_value(&args, "--format");
            dsk_bool json = dsk_cli_is_json_requested(&args);
            std::vector<dsk_u8> bytes;
            dsk_manifest_t manifest;
            dsk_status_t st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
            std::string payload;
            if (!path || !out_path || !format || std::strcmp(format, "json") != 0) {
                st = dsk_error_make(DSK_DOMAIN_FRONTEND,
                                    DSK_CODE_INVALID_ARGS,
                                    DSK_SUBCODE_MISSING_FIELD,
                                    DSK_ERROR_FLAG_USER_ACTIONABLE);
            } else if (!load_file(&services.fs, path, bytes)) {
                st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                    DSK_CODE_IO_ERROR,
                                    DSK_SUBCODE_NONE,
                                    0u);
            } else {
                st = dsk_manifest_parse(&bytes[0], (dsk_u32)bytes.size(), &manifest);
            }
            if (dsk_error_is_ok(st)) {
                dsk_json_writer_t json_writer;
                dsk_json_writer_init(&json_writer);
                dsk_json_write_manifest(&json_writer, manifest);
                payload = dsk_json_writer_str(&json_writer);
                if (!write_file(&services.fs,
                                out_path,
                                std::vector<dsk_u8>(payload.begin(), payload.end()))) {
                    st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                        DSK_CODE_IO_ERROR,
                                        DSK_SUBCODE_NONE,
                                        0u);
                }
            }
            if (json) {
                dsk_cli_artifacts_t artifacts = dsk_cli_artifacts_empty();
                dsk_cli_digests_t digests = dsk_cli_digests_empty();
                dsk_json_writer_t writer;
                artifacts.manifest = path ? path : "";
                digests.has_manifest = dsk_digest_from_bytes(bytes, &digests.manifest);
                dsk_json_writer_init(&writer);
                dsk_cli_json_begin(&writer,
                                   "manifest dump",
                                   st,
                                   dsk_error_to_exit_code(st),
                                   artifacts,
                                   digests);
                dsk_json_key(&writer, "error");
                dsk_json_write_error(&writer, st);
                dsk_json_key(&writer, "format");
                dsk_json_string(&writer, format ? format : "");
                dsk_json_key(&writer, "output_path");
                dsk_json_string(&writer, out_path ? out_path : "");
                dsk_json_key(&writer, "output_bytes");
                dsk_json_u32(&writer, (dsk_u32)payload.size());
                dsk_cli_json_end(&writer);
                std::printf("%s\n", dsk_json_writer_str(&writer).c_str());
            } else if (dsk_error_is_ok(st)) {
                std::printf("ok\n");
            } else {
                std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
            }
            return finish(&services, dsk_error_to_exit_code(st));
        }
        print_usage();
        return finish(&services, 1);
    }

    if (std::strcmp(argv[1], "request") == 0) {
        if (argc < 3) {
            print_usage();
            return finish(&services, 1);
        }
        dsk_args_view_t args;
        dsk_args_view_init(&args, argc, argv, 3);
        if (std::strcmp(argv[2], "validate") == 0) {
            const char *path = dsk_args_get_value(&args, "--in");
            dsk_bool json = dsk_cli_is_json_requested(&args);
            std::vector<dsk_u8> bytes;
            dsk_request_t request;
            dsk_status_t st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
            if (!path) {
                st = dsk_error_make(DSK_DOMAIN_FRONTEND,
                                    DSK_CODE_INVALID_ARGS,
                                    DSK_SUBCODE_MISSING_FIELD,
                                    DSK_ERROR_FLAG_USER_ACTIONABLE);
            } else if (!load_file(&services.fs, path, bytes)) {
                st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                    DSK_CODE_IO_ERROR,
                                    DSK_SUBCODE_NONE,
                                    0u);
            } else {
                st = dsk_request_parse(&bytes[0], (dsk_u32)bytes.size(), &request);
            }
            if (json) {
                dsk_cli_artifacts_t artifacts = dsk_cli_artifacts_empty();
                dsk_cli_digests_t digests = dsk_cli_digests_empty();
                dsk_json_writer_t writer;
                artifacts.request = path ? path : "";
                digests.has_request = dsk_digest_from_bytes(bytes, &digests.request);
                dsk_json_writer_init(&writer);
                dsk_cli_json_begin(&writer,
                                   "request validate",
                                   st,
                                   dsk_error_to_exit_code(st),
                                   artifacts,
                                   digests);
                dsk_json_key(&writer, "error");
                dsk_json_write_error(&writer, st);
                dsk_json_key(&writer, "valid");
                dsk_json_bool(&writer, dsk_error_is_ok(st));
                dsk_cli_json_end(&writer);
                std::printf("%s\n", dsk_json_writer_str(&writer).c_str());
            } else if (dsk_error_is_ok(st)) {
                std::printf("ok\n");
            } else {
                std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
            }
            return finish(&services, dsk_error_to_exit_code(st));
        }
        if (std::strcmp(argv[2], "dump") == 0) {
            const char *path = dsk_args_get_value(&args, "--in");
            const char *out_path = dsk_args_get_value(&args, "--out");
            const char *format = dsk_args_get_value(&args, "--format");
            dsk_bool json = dsk_cli_is_json_requested(&args);
            std::vector<dsk_u8> bytes;
            dsk_request_t request;
            dsk_status_t st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
            std::string payload;
            if (!path || !out_path || !format || std::strcmp(format, "json") != 0) {
                st = dsk_error_make(DSK_DOMAIN_FRONTEND,
                                    DSK_CODE_INVALID_ARGS,
                                    DSK_SUBCODE_MISSING_FIELD,
                                    DSK_ERROR_FLAG_USER_ACTIONABLE);
            } else if (!load_file(&services.fs, path, bytes)) {
                st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                    DSK_CODE_IO_ERROR,
                                    DSK_SUBCODE_NONE,
                                    0u);
            } else {
                st = dsk_request_parse(&bytes[0], (dsk_u32)bytes.size(), &request);
            }
            if (dsk_error_is_ok(st)) {
                dsk_json_writer_t json_writer;
                dsk_json_writer_init(&json_writer);
                dsk_json_write_request(&json_writer, request);
                payload = dsk_json_writer_str(&json_writer);
                if (!write_file(&services.fs,
                                out_path,
                                std::vector<dsk_u8>(payload.begin(), payload.end()))) {
                    st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                        DSK_CODE_IO_ERROR,
                                        DSK_SUBCODE_NONE,
                                        0u);
                }
            }
            if (json) {
                dsk_cli_artifacts_t artifacts = dsk_cli_artifacts_empty();
                dsk_cli_digests_t digests = dsk_cli_digests_empty();
                dsk_json_writer_t writer;
                artifacts.request = path ? path : "";
                digests.has_request = dsk_digest_from_bytes(bytes, &digests.request);
                dsk_json_writer_init(&writer);
                dsk_cli_json_begin(&writer,
                                   "request dump",
                                   st,
                                   dsk_error_to_exit_code(st),
                                   artifacts,
                                   digests);
                dsk_json_key(&writer, "error");
                dsk_json_write_error(&writer, st);
                dsk_json_key(&writer, "format");
                dsk_json_string(&writer, format ? format : "");
                dsk_json_key(&writer, "output_path");
                dsk_json_string(&writer, out_path ? out_path : "");
                dsk_json_key(&writer, "output_bytes");
                dsk_json_u32(&writer, (dsk_u32)payload.size());
                dsk_cli_json_end(&writer);
                std::printf("%s\n", dsk_json_writer_str(&writer).c_str());
            } else if (dsk_error_is_ok(st)) {
                std::printf("ok\n");
            } else {
                std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
            }
            return finish(&services, dsk_error_to_exit_code(st));
        }
        if (std::strcmp(argv[2], "make") == 0) {
            const char *manifest_path = dsk_args_get_value(&args, "--manifest");
            const char *op = dsk_args_get_value(&args, "--op");
            const char *scope = dsk_args_get_value(&args, "--scope");
            const char *ui_mode = dsk_args_get_value(&args, "--ui-mode");
            const char *components = dsk_args_get_value(&args, "--components");
            const char *exclude = dsk_args_get_value(&args, "--exclude");
            const char *root = dsk_args_get_value(&args, "--root");
            const char *out_request = dsk_args_get_value(&args, "--out-request");
            dsk_bool json = dsk_cli_is_json_requested(&args);
            dsk_bool deterministic = dsk_cli_parse_bool_option(&args, "--deterministic", DSK_TRUE);
            dsk_request_build_opts_t opts;
            std::vector<std::string> component_list;
            std::vector<std::string> exclude_list;
            std::vector<dsk_u8> request_bytes;
            dsk_request_t request;
            dsk_status_t st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);

            dsk_request_clear(&request);
            if (components) {
                dsk_args_split_csv(components, &component_list);
            }
            if (exclude) {
                dsk_args_split_csv(exclude, &exclude_list);
            }

            dsk_request_build_opts_init(&opts);
            opts.manifest_path = manifest_path ? manifest_path : "";
            opts.operation = dsk_request_parse_operation(op);
            opts.install_scope = dsk_request_parse_scope(scope);
            opts.ui_mode = dsk_request_parse_ui_mode(ui_mode);
            opts.policy_flags = deterministic ? DSK_POLICY_DETERMINISTIC : 0u;
            opts.preferred_install_root = root ? root : "";
            opts.requested_components = component_list;
            opts.excluded_components = exclude_list;

            if (!manifest_path || !op || !scope || !ui_mode || !out_request ||
                opts.operation == 0u || opts.install_scope == 0u || opts.ui_mode == 0u) {
                st = dsk_error_make(DSK_DOMAIN_FRONTEND,
                                    DSK_CODE_INVALID_ARGS,
                                    DSK_SUBCODE_MISSING_FIELD,
                                    DSK_ERROR_FLAG_USER_ACTIONABLE);
            } else {
                st = dsk_request_build_bytes(&opts, &services, &request_bytes, &request);
            }

            if (dsk_error_is_ok(st)) {
                if (!write_file(&services.fs, out_request, request_bytes)) {
                    st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                        DSK_CODE_IO_ERROR,
                                        DSK_SUBCODE_NONE,
                                        0u);
                }
            }

            if (json) {
                dsk_cli_artifacts_t artifacts = dsk_cli_artifacts_empty();
                dsk_cli_digests_t digests = dsk_cli_digests_empty();
                dsk_json_writer_t writer;
                artifacts.request = out_request ? out_request : "";
                digests.has_request = dsk_digest_from_bytes(request_bytes, &digests.request);
                dsk_json_writer_init(&writer);
                dsk_cli_json_begin(&writer,
                                   "request make",
                                   st,
                                   dsk_error_to_exit_code(st),
                                   artifacts,
                                   digests);
                dsk_json_key(&writer, "error");
                dsk_json_write_error(&writer, st);
                dsk_json_key(&writer, "operation");
                dsk_json_string(&writer, op_to_string(request.operation));
                dsk_json_key(&writer, "install_scope");
                dsk_json_string(&writer, scope_to_string(request.install_scope));
                dsk_json_key(&writer, "ui_mode");
                dsk_json_string(&writer, ui_mode_to_string(request.ui_mode));
                dsk_json_key(&writer, "requested_component_count");
                dsk_json_u32(&writer, (dsk_u32)request.requested_components.size());
                dsk_json_key(&writer, "excluded_component_count");
                dsk_json_u32(&writer, (dsk_u32)request.excluded_components.size());
                dsk_cli_json_end(&writer);
                std::printf("%s\n", dsk_json_writer_str(&writer).c_str());
            } else if (dsk_error_is_ok(st)) {
                std::printf("ok\n");
            } else {
                std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
            }

            return finish(&services, dsk_error_to_exit_code(st));
        }
        print_usage();
        return finish(&services, 1);
    }

    if (std::strcmp(argv[1], "validate-manifest") == 0) {
        const char *path = get_arg_value(argc, argv, "--in");
        std::vector<dsk_u8> bytes;
        dsk_manifest_t manifest;
        dsk_status_t st;
        if (!path || !load_file(&services.fs, path, bytes)) {
            std::fprintf(stderr, "error: failed to read manifest\n");
            return finish(&services, 1);
        }
        st = dsk_manifest_parse(&bytes[0], (dsk_u32)bytes.size(), &manifest);
        if (!dsk_error_is_ok(st)) {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
            return finish(&services, dsk_error_to_exit_code(st));
        }
        std::printf("ok\n");
        return finish(&services, 0);
    }

    if (std::strcmp(argv[1], "validate-request") == 0) {
        const char *path = get_arg_value(argc, argv, "--in");
        std::vector<dsk_u8> bytes;
        dsk_request_t request;
        dsk_status_t st;
        if (!path || !load_file(&services.fs, path, bytes)) {
            std::fprintf(stderr, "error: failed to read request\n");
            return finish(&services, 1);
        }
        st = dsk_request_parse(&bytes[0], (dsk_u32)bytes.size(), &request);
        if (!dsk_error_is_ok(st)) {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
            return finish(&services, dsk_error_to_exit_code(st));
        }
        std::printf("ok\n");
        return finish(&services, 0);
    }

    if (std::strcmp(argv[1], "dump-splats") == 0) {
        std::vector<dsk_splat_candidate_t> splats;
        size_t i;
        dsk_args_view_t args;
        dsk_args_view_init(&args, argc, argv, 2);
        dsk_bool json = dsk_cli_is_json_requested(&args);
        dsk_status_t st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        dsk_splat_registry_list(splats);
        if (json) {
            dsk_cli_artifacts_t artifacts = dsk_cli_artifacts_empty();
            dsk_cli_digests_t digests = dsk_cli_digests_empty();
            dsk_json_writer_t writer;
            dsk_json_writer_init(&writer);
            dsk_cli_json_begin(&writer,
                               "dump-splats",
                               st,
                               dsk_error_to_exit_code(st),
                               artifacts,
                               digests);
            dsk_json_key(&writer, "error");
            dsk_json_write_error(&writer, st);
            dsk_json_key(&writer, "count");
            dsk_json_u32(&writer, (dsk_u32)splats.size());
            dsk_json_key(&writer, "splats");
            dsk_json_write_splat_registry(&writer, splats);
            dsk_cli_json_end(&writer);
            std::printf("%s\n", dsk_json_writer_str(&writer).c_str());
        } else {
            for (i = 0u; i < splats.size(); ++i) {
                std::printf("%s\n", splats[i].id.c_str());
            }
        }
        return finish(&services, 0);
    }

    if (std::strcmp(argv[1], "select-splat") == 0) {
        const char *manifest_path = get_arg_value(argc, argv, "--manifest");
        const char *request_path = get_arg_value(argc, argv, "--request");
        dsk_args_view_t args;
        dsk_args_view_init(&args, argc, argv, 2);
        dsk_bool json = dsk_cli_is_json_requested(&args);
        std::vector<dsk_u8> manifest_bytes;
        std::vector<dsk_u8> request_bytes;
        dsk_manifest_t manifest;
        dsk_request_t request;
        dsk_splat_selection_t selection;
        dsk_status_t st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);

        if (!manifest_path || !request_path) {
            st = dsk_error_make(DSK_DOMAIN_FRONTEND,
                                DSK_CODE_INVALID_ARGS,
                                DSK_SUBCODE_MISSING_FIELD,
                                DSK_ERROR_FLAG_USER_ACTIONABLE);
        } else if (!load_file(&services.fs, manifest_path, manifest_bytes)) {
            st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                DSK_CODE_IO_ERROR,
                                DSK_SUBCODE_NONE,
                                0u);
        } else if (!load_file(&services.fs, request_path, request_bytes)) {
            st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                DSK_CODE_IO_ERROR,
                                DSK_SUBCODE_NONE,
                                0u);
        }

        if (dsk_error_is_ok(st)) {
            st = dsk_manifest_parse(&manifest_bytes[0],
                                    (dsk_u32)manifest_bytes.size(),
                                    &manifest);
        }
        if (dsk_error_is_ok(st)) {
            st = dsk_request_parse(&request_bytes[0],
                                   (dsk_u32)request_bytes.size(),
                                   &request);
        }
        if (dsk_error_is_ok(st)) {
            if (services.platform.get_platform_triple) {
                std::string platform_override;
                dss_error_t pst = services.platform.get_platform_triple(services.platform.ctx,
                                                                        &platform_override);
                if (dss_error_is_ok(pst) && !platform_override.empty()) {
                    request.target_platform_triple = platform_override;
                }
            }
            st = dsk_splat_select(manifest, request, &selection);
        }
        if (json) {
            dsk_cli_artifacts_t artifacts = dsk_cli_artifacts_empty();
            dsk_cli_digests_t digests = dsk_cli_digests_empty();
            dsk_json_writer_t writer;
            artifacts.manifest = manifest_path ? manifest_path : "";
            artifacts.request = request_path ? request_path : "";
            digests.has_manifest = dsk_digest_from_bytes(manifest_bytes, &digests.manifest);
            digests.has_request = dsk_digest_from_bytes(request_bytes, &digests.request);
            dsk_json_writer_init(&writer);
            dsk_cli_json_begin(&writer,
                               "select-splat",
                               st,
                               dsk_error_to_exit_code(st),
                               artifacts,
                               digests);
            dsk_json_key(&writer, "error");
            dsk_json_write_error(&writer, st);
            dsk_json_key(&writer, "selection");
            dsk_json_write_selection(&writer, selection, st);
            dsk_cli_json_end(&writer);
            std::printf("%s\n", dsk_json_writer_str(&writer).c_str());
        } else if (dsk_error_is_ok(st)) {
            std::printf("%s\n", selection.selected_id.c_str());
        } else {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
        }
        return finish(&services, dsk_error_to_exit_code(st));
    }

    if (std::strcmp(argv[1], "plan") == 0) {
        const char *manifest_path = get_arg_value(argc, argv, "--manifest");
        const char *request_path = get_arg_value(argc, argv, "--request");
        const char *out_plan = get_arg_value(argc, argv, "--out-plan");
        dsk_args_view_t args;
        dsk_args_view_init(&args, argc, argv, 2);
        dsk_bool json = dsk_cli_is_json_requested(&args);
        std::vector<dsk_u8> manifest_bytes;
        std::vector<dsk_u8> request_bytes;
        dsk_request_t request;
        dsk_kernel_request_ex_t kernel_req;
        dsk_mem_sink_t plan_sink;
        dsk_mem_sink_t state_sink;
        dsk_mem_sink_t audit_sink;
        dsk_status_t st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        dsk_plan_t plan;

        if (!manifest_path || !request_path || !out_plan) {
            st = dsk_error_make(DSK_DOMAIN_FRONTEND,
                                DSK_CODE_INVALID_ARGS,
                                DSK_SUBCODE_MISSING_FIELD,
                                DSK_ERROR_FLAG_USER_ACTIONABLE);
        } else if (!load_file(&services.fs, manifest_path, manifest_bytes)) {
            st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                DSK_CODE_IO_ERROR,
                                DSK_SUBCODE_NONE,
                                0u);
        } else if (!load_file(&services.fs, request_path, request_bytes)) {
            st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                DSK_CODE_IO_ERROR,
                                DSK_SUBCODE_NONE,
                                0u);
        } else {
            st = dsk_request_parse(&request_bytes[0], (dsk_u32)request_bytes.size(), &request);
        }

        if (dsk_error_is_ok(st)) {
            dsk_kernel_request_ex_init(&kernel_req);
            kernel_req.base.manifest_bytes = &manifest_bytes[0];
            kernel_req.base.manifest_size = (dsk_u32)manifest_bytes.size();
            kernel_req.base.request_bytes = &request_bytes[0];
            kernel_req.base.request_size = (dsk_u32)request_bytes.size();
            kernel_req.base.services = &services;
            kernel_req.base.deterministic_mode = (request.policy_flags & DSK_POLICY_DETERMINISTIC) ? 1u : 0u;
            kernel_req.base.out_plan.user = &plan_sink;
            kernel_req.base.out_plan.write = dsk_mem_sink_write;
            kernel_req.base.out_state.user = &state_sink;
            kernel_req.base.out_state.write = dsk_mem_sink_write;
            kernel_req.base.out_audit.user = &audit_sink;
            kernel_req.base.out_audit.write = dsk_mem_sink_write;

            switch (request.operation) {
            case DSK_OPERATION_INSTALL:
                st = dsk_install_ex(&kernel_req);
                break;
            case DSK_OPERATION_UPGRADE:
                st = dsk_upgrade_ex(&kernel_req);
                break;
            case DSK_OPERATION_REPAIR:
                st = dsk_repair_ex(&kernel_req);
                break;
            case DSK_OPERATION_UNINSTALL:
                st = dsk_uninstall_ex(&kernel_req);
                break;
            case DSK_OPERATION_VERIFY:
                st = dsk_verify_ex(&kernel_req);
                break;
            case DSK_OPERATION_STATUS:
                st = dsk_status_ex(&kernel_req);
                break;
            default:
                st = dsk_error_make(DSK_DOMAIN_FRONTEND,
                                    DSK_CODE_VALIDATION_ERROR,
                                    DSK_SUBCODE_INVALID_FIELD,
                                    DSK_ERROR_FLAG_USER_ACTIONABLE);
                break;
            }
        }

        if (dsk_error_is_ok(st) && plan_sink.data.empty()) {
            st = dsk_error_make(DSK_DOMAIN_KERNEL,
                                DSK_CODE_INTERNAL_ERROR,
                                DSK_SUBCODE_NONE,
                                0u);
        }
        if (dsk_error_is_ok(st)) {
            if (!write_file(&services.fs, out_plan, plan_sink.data)) {
                st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                    DSK_CODE_IO_ERROR,
                                    DSK_SUBCODE_NONE,
                                    0u);
            }
        }

        if (json) {
            dsk_cli_artifacts_t artifacts = dsk_cli_artifacts_empty();
            dsk_cli_digests_t digests = dsk_cli_digests_empty();
            dsk_json_writer_t writer;
            artifacts.manifest = manifest_path ? manifest_path : "";
            artifacts.request = request_path ? request_path : "";
            artifacts.plan = out_plan ? out_plan : "";
            digests.has_manifest = dsk_digest_from_bytes(manifest_bytes, &digests.manifest);
            digests.has_request = dsk_digest_from_bytes(request_bytes, &digests.request);
            if (dsk_error_is_ok(st)) {
                dsk_status_t parse_st = dsk_plan_parse(&plan_sink.data[0],
                                                       (dsk_u32)plan_sink.data.size(),
                                                       &plan);
                if (dsk_error_is_ok(parse_st)) {
                    digests.has_plan = DSK_TRUE;
                    digests.plan = plan.plan_digest64;
                }
            }
            dsk_json_writer_init(&writer);
            dsk_cli_json_begin(&writer,
                               "plan",
                               st,
                               dsk_error_to_exit_code(st),
                               artifacts,
                               digests);
            dsk_json_key(&writer, "error");
            dsk_json_write_error(&writer, st);
            if (dsk_error_is_ok(st)) {
                dsk_json_key(&writer, "plan");
                dsk_json_write_plan_summary(&writer, plan);
            }
            dsk_cli_json_end(&writer);
            std::printf("%s\n", dsk_json_writer_str(&writer).c_str());
        } else if (!dsk_error_is_ok(st)) {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
        } else {
            std::printf("ok\n");
        }

        return finish(&services, dsk_error_to_exit_code(st));
    }

    if (std::strcmp(argv[1], "dump-plan") == 0) {
        const char *plan_path = get_arg_value(argc, argv, "--plan");
        dsk_args_view_t args;
        dsk_args_view_init(&args, argc, argv, 2);
        dsk_bool json = dsk_cli_is_json_requested(&args);
        std::vector<dsk_u8> plan_bytes;
        dsk_plan_t plan;
        dsk_status_t st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);

        if (!plan_path) {
            st = dsk_error_make(DSK_DOMAIN_FRONTEND,
                                DSK_CODE_INVALID_ARGS,
                                DSK_SUBCODE_MISSING_FIELD,
                                DSK_ERROR_FLAG_USER_ACTIONABLE);
        } else if (!load_file(&services.fs, plan_path, plan_bytes)) {
            st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                DSK_CODE_IO_ERROR,
                                DSK_SUBCODE_NONE,
                                0u);
        } else {
            st = dsk_plan_parse(&plan_bytes[0], (dsk_u32)plan_bytes.size(), &plan);
        }
        if (json) {
            dsk_cli_artifacts_t artifacts = dsk_cli_artifacts_empty();
            dsk_cli_digests_t digests = dsk_cli_digests_empty();
            dsk_json_writer_t writer;
            artifacts.plan = plan_path ? plan_path : "";
            if (dsk_error_is_ok(st)) {
                digests.has_plan = DSK_TRUE;
                digests.plan = plan.plan_digest64;
                digests.has_manifest = DSK_TRUE;
                digests.manifest = plan.manifest_digest64;
                digests.has_request = DSK_TRUE;
                digests.request = plan.request_digest64;
            }
            dsk_json_writer_init(&writer);
            dsk_cli_json_begin(&writer,
                               "dump-plan",
                               st,
                               dsk_error_to_exit_code(st),
                               artifacts,
                               digests);
            dsk_json_key(&writer, "error");
            dsk_json_write_error(&writer, st);
            if (dsk_error_is_ok(st)) {
                dsk_json_key(&writer, "plan");
                dsk_status_t json_st = dsk_json_write_plan_payload(&writer, plan);
                if (!dsk_error_is_ok(json_st)) {
                    dsk_json_key(&writer, "plan_error");
                    dsk_json_write_error(&writer, json_st);
                }
            }
            dsk_cli_json_end(&writer);
            std::printf("%s\n", dsk_json_writer_str(&writer).c_str());
        } else if (dsk_error_is_ok(st)) {
            std::printf("ok\n");
        } else {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
        }
        return finish(&services, dsk_error_to_exit_code(st));
    }

    if (std::strcmp(argv[1], "resolve") == 0) {
        const char *manifest_path = get_arg_value(argc, argv, "--manifest");
        const char *request_path = get_arg_value(argc, argv, "--request");
        dsk_args_view_t args;
        dsk_args_view_init(&args, argc, argv, 2);
        dsk_bool json = dsk_cli_is_json_requested(&args);
        std::vector<dsk_u8> manifest_bytes;
        std::vector<dsk_u8> request_bytes;
        dsk_request_t request;
        dsk_kernel_request_ex_t kernel_req;
        dsk_mem_sink_t plan_sink;
        dsk_mem_sink_t state_sink;
        dsk_mem_sink_t audit_sink;
        dsk_status_t st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        dsk_plan_t plan;

        if (!manifest_path || !request_path) {
            st = dsk_error_make(DSK_DOMAIN_FRONTEND,
                                DSK_CODE_INVALID_ARGS,
                                DSK_SUBCODE_MISSING_FIELD,
                                DSK_ERROR_FLAG_USER_ACTIONABLE);
        } else if (!load_file(&services.fs, manifest_path, manifest_bytes)) {
            st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                DSK_CODE_IO_ERROR,
                                DSK_SUBCODE_NONE,
                                0u);
        } else if (!load_file(&services.fs, request_path, request_bytes)) {
            st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                DSK_CODE_IO_ERROR,
                                DSK_SUBCODE_NONE,
                                0u);
        } else {
            st = dsk_request_parse(&request_bytes[0], (dsk_u32)request_bytes.size(), &request);
        }

        if (dsk_error_is_ok(st)) {
            dsk_kernel_request_ex_init(&kernel_req);
            kernel_req.base.manifest_bytes = &manifest_bytes[0];
            kernel_req.base.manifest_size = (dsk_u32)manifest_bytes.size();
            kernel_req.base.request_bytes = &request_bytes[0];
            kernel_req.base.request_size = (dsk_u32)request_bytes.size();
            kernel_req.base.services = &services;
            kernel_req.base.deterministic_mode = (request.policy_flags & DSK_POLICY_DETERMINISTIC) ? 1u : 0u;
            kernel_req.base.out_plan.user = &plan_sink;
            kernel_req.base.out_plan.write = dsk_mem_sink_write;
            kernel_req.base.out_state.user = &state_sink;
            kernel_req.base.out_state.write = dsk_mem_sink_write;
            kernel_req.base.out_audit.user = &audit_sink;
            kernel_req.base.out_audit.write = dsk_mem_sink_write;

            switch (request.operation) {
            case DSK_OPERATION_INSTALL:
                st = dsk_install_ex(&kernel_req);
                break;
            case DSK_OPERATION_UPGRADE:
                st = dsk_upgrade_ex(&kernel_req);
                break;
            case DSK_OPERATION_REPAIR:
                st = dsk_repair_ex(&kernel_req);
                break;
            case DSK_OPERATION_UNINSTALL:
                st = dsk_uninstall_ex(&kernel_req);
                break;
            case DSK_OPERATION_VERIFY:
                st = dsk_verify_ex(&kernel_req);
                break;
            case DSK_OPERATION_STATUS:
                st = dsk_status_ex(&kernel_req);
                break;
            default:
                st = dsk_error_make(DSK_DOMAIN_FRONTEND,
                                    DSK_CODE_VALIDATION_ERROR,
                                    DSK_SUBCODE_INVALID_FIELD,
                                    DSK_ERROR_FLAG_USER_ACTIONABLE);
                break;
            }
        }

        if (dsk_error_is_ok(st) && plan_sink.data.empty()) {
            st = dsk_error_make(DSK_DOMAIN_KERNEL,
                                DSK_CODE_INTERNAL_ERROR,
                                DSK_SUBCODE_NONE,
                                0u);
        }
        if (dsk_error_is_ok(st)) {
            st = dsk_plan_parse(&plan_sink.data[0], (dsk_u32)plan_sink.data.size(), &plan);
        }
        if (json) {
            dsk_cli_artifacts_t artifacts = dsk_cli_artifacts_empty();
            dsk_cli_digests_t digests = dsk_cli_digests_empty();
            dsk_json_writer_t writer;
            artifacts.manifest = manifest_path ? manifest_path : "";
            artifacts.request = request_path ? request_path : "";
            digests.has_manifest = dsk_digest_from_bytes(manifest_bytes, &digests.manifest);
            digests.has_request = dsk_digest_from_bytes(request_bytes, &digests.request);
            if (dsk_error_is_ok(st)) {
                digests.has_plan = DSK_TRUE;
                digests.plan = plan.plan_digest64;
            }
            dsk_json_writer_init(&writer);
            dsk_cli_json_begin(&writer,
                               "resolve",
                               st,
                               dsk_error_to_exit_code(st),
                               artifacts,
                               digests);
            dsk_json_key(&writer, "error");
            dsk_json_write_error(&writer, st);
            if (dsk_error_is_ok(st)) {
                dsk_json_key(&writer, "resolved_set");
                dsk_json_write_resolved_set(&writer, plan);
            }
            dsk_cli_json_end(&writer);
            std::printf("%s\n", dsk_json_writer_str(&writer).c_str());
        } else if (dsk_error_is_ok(st)) {
            std::printf("ok\n");
        } else {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
        }
        return finish(&services, dsk_error_to_exit_code(st));
    }

    if (std::strcmp(argv[1], "apply") == 0) {
        const char *plan_path = get_arg_value(argc, argv, "--plan");
        const char *out_state = get_arg_value(argc, argv, "--out-state");
        const char *out_audit = get_arg_value(argc, argv, "--out-audit");
        dsk_args_view_t args;
        dsk_args_view_init(&args, argc, argv, 2);
        const char *out_journal = dsk_args_get_value(&args, "--out-journal");
        if (!out_journal) {
            out_journal = dsk_args_get_value(&args, "--journal");
        }
        dsk_bool dry_run = dsk_args_has_flag(&args, "--dry-run");
        dsk_bool json = dsk_cli_is_json_requested(&args);
        std::vector<dsk_u8> plan_bytes;
        dsk_apply_request_t apply;
        dsk_status_t st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        dsk_audit_t audit;

        if (!plan_path) {
            st = dsk_error_make(DSK_DOMAIN_FRONTEND,
                                DSK_CODE_INVALID_ARGS,
                                DSK_SUBCODE_MISSING_FIELD,
                                DSK_ERROR_FLAG_USER_ACTIONABLE);
        }
        if (!out_state) {
            out_state = "installed_state.tlv";
        }
        if (!out_audit) {
            out_audit = "setup_audit.tlv";
        }
        if (!out_journal) {
            out_journal = "job_journal.tlv";
        }
        if (dsk_error_is_ok(st)) {
            if (!load_file(&services.fs, plan_path, plan_bytes)) {
                st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                    DSK_CODE_IO_ERROR,
                                    DSK_SUBCODE_NONE,
                                    0u);
            } else if (plan_bytes.empty()) {
                st = dsk_error_make(DSK_DOMAIN_KERNEL,
                                    DSK_CODE_VALIDATION_ERROR,
                                    DSK_SUBCODE_INVALID_FIELD,
                                    DSK_ERROR_FLAG_USER_ACTIONABLE);
            }
        }

        if (dsk_error_is_ok(st)) {
            dsk_apply_request_init(&apply);
            apply.services = &services;
            apply.plan_bytes = &plan_bytes[0];
            apply.plan_size = (dsk_u32)plan_bytes.size();
            apply.out_state_path = dry_run ? 0 : out_state;
            apply.out_audit_path = out_audit;
            apply.out_journal_path = out_journal;
            apply.dry_run = dry_run ? 1u : 0u;

            st = dsk_apply_plan(&apply);
        }
        if (json) {
            dsk_cli_artifacts_t artifacts = dsk_cli_artifacts_empty();
            dsk_cli_digests_t digests = dsk_cli_digests_empty();
            dsk_json_writer_t writer;
            std::vector<dsk_u8> audit_bytes;
            dsk_plan_t plan;
            dsk_bool have_audit = DSK_FALSE;
            artifacts.plan = plan_path ? plan_path : "";
            artifacts.audit = out_audit ? out_audit : "";
            artifacts.journal = out_journal ? out_journal : "";
            if (!dry_run) {
                artifacts.state = out_state ? out_state : "";
            }
            if (dsk_error_is_ok(st)) {
                dsk_status_t plan_st = dsk_plan_parse(&plan_bytes[0],
                                                      (dsk_u32)plan_bytes.size(),
                                                      &plan);
                if (dsk_error_is_ok(plan_st)) {
                    digests.has_plan = DSK_TRUE;
                    digests.plan = plan.plan_digest64;
                    digests.has_manifest = DSK_TRUE;
                    digests.manifest = plan.manifest_digest64;
                    digests.has_request = DSK_TRUE;
                    digests.request = plan.request_digest64;
                }
                if (load_file(&services.fs, out_audit, audit_bytes)) {
                    digests.has_audit = dsk_digest_from_bytes(audit_bytes, &digests.audit);
                    if (dsk_error_is_ok(dsk_audit_parse(&audit_bytes[0],
                                                        (dsk_u32)audit_bytes.size(),
                                                        &audit))) {
                        have_audit = DSK_TRUE;
                    }
                }
            }
            dsk_json_writer_init(&writer);
            dsk_cli_json_begin(&writer,
                               "apply",
                               st,
                               dsk_error_to_exit_code(st),
                               artifacts,
                               digests);
            dsk_json_key(&writer, "error");
            dsk_json_write_error(&writer, st);
            dsk_json_key(&writer, "dry_run");
            dsk_json_bool(&writer, dry_run);
            if (have_audit) {
                dsk_json_key(&writer, "audit");
                dsk_json_write_audit_summary(&writer, audit);
            }
            dsk_cli_json_end(&writer);
            std::printf("%s\n", dsk_json_writer_str(&writer).c_str());
        } else if (dsk_error_is_ok(st)) {
            std::printf("audit: %s\n", out_audit);
            std::printf("journal: %s\n", out_journal);
            if (!dry_run) {
                std::printf("state: %s\n", out_state);
            }
        } else {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
        }
        return finish(&services, dsk_error_to_exit_code(st));
    }

    if (std::strcmp(argv[1], "resume") == 0) {
        const char *journal_path = get_arg_value(argc, argv, "--journal");
        const char *out_state = get_arg_value(argc, argv, "--out-state");
        const char *out_audit = get_arg_value(argc, argv, "--out-audit");
        dsk_args_view_t args;
        dsk_args_view_init(&args, argc, argv, 2);
        dsk_bool json = dsk_cli_is_json_requested(&args);
        dsk_resume_request_t resume;
        dsk_status_t st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        dsk_audit_t audit;

        if (!journal_path) {
            journal_path = "job_journal.tlv";
        }
        if (!out_state) {
            out_state = "installed_state.tlv";
        }
        if (!out_audit) {
            out_audit = "setup_audit.tlv";
        }

        dsk_resume_request_init(&resume);
        resume.services = &services;
        resume.journal_path = journal_path;
        resume.out_state_path = out_state;
        resume.out_audit_path = out_audit;

        st = dsk_resume(&resume);
        if (json) {
            dsk_cli_artifacts_t artifacts = dsk_cli_artifacts_empty();
            dsk_cli_digests_t digests = dsk_cli_digests_empty();
            dsk_json_writer_t writer;
            std::vector<dsk_u8> audit_bytes;
            dsk_bool have_audit = DSK_FALSE;
            artifacts.journal = journal_path ? journal_path : "";
            artifacts.audit = out_audit ? out_audit : "";
            artifacts.state = out_state ? out_state : "";
            if (load_file(&services.fs, out_audit, audit_bytes)) {
                digests.has_audit = dsk_digest_from_bytes(audit_bytes, &digests.audit);
                if (dsk_error_is_ok(dsk_audit_parse(&audit_bytes[0],
                                                    (dsk_u32)audit_bytes.size(),
                                                    &audit))) {
                    have_audit = DSK_TRUE;
                }
            }
            dsk_json_writer_init(&writer);
            dsk_cli_json_begin(&writer,
                               "resume",
                               st,
                               dsk_error_to_exit_code(st),
                               artifacts,
                               digests);
            dsk_json_key(&writer, "error");
            dsk_json_write_error(&writer, st);
            if (have_audit) {
                dsk_json_key(&writer, "audit");
                dsk_json_write_audit_summary(&writer, audit);
            }
            dsk_cli_json_end(&writer);
            std::printf("%s\n", dsk_json_writer_str(&writer).c_str());
        } else if (dsk_error_is_ok(st)) {
            std::printf("audit: %s\n", out_audit);
            std::printf("journal: %s\n", journal_path);
            std::printf("state: %s\n", out_state);
        } else {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
        }
        return finish(&services, dsk_error_to_exit_code(st));
    }

    if (std::strcmp(argv[1], "rollback") == 0) {
        const char *journal_path = get_arg_value(argc, argv, "--journal");
        const char *out_audit = get_arg_value(argc, argv, "--out-audit");
        dsk_args_view_t args;
        dsk_args_view_init(&args, argc, argv, 2);
        dsk_bool json = dsk_cli_is_json_requested(&args);
        dsk_resume_request_t resume;
        dsk_status_t st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        dsk_audit_t audit;

        if (!journal_path) {
            journal_path = "job_journal.tlv";
        }
        if (!out_audit) {
            out_audit = "setup_audit.tlv";
        }

        dsk_resume_request_init(&resume);
        resume.services = &services;
        resume.journal_path = journal_path;
        resume.out_audit_path = out_audit;

        st = dsk_rollback(&resume);
        if (json) {
            dsk_cli_artifacts_t artifacts = dsk_cli_artifacts_empty();
            dsk_cli_digests_t digests = dsk_cli_digests_empty();
            dsk_json_writer_t writer;
            std::vector<dsk_u8> audit_bytes;
            dsk_bool have_audit = DSK_FALSE;
            artifacts.journal = journal_path ? journal_path : "";
            artifacts.audit = out_audit ? out_audit : "";
            if (load_file(&services.fs, out_audit, audit_bytes)) {
                digests.has_audit = dsk_digest_from_bytes(audit_bytes, &digests.audit);
                if (dsk_error_is_ok(dsk_audit_parse(&audit_bytes[0],
                                                    (dsk_u32)audit_bytes.size(),
                                                    &audit))) {
                    have_audit = DSK_TRUE;
                }
            }
            dsk_json_writer_init(&writer);
            dsk_cli_json_begin(&writer,
                               "rollback",
                               st,
                               dsk_error_to_exit_code(st),
                               artifacts,
                               digests);
            dsk_json_key(&writer, "error");
            dsk_json_write_error(&writer, st);
            if (have_audit) {
                dsk_json_key(&writer, "audit");
                dsk_json_write_audit_summary(&writer, audit);
            }
            dsk_cli_json_end(&writer);
            std::printf("%s\n", dsk_json_writer_str(&writer).c_str());
        } else if (dsk_error_is_ok(st)) {
            std::printf("audit: %s\n", out_audit);
            std::printf("journal: %s\n", journal_path);
        } else {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
        }
        return finish(&services, dsk_error_to_exit_code(st));
    }

    if (std::strcmp(argv[1], "verify") == 0) {
        const char *state_path = get_arg_value(argc, argv, "--state");
        dsk_args_view_t args;
        dsk_args_view_init(&args, argc, argv, 2);
        dsk_bool json = dsk_cli_is_json_requested(&args);
        std::vector<dsk_u8> state_bytes;
        dsk_installed_state_t state;
        dsk_status_t st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);

        if (!state_path) {
            st = dsk_error_make(DSK_DOMAIN_FRONTEND,
                                DSK_CODE_INVALID_ARGS,
                                DSK_SUBCODE_MISSING_FIELD,
                                DSK_ERROR_FLAG_USER_ACTIONABLE);
        } else if (!load_file(&services.fs, state_path, state_bytes)) {
            st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                DSK_CODE_IO_ERROR,
                                DSK_SUBCODE_NONE,
                                0u);
        } else {
            st = dsk_installed_state_parse(&state_bytes[0],
                                           (dsk_u32)state_bytes.size(),
                                           &state);
        }
        if (json) {
            dsk_cli_artifacts_t artifacts = dsk_cli_artifacts_empty();
            dsk_cli_digests_t digests = dsk_cli_digests_empty();
            dsk_json_writer_t writer;
            artifacts.state = state_path ? state_path : "";
            digests.has_state = dsk_digest_from_bytes(state_bytes, &digests.state);
            dsk_json_writer_init(&writer);
            dsk_cli_json_begin(&writer,
                               "verify",
                               st,
                               dsk_error_to_exit_code(st),
                               artifacts,
                               digests);
            dsk_json_key(&writer, "error");
            dsk_json_write_error(&writer, st);
            if (dsk_error_is_ok(st)) {
                dsk_json_key(&writer, "state");
                dsk_json_write_state_summary(&writer, state);
            }
            dsk_cli_json_end(&writer);
            std::printf("%s\n", dsk_json_writer_str(&writer).c_str());
        } else if (dsk_error_is_ok(st)) {
            std::printf("ok\n");
        } else {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
        }
        return finish(&services, dsk_error_to_exit_code(st));
    }

    if (std::strcmp(argv[1], "uninstall-preview") == 0) {
        const char *state_path = get_arg_value(argc, argv, "--state");
        dsk_args_view_t args;
        dsk_args_view_init(&args, argc, argv, 2);
        dsk_bool json = dsk_cli_is_json_requested(&args);
        const char *components_csv = dsk_args_get_value(&args, "--components");
        std::vector<dsk_u8> state_bytes;
        dsk_installed_state_t state;
        dsk_status_t st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        std::vector<std::string> requested;
        std::vector<std::string> preview;
        size_t i;

        if (components_csv) {
            dsk_args_split_csv(components_csv, &requested);
            for (i = 0u; i < requested.size(); ++i) {
                size_t j;
                for (j = 0u; j < requested[i].size(); ++j) {
                    char c = requested[i][j];
                    if (c >= 'A' && c <= 'Z') {
                        requested[i][j] = (char)(c - 'A' + 'a');
                    }
                }
            }
        }

        if (!state_path) {
            st = dsk_error_make(DSK_DOMAIN_FRONTEND,
                                DSK_CODE_INVALID_ARGS,
                                DSK_SUBCODE_MISSING_FIELD,
                                DSK_ERROR_FLAG_USER_ACTIONABLE);
        } else if (!load_file(&services.fs, state_path, state_bytes)) {
            st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                DSK_CODE_IO_ERROR,
                                DSK_SUBCODE_NONE,
                                0u);
        } else {
            st = dsk_installed_state_parse(&state_bytes[0],
                                           (dsk_u32)state_bytes.size(),
                                           &state);
        }

        if (dsk_error_is_ok(st)) {
            preview = state.installed_components;
            if (!requested.empty()) {
                std::vector<std::string> lowered = requested;
                size_t j;
                preview.clear();
                for (j = 0u; j < state.installed_components.size(); ++j) {
                    std::string comp = state.installed_components[j];
                    size_t k;
                    for (k = 0u; k < comp.size(); ++k) {
                        char c = comp[k];
                        if (c >= 'A' && c <= 'Z') {
                            comp[k] = (char)(c - 'A' + 'a');
                        }
                    }
                    if (std::find(lowered.begin(), lowered.end(), comp) != lowered.end()) {
                        preview.push_back(state.installed_components[j]);
                    }
                }
            }
        }

        if (json) {
            dsk_cli_artifacts_t artifacts = dsk_cli_artifacts_empty();
            dsk_cli_digests_t digests = dsk_cli_digests_empty();
            dsk_json_writer_t writer;
            artifacts.state = state_path ? state_path : "";
            digests.has_state = dsk_digest_from_bytes(state_bytes, &digests.state);
            dsk_json_writer_init(&writer);
            dsk_cli_json_begin(&writer,
                               "uninstall-preview",
                               st,
                               dsk_error_to_exit_code(st),
                               artifacts,
                               digests);
            dsk_json_key(&writer, "error");
            dsk_json_write_error(&writer, st);
            if (dsk_error_is_ok(st)) {
                dsk_json_key(&writer, "components");
                dsk_json_write_string_list_sorted(&writer, preview);
            }
            dsk_cli_json_end(&writer);
            std::printf("%s\n", dsk_json_writer_str(&writer).c_str());
        } else if (dsk_error_is_ok(st)) {
            std::sort(preview.begin(), preview.end());
            for (i = 0u; i < preview.size(); ++i) {
                std::printf("%s\n", preview[i].c_str());
            }
        } else {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
        }
        return finish(&services, dsk_error_to_exit_code(st));
    }

    if (std::strcmp(argv[1], "status") == 0) {
        const char *journal_path = get_arg_value(argc, argv, "--journal");
        dsk_args_view_t args;
        dsk_args_view_init(&args, argc, argv, 2);
        dsk_bool json = dsk_cli_is_json_requested(&args);
        std::vector<dsk_u8> journal_bytes;
        dsk_job_journal_t journal;
        dsk_status_t st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        size_t i;
        dsk_u32 pending = 0u;
        dsk_u32 in_progress = 0u;
        dsk_u32 complete = 0u;
        dsk_u32 failed = 0u;

        if (!journal_path) {
            journal_path = "job_journal.tlv";
        }
        if (!load_file(&services.fs, journal_path, journal_bytes)) {
            st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                DSK_CODE_IO_ERROR,
                                DSK_SUBCODE_NONE,
                                0u);
        } else {
            st = dsk_job_journal_parse(&journal_bytes[0],
                                       (dsk_u32)journal_bytes.size(),
                                       &journal);
        }
        if (json) {
            dsk_cli_artifacts_t artifacts = dsk_cli_artifacts_empty();
            dsk_cli_digests_t digests = dsk_cli_digests_empty();
            dsk_json_writer_t writer;
            artifacts.journal = journal_path ? journal_path : "";
            dsk_json_writer_init(&writer);
            dsk_cli_json_begin(&writer,
                               "status",
                               st,
                               dsk_error_to_exit_code(st),
                               artifacts,
                               digests);
            dsk_json_key(&writer, "error");
            dsk_json_write_error(&writer, st);
            if (dsk_error_is_ok(st)) {
                dsk_json_key(&writer, "status");
                dsk_json_write_status_summary(&writer, journal);
            }
            dsk_cli_json_end(&writer);
            std::printf("%s\n", dsk_json_writer_str(&writer).c_str());
            return finish(&services, dsk_error_to_exit_code(st));
        }
        if (!dsk_error_is_ok(st)) {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
            return finish(&services, dsk_error_to_exit_code(st));
        }
        for (i = 0u; i < journal.checkpoints.size(); ++i) {
            dsk_u16 status = journal.checkpoints[i].status;
            if (status == DSK_JOB_STATUS_PENDING) {
                ++pending;
            } else if (status == DSK_JOB_STATUS_IN_PROGRESS) {
                ++in_progress;
            } else if (status == DSK_JOB_STATUS_COMPLETE || status == DSK_JOB_STATUS_SKIPPED) {
                ++complete;
            } else if (status == DSK_JOB_STATUS_FAILED) {
                ++failed;
            }
        }
        std::printf("pending: %u\n", (unsigned)pending);
        std::printf("in_progress: %u\n", (unsigned)in_progress);
        std::printf("complete: %u\n", (unsigned)complete);
        std::printf("failed: %u\n", (unsigned)failed);
        if (!dsk_error_is_ok(journal.last_error)) {
            std::printf("last_error: %s\n", dsk_error_to_string_stable(journal.last_error));
        }
        return finish(&services, 0);
    }

    if (std::strcmp(argv[1], "run") == 0) {
        const char *manifest_path = get_arg_value(argc, argv, "--manifest");
        const char *request_path = get_arg_value(argc, argv, "--request");
        const char *out_state = get_arg_value(argc, argv, "--out-state");
        const char *out_audit = get_arg_value(argc, argv, "--out-audit");
        const char *out_plan = get_arg_value(argc, argv, "--out-plan");
        const char *out_log = get_arg_value(argc, argv, "--out-log");
        dsk_args_view_t args;
        dsk_args_view_init(&args, argc, argv, 2);
        dsk_bool json = dsk_cli_is_json_requested(&args);
        std::vector<dsk_u8> manifest_bytes;
        std::vector<dsk_u8> request_bytes;
        dsk_request_t request;
        dsk_kernel_request_ex_t kernel_req;
        dsk_mem_sink_t plan_sink;
        dsk_mem_sink_t state_sink;
        dsk_mem_sink_t audit_sink;
        dsk_mem_sink_t log_sink;
        dsk_status_t st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        dsk_audit_t audit;

        if (!manifest_path || !request_path || !out_state || !out_audit) {
            st = dsk_error_make(DSK_DOMAIN_FRONTEND,
                                DSK_CODE_INVALID_ARGS,
                                DSK_SUBCODE_MISSING_FIELD,
                                DSK_ERROR_FLAG_USER_ACTIONABLE);
        } else if (!load_file(&services.fs, manifest_path, manifest_bytes)) {
            st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                DSK_CODE_IO_ERROR,
                                DSK_SUBCODE_NONE,
                                0u);
        } else if (!load_file(&services.fs, request_path, request_bytes)) {
            st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                DSK_CODE_IO_ERROR,
                                DSK_SUBCODE_NONE,
                                0u);
        } else {
            st = dsk_request_parse(&request_bytes[0], (dsk_u32)request_bytes.size(), &request);
        }

        if (dsk_error_is_ok(st)) {
            dsk_kernel_request_ex_init(&kernel_req);
            kernel_req.base.manifest_bytes = &manifest_bytes[0];
            kernel_req.base.manifest_size = (dsk_u32)manifest_bytes.size();
            kernel_req.base.request_bytes = &request_bytes[0];
            kernel_req.base.request_size = (dsk_u32)request_bytes.size();
            kernel_req.base.services = &services;
            kernel_req.base.deterministic_mode = (request.policy_flags & DSK_POLICY_DETERMINISTIC) ? 1u : 0u;
            if (out_plan && out_plan[0]) {
                kernel_req.base.out_plan.user = &plan_sink;
                kernel_req.base.out_plan.write = dsk_mem_sink_write;
            }
            kernel_req.base.out_state.user = &state_sink;
            kernel_req.base.out_state.write = dsk_mem_sink_write;
            kernel_req.base.out_audit.user = &audit_sink;
            kernel_req.base.out_audit.write = dsk_mem_sink_write;
            if (out_log && out_log[0]) {
                kernel_req.out_log.user = &log_sink;
                kernel_req.out_log.write = dsk_mem_sink_write;
            }

            switch (request.operation) {
            case DSK_OPERATION_INSTALL:
                st = dsk_install_ex(&kernel_req);
                break;
            case DSK_OPERATION_UPGRADE:
                st = dsk_upgrade_ex(&kernel_req);
                break;
            case DSK_OPERATION_REPAIR:
                st = dsk_repair_ex(&kernel_req);
                break;
            case DSK_OPERATION_UNINSTALL:
                st = dsk_uninstall_ex(&kernel_req);
                break;
            case DSK_OPERATION_VERIFY:
                st = dsk_verify_ex(&kernel_req);
                break;
            case DSK_OPERATION_STATUS:
                st = dsk_status_ex(&kernel_req);
                break;
            default:
                st = dsk_error_make(DSK_DOMAIN_FRONTEND,
                                    DSK_CODE_VALIDATION_ERROR,
                                    DSK_SUBCODE_INVALID_FIELD,
                                    DSK_ERROR_FLAG_USER_ACTIONABLE);
                break;
            }
        }

        if (dsk_error_is_ok(st)) {
            if (!write_file(&services.fs, out_state, state_sink.data)) {
                st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                    DSK_CODE_IO_ERROR,
                                    DSK_SUBCODE_NONE,
                                    0u);
            }
            if (dsk_error_is_ok(st) &&
                !write_file(&services.fs, out_audit, audit_sink.data)) {
                st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                    DSK_CODE_IO_ERROR,
                                    DSK_SUBCODE_NONE,
                                    0u);
            }
            if (dsk_error_is_ok(st) && out_plan && out_plan[0]) {
                if (!write_file(&services.fs, out_plan, plan_sink.data)) {
                    st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                        DSK_CODE_IO_ERROR,
                                        DSK_SUBCODE_NONE,
                                        0u);
                }
            }
            if (dsk_error_is_ok(st) && out_log && out_log[0]) {
                if (!write_file(&services.fs, out_log, log_sink.data)) {
                    st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                        DSK_CODE_IO_ERROR,
                                        DSK_SUBCODE_NONE,
                                        0u);
                }
            }
        }

        if (json) {
            dsk_cli_artifacts_t artifacts = dsk_cli_artifacts_empty();
            dsk_cli_digests_t digests = dsk_cli_digests_empty();
            dsk_json_writer_t writer;
            dsk_plan_t plan;
            dsk_bool have_audit = DSK_FALSE;
            artifacts.manifest = manifest_path ? manifest_path : "";
            artifacts.request = request_path ? request_path : "";
            artifacts.state = out_state ? out_state : "";
            artifacts.audit = out_audit ? out_audit : "";
            if (out_plan && out_plan[0]) {
                artifacts.plan = out_plan;
            }
            digests.has_manifest = dsk_digest_from_bytes(manifest_bytes, &digests.manifest);
            digests.has_request = dsk_digest_from_bytes(request_bytes, &digests.request);
            digests.has_state = dsk_digest_from_bytes(state_sink.data, &digests.state);
            digests.has_audit = dsk_digest_from_bytes(audit_sink.data, &digests.audit);
            if (out_plan && !plan_sink.data.empty()) {
                if (dsk_error_is_ok(dsk_plan_parse(&plan_sink.data[0],
                                                   (dsk_u32)plan_sink.data.size(),
                                                   &plan))) {
                    digests.has_plan = DSK_TRUE;
                    digests.plan = plan.plan_digest64;
                }
            }
            if (!audit_sink.data.empty() &&
                dsk_error_is_ok(dsk_audit_parse(&audit_sink.data[0],
                                                (dsk_u32)audit_sink.data.size(),
                                                &audit))) {
                have_audit = DSK_TRUE;
            }
            dsk_json_writer_init(&writer);
            dsk_cli_json_begin(&writer,
                               "run",
                               st,
                               dsk_error_to_exit_code(st),
                               artifacts,
                               digests);
            dsk_json_key(&writer, "error");
            dsk_json_write_error(&writer, st);
            if (have_audit) {
                dsk_json_key(&writer, "audit");
                dsk_json_write_audit_summary(&writer, audit);
            }
            dsk_cli_json_end(&writer);
            std::printf("%s\n", dsk_json_writer_str(&writer).c_str());
        } else if (dsk_error_is_ok(st)) {
            std::printf("state: %s\n", out_state);
            std::printf("audit: %s\n", out_audit);
            if (out_plan && out_plan[0]) {
                std::printf("plan: %s\n", out_plan);
            }
            if (out_log && out_log[0]) {
                std::printf("log: %s\n", out_log);
            }
        } else {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
        }

        return finish(&services, dsk_error_to_exit_code(st));
    }

    print_usage();
    return finish(&services, 1);
}
