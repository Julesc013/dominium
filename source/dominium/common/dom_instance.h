/*
FILE: source/dominium/common/dom_instance.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / common/dom_instance
RESPONSIBILITY: Defines internal contract for `dom_instance`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_INSTANCE_H
#define DOM_INSTANCE_H

#include <string>
#include <vector>
#include "dom_paths.h"

namespace dom {

struct PackRef {
    std::string id;
    unsigned    version;
};

struct ModRef {
    std::string id;
    unsigned    version;
};

struct InstanceInfo {
    std::string id;

    unsigned world_seed;
    unsigned world_size_m;

    int vertical_min_m;
    int vertical_max_m;

    unsigned suite_version;
    unsigned core_version;

    std::vector<PackRef> packs;
    std::vector<ModRef>  mods;

    std::string last_product;          /* "game", "launcher", etc. */
    std::string last_product_version;  /* e.g. "0.1.0" */

    /* Serialization helpers */
    bool load(const Paths &paths);
    bool save(const Paths &paths) const;
};

} // namespace dom

#endif
