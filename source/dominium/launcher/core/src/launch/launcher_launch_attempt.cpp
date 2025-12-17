/*
FILE: source/dominium/launcher/core/src/launch/launcher_launch_attempt.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / launch_attempt
RESPONSIBILITY: Implements failure tracking, recovery suggestion logic, and post-launch bookkeeping (audit + last-known-good).
*/

#include "launcher_launch_attempt.h"

#include <cstdio>
#include <cstring>

#include "launcher_audit.h"
#include "launcher_instance_artifact_ops.h"
#include "launcher_instance_ops.h"
#include "launcher_safety.h"

namespace dom {
namespace launcher_core {

namespace {

static void audit_reason(LauncherAuditLog* audit, const std::string& r) {
    if (!audit) {
        return;
    }
    audit->reasons.push_back(r);
}

static void u64_to_hex16(u64 v, char out_hex[17]) {
    static const char* hex = "0123456789abcdef";
    int i;
    for (i = 0; i < 16; ++i) {
        unsigned shift = (unsigned)((15 - i) * 4);
        unsigned nib = (unsigned)((v >> shift) & (u64)0xFu);
        out_hex[i] = hex[nib & 0xFu];
    }
    out_hex[16] = '\0';
}

static std::string u64_hex16_string(u64 v) {
    char buf[17];
    u64_to_hex16(v, buf);
    return std::string(buf);
}

static std::string u32_dec_string(u32 v) {
    char buf[32];
    std::snprintf(buf, sizeof(buf), "%u", (unsigned)v);
    return std::string(buf);
}

static std::string i32_dec_string(i32 v) {
    char buf[32];
    std::snprintf(buf, sizeof(buf), "%d", (int)v);
    return std::string(buf);
}

static const launcher_fs_api_v1* get_fs(const launcher_services_api_v1* services) {
    void* iface = 0;
    if (!services || !services->query_interface) {
        return 0;
    }
    if (services->query_interface(LAUNCHER_IID_FS_V1, &iface) != 0) {
        return 0;
    }
    return (const launcher_fs_api_v1*)iface;
}

static const launcher_time_api_v1* get_time(const launcher_services_api_v1* services) {
    void* iface = 0;
    if (!services || !services->query_interface) {
        return 0;
    }
    if (services->query_interface(LAUNCHER_IID_TIME_V1, &iface) != 0) {
        return 0;
    }
    return (const launcher_time_api_v1*)iface;
}

static bool get_state_root(const launcher_fs_api_v1* fs, std::string& out_state_root) {
    char buf[260];
    std::memset(buf, 0, sizeof(buf));
    out_state_root.clear();
    if (!fs || !fs->get_path) {
        return false;
    }
    if (!fs->get_path(LAUNCHER_FS_PATH_STATE, buf, sizeof(buf))) {
        return false;
    }
    if (!buf[0]) {
        return false;
    }
    out_state_root = buf;
    return true;
}

static u32 clamp_u32(u32 v, u32 lo, u32 hi, u32 defv) {
    if (v == 0u) {
        return defv;
    }
    if (v < lo) {
        return lo;
    }
    if (v > hi) {
        return hi;
    }
    return v;
}

static u32 consecutive_failures(const LauncherInstanceLaunchHistory& h) {
    u32 count = 0u;
    size_t i = h.attempts.size();
    while (i > 0u) {
        const LauncherInstanceLaunchAttempt& a = h.attempts[i - 1u];
        if (a.outcome == (u32)LAUNCHER_LAUNCH_OUTCOME_SUCCESS) {
            break;
        }
        count += 1u;
        i -= 1u;
    }
    return count;
}

static const char* outcome_name(u32 outcome) {
    switch (outcome) {
    case LAUNCHER_LAUNCH_OUTCOME_SUCCESS: return "success";
    case LAUNCHER_LAUNCH_OUTCOME_CRASH: return "crash";
    case LAUNCHER_LAUNCH_OUTCOME_REFUSAL: return "refusal";
    case LAUNCHER_LAUNCH_OUTCOME_MISSING_ARTIFACT: return "missing_artifact";
    default: break;
    }
    return "unknown";
}

static u32 classify_refusal_outcome(const LauncherPrelaunchPlan& plan) {
    size_t i;
    for (i = 0u; i < plan.validation.failures.size(); ++i) {
        const std::string& code = plan.validation.failures[i].code;
        if (code.find("missing_artifact") == 0u || code == "artifact_paths_failed") {
            return (u32)LAUNCHER_LAUNCH_OUTCOME_MISSING_ARTIFACT;
        }
    }
    return (u32)LAUNCHER_LAUNCH_OUTCOME_REFUSAL;
}

static void audit_emit_overrides(LauncherAuditLog* audit,
                                 const LauncherPrelaunchPlan& plan,
                                 const LauncherRecoverySuggestion& rec) {
    const LauncherInstanceConfig& p = plan.persisted_config;
    const LauncherLaunchOverrides& o = plan.overrides;

    /* Persisted overrides (config/config.tlv). */
    if (!p.gfx_backend.empty()) {
        audit_reason(audit, std::string("override;persistent=1;field=gfx_backend;value=") + p.gfx_backend + ";instance_id=" + plan.instance_id);
    }
    if (!p.renderer_api.empty()) {
        audit_reason(audit, std::string("override;persistent=1;field=renderer_api;value=") + p.renderer_api + ";instance_id=" + plan.instance_id);
    }
    if (p.window_mode != LAUNCHER_WINDOW_MODE_AUTO) {
        audit_reason(audit, std::string("override;persistent=1;field=window_mode;value=") + u32_dec_string(p.window_mode) + ";instance_id=" + plan.instance_id);
    }
    if (p.window_width != 0u) {
        audit_reason(audit, std::string("override;persistent=1;field=window_width;value=") + u32_dec_string(p.window_width) + ";instance_id=" + plan.instance_id);
    }
    if (p.window_height != 0u) {
        audit_reason(audit, std::string("override;persistent=1;field=window_height;value=") + u32_dec_string(p.window_height) + ";instance_id=" + plan.instance_id);
    }
    if (p.window_dpi != 0u) {
        audit_reason(audit, std::string("override;persistent=1;field=window_dpi;value=") + u32_dec_string(p.window_dpi) + ";instance_id=" + plan.instance_id);
    }
    if (p.window_monitor != 0u) {
        audit_reason(audit, std::string("override;persistent=1;field=window_monitor;value=") + u32_dec_string(p.window_monitor) + ";instance_id=" + plan.instance_id);
    }
    if (!p.audio_device_id.empty()) {
        audit_reason(audit, std::string("override;persistent=1;field=audio_device_id;value=") + p.audio_device_id + ";instance_id=" + plan.instance_id);
    }
    if (!p.input_backend.empty()) {
        audit_reason(audit, std::string("override;persistent=1;field=input_backend;value=") + p.input_backend + ";instance_id=" + plan.instance_id);
    }
    if (p.allow_network == 0u) {
        audit_reason(audit, std::string("override;persistent=1;field=allow_network;value=0;instance_id=") + plan.instance_id);
    }
    if (p.debug_flags != 0u) {
        audit_reason(audit, std::string("override;persistent=1;field=debug_flags;value=") + u32_dec_string(p.debug_flags) + ";instance_id=" + plan.instance_id);
    }
    if (!p.domain_overrides.empty()) {
        audit_reason(audit, std::string("override;persistent=1;field=domain_overrides;count=") + u32_dec_string((u32)p.domain_overrides.size()) + ";instance_id=" + plan.instance_id);
    }
    if (p.auto_recovery_failure_threshold != 0u && p.auto_recovery_failure_threshold != 3u) {
        audit_reason(audit, std::string("override;persistent=1;field=auto_recovery_failure_threshold;value=") + u32_dec_string(p.auto_recovery_failure_threshold) + ";instance_id=" + plan.instance_id);
    }
    if (p.launch_history_max_entries != 0u && p.launch_history_max_entries != 10u) {
        audit_reason(audit, std::string("override;persistent=1;field=launch_history_max_entries;value=") + u32_dec_string(p.launch_history_max_entries) + ";instance_id=" + plan.instance_id);
    }

    /* Auto safe mode entry (policy). */
    if (rec.auto_entered_safe_mode) {
        audit_reason(audit,
                     std::string("override;auto=1;field=safe_mode;value=1;instance_id=") + plan.instance_id +
                         ";why=consecutive_failures_ge_threshold");
    }

    /* Ephemeral overrides (CLI/UI). */
    if (o.request_safe_mode) {
        audit_reason(audit, std::string("override;ephemeral=1;field=safe_mode;value=1;instance_id=") + plan.instance_id);
        if (o.safe_mode_allow_network) {
            audit_reason(audit, std::string("override;ephemeral=1;field=safe_mode_allow_network;value=1;instance_id=") + plan.instance_id);
        }
    }
    if (o.has_gfx_backend) {
        audit_reason(audit, std::string("override;ephemeral=1;field=gfx_backend;value=") + o.gfx_backend + ";instance_id=" + plan.instance_id);
    }
    if (o.has_renderer_api) {
        audit_reason(audit, std::string("override;ephemeral=1;field=renderer_api;value=") + o.renderer_api + ";instance_id=" + plan.instance_id);
    }
    if (o.has_window_mode) {
        audit_reason(audit, std::string("override;ephemeral=1;field=window_mode;value=") + u32_dec_string(o.window_mode) + ";instance_id=" + plan.instance_id);
    }
    if (o.has_window_width) {
        audit_reason(audit, std::string("override;ephemeral=1;field=window_width;value=") + u32_dec_string(o.window_width) + ";instance_id=" + plan.instance_id);
    }
    if (o.has_window_height) {
        audit_reason(audit, std::string("override;ephemeral=1;field=window_height;value=") + u32_dec_string(o.window_height) + ";instance_id=" + plan.instance_id);
    }
    if (o.has_window_dpi) {
        audit_reason(audit, std::string("override;ephemeral=1;field=window_dpi;value=") + u32_dec_string(o.window_dpi) + ";instance_id=" + plan.instance_id);
    }
    if (o.has_window_monitor) {
        audit_reason(audit, std::string("override;ephemeral=1;field=window_monitor;value=") + u32_dec_string(o.window_monitor) + ";instance_id=" + plan.instance_id);
    }
    if (o.has_audio_device_id) {
        audit_reason(audit, std::string("override;ephemeral=1;field=audio_device_id;value=") + o.audio_device_id + ";instance_id=" + plan.instance_id);
    }
    if (o.has_input_backend) {
        audit_reason(audit, std::string("override;ephemeral=1;field=input_backend;value=") + o.input_backend + ";instance_id=" + plan.instance_id);
    }
    if (o.has_allow_network) {
        audit_reason(audit, std::string("override;ephemeral=1;field=allow_network;value=") + (o.allow_network ? "1" : "0") + ";instance_id=" + plan.instance_id);
    }
    if (o.has_debug_flags) {
        audit_reason(audit, std::string("override;ephemeral=1;field=debug_flags;value=") + u32_dec_string(o.debug_flags) + ";instance_id=" + plan.instance_id);
    }

    /* Safe-mode derived overrides (profile overlay). */
    if (plan.resolved.safe_mode) {
        audit_reason(audit, std::string("override;safe_mode=1;field=disable_mods;value=") + (plan.resolved.disable_mods ? "1" : "0") + ";instance_id=" + plan.instance_id);
        audit_reason(audit, std::string("override;safe_mode=1;field=disable_packs;value=") + (plan.resolved.disable_packs ? "1" : "0") + ";instance_id=" + plan.instance_id);
        audit_reason(audit, std::string("override;safe_mode=1;field=gfx_backend;value=") + (plan.resolved.gfx_backend.empty() ? std::string("<auto>") : plan.resolved.gfx_backend) + ";instance_id=" + plan.instance_id);
        audit_reason(audit, std::string("override;safe_mode=1;field=allow_network;value=") + (plan.resolved.allow_network ? "1" : "0") + ";instance_id=" + plan.instance_id);
    }
}

static void audit_emit_plan_summary(LauncherAuditLog* audit, const LauncherPrelaunchPlan& plan, const LauncherRecoverySuggestion& rec) {
    audit_reason(audit,
                 std::string("launch_prepare;instance_id=") + plan.instance_id +
                     ";safe_mode=" + (plan.resolved.safe_mode ? "1" : "0") +
                     ";auto_safe_mode=" + (rec.auto_entered_safe_mode ? "1" : "0") +
                     ";manifest_hash64=0x" + u64_hex16_string(plan.base_manifest_hash64) +
                     ";cfg_hash64=0x" + u64_hex16_string(plan.resolved_config_hash64));

    audit_reason(audit,
                 std::string("launch_recovery;instance_id=") + plan.instance_id +
                     ";threshold=" + u32_dec_string(rec.threshold) +
                     ";consecutive_failures=" + u32_dec_string(rec.consecutive_failures) +
                     ";suggest_safe_mode=" + (rec.suggest_safe_mode ? "1" : "0") +
                     ";suggest_rollback=" + (rec.suggest_rollback ? "1" : "0"));

    audit_reason(audit,
                 std::string("launch_config;instance_id=") + plan.instance_id +
                     ";gfx=" + (plan.resolved.gfx_backend.empty() ? std::string("<auto>") : plan.resolved.gfx_backend) +
                     ";renderer_api=" + (plan.resolved.renderer_api.empty() ? std::string("<auto>") : plan.resolved.renderer_api) +
                     ";window_mode=" + u32_dec_string(plan.resolved.window_mode) +
                     ";window_w=" + u32_dec_string(plan.resolved.window_width) +
                     ";window_h=" + u32_dec_string(plan.resolved.window_height) +
                     ";dpi=" + u32_dec_string(plan.resolved.window_dpi) +
                     ";monitor=" + u32_dec_string(plan.resolved.window_monitor) +
                     ";audio=" + (plan.resolved.audio_device_id.empty() ? std::string("<auto>") : plan.resolved.audio_device_id) +
                     ";input=" + (plan.resolved.input_backend.empty() ? std::string("<auto>") : plan.resolved.input_backend) +
                     ";allow_network=" + (plan.resolved.allow_network ? "1" : "0") +
                     ";debug_flags=" + u32_dec_string(plan.resolved.debug_flags) +
                     ";disable_mods=" + (plan.resolved.disable_mods ? "1" : "0") +
                     ";disable_packs=" + (plan.resolved.disable_packs ? "1" : "0") +
                     ";used_known_good=" + (plan.resolved.used_known_good_manifest ? "1" : "0") +
                     ";domains=" + u32_dec_string((u32)plan.resolved.domain_overrides.size()));

    audit_emit_overrides(audit, plan, rec);

    if (!plan.resolved.known_good_previous_dir.empty()) {
        audit_reason(audit,
                     std::string("launch_known_good;instance_id=") + plan.instance_id +
                         ";previous_dir=" + plan.resolved.known_good_previous_dir);
    }

    if (plan.validation.ok) {
        audit_reason(audit, std::string("validation;result=ok;instance_id=") + plan.instance_id);
    } else {
        size_t i;
        for (i = 0u; i < plan.validation.failures.size(); ++i) {
            const LauncherPrelaunchValidationFailure& f = plan.validation.failures[i];
            audit_reason(audit,
                         std::string("validation;result=fail;instance_id=") + plan.instance_id +
                             ";code=" + f.code +
                             ";suggestion=" + f.suggestion +
                             (f.detail.empty() ? std::string() : (std::string(";detail=") + f.detail)));
        }
    }
}

} /* namespace */

LauncherRecoverySuggestion::LauncherRecoverySuggestion()
    : threshold(3u),
      consecutive_failures(0u),
      suggest_safe_mode(0u),
      suggest_rollback(0u),
      auto_entered_safe_mode(0u) {
}

bool launcher_launch_prepare_attempt(const launcher_services_api_v1* services,
                                    const LauncherProfile* profile_constraints,
                                    const std::string& instance_id,
                                    const std::string& state_root_override,
                                    const LauncherLaunchOverrides& requested_overrides,
                                    LauncherPrelaunchPlan& out_plan,
                                    LauncherRecoverySuggestion& out_recovery,
                                    LauncherAuditLog* audit,
                                    std::string* out_error) {
    const launcher_fs_api_v1* fs = get_fs(services);
    std::string state_root = state_root_override;
    LauncherInstancePaths paths;
    LauncherInstanceConfig cfg;
    LauncherInstanceLaunchHistory hist;
    LauncherRecoverySuggestion rec;
    LauncherLaunchOverrides effective = requested_overrides;
    u32 threshold = 3u;
    u32 failures = 0u;

    if (out_error) {
        out_error->clear();
    }
    out_plan = LauncherPrelaunchPlan();
    out_recovery = LauncherRecoverySuggestion();

    if (!services || !fs) {
        if (out_error) *out_error = "missing_services_or_fs";
        return false;
    }
    if (instance_id.empty()) {
        if (out_error) *out_error = "empty_instance_id";
        return false;
    }
    if (!launcher_is_safe_id_component(instance_id)) {
        if (out_error) *out_error = "unsafe_instance_id";
        audit_reason(audit, std::string("launch_prepare;result=fail;code=unsafe_instance_id;instance_id=") + instance_id);
        return false;
    }
    if (state_root.empty()) {
        if (!get_state_root(fs, state_root)) {
            if (out_error) *out_error = "missing_state_root";
            return false;
        }
    }
    paths = launcher_instance_paths_make(state_root, instance_id);

    if (!launcher_instance_config_load(services, paths, cfg)) {
        if (out_error) *out_error = "load_config_failed";
        return false;
    }
    threshold = clamp_u32(cfg.auto_recovery_failure_threshold, 1u, 16u, 3u);

    if (!launcher_instance_launch_history_load(services, paths, hist)) {
        if (out_error) *out_error = "load_launch_history_failed";
        return false;
    }
    failures = consecutive_failures(hist);

    rec.threshold = threshold;
    rec.consecutive_failures = failures;
    rec.suggest_safe_mode = (failures >= threshold) ? 1u : 0u;
    rec.suggest_rollback = (failures >= threshold) ? 1u : 0u;

    if (!requested_overrides.request_safe_mode && failures >= threshold) {
        effective.request_safe_mode = 1u;
        effective.safe_mode_allow_network = 0u;
        rec.auto_entered_safe_mode = 1u;
    }

    if (!launcher_prelaunch_build_plan(services,
                                       profile_constraints,
                                       instance_id,
                                       state_root,
                                       effective,
                                       out_plan,
                                       audit,
                                       out_error)) {
        if (out_error && out_error->empty()) {
            *out_error = "prelaunch_plan_failed";
        }
        return false;
    }

    audit_emit_plan_summary(audit, out_plan, rec);

    out_recovery = rec;
    return true;
}

bool launcher_launch_finalize_attempt(const launcher_services_api_v1* services,
                                     const LauncherPrelaunchPlan& plan,
                                     u32 outcome,
                                     i32 exit_code,
                                     const std::string& detail,
                                     u32 confirm_safe_mode_writeback,
                                     LauncherAuditLog* audit,
                                     std::string* out_error) {
    const launcher_fs_api_v1* fs = get_fs(services);
    const launcher_time_api_v1* time_api = get_time(services);
    LauncherInstancePaths paths;
    LauncherInstanceLaunchHistory hist;
    LauncherInstanceLaunchAttempt att;
    u64 now_us = 0ull;
    u32 final_outcome = outcome;

    if (out_error) {
        out_error->clear();
    }
    if (!services || !fs || !time_api || !time_api->now_us) {
        if (out_error) *out_error = "missing_services_fs_or_time";
        return false;
    }
    if (plan.instance_id.empty() || plan.state_root.empty()) {
        if (out_error) *out_error = "missing_plan_ids";
        return false;
    }
    if (!launcher_is_safe_id_component(plan.instance_id)) {
        if (out_error) *out_error = "unsafe_instance_id";
        audit_reason(audit, std::string("launch_finalize;result=fail;code=unsafe_instance_id;instance_id=") + plan.instance_id);
        return false;
    }

    paths = launcher_instance_paths_make(plan.state_root, plan.instance_id);
    if (!launcher_instance_launch_history_load(services, paths, hist)) {
        if (out_error) *out_error = "load_launch_history_failed";
        return false;
    }

    hist.instance_id = plan.instance_id;
    hist.max_entries = clamp_u32(plan.persisted_config.launch_history_max_entries, 1u, 64u, 10u);

    if (!plan.validation.ok &&
        (outcome == (u32)LAUNCHER_LAUNCH_OUTCOME_REFUSAL || outcome == (u32)LAUNCHER_LAUNCH_OUTCOME_MISSING_ARTIFACT)) {
        final_outcome = classify_refusal_outcome(plan);
    }

    now_us = time_api->now_us();
    att.timestamp_us = now_us;
    att.manifest_hash64 = plan.base_manifest_hash64;
    att.config_hash64 = plan.resolved_config_hash64;
    att.safe_mode = plan.resolved.safe_mode ? 1u : 0u;
    att.outcome = final_outcome;
    att.exit_code = exit_code;
    att.detail = detail;

    launcher_instance_launch_history_append(hist, att);
    if (!launcher_instance_launch_history_store(services, paths, hist)) {
        if (out_error) *out_error = "store_launch_history_failed";
        return false;
    }

    audit_reason(audit,
                 std::string("launch_outcome;instance_id=") + plan.instance_id +
                     ";result=" + outcome_name(final_outcome) +
                     ";safe_mode=" + (plan.resolved.safe_mode ? "1" : "0") +
                     ";exit_code=" + i32_dec_string(exit_code) +
                     (detail.empty() ? std::string() : (std::string(";detail=") + detail)));

    /* Last-known-good management: mark only after successful launch; safe mode requires explicit confirmation. */
    if (outcome == (u32)LAUNCHER_LAUNCH_OUTCOME_SUCCESS) {
        const bool allow_writeback = (plan.resolved.safe_mode == 0u) || (confirm_safe_mode_writeback != 0u);
        if (allow_writeback) {
            LauncherInstanceManifest updated;
            if (!launcher_instance_verify_or_repair(services, plan.instance_id, plan.state_root, 0u, updated, audit)) {
                audit_reason(audit, std::string("last_known_good;result=fail;code=verify_or_repair_failed;instance_id=") + plan.instance_id);
                if (out_error) *out_error = "post_launch_known_good_failed";
            } else {
                audit_reason(audit, std::string("last_known_good;result=ok;instance_id=") + plan.instance_id);
            }
        } else {
            audit_reason(audit, std::string("last_known_good;result=skipped;reason=safe_mode_no_confirm;instance_id=") + plan.instance_id);
        }
    }

    return true;
}

} /* namespace launcher_core */
} /* namespace dom */
