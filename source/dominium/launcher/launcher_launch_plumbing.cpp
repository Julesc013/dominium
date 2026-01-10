/*
FILE: source/dominium/launcher/launcher_launch_plumbing.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher / launch_plumbing
RESPONSIBILITY: Implements per-attempt handshake generation, persistence, validation, and spawn plumbing.
*/

#include "launcher_launch_plumbing.h"

#include <algorithm>
#include <cstdio>
#include <cstring>
#include <cstdlib>

extern "C" {
#include "domino/caps.h"
#include "domino/core/spacetime.h"
#include "domino/profile.h"
#include "domino/system/dsys.h"
}

#include "core/include/launcher_audit.h"
#include "core/include/launcher_exit_status.h"
#include "core/include/launcher_handshake.h"
#include "core/include/launcher_instance_launch_history.h"
#include "core/include/launcher_job.h"
#include "core/include/launcher_launch_attempt.h"
#include "core/include/launcher_log.h"
#include "core/include/launcher_pack_resolver.h"
#include "core/include/launcher_run_summary.h"
#include "core/include/launcher_selection_summary.h"
#include "core/include/launcher_safety.h"
#include "core/include/launcher_sha256.h"
#include "core/include/launcher_tools_registry.h"

#include "launcher_caps_snapshot.h"
#include "launcher_caps_solver.h"
#include "launcher_coredata_sim.h"
#include "dom_feature_epoch.h"
#include "dominium/core_tlv.h"
#include "dominium/coredata_schema.h"

namespace dom {

namespace {

static bool str_lt(const std::string& a, const std::string& b) {
    return a < b;
}

static void sort_strings(std::vector<std::string>& v) {
    std::sort(v.begin(), v.end(), str_lt);
}

static bool is_sep(char c) {
    return c == '/' || c == '\\';
}

static std::string normalize_seps(const std::string& in) {
    std::string out = in;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        if (out[i] == '\\') out[i] = '/';
    }
    return out;
}

static std::string path_join(const std::string& a, const std::string& b) {
    std::string aa = normalize_seps(a);
    std::string bb = normalize_seps(b);
    if (aa.empty()) return bb;
    if (bb.empty()) return aa;
    if (is_sep(aa[aa.size() - 1u])) return aa + bb;
    return aa + "/" + bb;
}

static bool set_env_var_value(const char* key, const char* value) {
#if defined(_WIN32) || defined(_WIN64)
    if (!key) {
        return false;
    }
    if (!value) {
        value = "";
    }
    return _putenv_s(key, value) == 0;
#else
    if (!key) {
        return false;
    }
    if (!value) {
        return unsetenv(key) == 0;
    }
    return setenv(key, value, 1) == 0;
#endif
}

struct ScopedEnvVar {
    const char* key;
    std::string prev_value;
    bool had_prev;
    bool ok;

    ScopedEnvVar(const char* k, const char* value)
        : key(k),
          prev_value(),
          had_prev(false),
          ok(false) {
        if (!key) {
            return;
        }
        {
            const char* cur = std::getenv(key);
            if (cur) {
                had_prev = true;
                prev_value = cur;
            }
        }
        ok = set_env_var_value(key, value);
    }

    ~ScopedEnvVar() {
        if (!key) {
            return;
        }
        if (had_prev) {
            (void)set_env_var_value(key, prev_value.c_str());
        } else {
            (void)set_env_var_value(key, 0);
        }
    }
};

static bool write_file_all(const std::string& path, const std::vector<unsigned char>& bytes) {
    FILE* f = std::fopen(path.c_str(), "wb");
    size_t wrote = 0u;
    if (!f) return false;
    if (!bytes.empty()) {
        wrote = std::fwrite(&bytes[0], 1u, bytes.size(), f);
    }
    std::fclose(f);
    return wrote == bytes.size();
}

static bool file_exists(const std::string& path) {
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) return false;
    std::fclose(f);
    return true;
}

static bool read_file_all(const std::string& path, std::vector<unsigned char>& out_bytes) {
    FILE* f;
    long sz;
    size_t got;
    out_bytes.clear();
    f = std::fopen(path.c_str(), "rb");
    if (!f) {
        return false;
    }
    if (std::fseek(f, 0, SEEK_END) != 0) {
        std::fclose(f);
        return false;
    }
    sz = std::ftell(f);
    if (sz < 0) {
        std::fclose(f);
        return false;
    }
    if (std::fseek(f, 0, SEEK_SET) != 0) {
        std::fclose(f);
        return false;
    }
    if (sz == 0) {
        std::fclose(f);
        return true;
    }
    out_bytes.resize((size_t)sz);
    got = std::fread(out_bytes.empty() ? (void*)0 : &out_bytes[0], 1u, (size_t)sz, f);
    std::fclose(f);
    if (got != (size_t)sz) {
        out_bytes.clear();
        return false;
    }
    return true;
}

static std::string u64_hex16(u64 v) {
    char buf[17];
    static const char* hex = "0123456789abcdef";
    int i;
    for (i = 0; i < 16; ++i) {
        unsigned shift = (unsigned)((15 - i) * 4);
        unsigned nib = (unsigned)((v >> shift) & (u64)0xFu);
        buf[i] = hex[nib & 0xFu];
    }
    buf[16] = '\0';
    return std::string(buf);
}

static std::string i32_to_string(i32 v) {
    char buf[32];
    std::snprintf(buf, sizeof(buf), "%d", (int)v);
    return std::string(buf);
}

static std::string u32_to_string(u32 v) {
    char buf[32];
    std::snprintf(buf, sizeof(buf), "%u", (unsigned)v);
    return std::string(buf);
}

#if defined(_WIN32) || defined(_WIN64)
extern "C" int _mkdir(const char* path);
extern "C" int _rmdir(const char* path);
#else
extern "C" int mkdir(const char* path, unsigned int mode);
extern "C" int rmdir(const char* path);
#endif

static void mkdir_one_best_effort(const std::string& path) {
    if (path.empty()) return;
#if defined(_WIN32) || defined(_WIN64)
    (void)_mkdir(path.c_str());
#else
    (void)mkdir(path.c_str(), 0777u);
#endif
}

static void mkdir_p_best_effort(const std::string& path) {
    std::string p = normalize_seps(path);
    size_t i;
    if (p.empty()) return;
    for (i = 0u; i < p.size(); ++i) {
        if (p[i] == '/') {
            std::string part = p.substr(0u, i);
            if (!part.empty()) mkdir_one_best_effort(part);
        }
    }
    mkdir_one_best_effort(p);
}

static void rmdir_best_effort(const std::string& path) {
#if defined(_WIN32) || defined(_WIN64)
    (void)_rmdir(path.c_str());
#else
    (void)rmdir(path.c_str());
#endif
}

static void remove_file_best_effort(const std::string& path) {
    (void)std::remove(path.c_str());
}

static const char* selection_entry_why(const LauncherCapsSelection* e) {
    if (!e) {
        return "";
    }
    return e->chosen_by_override ? "override" : "priority";
}

static const LauncherCapsSelection* selection_find_entry(const std::vector<LauncherCapsSelection>& sel,
                                                         u32 subsystem_id) {
    size_t i;
    for (i = 0u; i < sel.size(); ++i) {
        const LauncherCapsSelection* e = &sel[i];
        if (e && e->subsystem_id == subsystem_id) {
            return e;
        }
    }
    return (const LauncherCapsSelection*)0;
}

static bool select_backends_for_handshake(const dom_profile* profile,
                                         std::vector<std::string>& out_platform,
                                         std::vector<std::string>& out_renderer,
                                         std::string& out_ui,
                                         std::string& out_error,
                                         LauncherCapsSolveResult* out_caps,
                                         std::string* out_note) {
    LauncherCapsSolveResult caps;

    out_platform.clear();
    out_renderer.clear();
    out_ui.clear();
    out_error.clear();
    if (out_note) {
        out_note->clear();
    }
    if (out_caps) {
        *out_caps = LauncherCapsSolveResult();
    }

    if (!launcher_caps_solve(profile, caps, out_error)) {
        if (out_caps) {
            *out_caps = caps;
        }
        return false;
    }

    out_platform = caps.platform_backends;
    out_renderer = caps.renderer_backends;
    out_ui = caps.ui_backend;

    if (out_platform.empty()) {
        out_error = "platform_backend_missing";
        if (out_caps) {
            *out_caps = caps;
        }
        return false;
    }
    if (out_ui.empty()) {
        out_error = "ui_backend_missing";
        if (out_caps) {
            *out_caps = caps;
        }
        return false;
    }

    if (out_note && !caps.note.empty()) {
        *out_note = caps.note;
    }
    if (out_caps) {
        *out_caps = caps;
    }
    return true;
}

static std::string launcher_profile_id_from_dom_profile(const dom_profile* p) {
    if (!p) {
        return std::string("unknown");
    }
    {
        const bool lockstep = (p->lockstep_strict != 0u);
        switch (p->kind) {
        case DOM_PROFILE_COMPAT:   return lockstep ? "compat.lockstep" : "compat";
        case DOM_PROFILE_BASELINE: return lockstep ? "baseline.lockstep" : "baseline";
        case DOM_PROFILE_PERF:     return lockstep ? "perf.lockstep" : "perf";
        default:                   return lockstep ? "unknown.lockstep" : "unknown";
        }
    }
}

static std::string determinism_profile_id_from_dom_profile(const dom_profile* p) {
    if (!p) {
        return std::string("default");
    }
    return (p->lockstep_strict != 0u) ? std::string("lockstep_strict") : std::string("default");
}

static u32 perf_tier_from_dom_profile(const dom_profile* p) {
    if (!p) {
        return dom::DOM_PERF_TIER_BASELINE;
    }
    switch (p->kind) {
    case DOM_PROFILE_PERF:     return dom::DOM_PERF_TIER_MODERN;
    case DOM_PROFILE_COMPAT:   return dom::DOM_PERF_TIER_BASELINE;
    case DOM_PROFILE_BASELINE: return dom::DOM_PERF_TIER_BASELINE;
    default:                   return dom::DOM_PERF_TIER_BASELINE;
    }
}

static std::vector<unsigned char> sha256_of_manifest(const dom::launcher_core::LauncherInstanceManifest& m) {
    std::vector<unsigned char> tlv;
    unsigned char h[dom::launcher_core::LAUNCHER_SHA256_BYTES];
    std::vector<unsigned char> out;
    std::memset(h, 0, sizeof(h));
    if (!dom::launcher_core::launcher_instance_manifest_to_tlv_bytes(m, tlv)) {
        return out;
    }
    dom::launcher_core::launcher_sha256_bytes(tlv.empty() ? (const unsigned char*)0 : &tlv[0], tlv.size(), h);
    out.assign(h, h + (size_t)dom::launcher_core::LAUNCHER_SHA256_BYTES);
    return out;
}

static bool manifest_has_enabled_entry_id(const dom::launcher_core::LauncherInstanceManifest& manifest, const std::string& id) {
    size_t i;
    for (i = 0u; i < manifest.content_entries.size(); ++i) {
        const dom::launcher_core::LauncherContentEntry& e = manifest.content_entries[i];
        if (e.id == id && e.enabled != 0u) {
            return true;
        }
    }
    return false;
}

static bool is_pack_like_content_type(u32 t) {
    return t == (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK ||
           t == (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD ||
           t == (u32)dom::launcher_core::LAUNCHER_CONTENT_RUNTIME;
}

static u32 manifest_enabled_for_type_and_id(const dom::launcher_core::LauncherInstanceManifest& manifest,
                                            u32 content_type,
                                            const std::string& id,
                                            u32 default_enabled) {
    size_t i;
    for (i = 0u; i < manifest.content_entries.size(); ++i) {
        const dom::launcher_core::LauncherContentEntry& e = manifest.content_entries[i];
        if (e.type == content_type && e.id == id) {
            return e.enabled ? 1u : 0u;
        }
    }
    return default_enabled ? 1u : 0u;
}

static void stable_sort_handshake_packs_by_id(std::vector<dom::launcher_core::LauncherHandshakePackEntry>& v) {
    size_t i;
    for (i = 1u; i < v.size(); ++i) {
        dom::launcher_core::LauncherHandshakePackEntry key = v[i];
        size_t j = i;
        while (j > 0u && key.pack_id < v[j - 1u].pack_id) {
            v[j] = v[j - 1u];
            --j;
        }
        v[j] = key;
    }
}

static void audit_add_reason(dom::launcher_core::LauncherAuditLog& audit, const std::string& s) {
    audit.reasons.push_back(s);
}

static err_t run_err_from_prelaunch_text(const std::string& text) {
    if (text == "missing_services_or_fs") {
        return err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_BAD_STATE, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_BAD_STATE);
    }
    if (text == "empty_instance_id" || text == "unsafe_instance_id") {
        return err_make((u16)ERRD_LAUNCHER, (u16)ERRC_LAUNCHER_INSTANCE_INVALID, 0u,
                        (u32)ERRMSG_LAUNCHER_INSTANCE_ID_INVALID);
    }
    if (text == "missing_state_root") {
        return err_make((u16)ERRD_LAUNCHER, (u16)ERRC_LAUNCHER_STATE_ROOT_UNAVAILABLE, 0u,
                        (u32)ERRMSG_LAUNCHER_STATE_ROOT_UNAVAILABLE);
    }
    if (text == "load_config_failed" || text == "load_launch_history_failed") {
        return err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_BAD_STATE, 0u, (u32)ERRMSG_COMMON_BAD_STATE);
    }
    if (text == "prelaunch_plan_failed") {
        return err_make((u16)ERRD_LAUNCHER, (u16)ERRC_LAUNCHER_HANDSHAKE_INVALID, 0u,
                        (u32)ERRMSG_LAUNCHER_HANDSHAKE_INVALID);
    }
    return err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INTERNAL, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_INTERNAL);
}

static err_t run_err_from_refusal_code(u32 refusal_code) {
    (void)refusal_code;
    return err_refuse((u16)ERRD_LAUNCHER, (u16)ERRC_LAUNCHER_HANDSHAKE_INVALID,
                      (u32)ERRMSG_LAUNCHER_HANDSHAKE_INVALID);
}

static void emit_run_event(const launcher_services_api_v1* services,
                           const std::string& instance_id,
                           const std::string& state_root,
                           u64 run_id,
                           u32 event_code,
                           const err_t* err,
                           u32 status_code,
                           u32 refusal_code) {
    core_log_event ev;
    core_log_scope scope;
    const bool safe_id = (!instance_id.empty() && dom::launcher_core::launcher_is_safe_id_component(instance_id));

    core_log_event_clear(&ev);
    ev.domain = CORE_LOG_DOMAIN_LAUNCHER;
    ev.code = (u16)event_code;
    if (event_code == CORE_LOG_EVT_OP_FAIL) {
        ev.severity = CORE_LOG_SEV_ERROR;
    } else if (event_code == CORE_LOG_EVT_OP_REFUSED) {
        ev.severity = CORE_LOG_SEV_WARN;
    } else {
        ev.severity = CORE_LOG_SEV_INFO;
    }
    ev.msg_id = 0u;
    ev.t_mono = 0u;
    (void)core_log_event_add_u32(&ev, CORE_LOG_KEY_OPERATION_ID, CORE_LOG_OP_LAUNCHER_LAUNCH_EXECUTE);
    (void)core_log_event_add_u64(&ev, CORE_LOG_KEY_RUN_ID, run_id);
    if (status_code != 0u) {
        (void)core_log_event_add_u32(&ev, CORE_LOG_KEY_STATUS_CODE, status_code);
    }
    if (refusal_code != 0u) {
        (void)core_log_event_add_u32(&ev, CORE_LOG_KEY_REFUSAL_CODE, refusal_code);
    }
    if (err && !err_is_ok(err)) {
        launcher_log_add_err_fields(&ev, err);
    }

    std::memset(&scope, 0, sizeof(scope));
    scope.state_root = state_root.empty() ? (const char*)0 : state_root.c_str();
    if (safe_id && run_id != 0ull) {
        scope.kind = CORE_LOG_SCOPE_RUN;
        scope.instance_id = instance_id.c_str();
        scope.run_id = run_id;
    } else if (safe_id) {
        scope.kind = CORE_LOG_SCOPE_INSTANCE;
        scope.instance_id = instance_id.c_str();
    } else {
        scope.kind = CORE_LOG_SCOPE_GLOBAL;
    }
    (void)launcher_services_emit_event(services, &scope, &ev);
}

static void write_exit_status_best_effort(const std::string& path,
                                          const dom::launcher_core::LauncherExitStatus& st) {
    std::vector<unsigned char> bytes;
    (void)dom::launcher_core::launcher_exit_status_to_tlv_bytes(st, bytes);
    (void)write_file_all(path, bytes);
}

static void write_run_summary_best_effort(const std::string& path,
                                          const dom::launcher_core::LauncherRunSummary& summary) {
    std::vector<unsigned char> bytes;
    (void)dom::launcher_core::launcher_run_summary_to_tlv_bytes(summary, bytes);
    (void)write_file_all(path, bytes);
}

static u32 classify_refusal_outcome(const dom::launcher_core::LauncherPrelaunchPlan& plan) {
    size_t i;
    for (i = 0u; i < plan.validation.failures.size(); ++i) {
        const std::string& code = plan.validation.failures[i].code;
        if (code.find("missing_artifact") == 0u || code == "artifact_paths_failed") {
            return (u32)dom::launcher_core::LAUNCHER_LAUNCH_OUTCOME_MISSING_ARTIFACT;
        }
    }
    return (u32)dom::launcher_core::LAUNCHER_LAUNCH_OUTCOME_REFUSAL;
}

static bool compute_run_paths(const std::string& state_root,
                              const std::string& instance_id,
                              u64 run_id,
                              std::string& out_run_dir,
                              std::string& out_handshake_path,
                              std::string& out_audit_path) {
    if (state_root.empty() || instance_id.empty() || run_id == 0ull) {
        return false;
    }
    {
        dom::launcher_core::LauncherInstancePaths paths = dom::launcher_core::launcher_instance_paths_make(state_root, instance_id);
        std::string runs_root = path_join(paths.logs_root, "runs");
        std::string run_hex = u64_hex16(run_id);
        out_run_dir = path_join(runs_root, run_hex);
        out_handshake_path = path_join(out_run_dir, "handshake.tlv");
        out_audit_path = path_join(out_run_dir, "audit_ref.tlv");
        return true;
    }
}

static void cleanup_old_runs_best_effort(const std::string& state_root,
                                        const std::string& instance_id,
                                        u32 keep_last_runs) {
    std::vector<std::string> run_ids;
    std::string err;
    std::string pinned_failed;
    size_t total;
    size_t keep_n;
    size_t i;

    /* keep_last_runs==0 => caller opted out of cleanup. */
    if (keep_last_runs == 0u) {
        return;
    }
    if (!launcher_list_instance_runs(state_root, instance_id, run_ids, err)) {
        return;
    }
    total = run_ids.size();
    if (total == 0u) {
        return;
    }
    keep_n = (size_t)keep_last_runs;
    if (keep_n > total) {
        keep_n = total;
    }

    /* Never delete the most recent failed run automatically.
       Failure heuristic: audit exit_result != 0 (or audit missing/unreadable). */
    {
        dom::launcher_core::LauncherInstancePaths paths = dom::launcher_core::launcher_instance_paths_make(state_root, instance_id);
        const std::string runs_root = path_join(paths.logs_root, "runs");

        for (i = total; i > 0u; --i) {
            const std::string id = run_ids[i - 1u];
            const std::string dir = path_join(runs_root, id);
            std::vector<unsigned char> bytes;
            dom::launcher_core::LauncherAuditLog audit;
            const std::string p_new = path_join(dir, "audit_ref.tlv");
            const std::string p_old = path_join(dir, "launcher_audit.tlv");

            if ((!read_file_all(p_new, bytes) || bytes.empty()) && (!read_file_all(p_old, bytes) || bytes.empty())) {
                pinned_failed = id;
                break;
            }
            if (!dom::launcher_core::launcher_audit_from_tlv_bytes(bytes.empty() ? (const unsigned char*)0 : &bytes[0], bytes.size(), audit)) {
                pinned_failed = id;
                break;
            }
            if (audit.exit_result != 0) {
                pinned_failed = id;
                break;
            }
        }
    }

    /* Build keep-set: last N runs + pinned_failed (if any). */
    {
        dom::launcher_core::LauncherInstancePaths paths = dom::launcher_core::launcher_instance_paths_make(state_root, instance_id);
        const std::string runs_root = path_join(paths.logs_root, "runs");
        std::vector<std::string> keep_ids;

        keep_ids.reserve(keep_n + 1u);
        for (i = total - keep_n; i < total; ++i) {
            keep_ids.push_back(run_ids[i]);
        }
        if (!pinned_failed.empty() && std::find(keep_ids.begin(), keep_ids.end(), pinned_failed) == keep_ids.end()) {
            keep_ids.push_back(pinned_failed);
        }

        for (i = 0u; i < total; ++i) {
            const std::string id = run_ids[i];
            const std::string dir = path_join(runs_root, id);
            if (std::find(keep_ids.begin(), keep_ids.end(), id) != keep_ids.end()) {
                continue;
            }

            /* Remove known run artifacts (both legacy and current names), then rmdir. */
            remove_file_best_effort(path_join(dir, "handshake.tlv"));
            remove_file_best_effort(path_join(dir, "launch_config.tlv"));
            remove_file_best_effort(path_join(dir, "selection_summary.tlv"));
            remove_file_best_effort(path_join(dir, "last_run_summary.tlv"));
            remove_file_best_effort(path_join(dir, "caps.tlv"));
            remove_file_best_effort(path_join(dir, "events.tlv"));
            remove_file_best_effort(path_join(dir, "exit_status.tlv"));
            remove_file_best_effort(path_join(dir, "audit_ref.tlv"));
            remove_file_best_effort(path_join(dir, "stdout.txt"));
            remove_file_best_effort(path_join(dir, "stderr.txt"));

            remove_file_best_effort(path_join(dir, "launcher_handshake.tlv"));
            remove_file_best_effort(path_join(dir, "launcher_audit.tlv"));

            rmdir_best_effort(dir);
        }
    }
}

} /* namespace */

LaunchTarget::LaunchTarget()
    : is_tool(0u),
      tool_id() {
}

bool launcher_parse_launch_target(const std::string& text,
                                  LaunchTarget& out_target,
                                  std::string& out_error) {
    out_error.clear();
    out_target = LaunchTarget();
    if (text == "game") {
        out_target.is_tool = 0u;
        return true;
    }
    if (text.size() > 5u && text.compare(0u, 5u, "tool:") == 0) {
        std::string id = text.substr(5u);
        if (id.empty()) {
            out_error = "empty_tool_id";
            return false;
        }
        if (!dom::launcher_core::launcher_is_safe_id_component(id)) {
            out_error = "unsafe_tool_id";
            return false;
        }
        out_target.is_tool = 1u;
        out_target.tool_id = id;
        return true;
    }
    out_error = "bad_target";
    return false;
}

std::string launcher_launch_target_to_string(const LaunchTarget& t) {
    if (t.is_tool != 0u) {
        return std::string("tool:") + t.tool_id;
    }
    return std::string("game");
}

LaunchRunResult::LaunchRunResult()
    : ok(0u),
      run_id(0ull),
      run_dir(),
      handshake_path(),
      launch_config_path(),
      audit_path(),
      selection_summary_path(),
      run_summary_path(),
      caps_path(),
      exit_status_path(),
      refused(0u),
      refusal_code(0u),
      refusal_detail(),
      spawned(0u),
      waited(0u),
      child_exit_code(0),
      error() {
}

bool launcher_list_instance_runs(const std::string& state_root,
                                 const std::string& instance_id,
                                 std::vector<std::string>& out_run_ids,
                                 std::string& out_error) {
    std::string runs_root;
    dsys_dir_iter* it;
    dsys_dir_entry e;

    out_run_ids.clear();
    out_error.clear();

    if (state_root.empty() || instance_id.empty()) {
        out_error = "bad_args";
        return false;
    }

    {
        dom::launcher_core::LauncherInstancePaths paths = dom::launcher_core::launcher_instance_paths_make(state_root, instance_id);
        runs_root = path_join(paths.logs_root, "runs");
    }

    it = dsys_dir_open(runs_root.c_str());
    if (!it) {
        return true; /* missing directory => empty */
    }

    std::memset(&e, 0, sizeof(e));
    while (dsys_dir_next(it, &e)) {
        std::string id;
        if (!e.is_dir) {
            continue;
        }
        id = std::string(e.name);
        if (!dom::launcher_core::launcher_is_safe_id_component(id)) {
            continue;
        }
        out_run_ids.push_back(id);
    }

    dsys_dir_close(it);
    sort_strings(out_run_ids);
    return true;
}

bool launcher_execute_launch_attempt(const std::string& state_root,
                                     const std::string& instance_id,
                                     const LaunchTarget& target,
                                     const dom_profile* profile,
                                     const std::string& executable_path,
                                     const std::vector<std::string>& child_args,
                                     u32 wait_for_exit,
                                     u32 keep_last_runs,
                                     const dom::launcher_core::LauncherLaunchOverrides& overrides,
                                     LaunchRunResult& out_result) {
    const ::launcher_services_api_v1* services = ::launcher_services_null_v1();
    void* iface = 0;
    const ::launcher_time_api_v1* time = 0;
    u64 now_us = 0ull;
    dom::launcher_core::LauncherExitStatus exit_status;
    dom::launcher_core::LauncherRunSummary run_summary;
    err_t run_err;

    dom::launcher_core::LauncherPrelaunchPlan plan;
    err_t prelaunch_err = err_ok();
    bool have_plan = false;

    std::vector<std::string> platform_backends;
    std::vector<std::string> renderer_backends;
    std::string ui_backend;
    std::string caps_err;
    LauncherCapsSolveResult caps_sel;
    std::string caps_note;

    dom::launcher_core::LauncherHandshake hs;
    std::vector<unsigned char> hs_bytes;

    dom::launcher_core::LauncherAuditLog run_audit;
    std::vector<unsigned char> run_audit_bytes;

    dom::launcher_core::LauncherSelectionSummary sel_summary;
    std::vector<unsigned char> sel_summary_bytes;

    std::vector<std::string> argv_full;
    std::vector<const char*> argv_ptrs;
    dsys_proc_result pr;
    dsys_process_handle handle;
    int exit_code = 0;

    out_result = LaunchRunResult();
    caps_sel = LauncherCapsSolveResult();

    if (services && services->query_interface && services->query_interface(LAUNCHER_IID_TIME_V1, &iface) == 0) {
        time = (const ::launcher_time_api_v1*)iface;
    }
    if (time && time->now_us) {
        now_us = time->now_us();
    }
    if (now_us == 0ull) {
        now_us = 1ull;
    }

    out_result.run_id = now_us;
    exit_status = dom::launcher_core::LauncherExitStatus();
    exit_status.run_id = out_result.run_id;
    exit_status.timestamp_start_us = now_us;
    exit_status.timestamp_end_us = now_us;
    exit_status.stdout_capture_supported = 0u;
    exit_status.stderr_capture_supported = 0u;
    run_err = err_ok();

    if (state_root.empty() || instance_id.empty()) {
        out_result.error = "bad_args";
        return false;
    }
    if (!dom::launcher_core::launcher_is_safe_id_component(instance_id)) {
        out_result.error = "unsafe_instance_id";
        return false;
    }
    if (executable_path.empty()) {
        out_result.error = "missing_executable_path";
        return false;
    }

    if (!compute_run_paths(state_root, instance_id, out_result.run_id, out_result.run_dir, out_result.handshake_path, out_result.audit_path)) {
        out_result.error = "run_paths_failed";
        return false;
    }

    mkdir_p_best_effort(out_result.run_dir);
    out_result.launch_config_path = path_join(out_result.run_dir, "launch_config.tlv");
    out_result.run_summary_path = path_join(out_result.run_dir, "last_run_summary.tlv");
    out_result.caps_path = path_join(out_result.run_dir, "caps.tlv");
    out_result.exit_status_path = path_join(out_result.run_dir, "exit_status.tlv");
    emit_run_event(services,
                   instance_id,
                   state_root,
                   out_result.run_id,
                   CORE_LOG_EVT_OP_BEGIN,
                   (const err_t*)0,
                   0u,
                   0u);

    if (!dom::launcher_core::launcher_job_run_launch_prepare(services,
                                                             instance_id,
                                                             state_root,
                                                             overrides,
                                                             plan,
                                                             &prelaunch_err)) {
        const bool has_err_id = !err_is_ok(&prelaunch_err);
        const char* err_id = has_err_id ? err_to_string_id(&prelaunch_err) : "";
        if (!plan.instance_id.empty()) {
            have_plan = true;
        }
        out_result.refused = 1u;
        if (prelaunch_err.flags & (u32)ERRF_POLICY_REFUSAL) {
            out_result.refusal_code = (u32)dom::launcher_core::LAUNCHER_HANDSHAKE_REFUSAL_PRELAUNCH_VALIDATION_FAILED;
            out_result.refusal_detail = std::string("prelaunch_validation_failed") +
                                        (has_err_id ? std::string(";err=") + err_id : std::string());
        } else {
            out_result.refusal_code = (u32)dom::launcher_core::LAUNCHER_HANDSHAKE_REFUSAL_MISSING_REQUIRED_FIELDS;
            out_result.refusal_detail = std::string("prelaunch_failed") +
                                        (has_err_id ? std::string(";err=") + err_id : std::string());
        }
        if (err_is_ok(&run_err)) {
            run_err = has_err_id ? prelaunch_err : run_err_from_prelaunch_text(std::string("prelaunch_plan_failed"));
        }
    } else {
        have_plan = true;
    }

    /* Persist resolved launch config for this attempt (best-effort). */
    {
        std::vector<unsigned char> cfg_bytes;
        (void)dom::launcher_core::launcher_resolved_launch_config_to_tlv_bytes(plan.resolved, cfg_bytes);
        (void)write_file_all(out_result.launch_config_path, cfg_bytes);
    }

    if (have_plan && out_result.refused == 0u && plan.validation.ok == 0u) {
        out_result.refused = 1u;
        out_result.refusal_code = (u32)dom::launcher_core::LAUNCHER_HANDSHAKE_REFUSAL_PRELAUNCH_VALIDATION_FAILED;
        if (!plan.validation.failures.empty()) {
            out_result.refusal_detail = std::string("prelaunch_validation_failed;code=") + plan.validation.failures[0].code;
            if (!plan.validation.failures[0].detail.empty()) {
                out_result.refusal_detail += std::string(";detail=") + plan.validation.failures[0].detail;
            }
        } else {
            out_result.refusal_detail = "prelaunch_validation_failed";
        }
        if (err_is_ok(&run_err)) {
            run_err = run_err_from_refusal_code(out_result.refusal_code);
        }
    }

    {
        const bool caps_ok = select_backends_for_handshake(profile,
                                                           platform_backends,
                                                           renderer_backends,
                                                           ui_backend,
                                                           caps_err,
                                                           &caps_sel,
                                                           &caps_note);
        if (!caps_ok && out_result.refused == 0u) {
            out_result.refused = 1u;
            out_result.refusal_code = (u32)dom::launcher_core::LAUNCHER_HANDSHAKE_REFUSAL_MISSING_REQUIRED_FIELDS;
            out_result.refusal_detail = std::string("caps_failed;") + caps_err;
            if (err_is_ok(&run_err)) {
                run_err = run_err_from_refusal_code(out_result.refusal_code);
            }
        }
    }

    if (out_result.refused == 0u && target.is_tool != 0u) {
        dom::launcher_core::LauncherToolsRegistry reg;
        dom::launcher_core::LauncherToolEntry te;
        std::string loaded_path;
        std::string tool_err;
        size_t i;

        if (!dom::launcher_core::launcher_tools_registry_load(services, state_root, reg, &loaded_path, &tool_err)) {
            out_result.refused = 1u;
            out_result.refusal_code = (u32)dom::launcher_core::LAUNCHER_HANDSHAKE_REFUSAL_MISSING_REQUIRED_FIELDS;
            out_result.refusal_detail = std::string("tools_registry_load_failed;") + tool_err;
            if (err_is_ok(&run_err)) {
                run_err = run_err_from_refusal_code(out_result.refusal_code);
            }
        } else if (!dom::launcher_core::launcher_tools_registry_find(reg, target.tool_id, te)) {
            out_result.refused = 1u;
            out_result.refusal_code = (u32)dom::launcher_core::LAUNCHER_HANDSHAKE_REFUSAL_MISSING_REQUIRED_FIELDS;
            out_result.refusal_detail = std::string("tool_not_found;tool_id=") + target.tool_id;
            if (err_is_ok(&run_err)) {
                run_err = run_err_from_refusal_code(out_result.refusal_code);
            }
        } else {
            for (i = 0u; i < te.required_packs.size(); ++i) {
                if (!manifest_has_enabled_entry_id(plan.effective_manifest, te.required_packs[i])) {
                    out_result.refused = 1u;
                    out_result.refusal_code = (u32)dom::launcher_core::LAUNCHER_HANDSHAKE_REFUSAL_MISSING_REQUIRED_FIELDS;
                    out_result.refusal_detail = std::string("tool_required_pack_missing;tool_id=") + target.tool_id +
                                                ";pack_id=" + te.required_packs[i];
                    if (err_is_ok(&run_err)) {
                        run_err = run_err_from_refusal_code(out_result.refusal_code);
                    }
                    break;
                }
            }
        }
    }

    /* Caps snapshot (per-run + latest). */
    {
        LauncherCapsSnapshot caps;
        std::string caps_err;
        if (launcher_caps_snapshot_build(profile, caps, caps_err)) {
            if (!out_result.caps_path.empty()) {
                (void)launcher_caps_snapshot_write_tlv(caps, out_result.caps_path, caps_err);
            }
            if (!state_root.empty()) {
                const std::string logs_root = path_join(state_root, "logs");
                const std::string latest = path_join(logs_root, "caps_latest.tlv");
                mkdir_p_best_effort(logs_root);
                (void)launcher_caps_snapshot_write_tlv(caps, latest, caps_err);
            }
        }
    }

    /* Build handshake (always attempt to write one for this run). */
    hs = dom::launcher_core::LauncherHandshake();
    hs.run_id = out_result.run_id;
    hs.instance_id = instance_id;
    hs.launcher_profile_id = launcher_profile_id_from_dom_profile(profile);
    hs.determinism_profile_id = determinism_profile_id_from_dom_profile(profile);
    hs.selected_platform_backends = platform_backends;
    hs.selected_renderer_backends = renderer_backends;
    hs.selected_ui_backend_id = ui_backend;
    hs.timestamp_monotonic_us = now_us;
    hs.has_timestamp_wall_us = 0u;
    hs.has_sim_caps = 1u;
    dom_sim_caps_init_default(hs.sim_caps);
    hs.has_perf_caps = 1u;
    dom_perf_caps_init_default(hs.perf_caps, perf_tier_from_dom_profile(profile));
    hs.has_feature_epoch = 1u;
    hs.feature_epoch = dom_feature_epoch_current();
    hs.has_coredata_sim_hash = 0u;
    hs.coredata_sim_hash64 = 0ull;
    hs.has_provider_bindings_hash = 0u;
    hs.provider_bindings_hash64 = 0ull;
    if (have_plan && out_result.refused == 0u) {
        u64 sim_hash = 0ull;
        std::string core_err;
        if (launcher_coredata_sim_hash_from_manifest(plan.effective_manifest,
                                                      state_root,
                                                      sim_hash,
                                                      core_err)) {
            hs.has_coredata_sim_hash = 1u;
            hs.coredata_sim_hash64 = sim_hash;
        } else {
            out_result.refused = 1u;
            out_result.refusal_code = (u32)dom::launcher_core::LAUNCHER_HANDSHAKE_REFUSAL_MISSING_REQUIRED_FIELDS;
            out_result.refusal_detail = std::string("coredata_sim_hash_failed;") + core_err;
            if (err_is_ok(&run_err)) {
                run_err = run_err_from_refusal_code(out_result.refusal_code);
            }
        }
    }
    if (have_plan) {
        hs.pinned_engine_build_id = plan.effective_manifest.pinned_engine_build_id;
        hs.pinned_game_build_id = plan.effective_manifest.pinned_game_build_id;
        hs.instance_manifest_hash_bytes = sha256_of_manifest(plan.effective_manifest);
        {
            std::vector<dom::launcher_core::LauncherResolvedPack> ordered;
            std::string pack_err;
            size_t i;
            if (dom::launcher_core::launcher_pack_resolve_enabled(services, plan.effective_manifest, state_root, ordered, &pack_err)) {
                for (i = 0u; i < ordered.size(); ++i) {
                    dom::launcher_core::LauncherHandshakePackEntry pe;
                    pe.pack_id = ordered[i].pack_id;
                    pe.version = ordered[i].version;
                    pe.hash_bytes = ordered[i].artifact_hash_bytes;
                    pe.enabled = 1u;
                    pe.sim_affecting_flags = ordered[i].sim_affecting_flags;
                    if (plan.resolved.safe_mode) {
                        pe.safe_mode_flags.push_back("safe_mode");
                    }
                    pe.offline_mode_flag = (plan.resolved.allow_network != 0u) ? 0u : 1u;
                    hs.resolved_packs.push_back(pe);
                }
            } else {
                /* Preserve refusal behavior via handshake validation below. */
                (void)pack_err;
            }
        }

        /* Safe mode: include pack-like entries that were disabled by safe mode for diagnostics. */
        if (plan.resolved.safe_mode) {
            std::vector<dom::launcher_core::LauncherHandshakePackEntry> disabled;
            size_t i;
            for (i = 0u; i < plan.base_manifest.content_entries.size(); ++i) {
                const dom::launcher_core::LauncherContentEntry& e = plan.base_manifest.content_entries[i];
                const u32 eff_enabled = manifest_enabled_for_type_and_id(plan.effective_manifest, e.type, e.id, e.enabled);
                if (e.enabled == 0u) {
                    continue;
                }
                if (!is_pack_like_content_type(e.type)) {
                    continue;
                }
                if (eff_enabled != 0u) {
                    continue;
                }

                dom::launcher_core::LauncherHandshakePackEntry pe;
                pe.pack_id = e.id;
                pe.version = e.version;
                pe.hash_bytes = e.hash_bytes;
                pe.enabled = 0u;
                pe.safe_mode_flags.push_back("safe_mode");
                pe.safe_mode_flags.push_back("disabled_by_safe_mode");
                pe.offline_mode_flag = (plan.resolved.allow_network != 0u) ? 0u : 1u;
                disabled.push_back(pe);
            }

            if (!disabled.empty()) {
                stable_sort_handshake_packs_by_id(disabled);
                for (i = 0u; i < disabled.size(); ++i) {
                    hs.resolved_packs.push_back(disabled[i]);
                }
            }
        }
    }

    (void)dom::launcher_core::launcher_handshake_to_tlv_bytes(hs, hs_bytes);
    (void)write_file_all(out_result.handshake_path, hs_bytes);

    if (out_result.refused == 0u) {
        std::string detail;
        u32 code = dom::launcher_core::launcher_handshake_validate(services,
                                                                   hs,
                                                                   plan.effective_manifest,
                                                                   state_root,
                                                                   &detail);
        if (code != (u32)dom::launcher_core::LAUNCHER_HANDSHAKE_REFUSAL_OK) {
            out_result.refused = 1u;
            out_result.refusal_code = code;
            out_result.refusal_detail = detail;
            if (err_is_ok(&run_err)) {
                run_err = run_err_from_refusal_code(out_result.refusal_code);
            }
        }
    }

    /* Per-run audit record */
    run_audit = dom::launcher_core::LauncherAuditLog();
    run_audit.run_id = out_result.run_id;
    run_audit.timestamp_us = now_us;
    run_audit.selected_profile_id = launcher_profile_id_from_dom_profile(profile);
    run_audit.manifest_hash64 = have_plan ? dom::launcher_core::launcher_instance_manifest_hash64(plan.effective_manifest) : 0ull;

    audit_add_reason(run_audit, std::string("operation=launch"));
    audit_add_reason(run_audit, std::string("instance_id=") + instance_id);
    audit_add_reason(run_audit, std::string("launch_target=") + launcher_launch_target_to_string(target));
    audit_add_reason(run_audit, std::string("executable_path=") + executable_path);
    audit_add_reason(run_audit, std::string("handshake_path=") + out_result.handshake_path);
    audit_add_reason(run_audit, std::string("launch_config_path=") + out_result.launch_config_path);
    audit_add_reason(run_audit, std::string("exit_status_path=") + out_result.exit_status_path);

    audit_add_reason(run_audit, std::string("safe_mode=") + std::string(plan.resolved.safe_mode ? "1" : "0"));
    audit_add_reason(run_audit, std::string("offline_mode=") + std::string(plan.resolved.allow_network ? "0" : "1"));
    if (!caps_note.empty()) {
        audit_add_reason(run_audit, caps_note);
    }

    /* Selected backends (selected-and-why) */
    {
        size_t i;
        for (i = 0u; i < caps_sel.selections.size(); ++i) {
            const LauncherCapsSelection* e = &caps_sel.selections[i];
            if (!e || e->backend_name.empty()) {
                continue;
            }
            dom::launcher_core::LauncherAuditBackend b;
            b.subsystem_id = e->subsystem_id;
            b.subsystem_name = e->subsystem_name;
            b.backend_name = e->backend_name;
            b.determinism_grade = e->determinism;
            b.perf_class = e->perf_class;
            b.priority = e->priority;
            b.chosen_by_override = e->chosen_by_override ? 1u : 0u;
            run_audit.selected_backends.push_back(b);
        }
    }

    /* Selection summary snapshot (single source of truth for CLI/UI/diag/audit). */
    {
        const std::string selection_path = path_join(out_result.run_dir, "selection_summary.tlv");
        out_result.selection_summary_path = selection_path;

        sel_summary = dom::launcher_core::LauncherSelectionSummary();
        sel_summary.run_id = out_result.run_id;
        sel_summary.instance_id = instance_id;
        sel_summary.launcher_profile_id = hs.launcher_profile_id;
        sel_summary.determinism_profile_id = hs.determinism_profile_id;
        sel_summary.offline_mode = (plan.resolved.allow_network != 0u) ? 0u : 1u;
        sel_summary.safe_mode = plan.resolved.safe_mode ? 1u : 0u;
        sel_summary.manifest_hash64 = run_audit.manifest_hash64;
        sel_summary.manifest_hash_bytes = hs.instance_manifest_hash_bytes;

        sel_summary.ui_backend.backend_id = hs.selected_ui_backend_id;
        {
            const LauncherCapsSelection* e = selection_find_entry(caps_sel.selections, (u32)DOM_SUBSYS_DUI);
            sel_summary.ui_backend.why = selection_entry_why(e);
        }
        {
            size_t i;
            for (i = 0u; i < platform_backends.size(); ++i) {
                dom::launcher_core::LauncherSelectionBackendChoice c;
                c.backend_id = platform_backends[i];
                {
                    const LauncherCapsSelection* e = selection_find_entry(caps_sel.selections, (u32)DOM_SUBSYS_DSYS);
                    c.why = selection_entry_why(e);
                }
                sel_summary.platform_backends.push_back(c);
            }
        }
        {
            size_t i;
            for (i = 0u; i < renderer_backends.size(); ++i) {
                dom::launcher_core::LauncherSelectionBackendChoice c;
                c.backend_id = renderer_backends[i];
                {
                    const LauncherCapsSelection* e = selection_find_entry(caps_sel.selections, (u32)DOM_SUBSYS_DGFX);
                    c.why = selection_entry_why(e);
                }
                sel_summary.renderer_backends.push_back(c);
            }
        }
        {
            size_t i;
            for (i = 0u; i < caps_sel.provider_backends.size(); ++i) {
                dom::launcher_core::LauncherSelectionProviderChoice p;
                p.provider_type = caps_sel.provider_backends[i].provider_type;
                p.provider_id = caps_sel.provider_backends[i].provider_id;
                p.why = caps_sel.provider_backends[i].why;
                sel_summary.provider_backends.push_back(p);
            }
        }

        sel_summary.resolved_packs_count = 0u;
        {
            size_t i;
            for (i = 0u; i < hs.resolved_packs.size(); ++i) {
                if (hs.resolved_packs[i].enabled == 0u) {
                    continue;
                }
                if (sel_summary.resolved_packs_count) {
                    sel_summary.resolved_packs_summary += ",";
                }
                sel_summary.resolved_packs_summary += hs.resolved_packs[i].pack_id;
                sel_summary.resolved_packs_count += 1u;
            }
        }

        (void)launcher_caps_write_effective_caps_tlv(caps_sel.effective_caps, sel_summary.effective_caps_tlv);
        (void)launcher_caps_write_explain_tlv(caps_sel.solver_result, sel_summary.explanation_tlv);

        (void)dom::launcher_core::launcher_selection_summary_to_tlv_bytes(sel_summary, sel_summary_bytes);
        (void)write_file_all(selection_path, sel_summary_bytes);

        run_audit.has_selection_summary = 1u;
        run_audit.selection_summary_tlv = sel_summary_bytes;
        audit_add_reason(run_audit, std::string("selection_summary_path=") + selection_path);
    }

    if (out_result.refused != 0u) {
        u32 outcome = (u32)dom::launcher_core::LAUNCHER_LAUNCH_OUTCOME_REFUSAL;
        if (have_plan) {
            outcome = classify_refusal_outcome(plan);
        }
        audit_add_reason(run_audit, std::string("outcome=refusal"));
        audit_add_reason(run_audit, std::string("refusal_code=") + u32_to_string(out_result.refusal_code));
        audit_add_reason(run_audit, std::string("refusal_detail=") + out_result.refusal_detail);
        run_audit.exit_result = 2;
        run_audit.err = run_err;
        (void)dom::launcher_core::launcher_audit_to_tlv_bytes(run_audit, run_audit_bytes);
        (void)write_file_all(out_result.audit_path, run_audit_bytes);
        if (time && time->now_us) {
            const u64 end_us = time->now_us();
            exit_status.timestamp_end_us = (end_us < exit_status.timestamp_start_us) ? exit_status.timestamp_start_us : end_us;
        }
        exit_status.exit_code = 2;
        exit_status.termination_type = (u32)dom::launcher_core::LAUNCHER_TERM_REFUSED;
        write_exit_status_best_effort(out_result.exit_status_path, exit_status);
        emit_run_event(services,
                       instance_id,
                       state_root,
                       out_result.run_id,
                       CORE_LOG_EVT_OP_REFUSED,
                       err_is_ok(&run_err) ? (const err_t*)0 : &run_err,
                       (u32)exit_status.exit_code,
                       out_result.refusal_code);
        run_summary = dom::launcher_core::LauncherRunSummary();
        run_summary.run_id = out_result.run_id;
        run_summary.instance_id = instance_id;
        run_summary.outcome = outcome;
        run_summary.exit_code = exit_status.exit_code;
        run_summary.termination_type = exit_status.termination_type;
        run_summary.refusal_code = out_result.refusal_code;
        run_summary.err = run_err;
        write_run_summary_best_effort(out_result.run_summary_path, run_summary);
        cleanup_old_runs_best_effort(state_root, instance_id, keep_last_runs);
        out_result.ok = 0u;
        return false;
    }

    /* Spawn child */
    argv_full.clear();
    argv_full.push_back(executable_path);
    {
        size_t i;
        for (i = 0u; i < child_args.size(); ++i) {
            argv_full.push_back(child_args[i]);
        }
    }
    {
        std::string handshake_rel = "handshake.tlv";
        if (!out_result.run_dir.empty()) {
            std::string run_dir = normalize_seps(out_result.run_dir);
            std::string hs_path = normalize_seps(out_result.handshake_path);
            if (!run_dir.empty() && run_dir[run_dir.size() - 1u] != '/') {
                run_dir.push_back('/');
            }
            if (!run_dir.empty() && hs_path.compare(0u, run_dir.size(), run_dir) == 0u) {
                handshake_rel = hs_path.substr(run_dir.size());
            }
        }
        argv_full.push_back(std::string("--handshake=") + handshake_rel);
    }

    argv_ptrs.resize(argv_full.size() + 1u);
    {
        size_t i;
        for (i = 0u; i < argv_full.size(); ++i) {
            argv_ptrs[i] = argv_full[i].c_str();
        }
        argv_ptrs[argv_full.size()] = 0;
    }

    bool env_ok = !out_result.run_dir.empty();
    std::memset(&handle, 0, sizeof(handle));
    {
        ScopedEnvVar run_root_env("DOMINIUM_RUN_ROOT", out_result.run_dir.c_str());
        ScopedEnvVar home_root_env("DOMINIUM_HOME", state_root.empty() ? (const char*)0 : state_root.c_str());
        env_ok = env_ok && run_root_env.ok && home_root_env.ok;
        if (env_ok) {
            pr = dsys_proc_spawn(executable_path.c_str(), &argv_ptrs[0], 1, wait_for_exit ? &handle : (dsys_process_handle*)0);
        } else {
            pr = DSYS_PROC_ERROR_GENERIC;
        }
    }
    if (pr != DSYS_PROC_OK) {
        out_result.spawned = 0u;
        out_result.ok = 0u;
        run_err = err_make((u16)ERRD_PROC, (u16)ERRC_PROC_SPAWN_FAILED,
                           (u32)(ERRF_TRANSIENT | ERRF_RETRYABLE),
                           (u32)ERRMSG_PROC_SPAWN_FAILED);
        run_audit.exit_result = 1;
        audit_add_reason(run_audit, "outcome=spawn_failed");
        if (!env_ok) {
            audit_add_reason(run_audit, "env_set_failed");
        }
        run_audit.err = run_err;
        (void)dom::launcher_core::launcher_audit_to_tlv_bytes(run_audit, run_audit_bytes);
        (void)write_file_all(out_result.audit_path, run_audit_bytes);
        if (time && time->now_us) {
            const u64 end_us = time->now_us();
            exit_status.timestamp_end_us = (end_us < exit_status.timestamp_start_us) ? exit_status.timestamp_start_us : end_us;
        }
        exit_status.exit_code = 1;
        exit_status.termination_type = (u32)dom::launcher_core::LAUNCHER_TERM_UNKNOWN;
        write_exit_status_best_effort(out_result.exit_status_path, exit_status);
        emit_run_event(services,
                       instance_id,
                       state_root,
                       out_result.run_id,
                       CORE_LOG_EVT_OP_FAIL,
                       &run_err,
                       (u32)exit_status.exit_code,
                       0u);
        run_summary = dom::launcher_core::LauncherRunSummary();
        run_summary.run_id = out_result.run_id;
        run_summary.instance_id = instance_id;
        run_summary.outcome = (u32)dom::launcher_core::LAUNCHER_LAUNCH_OUTCOME_CRASH;
        run_summary.exit_code = exit_status.exit_code;
        run_summary.termination_type = exit_status.termination_type;
        run_summary.err = run_err;
        write_run_summary_best_effort(out_result.run_summary_path, run_summary);
        cleanup_old_runs_best_effort(state_root, instance_id, keep_last_runs);
        out_result.error = env_ok ? "spawn_failed" : "spawn_env_failed";
        return false;
    }

    out_result.spawned = 1u;

    if (wait_for_exit) {
        out_result.waited = 1u;
        pr = dsys_proc_wait(&handle, &exit_code);
        if (pr != DSYS_PROC_OK) {
            out_result.ok = 0u;
            run_err = err_make((u16)ERRD_PROC, (u16)ERRC_PROC_WAIT_FAILED,
                               (u32)(ERRF_TRANSIENT | ERRF_RETRYABLE),
                               (u32)ERRMSG_PROC_WAIT_FAILED);
            run_audit.exit_result = 1;
            audit_add_reason(run_audit, "outcome=wait_failed");
            run_audit.err = run_err;
            (void)dom::launcher_core::launcher_audit_to_tlv_bytes(run_audit, run_audit_bytes);
            (void)write_file_all(out_result.audit_path, run_audit_bytes);
            if (time && time->now_us) {
                const u64 end_us = time->now_us();
                exit_status.timestamp_end_us = (end_us < exit_status.timestamp_start_us) ? exit_status.timestamp_start_us : end_us;
            }
            exit_status.exit_code = 1;
            exit_status.termination_type = (u32)dom::launcher_core::LAUNCHER_TERM_UNKNOWN;
            write_exit_status_best_effort(out_result.exit_status_path, exit_status);
            emit_run_event(services,
                           instance_id,
                           state_root,
                           out_result.run_id,
                           CORE_LOG_EVT_OP_FAIL,
                           &run_err,
                           (u32)exit_status.exit_code,
                           0u);
            run_summary = dom::launcher_core::LauncherRunSummary();
            run_summary.run_id = out_result.run_id;
            run_summary.instance_id = instance_id;
            run_summary.outcome = (u32)dom::launcher_core::LAUNCHER_LAUNCH_OUTCOME_CRASH;
            run_summary.exit_code = exit_status.exit_code;
            run_summary.termination_type = exit_status.termination_type;
            run_summary.err = run_err;
            write_run_summary_best_effort(out_result.run_summary_path, run_summary);
            cleanup_old_runs_best_effort(state_root, instance_id, keep_last_runs);
            out_result.error = "wait_failed";
            return false;
        }
        out_result.child_exit_code = (i32)exit_code;
        run_audit.exit_result = (i32)exit_code;
        audit_add_reason(run_audit, std::string("outcome=exit"));
        audit_add_reason(run_audit, std::string("child_exit_code=") + i32_to_string((i32)exit_code));
    } else {
        out_result.waited = 0u;
        run_audit.exit_result = 0;
        audit_add_reason(run_audit, std::string("outcome=spawned"));
    }

    (void)dom::launcher_core::launcher_audit_to_tlv_bytes(run_audit, run_audit_bytes);
    (void)write_file_all(out_result.audit_path, run_audit_bytes);

    if (time && time->now_us) {
        const u64 end_us = time->now_us();
        exit_status.timestamp_end_us = (end_us < exit_status.timestamp_start_us) ? exit_status.timestamp_start_us : end_us;
    }
    if (out_result.waited) {
        exit_status.exit_code = out_result.child_exit_code;
        exit_status.termination_type = (u32)dom::launcher_core::LAUNCHER_TERM_NORMAL;
    } else {
        exit_status.exit_code = 0;
        exit_status.termination_type = (u32)dom::launcher_core::LAUNCHER_TERM_UNKNOWN;
    }
    write_exit_status_best_effort(out_result.exit_status_path, exit_status);

    {
        u32 outcome = (u32)dom::launcher_core::LAUNCHER_LAUNCH_OUTCOME_SUCCESS;
        u32 event_code = CORE_LOG_EVT_OP_OK;
        if (out_result.waited && out_result.child_exit_code != 0) {
            outcome = (u32)dom::launcher_core::LAUNCHER_LAUNCH_OUTCOME_CRASH;
            event_code = CORE_LOG_EVT_OP_FAIL;
        }
        emit_run_event(services,
                       instance_id,
                       state_root,
                       out_result.run_id,
                       event_code,
                       (const err_t*)0,
                       (u32)exit_status.exit_code,
                       0u);
        run_summary = dom::launcher_core::LauncherRunSummary();
        run_summary.run_id = out_result.run_id;
        run_summary.instance_id = instance_id;
        run_summary.outcome = outcome;
        run_summary.exit_code = exit_status.exit_code;
        run_summary.termination_type = exit_status.termination_type;
        run_summary.err = err_ok();
        write_run_summary_best_effort(out_result.run_summary_path, run_summary);
    }

    cleanup_old_runs_best_effort(state_root, instance_id, keep_last_runs);

    if (wait_for_exit) {
        out_result.ok = (out_result.child_exit_code == 0) ? 1u : 0u;
    } else {
        out_result.ok = 1u;
    }
    return out_result.ok != 0u;
}

} /* namespace dom */
