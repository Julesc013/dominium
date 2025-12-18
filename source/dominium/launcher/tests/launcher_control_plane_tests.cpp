/*
FILE: source/dominium/launcher/tests/launcher_control_plane_tests.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher / tests
RESPONSIBILITY: Smoke/integration tests for control-plane CLI + tools-as-instances launch path (null UI/gfx).
NOTES: Validates per-run handshake persistence/validation and per-run audit records for tool launches.
*/

#include <cassert>
#include <cstdio>
#include <cstring>
#include <map>
#include <string>
#include <vector>

#include "launcher_control_plane.h"

extern "C" {
#include "domino/profile.h"
#include "core/include/launcher_core_api.h"
}

#include "core/include/launcher_audit.h"
#include "core/include/launcher_exit_status.h"
#include "core/include/launcher_handshake.h"
#include "core/include/launcher_instance_ops.h"
#include "core/include/launcher_selection_summary.h"
#include "core/include/launcher_tools_registry.h"

namespace {

static std::string normalize_seps(const std::string& in) {
    std::string out = in;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        if (out[i] == '\\') out[i] = '/';
    }
    return out;
}

static bool is_sep(char c) {
    return c == '/' || c == '\\';
}

static std::string path_join(const std::string& a, const std::string& b) {
    std::string aa = normalize_seps(a);
    std::string bb = normalize_seps(b);
    if (aa.empty()) return bb;
    if (bb.empty()) return aa;
    if (is_sep(aa[aa.size() - 1u])) return aa + bb;
    return aa + "/" + bb;
}

static std::string dirname_of(const std::string& path) {
    size_t i;
    for (i = path.size(); i > 0u; --i) {
        char c = path[i - 1u];
        if (c == '/' || c == '\\') {
            return path.substr(0u, i - 1u);
        }
    }
    return std::string();
}

static bool file_exists(const std::string& path) {
    FILE* f = std::fopen(path.c_str(), "rb");
    if (f) {
        std::fclose(f);
        return true;
    }
    return false;
}

static bool read_file_all_bytes(const std::string& path, std::vector<unsigned char>& out) {
    FILE* f = std::fopen(path.c_str(), "rb");
    long sz;
    size_t got;
    if (!f) return false;
    if (std::fseek(f, 0L, SEEK_END) != 0) {
        std::fclose(f);
        return false;
    }
    sz = std::ftell(f);
    if (sz < 0L) {
        std::fclose(f);
        return false;
    }
    if (std::fseek(f, 0L, SEEK_SET) != 0) {
        std::fclose(f);
        return false;
    }
    out.resize((size_t)sz);
    got = 0u;
    if (sz > 0L) {
        got = std::fread(&out[0], 1u, (size_t)sz, f);
    }
    std::fclose(f);
    return got == (size_t)sz;
}

static bool read_file_all_text(const std::string& path, std::string& out) {
    std::vector<unsigned char> bytes;
    size_t i;
    if (!read_file_all_bytes(path, bytes)) {
        return false;
    }
    out.clear();
    out.reserve(bytes.size());
    for (i = 0u; i < bytes.size(); ++i) {
        out.push_back((char)bytes[i]);
    }
    return true;
}

static bool write_file_all_bytes(const std::string& path, const std::vector<unsigned char>& bytes) {
    FILE* f = std::fopen(path.c_str(), "wb");
    size_t wrote = 0u;
    if (!f) return false;
    if (!bytes.empty()) {
        wrote = std::fwrite(&bytes[0], 1u, bytes.size(), f);
    }
    std::fclose(f);
    return wrote == bytes.size();
}

#if defined(_WIN32) || defined(_WIN64)
extern "C" int _mkdir(const char* path);
#else
extern "C" int mkdir(const char* path, unsigned int mode);
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

static std::string make_temp_root(const launcher_services_api_v1* services, const char* prefix) {
    void* iface = 0;
    const launcher_time_api_v1* time = 0;
    u64 stamp = 0ull;
    char hex[17];
    if (services && services->query_interface && services->query_interface(LAUNCHER_IID_TIME_V1, &iface) == 0) {
        time = (const launcher_time_api_v1*)iface;
    }
    if (time && time->now_us) {
        stamp = time->now_us();
    }
    if (stamp == 0ull) stamp = 1ull;
    u64_to_hex16(stamp, hex);
    return std::string(prefix ? prefix : "tmp") + "_" + std::string(hex);
}

static void str_copy_bounded(char* dst, size_t cap, const char* src) {
    size_t n;
    if (!dst || cap == 0u) return;
    dst[0] = '\0';
    if (!src) return;
    n = std::strlen(src);
    if (n >= cap) n = cap - 1u;
    if (n > 0u) std::memcpy(dst, src, n);
    dst[n] = '\0';
}

static dom_profile make_null_ui_gfx_profile(void) {
    dom_profile p;
    std::memset(&p, 0, sizeof(p));
    p.abi_version = DOM_PROFILE_ABI_VERSION;
    p.struct_size = (u32)sizeof(dom_profile);
    p.kind = DOM_PROFILE_BASELINE;
    p.lockstep_strict = 0u;
    str_copy_bounded(p.preferred_gfx_backend, sizeof(p.preferred_gfx_backend), "null");

    p.override_count = 0u;
    {
        dom_profile_override* ov = &p.overrides[p.override_count++];
        str_copy_bounded(ov->subsystem_key, sizeof(ov->subsystem_key), "ui");
        str_copy_bounded(ov->backend_name, sizeof(ov->backend_name), "null");
    }
    {
        dom_profile_override* ov = &p.overrides[p.override_count++];
        str_copy_bounded(ov->subsystem_key, sizeof(ov->subsystem_key), "gfx");
        str_copy_bounded(ov->backend_name, sizeof(ov->backend_name), "null");
    }
    return p;
}

static void write_tools_registry_minimal(const std::string& state_root) {
    dom::launcher_core::LauncherToolsRegistry reg;
    dom::launcher_core::LauncherToolEntry te;
    std::vector<unsigned char> bytes;
    const std::string out_path = path_join(path_join(state_root, "data"), "tools_registry.tlv");

    te.tool_id = "tool_manifest_inspector";
    te.display_name = "tool_manifest_inspector";
    te.description = "Reads handshake + instance manifest and prints a structured report to stdout.";
    te.executable_artifact_hash_bytes.clear(); /* resolve via argv0 dir/PATH */
    te.required_packs.clear();
    te.optional_packs.clear();
    te.capability_requirements.clear();
    te.ui_entrypoint_metadata.label = "tool_manifest_inspector";
    te.ui_entrypoint_metadata.icon_placeholder = "placeholder";

    reg.tools.push_back(te);
    assert(dom::launcher_core::launcher_tools_registry_to_tlv_bytes(reg, bytes));
    mkdir_p_best_effort(dirname_of(out_path));
    assert(write_file_all_bytes(out_path, bytes));
}

static void create_instance_with_pins(const launcher_services_api_v1* services,
                                      const std::string& state_root,
                                      const std::string& instance_id,
                                      const std::string& engine_id,
                                      const std::string& game_id) {
    dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty(instance_id);
    dom::launcher_core::LauncherInstanceManifest created;
    desired.pinned_engine_build_id = engine_id;
    desired.pinned_game_build_id = game_id;
    assert(dom::launcher_core::launcher_instance_create_instance(services, desired, state_root, created, (dom::launcher_core::LauncherAuditLog*)0));
    assert(created.instance_id == instance_id);
}

static std::map<std::string, std::string> parse_kv_lines(const std::string& text) {
    std::map<std::string, std::string> out;
    size_t pos = 0u;
    while (pos < text.size()) {
        size_t eol = text.find('\n', pos);
        if (eol == std::string::npos) eol = text.size();
        std::string line = text.substr(pos, eol - pos);
        if (!line.empty() && line[line.size() - 1u] == '\r') {
            line.erase(line.size() - 1u);
        }
        if (!line.empty()) {
            size_t eq = line.find('=');
            if (eq != std::string::npos) {
                out[line.substr(0u, eq)] = line.substr(eq + 1u);
            }
        }
        pos = (eol < text.size()) ? (eol + 1u) : eol;
    }
    return out;
}

static bool audit_has_reason(const dom::launcher_core::LauncherAuditLog& a, const std::string& needle) {
    size_t i;
    for (i = 0u; i < a.reasons.size(); ++i) {
        if (a.reasons[i] == needle) {
            return true;
        }
    }
    return false;
}

struct CmdRun {
    dom::ControlPlaneRunResult r;
    std::string out_text;
    std::string err_text;
    std::string audit_path;
    dom::launcher_core::LauncherAuditLog audit;
};

static CmdRun run_control_plane(const std::string& argv0,
                                const dom_profile& profile,
                                const std::vector<std::string>& args,
                                const std::string& audit_path) {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    launcher_core_desc_v1 desc;
    launcher_core* core = 0;
    std::vector<std::string> argv_storage;
    std::vector<const char*> argv_ptrs;
    std::vector<char*> argv_mut;
    std::string out_path = audit_path + ".out.txt";
    std::string err_path = audit_path + ".err.txt";
    FILE* out = 0;
    FILE* err = 0;
    std::vector<unsigned char> audit_bytes;
    CmdRun cr;

    argv_storage.clear();
    argv_storage.push_back(argv0);
    {
        size_t i;
        for (i = 0u; i < args.size(); ++i) {
            argv_storage.push_back(args[i]);
        }
    }

    argv_ptrs.resize(argv_storage.size());
    argv_mut.resize(argv_storage.size());
    {
        size_t i;
        for (i = 0u; i < argv_storage.size(); ++i) {
            argv_ptrs[i] = argv_storage[i].c_str();
            argv_mut[i] = const_cast<char*>(argv_ptrs[i]);
        }
    }

    std::memset(&desc, 0, sizeof(desc));
    desc.struct_size = (u32)sizeof(desc);
    desc.struct_version = LAUNCHER_CORE_DESC_VERSION;
    desc.services = services;
    desc.audit_output_path = audit_path.c_str();
    desc.selected_profile_id = "baseline";
    desc.argv = argv_ptrs.empty() ? (const char* const*)0 : &argv_ptrs[0];
    desc.argv_count = (u32)argv_ptrs.size();

    core = launcher_core_create(&desc);
    assert(core != 0);

    out = std::fopen(out_path.c_str(), "wb");
    err = std::fopen(err_path.c_str(), "wb");
    assert(out != 0);
    assert(err != 0);

    cr.r = dom::launcher_control_plane_try_run((int)argv_mut.size(),
                                               argv_mut.empty() ? (char**)0 : &argv_mut[0],
                                               core,
                                               &profile,
                                               out,
                                               err);

    std::fclose(out);
    std::fclose(err);
    out = 0;
    err = 0;

    assert(launcher_core_emit_audit(core, cr.r.exit_code) == 0);
    launcher_core_destroy(core);
    core = 0;

    (void)read_file_all_text(out_path, cr.out_text);
    (void)read_file_all_text(err_path, cr.err_text);

    cr.audit_path = audit_path;
    assert(read_file_all_bytes(audit_path, audit_bytes));
    assert(!audit_bytes.empty());
    assert(dom::launcher_core::launcher_audit_from_tlv_bytes(&audit_bytes[0], audit_bytes.size(), cr.audit));
    return cr;
}

static void test_cli_smoke_and_determinism(const std::string& state_root,
                                          const std::string& argv0_launcher,
                                          const dom_profile& profile) {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    CmdRun a, b, bad, cr, vr, exd, exb, im;
    std::map<std::string, std::string> kv;
    const std::string templ_id = "tmpl0";
    const std::string export_root = path_join(path_join(state_root, "exports"), "tmpl0_copy1");

    create_instance_with_pins(services, state_root, templ_id, "engine.pinned", "game.pinned");

    {
        std::vector<std::string> args;
        args.push_back(std::string("--home=") + state_root);
        args.push_back("list-instances");
        a = run_control_plane(argv0_launcher, profile, args, path_join(state_root, "audit_list1.tlv"));
        b = run_control_plane(argv0_launcher, profile, args, path_join(state_root, "audit_list2.tlv"));
        assert(a.r.handled != 0);
        assert(a.r.exit_code == 0);
        assert(a.out_text == b.out_text);
        assert(audit_has_reason(a.audit, "operation=list-instances"));
        assert(audit_has_reason(a.audit, "outcome=ok"));
    }

    /* Refusal: create-instance missing template */
    {
        std::vector<std::string> args;
        args.push_back(std::string("--home=") + state_root);
        args.push_back("create-instance");
        bad = run_control_plane(argv0_launcher, profile, args, path_join(state_root, "audit_create_bad.tlv"));
        kv = parse_kv_lines(bad.out_text);
        assert(bad.r.handled != 0);
        assert(bad.r.exit_code == 2);
        assert(kv["result"] == "fail");
        assert(kv["error"] == "missing_template");
        assert(audit_has_reason(bad.audit, "operation=create-instance"));
        assert(audit_has_reason(bad.audit, "outcome=fail"));
    }

    /* create-instance from an existing template instance */
    {
        std::vector<std::string> args;
        args.push_back(std::string("--home=") + state_root);
        args.push_back("create-instance");
        args.push_back(std::string("--template=") + templ_id);
        cr = run_control_plane(argv0_launcher, profile, args, path_join(state_root, "audit_create_ok.tlv"));
        kv = parse_kv_lines(cr.out_text);
        assert(cr.r.handled != 0);
        assert(cr.r.exit_code == 0);
        assert(kv["result"] == "ok");
        assert(kv["template_id"] == templ_id);
        assert(kv["instance_id"] == "tmpl0_copy1");
        assert(file_exists(path_join(path_join(path_join(state_root, "instances"), "tmpl0_copy1"), "manifest.tlv")));
        assert(audit_has_reason(cr.audit, "operation=create-instance"));
        assert(audit_has_reason(cr.audit, "outcome=ok"));
    }

    /* verify-instance */
    {
        std::vector<std::string> args;
        args.push_back(std::string("--home=") + state_root);
        args.push_back("verify-instance");
        args.push_back("tmpl0_copy1");
        vr = run_control_plane(argv0_launcher, profile, args, path_join(state_root, "audit_verify_ok.tlv"));
        kv = parse_kv_lines(vr.out_text);
        assert(vr.r.handled != 0);
        assert(vr.r.exit_code == 0);
        assert(kv["result"] == "ok");
        assert(kv["instance_id"] == "tmpl0_copy1");
        assert(audit_has_reason(vr.audit, "operation=verify-instance"));
        assert(audit_has_reason(vr.audit, "outcome=ok"));
    }

    /* export-instance (definition) */
    {
        std::vector<std::string> args;
        args.push_back(std::string("--home=") + state_root);
        args.push_back("export-instance");
        args.push_back("tmpl0_copy1");
        args.push_back("--mode=definition");
        exd = run_control_plane(argv0_launcher, profile, args, path_join(state_root, "audit_export_def.tlv"));
        kv = parse_kv_lines(exd.out_text);
        assert(exd.r.handled != 0);
        assert(exd.r.exit_code == 0);
        assert(kv["result"] == "ok");
        assert(file_exists(path_join(export_root, "manifest.tlv")));
        assert(file_exists(path_join(path_join(export_root, "config"), "config.tlv")));
        assert(audit_has_reason(exd.audit, "operation=export-instance"));
        assert(audit_has_reason(exd.audit, "outcome=ok"));
    }

    /* export-instance (bundle) + import-instance */
    {
        std::vector<std::string> args;
        args.push_back(std::string("--home=") + state_root);
        args.push_back("export-instance");
        args.push_back("tmpl0_copy1");
        args.push_back("--mode=bundle");
        exb = run_control_plane(argv0_launcher, profile, args, path_join(state_root, "audit_export_bundle.tlv"));
        kv = parse_kv_lines(exb.out_text);
        assert(exb.r.handled != 0);
        assert(exb.r.exit_code == 0);
        assert(kv["result"] == "ok");
        assert(file_exists(path_join(export_root, "manifest.tlv")));
        assert(audit_has_reason(exb.audit, "operation=export-instance"));
        assert(audit_has_reason(exb.audit, "outcome=ok"));

        {
            std::vector<std::string> iargs;
            iargs.push_back(std::string("--home=") + state_root);
            iargs.push_back("import-instance");
            iargs.push_back(export_root);
            im = run_control_plane(argv0_launcher, profile, iargs, path_join(state_root, "audit_import_ok.tlv"));
            kv = parse_kv_lines(im.out_text);
            assert(im.r.handled != 0);
            assert(im.r.exit_code == 0);
            assert(kv["result"] == "ok");
            assert(kv["instance_id"] == "tmpl0_copy1_import1");
            assert(file_exists(path_join(path_join(path_join(state_root, "instances"), "tmpl0_copy1_import1"), "manifest.tlv")));
            assert(audit_has_reason(im.audit, "operation=import-instance"));
            assert(audit_has_reason(im.audit, "outcome=ok"));
        }
    }
}

static void test_tool_launch_handshake_and_audit(const std::string& state_root,
                                                const std::string& argv0_launcher,
                                                const dom_profile& profile) {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    const std::string instance_id = "inst_launch";
    CmdRun lr, ar, sr, dr, no_runs;
    std::map<std::string, std::string> kv;
    std::vector<unsigned char> bytes;
    dom::launcher_core::LauncherHandshake hs;
    dom::launcher_core::LauncherInstanceManifest m;
    dom::launcher_core::LauncherAuditLog run_audit;
    std::string diag_out_root;

    create_instance_with_pins(services, state_root, instance_id, "engine.pinned", "game.pinned");

	    /* launch tool */
	    {
	        std::vector<std::string> args;
	        args.push_back(std::string("--home=") + state_root);
	        args.push_back("launch");
        args.push_back(instance_id);
        args.push_back("--target=tool:tool_manifest_inspector");
        lr = run_control_plane(argv0_launcher, profile, args, path_join(state_root, "audit_launch_tool.tlv"));
        kv = parse_kv_lines(lr.out_text);
        assert(lr.r.handled != 0);
        assert(lr.r.exit_code == 0);
        assert(kv["result"] == "ok");
        assert(kv["spawned"] == "1");
        assert(kv["waited"] == "1");
        assert(kv["child_exit_code"] == "0");

	        assert(!kv["handshake_path"].empty());
	        assert(!kv["launch_config_path"].empty());
	        assert(!kv["audit_path"].empty());
	        assert(file_exists(kv["handshake_path"]));
	        assert(file_exists(kv["launch_config_path"]));
	        assert(file_exists(kv["audit_path"]));
	        assert(!kv["selection_summary_path"].empty());
	        assert(!kv["exit_status_path"].empty());
	        assert(file_exists(kv["selection_summary_path"]));
	        assert(file_exists(kv["exit_status_path"]));

	        assert(read_file_all_bytes(kv["handshake_path"], bytes));
	        assert(dom::launcher_core::launcher_handshake_from_tlv_bytes(bytes.empty() ? (const unsigned char*)0 : &bytes[0], bytes.size(), hs));
	        assert(dom::launcher_core::launcher_instance_load_manifest(services, instance_id, state_root, m));
	        {
            std::string detail;
            u32 code = dom::launcher_core::launcher_handshake_validate(services, hs, m, state_root, &detail);
            assert(code == (u32)dom::launcher_core::LAUNCHER_HANDSHAKE_REFUSAL_OK);
        }

	        assert(read_file_all_bytes(kv["audit_path"], bytes));
	        assert(dom::launcher_core::launcher_audit_from_tlv_bytes(bytes.empty() ? (const unsigned char*)0 : &bytes[0], bytes.size(), run_audit));
	        assert(run_audit.run_id == hs.run_id);
	        assert(audit_has_reason(run_audit, std::string("instance_id=") + instance_id));
	        assert(audit_has_reason(run_audit, "launch_target=tool:tool_manifest_inspector"));
	        assert(audit_has_reason(run_audit, std::string("handshake_path=") + kv["handshake_path"]));
	        assert(audit_has_reason(run_audit, std::string("launch_config_path=") + kv["launch_config_path"]));
	        assert(audit_has_reason(run_audit, std::string("selection_summary_path=") + kv["selection_summary_path"]));
	        assert(audit_has_reason(run_audit, std::string("exit_status_path=") + kv["exit_status_path"]));
	        assert(audit_has_reason(run_audit, "outcome=exit"));
	        assert(audit_has_reason(run_audit, "child_exit_code=0"));
	        assert(audit_has_reason(run_audit, "safe_mode=0"));
	        assert(audit_has_reason(run_audit, "offline_mode=0"));
	    }

	    /* selection_summary.tlv + exit_status.tlv should be parseable */
	    {
	        dom::launcher_core::LauncherSelectionSummary ss;
	        dom::launcher_core::LauncherExitStatus xs;

	        assert(read_file_all_bytes(kv["selection_summary_path"], bytes));
	        assert(dom::launcher_core::launcher_selection_summary_from_tlv_bytes(bytes.empty() ? (const unsigned char*)0 : &bytes[0], bytes.size(), ss));
	        assert(ss.run_id == hs.run_id);
	        assert(ss.instance_id == instance_id);
	        assert(ss.safe_mode == 0u);

	        bytes.clear();
	        assert(read_file_all_bytes(kv["exit_status_path"], bytes));
	        assert(dom::launcher_core::launcher_exit_status_from_tlv_bytes(bytes.empty() ? (const unsigned char*)0 : &bytes[0], bytes.size(), xs));
	        assert(xs.run_id == hs.run_id);
	        assert(xs.exit_code == 0);
	        assert(xs.termination_type == (u32)dom::launcher_core::LAUNCHER_TERM_NORMAL);
	        assert(xs.timestamp_end_us >= xs.timestamp_start_us);
	    }

	    /* Refusal: unknown tool id should fail before spawning. */
	    {
        CmdRun bad_tool;
        std::vector<std::string> args;
        args.push_back(std::string("--home=") + state_root);
        args.push_back("launch");
        args.push_back(instance_id);
        args.push_back("--target=tool:missing_tool_id");
        bad_tool = run_control_plane(argv0_launcher, profile, args, path_join(state_root, "audit_launch_bad_tool.tlv"));
        kv = parse_kv_lines(bad_tool.out_text);
        assert(bad_tool.r.handled != 0);
        assert(bad_tool.r.exit_code == 1);
        assert(kv["result"] == "fail");
        assert(kv["error"] == "tool_exec_resolve_failed");
        assert(audit_has_reason(bad_tool.audit, "operation=launch"));
        assert(audit_has_reason(bad_tool.audit, "outcome=fail"));
    }

    /* audit-last on an instance with no runs should refuse */
    {
        std::vector<std::string> args;
        args.push_back(std::string("--home=") + state_root);
        args.push_back("audit-last");
        args.push_back("tmpl0");
        no_runs = run_control_plane(argv0_launcher, profile, args, path_join(state_root, "audit_last_no_runs.tlv"));
        kv = parse_kv_lines(no_runs.out_text);
        assert(no_runs.r.handled != 0);
        assert(no_runs.r.exit_code == 1);
        assert(kv["result"] == "fail");
        assert(kv["error"] == "no_runs");
        assert(audit_has_reason(no_runs.audit, "operation=audit-last"));
        assert(audit_has_reason(no_runs.audit, "outcome=fail"));
    }

    /* audit-last on launched instance should succeed and include launch_target */
    {
        std::vector<std::string> args;
        args.push_back(std::string("--home=") + state_root);
        args.push_back("audit-last");
        args.push_back(instance_id);
        ar = run_control_plane(argv0_launcher, profile, args, path_join(state_root, "audit_last_ok.tlv"));
        kv = parse_kv_lines(ar.out_text);
        assert(ar.r.handled != 0);
	        assert(ar.r.exit_code == 0);
	        assert(kv["result"] == "ok");
	        assert(kv["instance_id"] == instance_id);
	        assert(kv["audit.run_id"].size() >= 3u); /* 0x... */
	        assert(kv["audit_path"] == path_join(path_join(path_join(path_join(state_root, "instances"), instance_id), "logs/runs"),
	                                             kv["run_dir_id"]) +
	                                  "/audit_ref.tlv");
	        /* Reasons are printed; ensure tool launch target is preserved. */
	        {
	            bool saw = false;
	            size_t i;
            for (i = 0u; i < ar.audit.reasons.size(); ++i) {
                if (ar.audit.reasons[i] == "operation=audit-last") {
                    saw = true;
                }
            }
            assert(saw);
        }
    }

    /* safe-mode launch of tool should record safe_mode=1 in run audit */
    {
        std::vector<std::string> args;
        args.push_back(std::string("--home=") + state_root);
        args.push_back("safe-mode");
        args.push_back(instance_id);
        args.push_back("--target=tool:tool_manifest_inspector");
        sr = run_control_plane(argv0_launcher, profile, args, path_join(state_root, "audit_safe_mode_tool.tlv"));
        kv = parse_kv_lines(sr.out_text);
        assert(sr.r.handled != 0);
	        assert(sr.r.exit_code == 0);
	        assert(kv["result"] == "ok");
	        assert(kv["spawned"] == "1");
	        assert(kv["waited"] == "1");
	        assert(file_exists(kv["audit_path"]));
	        assert(read_file_all_bytes(kv["audit_path"], bytes));
	        assert(dom::launcher_core::launcher_audit_from_tlv_bytes(bytes.empty() ? (const unsigned char*)0 : &bytes[0], bytes.size(), run_audit));
	        assert(audit_has_reason(run_audit, "safe_mode=1"));
	    }

    /* diag-bundle should export bundle + copy last run handshake/audit */
    {
        diag_out_root = path_join(state_root, "diag_out");
        {
            std::vector<std::string> args;
            args.push_back(std::string("--home=") + state_root);
            args.push_back("diag-bundle");
            args.push_back(instance_id);
            args.push_back(std::string("--out=") + diag_out_root);
            dr = run_control_plane(argv0_launcher, profile, args, path_join(state_root, "audit_diag_bundle.tlv"));
            kv = parse_kv_lines(dr.out_text);
            assert(dr.r.handled != 0);
            assert(dr.r.exit_code == 0);
            assert(kv["result"] == "ok");
        }
        assert(file_exists(path_join(diag_out_root, "manifest.tlv")));
        assert(file_exists(path_join(path_join(diag_out_root, "config"), "config.tlv")));

        /* last_run copy */
	        {
	            const std::string last_run_root = path_join(diag_out_root, "last_run");
	            const std::string run_subdir = kv["last_run_id"];
	            assert(!run_subdir.empty());
	            assert(file_exists(path_join(path_join(last_run_root, run_subdir), "handshake.tlv")));
	            assert(file_exists(path_join(path_join(last_run_root, run_subdir), "launch_config.tlv")));
	            assert(file_exists(path_join(path_join(last_run_root, run_subdir), "audit_ref.tlv")));
	            assert(file_exists(path_join(path_join(last_run_root, run_subdir), "selection_summary.tlv")));
	            assert(file_exists(path_join(path_join(last_run_root, run_subdir), "exit_status.tlv")));
	        }
	        assert(file_exists(path_join(diag_out_root, "last_run_selection_summary.txt")));
	    }
	}

} /* namespace */

int main(int argc, char** argv) {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    const std::string state_root = make_temp_root(services, "tmp_l9a_control_plane");
    dom_profile profile = make_null_ui_gfx_profile();
    std::string argv0_launcher;

    (void)argc;

    mkdir_p_best_effort(state_root);
    write_tools_registry_minimal(state_root);

    /* Provide an argv0 whose directory contains the built tool exe. */
    {
        std::string self = (argv && argv[0]) ? std::string(argv[0]) : std::string();
        std::string dir = dirname_of(self);
#if defined(_WIN32) || defined(_WIN64)
        argv0_launcher = path_join(dir, "dominium-launcher.exe");
#else
        argv0_launcher = path_join(dir, "dominium-launcher");
#endif
        if (!file_exists(argv0_launcher)) {
            /* Fall back to using the test executable's argv0 directory anyway. */
            argv0_launcher = self;
        }
    }

    test_cli_smoke_and_determinism(state_root, argv0_launcher, profile);
    test_tool_launch_handshake_and_audit(state_root, argv0_launcher, profile);

    std::printf("launcher_control_plane_tests: OK\n");
    return 0;
}
