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

extern "C" {
#include "domino/caps.h"
#include "domino/profile.h"
#include "domino/system/dsys.h"
}

#include "core/include/launcher_audit.h"
#include "core/include/launcher_handshake.h"
#include "core/include/launcher_launch_attempt.h"
#include "core/include/launcher_pack_resolver.h"
#include "core/include/launcher_safety.h"
#include "core/include/launcher_sha256.h"
#include "core/include/launcher_tools_registry.h"

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

static bool select_backends_for_handshake(const dom_profile* profile,
                                         std::vector<std::string>& out_platform,
                                         std::vector<std::string>& out_renderer,
                                         std::string& out_ui,
                                         std::string& out_error) {
    dom_hw_caps hw;
    dom_selection sel;
    dom_caps_result rc;
    u32 i;

    out_platform.clear();
    out_renderer.clear();
    out_ui.clear();
    out_error.clear();

    (void)dom_caps_register_builtin_backends();
    (void)dom_caps_finalize_registry();

    std::memset(&hw, 0, sizeof(hw));
    hw.abi_version = DOM_CAPS_ABI_VERSION;
    hw.struct_size = (u32)sizeof(hw);
    (void)dom_hw_caps_probe_host(&hw);

    std::memset(&sel, 0, sizeof(sel));
    sel.abi_version = DOM_CAPS_ABI_VERSION;
    sel.struct_size = (u32)sizeof(sel);

    rc = dom_caps_select(profile, &hw, &sel);
    if (rc != DOM_CAPS_OK) {
        out_error = "caps_select_failed";
        return false;
    }

    for (i = 0u; i < sel.entry_count; ++i) {
        const dom_selection_entry* e = &sel.entries[i];
        if (!e || !e->backend_name || !e->backend_name[0]) {
            continue;
        }
        if (e->subsystem_id == DOM_SUBSYS_DSYS) {
            out_platform.push_back(std::string(e->backend_name));
        } else if (e->subsystem_id == DOM_SUBSYS_DGFX) {
            out_renderer.push_back(std::string(e->backend_name));
        } else if (e->subsystem_id == DOM_SUBSYS_DUI) {
            out_ui = std::string(e->backend_name);
        }
    }

    if (out_platform.empty()) {
        out_error = "platform_backend_missing";
        return false;
    }
    if (out_ui.empty()) {
        out_error = "ui_backend_missing";
        return false;
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

static void audit_add_reason(dom::launcher_core::LauncherAuditLog& audit, const std::string& s) {
    audit.reasons.push_back(s);
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
        out_handshake_path = path_join(out_run_dir, "launcher_handshake.tlv");
        out_audit_path = path_join(out_run_dir, "launcher_audit.tlv");
        return true;
    }
}

static void cleanup_old_runs_best_effort(const std::string& state_root,
                                        const std::string& instance_id,
                                        u32 keep_last_runs) {
    std::vector<std::string> run_ids;
    std::string err;
    if (keep_last_runs == 0u) {
        return;
    }
    if (!launcher_list_instance_runs(state_root, instance_id, run_ids, err)) {
        return;
    }
    if (run_ids.size() <= (size_t)keep_last_runs) {
        return;
    }
    {
        dom::launcher_core::LauncherInstancePaths paths = dom::launcher_core::launcher_instance_paths_make(state_root, instance_id);
        std::string runs_root = path_join(paths.logs_root, "runs");
        while (run_ids.size() > (size_t)keep_last_runs) {
            const std::string oldest = run_ids[0];
            const std::string dir = path_join(runs_root, oldest);
            remove_file_best_effort(path_join(dir, "launcher_handshake.tlv"));
            remove_file_best_effort(path_join(dir, "launcher_audit.tlv"));
            rmdir_best_effort(dir);
            run_ids.erase(run_ids.begin());
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
      audit_path(),
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

    dom::launcher_core::LauncherPrelaunchPlan plan;
    dom::launcher_core::LauncherRecoverySuggestion recovery;
    std::string prelaunch_err;

    std::vector<std::string> platform_backends;
    std::vector<std::string> renderer_backends;
    std::string ui_backend;
    std::string caps_err;

    dom::launcher_core::LauncherHandshake hs;
    std::vector<unsigned char> hs_bytes;

    dom::launcher_core::LauncherAuditLog run_audit;
    std::vector<unsigned char> run_audit_bytes;

    std::vector<std::string> argv_full;
    std::vector<const char*> argv_ptrs;
    dsys_proc_result pr;
    dsys_process_handle handle;
    int exit_code = 0;

    out_result = LaunchRunResult();

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

    if (!dom::launcher_core::launcher_launch_prepare_attempt(services,
                                                            (const dom::launcher_core::LauncherProfile*)0,
                                                            instance_id,
                                                            state_root,
                                                            overrides,
                                                            plan,
                                                            recovery,
                                                            (dom::launcher_core::LauncherAuditLog*)0,
                                                            &prelaunch_err)) {
        out_result.refused = 1u;
        out_result.refusal_code = (u32)dom::launcher_core::LAUNCHER_HANDSHAKE_REFUSAL_MISSING_REQUIRED_FIELDS;
        out_result.refusal_detail = std::string("prelaunch_failed;") + prelaunch_err;
    }

    if (out_result.refused == 0u) {
        if (!select_backends_for_handshake(profile, platform_backends, renderer_backends, ui_backend, caps_err)) {
            out_result.refused = 1u;
            out_result.refusal_code = (u32)dom::launcher_core::LAUNCHER_HANDSHAKE_REFUSAL_MISSING_REQUIRED_FIELDS;
            out_result.refusal_detail = std::string("caps_failed;") + caps_err;
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
        } else if (!dom::launcher_core::launcher_tools_registry_find(reg, target.tool_id, te)) {
            out_result.refused = 1u;
            out_result.refusal_code = (u32)dom::launcher_core::LAUNCHER_HANDSHAKE_REFUSAL_MISSING_REQUIRED_FIELDS;
            out_result.refusal_detail = std::string("tool_not_found;tool_id=") + target.tool_id;
        } else {
            for (i = 0u; i < te.required_packs.size(); ++i) {
                if (!manifest_has_enabled_entry_id(plan.effective_manifest, te.required_packs[i])) {
                    out_result.refused = 1u;
                    out_result.refusal_code = (u32)dom::launcher_core::LAUNCHER_HANDSHAKE_REFUSAL_MISSING_REQUIRED_FIELDS;
                    out_result.refusal_detail = std::string("tool_required_pack_missing;tool_id=") + target.tool_id +
                                                ";pack_id=" + te.required_packs[i];
                    break;
                }
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
    if (out_result.refused == 0u) {
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
        }
    }

    /* Per-run audit record */
    run_audit = dom::launcher_core::LauncherAuditLog();
    run_audit.run_id = out_result.run_id;
    run_audit.timestamp_us = now_us;
    run_audit.selected_profile_id = launcher_profile_id_from_dom_profile(profile);
    run_audit.manifest_hash64 = (out_result.refused == 0u) ? dom::launcher_core::launcher_instance_manifest_hash64(plan.effective_manifest) : 0ull;

    audit_add_reason(run_audit, std::string("operation=launch"));
    audit_add_reason(run_audit, std::string("instance_id=") + instance_id);
    audit_add_reason(run_audit, std::string("launch_target=") + launcher_launch_target_to_string(target));
    audit_add_reason(run_audit, std::string("executable_path=") + executable_path);
    audit_add_reason(run_audit, std::string("handshake_path=") + out_result.handshake_path);

    audit_add_reason(run_audit, std::string("safe_mode=") + std::string(plan.resolved.safe_mode ? "1" : "0"));
    audit_add_reason(run_audit, std::string("offline_mode=") + std::string(plan.resolved.allow_network ? "0" : "1"));

    if (out_result.refused != 0u) {
        audit_add_reason(run_audit, std::string("outcome=refusal"));
        audit_add_reason(run_audit, std::string("refusal_code=") + u32_to_string(out_result.refusal_code));
        audit_add_reason(run_audit, std::string("refusal_detail=") + out_result.refusal_detail);
        run_audit.exit_result = 2;
        (void)dom::launcher_core::launcher_audit_to_tlv_bytes(run_audit, run_audit_bytes);
        (void)write_file_all(out_result.audit_path, run_audit_bytes);
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
    argv_full.push_back(std::string("--handshake=") + out_result.handshake_path);

    argv_ptrs.resize(argv_full.size() + 1u);
    {
        size_t i;
        for (i = 0u; i < argv_full.size(); ++i) {
            argv_ptrs[i] = argv_full[i].c_str();
        }
        argv_ptrs[argv_full.size()] = 0;
    }

    std::memset(&handle, 0, sizeof(handle));
    pr = dsys_proc_spawn(executable_path.c_str(), &argv_ptrs[0], 1, wait_for_exit ? &handle : (dsys_process_handle*)0);
    if (pr != DSYS_PROC_OK) {
        out_result.spawned = 0u;
        out_result.ok = 0u;
        run_audit.exit_result = 1;
        audit_add_reason(run_audit, "outcome=spawn_failed");
        (void)dom::launcher_core::launcher_audit_to_tlv_bytes(run_audit, run_audit_bytes);
        (void)write_file_all(out_result.audit_path, run_audit_bytes);
        cleanup_old_runs_best_effort(state_root, instance_id, keep_last_runs);
        out_result.error = "spawn_failed";
        return false;
    }

    out_result.spawned = 1u;

    if (wait_for_exit) {
        out_result.waited = 1u;
        pr = dsys_proc_wait(&handle, &exit_code);
        if (pr != DSYS_PROC_OK) {
            out_result.ok = 0u;
            run_audit.exit_result = 1;
            audit_add_reason(run_audit, "outcome=wait_failed");
            (void)dom::launcher_core::launcher_audit_to_tlv_bytes(run_audit, run_audit_bytes);
            (void)write_file_all(out_result.audit_path, run_audit_bytes);
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

    cleanup_old_runs_best_effort(state_root, instance_id, keep_last_runs);

    if (wait_for_exit) {
        out_result.ok = (out_result.child_exit_code == 0) ? 1u : 0u;
    } else {
        out_result.ok = 1u;
    }
    return out_result.ok != 0u;
}

} /* namespace dom */
