/*
FILE: source/dominium/launcher/launcher_control_plane.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher / control_plane
RESPONSIBILITY: Non-interactive orchestration surface for dominium-launcher (command-style CLI).
*/

#include "launcher_control_plane.h"

#include <algorithm>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

extern "C" {
#include "domino/sys.h"
}

#include "launcher_launch_plumbing.h"

#include "core/include/launcher_pack_ops.h"
#include "core/include/launcher_safety.h"

#include "core/include/launcher_audit.h"
#include "core/include/launcher_artifact_store.h"
#include "core/include/launcher_instance.h"
#include "core/include/launcher_instance_ops.h"
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

static void out_kv(FILE* out, const char* key, const std::string& val) {
    if (!out || !key) return;
    std::fprintf(out, "%s=%s\n", key, val.c_str());
}

static void out_kv(FILE* out, const char* key, const char* val) {
    if (!out || !key) return;
    std::fprintf(out, "%s=%s\n", key, val ? val : "");
}

static void out_kv_u32(FILE* out, const char* key, u32 v) {
    char buf[32];
    std::snprintf(buf, sizeof(buf), "%u", (unsigned)v);
    out_kv(out, key, buf);
}

static void audit_reason_kv(::launcher_core* core, const char* key, const std::string& val) {
    if (!core || !key) return;
    (void)launcher_core_add_reason(core, (std::string(key) + "=" + val).c_str());
}

static void audit_reason_kv(::launcher_core* core, const char* key, const char* val) {
    if (!core || !key) return;
    (void)launcher_core_add_reason(core, (std::string(key) + "=" + (val ? val : "")).c_str());
}

static int find_command_index(int argc, char** argv) {
    int i;
    for (i = 1; i < argc; ++i) {
        const char* a = argv[i];
        if (!a || !a[0]) continue;
        if (a[0] == '-') continue;
        return i;
    }
    return -1;
}

static const char* find_arg_value(int argc, char** argv, const char* prefix) {
    int i;
    size_t n;
    if (!prefix) return 0;
    n = std::strlen(prefix);
    for (i = 1; i < argc; ++i) {
        const char* a = argv[i];
        if (!a) continue;
        if (std::strncmp(a, prefix, n) == 0) {
            return a + (int)n;
        }
    }
    return 0;
}

static std::string compute_state_root(int argc, char** argv) {
    const char* h = find_arg_value(argc, argv, "--home=");
    if (h && h[0]) {
        return std::string(h);
    }
    return std::string(".");
}

static bool list_instances(const std::string& state_root, std::vector<std::string>& out_ids) {
    dsys_dir_iter* it;
    dsys_dir_entry e;
    std::string instances_root = path_join(state_root, "instances");

    out_ids.clear();

    it = dsys_dir_open(instances_root.c_str());
    if (!it) {
        return true;
    }

    std::memset(&e, 0, sizeof(e));
    while (dsys_dir_next(it, &e)) {
        std::string id;
        std::string manifest_path;

        if (!e.is_dir) {
            continue;
        }
        id = std::string(e.name);
        if (!dom::launcher_core::launcher_is_safe_id_component(id)) {
            continue;
        }
        manifest_path = path_join(path_join(instances_root, id), "manifest.tlv");
        if (!file_exists(manifest_path)) {
            continue;
        }
        out_ids.push_back(id);
    }

    dsys_dir_close(it);
    sort_strings(out_ids);
    return true;
}

static bool instance_exists(const std::string& state_root, const std::string& instance_id) {
    const std::string p = path_join(path_join(path_join(state_root, "instances"), instance_id), "manifest.tlv");
    return file_exists(p);
}

static std::string u32_to_string(u32 v) {
    char buf[32];
    std::snprintf(buf, sizeof(buf), "%u", (unsigned)v);
    return std::string(buf);
}

static std::string i32_to_string(i32 v) {
    char buf[32];
    std::snprintf(buf, sizeof(buf), "%d", (int)v);
    return std::string(buf);
}

static std::string u64_hex16(u64 v) {
    static const char* hex = "0123456789abcdef";
    char buf[17];
    int i;
    for (i = 0; i < 16; ++i) {
        unsigned shift = (unsigned)((15 - i) * 4);
        unsigned nib = (unsigned)((v >> shift) & (u64)0xFu);
        buf[i] = hex[nib & 0xFu];
    }
    buf[16] = '\0';
    return std::string(buf);
}

static bool ends_with_ci(const std::string& s, const char* suffix) {
    size_t ls;
    size_t lx;
    size_t i;
    if (!suffix) return false;
    ls = s.size();
    lx = std::strlen(suffix);
    if (lx == 0u || ls < lx) return false;
    for (i = 0u; i < lx; ++i) {
        char a = s[ls - lx + i];
        char b = suffix[i];
        if (a >= 'A' && a <= 'Z') a = (char)(a - 'A' + 'a');
        if (b >= 'A' && b <= 'Z') b = (char)(b - 'A' + 'a');
        if (a != b) return false;
    }
    return true;
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

static std::string basename_of(const std::string& path) {
    size_t i;
    for (i = path.size(); i > 0u; --i) {
        char c = path[i - 1u];
        if (c == '/' || c == '\\') {
            return path.substr(i);
        }
    }
    return path;
}

#if defined(_WIN32) || defined(_WIN64)
static std::string add_exe_if_missing(const std::string& p) {
    if (ends_with_ci(p, ".exe")) {
        return p;
    }
    return p + ".exe";
}
#else
static std::string add_exe_if_missing(const std::string& p) { return p; }
#endif

static bool resolve_tool_executable_path(const ::launcher_services_api_v1* services,
                                        const std::string& state_root,
                                        const std::string& argv0,
                                        const std::string& tool_id,
                                        std::string& out_path,
                                        std::string& out_error) {
    dom::launcher_core::LauncherToolsRegistry reg;
    dom::launcher_core::LauncherToolEntry te;
    std::string loaded;
    std::string err;
    std::string dir;

    out_path.clear();
    out_error.clear();

    if (!dom::launcher_core::launcher_tools_registry_load(services, state_root, reg, &loaded, &err)) {
        out_error = std::string("tools_registry_load_failed;") + err;
        return false;
    }
    if (!dom::launcher_core::launcher_tools_registry_find(reg, tool_id, te)) {
        out_error = std::string("tool_not_found;tool_id=") + tool_id;
        return false;
    }

    if (!te.executable_artifact_hash_bytes.empty()) {
        std::string artifact_dir;
        std::string meta_path;
        std::string payload_path;
        if (dom::launcher_core::launcher_artifact_store_paths(state_root,
                                                              te.executable_artifact_hash_bytes,
                                                              artifact_dir,
                                                              meta_path,
                                                              payload_path) &&
            file_exists(payload_path)) {
            out_path = payload_path;
            return true;
        }
    }

    dir = dirname_of(argv0);
    if (!dir.empty()) {
        std::string cand0 = path_join(dir, tool_id);
        std::string cand1 = add_exe_if_missing(cand0);
        if (file_exists(cand0)) {
            out_path = cand0;
            return true;
        }
        if (file_exists(cand1)) {
            out_path = cand1;
            return true;
        }
    }

    /* Fall back to PATH/current-directory resolution by the process layer. */
    out_path = add_exe_if_missing(tool_id);
    return true;
}

static bool resolve_game_executable_path(const std::string& argv0,
                                        std::string& out_path) {
    std::string dir = dirname_of(argv0);
    std::string name0 = "dominium_game";
    std::string name1 = add_exe_if_missing(name0);

    out_path.clear();

    if (!dir.empty()) {
        std::string cand0 = path_join(dir, name0);
        std::string cand1 = path_join(dir, name1);
        if (file_exists(cand0)) {
            out_path = cand0;
            return true;
        }
        if (file_exists(cand1)) {
            out_path = cand1;
            return true;
        }

        {
            const std::string tail = basename_of(dir);
            if (tail == "Debug" || tail == "Release") {
                const std::string config = tail;
                const std::string dominium_dir = dirname_of(dirname_of(dir));
                if (!dominium_dir.empty()) {
                    std::string cand2 = path_join(path_join(path_join(dominium_dir, "game"), config), name1);
                    if (file_exists(cand2)) {
                        out_path = cand2;
                        return true;
                    }
                }
            }
        }
    }

    if (file_exists(name1)) {
        out_path = name1;
        return true;
    }

    return false;
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

static bool copy_file_best_effort(const std::string& src, const std::string& dst) {
    std::vector<unsigned char> bytes;
    if (!read_file_all(src, bytes)) {
        return false;
    }
    mkdir_p_best_effort(dirname_of(dst));
    return write_file_all(dst, bytes);
}

static std::string choose_new_instance_id(const std::string& state_root, const std::string& template_id) {
    const std::string base = template_id + std::string("_copy");
    u32 i;
    for (i = 1u; i < 10000u; ++i) {
        std::string candidate = base + u32_to_string(i);
        if (!instance_exists(state_root, candidate)) {
            return candidate;
        }
    }
    return base + std::string("10000");
}

static std::string choose_import_instance_id(const std::string& state_root, const std::string& imported_id) {
    if (dom::launcher_core::launcher_is_safe_id_component(imported_id) && !instance_exists(state_root, imported_id)) {
        return imported_id;
    }
    {
        const std::string base = imported_id + std::string("_import");
        u32 i;
        for (i = 1u; i < 10000u; ++i) {
            std::string candidate = base + u32_to_string(i);
            if (dom::launcher_core::launcher_is_safe_id_component(candidate) && !instance_exists(state_root, candidate)) {
                return candidate;
            }
        }
        return base + std::string("10000");
    }
}

} /* namespace */

ControlPlaneRunResult::ControlPlaneRunResult()
    : handled(0),
      exit_code(0) {
}

ControlPlaneRunResult launcher_control_plane_try_run(int argc,
                                                     char** argv,
                                                     ::launcher_core* audit_core,
                                                     const dom_profile* profile,
                                                     FILE* out,
                                                     FILE* err) {
    ControlPlaneRunResult r;
    int cmd_i;
    const char* cmd;
    std::string state_root;
    const ::launcher_services_api_v1* services = ::launcher_services_null_v1();

    (void)profile;
    (void)err;

    cmd_i = find_command_index(argc, argv);
    if (cmd_i < 0) {
        return r;
    }
    cmd = argv[cmd_i];
    if (!cmd || !cmd[0]) {
        return r;
    }

    if (std::strcmp(cmd, "list-instances") != 0 &&
        std::strcmp(cmd, "create-instance") != 0 &&
        std::strcmp(cmd, "verify-instance") != 0 &&
        std::strcmp(cmd, "export-instance") != 0 &&
        std::strcmp(cmd, "import-instance") != 0 &&
        std::strcmp(cmd, "launch") != 0 &&
        std::strcmp(cmd, "safe-mode") != 0 &&
        std::strcmp(cmd, "audit-last") != 0 &&
        std::strcmp(cmd, "diag-bundle") != 0) {
        return r;
    }

    r.handled = 1;
    state_root = compute_state_root(argc, argv);

    audit_reason_kv(audit_core, "operation", cmd);
    audit_reason_kv(audit_core, "state_root", state_root);

    if (std::strcmp(cmd, "list-instances") == 0) {
        std::vector<std::string> ids;
        bool ok = list_instances(state_root, ids);
        audit_reason_kv(audit_core, "instance_id", "*");
        audit_reason_kv(audit_core, "outcome", ok ? "ok" : "fail");
        out_kv(out, "result", ok ? "ok" : "fail");
        out_kv_u32(out, "instances.count", (u32)ids.size());
        if (ok) {
            size_t i;
            for (i = 0u; i < ids.size(); ++i) {
                out_kv(out, (std::string("instances[") + u32_to_string((u32)i) + "].id").c_str(), ids[i]);
            }
            r.exit_code = 0;
        } else {
            out_kv(out, "error", "list_instances_failed");
            r.exit_code = 1;
        }
        return r;
    }

    if (std::strcmp(cmd, "create-instance") == 0) {
        const char* templ = find_arg_value(argc, argv, "--template=");
        std::string template_id = (templ && templ[0]) ? std::string(templ) : std::string();
        std::string new_id;
        dom::launcher_core::LauncherInstanceManifest created;

        if (template_id.empty()) {
            audit_reason_kv(audit_core, "instance_id", "");
            audit_reason_kv(audit_core, "outcome", "fail");
            out_kv(out, "result", "fail");
            out_kv(out, "error", "missing_template");
            r.exit_code = 2;
            return r;
        }

        new_id = choose_new_instance_id(state_root, template_id);
        audit_reason_kv(audit_core, "instance_id", new_id);
        audit_reason_kv(audit_core, "template_id", template_id);

        if (!dom::launcher_core::launcher_instance_template_instance(services,
                                                                     template_id,
                                                                     new_id,
                                                                     state_root,
                                                                     created,
                                                                     (dom::launcher_core::LauncherAuditLog*)0)) {
            audit_reason_kv(audit_core, "outcome", "fail");
            out_kv(out, "result", "fail");
            out_kv(out, "error", "template_instance_failed");
            out_kv(out, "template_id", template_id);
            r.exit_code = 1;
            return r;
        }

        audit_reason_kv(audit_core, "outcome", "ok");
        out_kv(out, "result", "ok");
        out_kv(out, "template_id", template_id);
        out_kv(out, "instance_id", new_id);
        r.exit_code = 0;
        return r;
    }

    if (std::strcmp(cmd, "verify-instance") == 0) {
        std::string instance_id;
        std::string err_text;
        int i;

        for (i = cmd_i + 1; i < argc; ++i) {
            const char* a = argv[i];
            if (!a || !a[0]) continue;
            if (a[0] == '-') continue;
            instance_id = std::string(a);
            break;
        }

        audit_reason_kv(audit_core, "instance_id", instance_id);

        if (instance_id.empty()) {
            audit_reason_kv(audit_core, "outcome", "fail");
            out_kv(out, "result", "fail");
            out_kv(out, "error", "missing_instance_id");
            r.exit_code = 2;
            return r;
        }

        if (!dom::launcher_core::launcher_pack_prelaunch_validate_instance(services,
                                                                           instance_id,
                                                                           state_root,
                                                                           (dom::launcher_core::LauncherAuditLog*)0,
                                                                           &err_text)) {
            audit_reason_kv(audit_core, "outcome", "fail");
            out_kv(out, "result", "fail");
            out_kv(out, "instance_id", instance_id);
            out_kv(out, "error", "verify_failed");
            out_kv(out, "detail", err_text);
            r.exit_code = 1;
            return r;
        }

        audit_reason_kv(audit_core, "outcome", "ok");
        out_kv(out, "result", "ok");
        out_kv(out, "instance_id", instance_id);
        r.exit_code = 0;
        return r;
    }

    if (std::strcmp(cmd, "export-instance") == 0) {
        std::string instance_id;
        std::string mode;
        u32 export_mode = 0u;
        std::string export_root;
        int i;

        for (i = cmd_i + 1; i < argc; ++i) {
            const char* a = argv[i];
            if (!a || !a[0]) continue;
            if (a[0] == '-') continue;
            instance_id = std::string(a);
            break;
        }
        {
            const char* mv = find_arg_value(argc, argv, "--mode=");
            if (mv && mv[0]) mode = std::string(mv);
        }

        audit_reason_kv(audit_core, "instance_id", instance_id);
        audit_reason_kv(audit_core, "export_mode", mode);

        if (instance_id.empty() || mode.empty()) {
            audit_reason_kv(audit_core, "outcome", "fail");
            out_kv(out, "result", "fail");
            out_kv(out, "error", "missing_args");
            r.exit_code = 2;
            return r;
        }

        if (mode == "definition") {
            export_mode = (u32)dom::launcher_core::LAUNCHER_INSTANCE_EXPORT_DEFINITION_ONLY;
        } else if (mode == "bundle") {
            export_mode = (u32)dom::launcher_core::LAUNCHER_INSTANCE_EXPORT_FULL_BUNDLE;
        } else {
            audit_reason_kv(audit_core, "outcome", "fail");
            out_kv(out, "result", "fail");
            out_kv(out, "error", "bad_mode");
            out_kv(out, "mode", mode);
            r.exit_code = 2;
            return r;
        }

        export_root = path_join(path_join(state_root, "exports"), instance_id);
        if (!dom::launcher_core::launcher_instance_export_instance(services,
                                                                   instance_id,
                                                                   export_root,
                                                                   state_root,
                                                                   export_mode,
                                                                   (dom::launcher_core::LauncherAuditLog*)0)) {
            audit_reason_kv(audit_core, "outcome", "fail");
            out_kv(out, "result", "fail");
            out_kv(out, "error", "export_failed");
            out_kv(out, "instance_id", instance_id);
            out_kv(out, "export_root", export_root);
            r.exit_code = 1;
            return r;
        }

        audit_reason_kv(audit_core, "outcome", "ok");
        out_kv(out, "result", "ok");
        out_kv(out, "instance_id", instance_id);
        out_kv(out, "export_root", export_root);
        out_kv(out, "mode", mode);
        r.exit_code = 0;
        return r;
    }

    if (std::strcmp(cmd, "import-instance") == 0) {
        std::string import_root;
        std::vector<unsigned char> bytes;
        dom::launcher_core::LauncherInstanceManifest imported;
        std::string new_id;
        dom::launcher_core::LauncherInstanceManifest created;
        int i;

        for (i = cmd_i + 1; i < argc; ++i) {
            const char* a = argv[i];
            if (!a || !a[0]) continue;
            if (a[0] == '-') continue;
            import_root = std::string(a);
            break;
        }

        audit_reason_kv(audit_core, "instance_id", "");
        audit_reason_kv(audit_core, "import_root", import_root);

        if (import_root.empty()) {
            audit_reason_kv(audit_core, "outcome", "fail");
            out_kv(out, "result", "fail");
            out_kv(out, "error", "missing_import_root");
            r.exit_code = 2;
            return r;
        }

        if (!read_file_all(path_join(import_root, "manifest.tlv"), bytes) || bytes.empty()) {
            audit_reason_kv(audit_core, "outcome", "fail");
            out_kv(out, "result", "fail");
            out_kv(out, "error", "read_import_manifest_failed");
            r.exit_code = 1;
            return r;
        }
        if (!dom::launcher_core::launcher_instance_manifest_from_tlv_bytes(&bytes[0], bytes.size(), imported)) {
            audit_reason_kv(audit_core, "outcome", "fail");
            out_kv(out, "result", "fail");
            out_kv(out, "error", "decode_import_manifest_failed");
            r.exit_code = 1;
            return r;
        }

        new_id = choose_import_instance_id(state_root, imported.instance_id);
        audit_reason_kv(audit_core, "instance_id", new_id);
        audit_reason_kv(audit_core, "imported_instance_id", imported.instance_id);

        if (!dom::launcher_core::launcher_instance_import_instance(services,
                                                                   import_root,
                                                                   new_id,
                                                                   state_root,
                                                                   (u32)dom::launcher_core::LAUNCHER_INSTANCE_IMPORT_FULL_BUNDLE,
                                                                   0u,
                                                                   created,
                                                                   (dom::launcher_core::LauncherAuditLog*)0)) {
            audit_reason_kv(audit_core, "outcome", "fail");
            out_kv(out, "result", "fail");
            out_kv(out, "error", "import_failed");
            out_kv(out, "import_root", import_root);
            out_kv(out, "instance_id", new_id);
            r.exit_code = 1;
            return r;
        }

        audit_reason_kv(audit_core, "outcome", "ok");
        out_kv(out, "result", "ok");
        out_kv(out, "import_root", import_root);
        out_kv(out, "instance_id", new_id);
        r.exit_code = 0;
        return r;
    }

    if (std::strcmp(cmd, "launch") == 0 || std::strcmp(cmd, "safe-mode") == 0) {
        std::string instance_id;
        std::string target_text;
        std::string target_err;
        dom::LaunchTarget target;
        std::string exe_path;
        std::string exe_err;
        std::vector<std::string> child_args;
        dom::launcher_core::LauncherLaunchOverrides ov;
        dom::LaunchRunResult lr;
        u32 wait = 1u;
        u32 keep_last = 8u;
        int i;

        for (i = cmd_i + 1; i < argc; ++i) {
            const char* a = argv[i];
            if (!a || !a[0]) continue;
            if (a[0] == '-') continue;
            instance_id = std::string(a);
            break;
        }
        {
            const char* tv = find_arg_value(argc, argv, "--target=");
            if (tv && tv[0]) target_text = std::string(tv);
        }

        audit_reason_kv(audit_core, "instance_id", instance_id);
        audit_reason_kv(audit_core, "launch_target", target_text);

        if (instance_id.empty() || target_text.empty()) {
            audit_reason_kv(audit_core, "outcome", "fail");
            out_kv(out, "result", "fail");
            out_kv(out, "error", "missing_args");
            r.exit_code = 2;
            return r;
        }

        if (!launcher_parse_launch_target(target_text, target, target_err)) {
            audit_reason_kv(audit_core, "outcome", "fail");
            out_kv(out, "result", "fail");
            out_kv(out, "error", "bad_target");
            out_kv(out, "detail", target_err);
            r.exit_code = 2;
            return r;
        }

        if (target.is_tool != 0u) {
            const std::string argv0 = (argc > 0 && argv[0]) ? std::string(argv[0]) : std::string();
            if (!resolve_tool_executable_path(services, state_root, argv0, target.tool_id, exe_path, exe_err)) {
                audit_reason_kv(audit_core, "outcome", "fail");
                out_kv(out, "result", "fail");
                out_kv(out, "error", "tool_exec_resolve_failed");
                out_kv(out, "detail", exe_err);
                r.exit_code = 1;
                return r;
            }
        } else {
            const std::string argv0 = (argc > 0 && argv[0]) ? std::string(argv[0]) : std::string();
            if (!resolve_game_executable_path(argv0, exe_path)) {
                audit_reason_kv(audit_core, "outcome", "fail");
                out_kv(out, "result", "fail");
                out_kv(out, "error", "game_exec_not_found");
                r.exit_code = 1;
                return r;
            }
        }

        child_args.push_back(std::string("--instance=") + instance_id);

        ov = dom::launcher_core::LauncherLaunchOverrides();
        if (std::strcmp(cmd, "safe-mode") == 0) {
            ov.request_safe_mode = 1u;
            ov.safe_mode_allow_network = 0u;
        }

        (void)launcher_execute_launch_attempt(state_root,
                                              instance_id,
                                              target,
                                              profile,
                                              exe_path,
                                              child_args,
                                              wait,
                                              keep_last,
                                              ov,
                                              lr);

        audit_reason_kv(audit_core, "handshake_path", lr.handshake_path);
        audit_reason_kv(audit_core, "run_dir", lr.run_dir);
        audit_reason_kv(audit_core, "outcome", lr.ok ? "ok" : (lr.refused ? "refusal" : "fail"));

        out_kv(out, "result", lr.ok ? "ok" : "fail");
        out_kv(out, "instance_id", instance_id);
        out_kv(out, "launch_target", launcher_launch_target_to_string(target));
        out_kv(out, "run_id", std::string("0x") + u64_hex16(lr.run_id));
        out_kv(out, "run_dir", lr.run_dir);
        out_kv(out, "handshake_path", lr.handshake_path);
        out_kv(out, "audit_path", lr.audit_path);
        out_kv(out, "refused", lr.refused ? "1" : "0");
        if (lr.refused) {
            out_kv(out, "refusal_code", u32_to_string(lr.refusal_code));
            out_kv(out, "refusal_detail", lr.refusal_detail);
        }
        if (lr.spawned) {
            out_kv(out, "spawned", "1");
            out_kv(out, "waited", lr.waited ? "1" : "0");
            if (lr.waited) {
                out_kv(out, "child_exit_code", i32_to_string(lr.child_exit_code));
            }
        } else {
            out_kv(out, "spawned", "0");
        }

        if (lr.waited) {
            r.exit_code = (int)lr.child_exit_code;
        } else {
            r.exit_code = lr.ok ? 0 : 1;
        }
        return r;
    }

    if (std::strcmp(cmd, "audit-last") == 0) {
        std::string instance_id;
        std::vector<std::string> run_ids;
        std::string list_err;
        std::string last_run;
        std::string run_dir;
        std::string audit_path;
        std::vector<unsigned char> bytes;
        dom::launcher_core::LauncherAuditLog audit;
        int i;

        for (i = cmd_i + 1; i < argc; ++i) {
            const char* a = argv[i];
            if (!a || !a[0]) continue;
            if (a[0] == '-') continue;
            instance_id = std::string(a);
            break;
        }

        audit_reason_kv(audit_core, "instance_id", instance_id);

        if (instance_id.empty()) {
            audit_reason_kv(audit_core, "outcome", "fail");
            out_kv(out, "result", "fail");
            out_kv(out, "error", "missing_instance_id");
            r.exit_code = 2;
            return r;
        }

        if (!launcher_list_instance_runs(state_root, instance_id, run_ids, list_err) || run_ids.empty()) {
            audit_reason_kv(audit_core, "outcome", "fail");
            out_kv(out, "result", "fail");
            out_kv(out, "error", "no_runs");
            out_kv(out, "detail", list_err);
            r.exit_code = 1;
            return r;
        }

        last_run = run_ids[run_ids.size() - 1u];
        run_dir = path_join(path_join(path_join(path_join(state_root, "instances"), instance_id), "logs/runs"), last_run);
        audit_path = path_join(run_dir, "launcher_audit.tlv");

        if (!read_file_all(audit_path, bytes) || bytes.empty() ||
            !dom::launcher_core::launcher_audit_from_tlv_bytes(&bytes[0], bytes.size(), audit)) {
            audit_reason_kv(audit_core, "outcome", "fail");
            out_kv(out, "result", "fail");
            out_kv(out, "error", "read_audit_failed");
            out_kv(out, "audit_path", audit_path);
            r.exit_code = 1;
            return r;
        }

        audit_reason_kv(audit_core, "outcome", "ok");
        out_kv(out, "result", "ok");
        out_kv(out, "instance_id", instance_id);
        out_kv(out, "run_dir_id", last_run);
        out_kv(out, "audit_path", audit_path);
        out_kv(out, "audit.run_id", std::string("0x") + u64_hex16(audit.run_id));
        out_kv(out, "audit.exit_result", i32_to_string(audit.exit_result));
        out_kv_u32(out, "audit.reasons.count", (u32)audit.reasons.size());
        {
            size_t j;
            for (j = 0u; j < audit.reasons.size(); ++j) {
                out_kv(out, (std::string("audit.reasons[") + u32_to_string((u32)j) + "]").c_str(), audit.reasons[j]);
            }
        }
        r.exit_code = 0;
        return r;
    }

    if (std::strcmp(cmd, "diag-bundle") == 0) {
        std::string instance_id;
        std::string out_root;
        std::vector<std::string> run_ids;
        std::string list_err;
        std::string last_run;
        std::string src_run_dir;
        std::string dst_run_dir;
        int i;

        for (i = cmd_i + 1; i < argc; ++i) {
            const char* a = argv[i];
            if (!a || !a[0]) continue;
            if (a[0] == '-') continue;
            instance_id = std::string(a);
            break;
        }
        {
            const char* ov = find_arg_value(argc, argv, "--out=");
            if (ov && ov[0]) out_root = std::string(ov);
        }

        audit_reason_kv(audit_core, "instance_id", instance_id);
        audit_reason_kv(audit_core, "diag_out", out_root);

        if (instance_id.empty() || out_root.empty()) {
            audit_reason_kv(audit_core, "outcome", "fail");
            out_kv(out, "result", "fail");
            out_kv(out, "error", "missing_args");
            r.exit_code = 2;
            return r;
        }

        mkdir_p_best_effort(out_root);

        if (!dom::launcher_core::launcher_instance_export_instance(services,
                                                                   instance_id,
                                                                   out_root,
                                                                   state_root,
                                                                   (u32)dom::launcher_core::LAUNCHER_INSTANCE_EXPORT_FULL_BUNDLE,
                                                                   (dom::launcher_core::LauncherAuditLog*)0)) {
            audit_reason_kv(audit_core, "outcome", "fail");
            out_kv(out, "result", "fail");
            out_kv(out, "error", "export_failed");
            r.exit_code = 1;
            return r;
        }

        /* Copy last run audit+handshake when present. */
        if (launcher_list_instance_runs(state_root, instance_id, run_ids, list_err) && !run_ids.empty()) {
            last_run = run_ids[run_ids.size() - 1u];
            src_run_dir = path_join(path_join(path_join(path_join(state_root, "instances"), instance_id), "logs/runs"), last_run);
            dst_run_dir = path_join(path_join(out_root, "last_run"), last_run);
            mkdir_p_best_effort(dst_run_dir);
            (void)copy_file_best_effort(path_join(src_run_dir, "launcher_handshake.tlv"),
                                        path_join(dst_run_dir, "launcher_handshake.tlv"));
            (void)copy_file_best_effort(path_join(src_run_dir, "launcher_audit.tlv"),
                                        path_join(dst_run_dir, "launcher_audit.tlv"));
        }

        /* Copy launch history when present. */
        {
            const std::string src = path_join(path_join(path_join(path_join(state_root, "instances"), instance_id), "logs"), "launch_history.tlv");
            const std::string dst = path_join(out_root, "launch_history.tlv");
            if (file_exists(src)) {
                (void)copy_file_best_effort(src, dst);
            }
        }

        audit_reason_kv(audit_core, "outcome", "ok");
        out_kv(out, "result", "ok");
        out_kv(out, "instance_id", instance_id);
        out_kv(out, "out", out_root);
        if (!last_run.empty()) {
            out_kv(out, "last_run_id", last_run);
        }
        r.exit_code = 0;
        return r;
    }

    audit_reason_kv(audit_core, "outcome", "fail");
    out_kv(out, "result", "fail");
    out_kv(out, "error", "unhandled_command");
    r.exit_code = 3;
    return r;
}

} /* namespace dom */
