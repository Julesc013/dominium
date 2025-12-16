/*
FILE: source/dominium/common/dom_compat.cpp
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
#include "dom_compat.h"

namespace dom {

CompatResult evaluate_compat(
    const ProductInfo &prod,
    const InstanceInfo &inst
) {
    if (prod.core_version < inst.core_version) {
        return COMPAT_SCHEMA_MISMATCH;
    }
    if (prod.suite_version < inst.suite_version) {
        return COMPAT_READONLY;
    }
    if (prod.suite_version > inst.suite_version) {
        /* Assume limited forward compatibility until declared otherwise. */
        return COMPAT_LIMITED;
    }

    /* TODO: evaluate declared compat profile once instances start exposing it. */
    (void)prod.product;
    (void)prod.role_detail;
    (void)prod.product_version;

    return COMPAT_OK;
}

} // namespace dom
