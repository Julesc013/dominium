/*
FILE: source/dominium/common/dom_paths.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / common/dom_paths
RESPONSIBILITY: Implements `dom_paths`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_paths.h"

#include <cstdio>
#include <cstring>

extern "C" {
#include "domino/sys.h"
}

namespace dom {

static std::string trim_trailing_slashes(const std::string &path) {
    std::string out = path;
    while (!out.empty()) {
        char c = out[out.size() - 1u];
        if (c == '/' || c == '\\') {
            out.resize(out.size() - 1u);
        } else {
            break;
        }
    }
    return out;
}

static std::string trim_leading_slashes(const std::string &path) {
    size_t start = 0u;
    while (start < path.size()) {
        char c = path[start];
        if (c == '/' || c == '\\') {
            ++start;
        } else {
            break;
        }
    }
    return path.substr(start);
}

std::string join(const std::string &a, const std::string &b) {
    if (a.empty()) {
        return b;
    }
    if (b.empty()) {
        return a;
    }

    std::string left = trim_trailing_slashes(a);
    std::string right = trim_leading_slashes(b);

    std::string out;
    out.reserve(left.size() + 1u + right.size());
    out.append(left);
    out.push_back('/');
    out.append(right);
    return out;
}

bool resolve_paths(Paths &out, const std::string &home) {
    if (home.empty()) {
        return false;
    }
    out.root = home;
    out.products = join(home, "repo/products");
    out.mods = join(home, "repo/mods");
    out.packs = join(home, "repo/packs");
    out.instances = join(home, "instances");
    out.temp = join(home, "temp");
    return true;
}

bool file_exists(const std::string &p) {
    if (p.empty()) {
        return false;
    }
    void *fh = dsys_file_open(p.c_str(), "rb");
    if (!fh) {
        /* TODO: replace with dedicated dsys file-exists helper when available. */
        return false;
    }
    dsys_file_close(fh);
    return true;
}

bool dir_exists(const std::string &p) {
    if (p.empty()) {
        return false;
    }
    dsys_dir_iter *it = dsys_dir_open(p.c_str());
    if (!it) {
        /* TODO: replace with dedicated dsys dir-exists helper when available. */
        return false;
    }
    dsys_dir_close(it);
    return true;
}

} // namespace dom
