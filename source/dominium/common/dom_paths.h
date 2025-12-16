/*
FILE: source/dominium/common/dom_paths.h
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
#ifndef DOM_PATHS_H
#define DOM_PATHS_H

#include <string>

namespace dom {

struct Paths {
    std::string root;      /* DOMINIUM_HOME */
    std::string products;  /* root + "/repo/products" */
    std::string mods;      /* root + "/repo/mods" */
    std::string packs;     /* root + "/repo/packs" */
    std::string instances; /* root + "/instances" */
    std::string temp;      /* root + "/temp" */
};

bool resolve_paths(Paths &out, const std::string &home);
std::string join(const std::string &a, const std::string &b);
bool file_exists(const std::string &p);
bool dir_exists(const std::string &p);

} // namespace dom

#endif
