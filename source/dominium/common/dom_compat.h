/*
FILE: source/dominium/common/dom_compat.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / common/dom_compat
RESPONSIBILITY: Implements `dom_compat`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_COMPAT_H
#define DOM_COMPAT_H

#include <string>
#include "dom_instance.h"

namespace dom {

enum CompatResult {
    COMPAT_OK = 0,
    COMPAT_LIMITED,
    COMPAT_READONLY,
    COMPAT_INCOMPATIBLE,
    COMPAT_MOD_UNSAFE,
    COMPAT_SCHEMA_MISMATCH
};

struct ProductInfo {
    std::string product;       /* "game", "launcher", "setup", "tool" */
    std::string role_detail;   /* "client", "server", "headless", etc. */

    unsigned product_version;
    unsigned core_version;
    unsigned suite_version;
};

CompatResult evaluate_compat(
    const ProductInfo &prod,
    const InstanceInfo &inst
);

} // namespace dom

#endif
