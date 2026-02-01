/*
FILE: source/dominium/tools/demo_gen/main_tools_demo_gen.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/demo_gen/main_tools_demo_gen
RESPONSIBILITY: Implements `main_tools_demo_gen`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/architecture/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <cstdio>
#include <cstring>
#include <string>

extern "C" {
#include "domino/sim/sim.h"
}

static int starts_with(const char *s, const char *prefix) {
    if (!s || !prefix) {
        return 0;
    }
    const size_t n = std::strlen(prefix);
    return std::strncmp(s, prefix, n) == 0;
}

static std::string join_slash(const std::string &a, const std::string &b) {
    if (a.empty()) return b;
    if (b.empty()) return a;
    std::string out = a;
    if (out[out.size() - 1u] != '/' && out[out.size() - 1u] != '\\') {
        out.push_back('/');
    }
    out.append(b);
    return out;
}

static void usage(void) {
    std::printf("Usage: dominium-tools-demo-gen [--home=<path>] [--out=<path>]\n");
    std::printf("  Default --out is data/tools_demo/world_demo.dwrl\n");
}

int main(int argc, char **argv) {
    std::string home = ".";
    std::string out_rel = "data/tools_demo/world_demo.dwrl";
    int i;

    for (i = 1; i < argc; ++i) {
        const char *a = argv[i] ? argv[i] : "";
        if (starts_with(a, "--home=")) {
            home = a + std::strlen("--home=");
        } else if (std::strcmp(a, "--home") == 0 && i + 1 < argc) {
            home = argv[++i] ? argv[i] : "";
        } else if (starts_with(a, "--out=")) {
            out_rel = a + std::strlen("--out=");
        } else if (std::strcmp(a, "--out") == 0 && i + 1 < argc) {
            out_rel = argv[++i] ? argv[i] : "";
        } else if (std::strcmp(a, "--help") == 0 || std::strcmp(a, "-h") == 0) {
            usage();
            return 0;
        } else {
            usage();
            return 1;
        }
    }

    if (home.empty()) {
        home = ".";
    }
    if (out_rel.empty()) {
        out_rel = "data/tools_demo/world_demo.dwrl";
    }

    const std::string out_path = join_slash(home, out_rel);

    d_world_config cfg;
    cfg.seed = 12345u;
    cfg.width = 64u;
    cfg.height = 64u;

    d_world *w = d_world_create_from_config(&cfg);
    if (!w) {
        std::printf("demo-gen: d_world_create_from_config failed\n");
        return 1;
    }

    if (!d_world_save_tlv(w, out_path.c_str())) {
        std::printf("demo-gen: d_world_save_tlv failed (%s)\n", out_path.c_str());
        d_world_destroy(w);
        return 1;
    }

    d_world_destroy(w);
    std::printf("demo-gen: wrote %s\n", out_path.c_str());
    return 0;
}

