/*
FILE: source/dominium/launcher/tests/launcher_tui_smoke_tests.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher / tests
RESPONSIBILITY: TUI smoke tests for the dominium launcher under non-interactive smoke mode.
*/

#include <cassert>
#include <cstdio>
#include <cstring>
#include <string>

#include "launcher_tui.h"

extern "C" {
#include "core/include/launcher_core_api.h"
}

#include "core/include/launcher_audit.h"
#include "core/include/launcher_instance_ops.h"

namespace {

static bool is_sep(char c) { return c == '/' || c == '\\'; }

static std::string normalize_seps(const std::string& in) {
    std::string out = in;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        if (out[i] == '\\') out[i] = '/';
    }
    return out;
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

static void create_empty_instance(const std::string& state_root, const std::string& instance_id) {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    dom::launcher_core::LauncherAuditLog audit;
    dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty(instance_id);
    dom::launcher_core::LauncherInstanceManifest created;

    assert(dom::launcher_core::launcher_instance_create_instance(services, desired, state_root, created, &audit));
}

} /* namespace */

int main(int argc, char** argv) {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    const std::string state_root = make_temp_root(services, "tmp_l9b_tui_smoke");
    const std::string argv0 = (argc > 0 && argv && argv[0]) ? std::string(argv[0]) : std::string();

    mkdir_p_best_effort(state_root);
    create_empty_instance(state_root, "smoke_instance");

    assert(dom::launcher_run_tui(argv0, state_root, 0, 0, 1) == 0);

    std::printf("launcher_tui_smoke_tests: OK\n");
    return 0;
}
