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

#include "core/include/launcher_pack_ops.h"
#include "core/include/launcher_safety.h"

#include "core/include/launcher_instance.h"
#include "core/include/launcher_instance_ops.h"

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

    /* launch/safe-mode/audit-last/diag-bundle are implemented in PART A plumbing step. */
    audit_reason_kv(audit_core, "outcome", "fail");
    out_kv(out, "result", "fail");
    out_kv(out, "error", "not_implemented_in_control_plane");
    r.exit_code = 3;
    return r;
}

} /* namespace dom */
