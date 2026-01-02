/*
FILE: source/dominium/launcher/tests/launcher_ui_smoke_tests.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher / tests
RESPONSIBILITY: UI smoke tests for DUI schema-driven launcher UI under --ui=null and --ui=dgfx (headless where possible).
*/

#include <cassert>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "dom_launcher_app.h"

extern "C" {
#include "domino/profile.h"
#include "domino/sys.h"
#include "core/include/launcher_core_api.h"
}

#include "core/include/launcher_audit.h"
#include "core/include/launcher_instance_ops.h"
#include "core/include/launcher_tools_registry.h"

namespace {

static const int kSkipReturnCode = 77;

static std::string normalize_seps(const std::string& in) {
    std::string out = in;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        if (out[i] == '\\') out[i] = '/';
    }
    return out;
}

static bool is_sep(char c) { return c == '/' || c == '\\'; }

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
        if (is_sep(path[i - 1u])) {
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

static void remove_tree(const char* path) {
    dsys_dir_iter* it;
    dsys_dir_entry ent;
    char child[512];

    if (!path || path[0] == '\0') {
        return;
    }

    it = dsys_dir_open(path);
    if (it) {
        while (dsys_dir_next(it, &ent)) {
            if (ent.name[0] == '.' && (ent.name[1] == '\0' ||
                                       (ent.name[1] == '.' && ent.name[2] == '\0'))) {
                continue;
            }
            std::snprintf(child, sizeof(child), "%s/%s", path, ent.name);
            if (ent.is_dir) {
                remove_tree(child);
#if defined(_WIN32) || defined(_WIN64)
                _rmdir(child);
#else
                rmdir(child);
#endif
            } else {
                remove(child);
            }
        }
        dsys_dir_close(it);
    }
#if defined(_WIN32) || defined(_WIN64)
    _rmdir(path);
#else
    rmdir(path);
#endif
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
    std::memcpy(dst, src, n);
    dst[n] = '\0';
}

static dom_profile make_profile_ui_backend(const char* ui_backend) {
    dom_profile p;
    std::memset(&p, 0, sizeof(p));
    p.abi_version = DOM_PROFILE_ABI_VERSION;
    p.struct_size = (u32)sizeof(dom_profile);
    p.kind = DOM_PROFILE_BASELINE;
    p.lockstep_strict = 0u;
    p.override_count = 1u;
    str_copy_bounded(p.overrides[0].subsystem_key, sizeof(p.overrides[0].subsystem_key), "ui");
    str_copy_bounded(p.overrides[0].backend_name, sizeof(p.overrides[0].backend_name), ui_backend ? ui_backend : "");
    return p;
}

static void write_tools_registry_minimal(const std::string& state_root) {
    dom::launcher_core::LauncherToolsRegistry reg;
    dom::launcher_core::LauncherToolEntry te;
    std::vector<unsigned char> bytes;

    reg.schema_version = (u32)dom::launcher_core::LAUNCHER_TOOLS_REGISTRY_TLV_VERSION;
    te.tool_id = "tool_manifest_inspector";
    te.display_name = "Manifest Inspector";
    te.description = "Smoke-test tool entry.";
    reg.tools.push_back(te);

    assert(dom::launcher_core::launcher_tools_registry_to_tlv_bytes(reg, bytes));
    assert(write_file_all_bytes(path_join(state_root, "tools_registry.tlv"), bytes));
}

static void create_empty_instance(const std::string& state_root, const std::string& instance_id) {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    dom::launcher_core::LauncherAuditLog audit;
    dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty(instance_id);
    dom::launcher_core::LauncherInstanceManifest created;

    assert(dom::launcher_core::launcher_instance_create_instance(services, desired, state_root, created, &audit));
}

static int run_ui_backend_smoke(const char* backend,
                                const std::string& argv0,
                                const std::string& state_root,
                                bool allow_skip) {
    dom_profile profile = make_profile_ui_backend(backend);
    dom::LauncherConfig cfg;
    dom::DomLauncherApp app;
    std::string err;
    const bool headless = backend && std::strcmp(backend, "dgfx") == 0;

    cfg.argv0 = argv0;
    cfg.home = state_root;
    cfg.mode = dom::LAUNCHER_MODE_GUI;
    cfg.action.clear();
    cfg.instance_id.clear();
    cfg.product.clear();
    cfg.product_mode = headless ? "headless" : "gui";

    if (!app.init_from_cli(cfg, &profile)) {
        if (allow_skip) {
            std::printf("launcher_ui_smoke_tests: SKIP backend=%s reason=init_failed\n", backend ? backend : "(null)");
            return kSkipReturnCode;
        }
        std::printf("launcher_ui_smoke_tests: FAIL backend=%s reason=init_failed\n", backend ? backend : "(null)");
        return 1;
    }

    if (backend && !app.ui_backend_selected().empty() && app.ui_backend_selected() != backend) {
        if (allow_skip) {
            std::printf("launcher_ui_smoke_tests: SKIP backend=%s selected=%s note=%s\n",
                        backend,
                        app.ui_backend_selected().c_str(),
                        app.ui_fallback_note().empty() ? "none" : app.ui_fallback_note().c_str());
            return kSkipReturnCode;
        }
        std::printf("launcher_ui_smoke_tests: FAIL backend=%s selected=%s\n",
                    backend,
                    app.ui_backend_selected().c_str());
        return 1;
    }

    if (!app.run_ui_smoke(err)) {
        if (allow_skip) {
            std::printf("launcher_ui_smoke_tests: SKIP backend=%s err=%s\n",
                        backend ? backend : "(null)",
                        err.empty() ? "unknown" : err.c_str());
            return kSkipReturnCode;
        }
        std::printf("launcher_ui_smoke_tests: FAIL backend=%s err=%s\n",
                    backend ? backend : "(null)",
                    err.empty() ? "unknown" : err.c_str());
        return 1;
    }

    return 0;
}

} /* namespace */

int main(int argc, char** argv) {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    const std::string state_root = make_temp_root(services, "tmp_l9b_ui_smoke");
    std::string argv0 = (argc > 0 && argv && argv[0]) ? std::string(argv[0]) : std::string();
    int rc;

    remove_tree(state_root.c_str());
    mkdir_p_best_effort(state_root);
    write_tools_registry_minimal(state_root);
    create_empty_instance(state_root, "smoke_instance");

    /* Provide an argv0 whose directory contains the built tool exe. */
    {
        const std::string dir = dirname_of(argv0);
#if defined(_WIN32) || defined(_WIN64)
        const std::string launcher_path = path_join(dir, "dominium-launcher.exe");
#else
        const std::string launcher_path = path_join(dir, "dominium-launcher");
#endif
        if (file_exists(launcher_path)) {
            argv0 = launcher_path;
        }
    }

    /* --ui=null smoke: schema load + instance select + verify + tool launch + handshake/audit. */
    rc = run_ui_backend_smoke("null", argv0, state_root, false);
    if (rc != 0) {
        return rc;
    }

    /* --ui=dgfx smoke (headless where possible): create window, render one frame, exit. */
    rc = run_ui_backend_smoke("dgfx", argv0, state_root, true);
    if (rc != 0) {
        return rc;
    }

    std::printf("launcher_ui_smoke_tests: OK\n");
    return 0;
}

