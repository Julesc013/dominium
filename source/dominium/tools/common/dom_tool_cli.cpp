/*
FILE: source/dominium/tools/common/dom_tool_cli.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/common/dom_tool_cli
RESPONSIBILITY: Implements `dom_tool_cli`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_tool_cli.h"

#include <cstring>

namespace dom {
namespace tools {
namespace {

static int starts_with(const char *s, const char *prefix) {
    if (!s || !prefix) {
        return 0;
    }
    const size_t n = std::strlen(prefix);
    return std::strncmp(s, prefix, n) == 0;
}

static const char *after_prefix(const char *s, const char *prefix) {
    if (!s || !prefix) {
        return (const char *)0;
    }
    const size_t n = std::strlen(prefix);
    return s + n;
}

} // namespace

bool parse_tool_cli(int argc, char **argv, DomToolCliConfig &out, std::string &err) {
    int i;
    (void)err;
    for (i = 1; i < argc; ++i) {
        const char *a = argv[i] ? argv[i] : "";
        if (std::strcmp(a, "--demo") == 0) {
            out.demo = true;
        } else if (starts_with(a, "--home=")) {
            out.home = after_prefix(a, "--home=");
        } else if ((std::strcmp(a, "--home") == 0) && i + 1 < argc) {
            out.home = argv[++i] ? argv[i] : "";
        } else if (starts_with(a, "--load=")) {
            out.load = after_prefix(a, "--load=");
        } else if ((std::strcmp(a, "--load") == 0) && i + 1 < argc) {
            out.load = argv[++i] ? argv[i] : "";
        } else if (starts_with(a, "--sys=")) {
            out.sys_backend = after_prefix(a, "--sys=");
        } else if ((std::strcmp(a, "--sys") == 0) && i + 1 < argc) {
            out.sys_backend = argv[++i] ? argv[i] : "";
        } else if (starts_with(a, "--gfx=")) {
            out.gfx_backend = after_prefix(a, "--gfx=");
        } else if ((std::strcmp(a, "--gfx") == 0) && i + 1 < argc) {
            out.gfx_backend = argv[++i] ? argv[i] : "";
        } else if (starts_with(a, "--tool=")) {
            /* Multiplexer compatibility; ignored by per-tool binaries. */
            continue;
        } else if (std::strcmp(a, "--tool") == 0 && i + 1 < argc) {
            ++i;
            continue;
        } else if (std::strcmp(a, "--help") == 0 || std::strcmp(a, "-h") == 0) {
            /* Let caller print usage. */
            err = "help";
            return false;
        } else {
            /* Unknown flag: ignore for forward compatibility. */
        }
    }
    return true;
}

} // namespace tools
} // namespace dom

