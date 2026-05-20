/*
FILE: source/dominium/tools/validators/modcheck/dom_modcheck.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/validators/modcheck/dom_modcheck
RESPONSIBILITY: Defines internal contract for `dom_modcheck`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C17/C++17 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/architecture/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/reference/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/reference/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_MODCHECK_H
#define DOM_MODCHECK_H

#include <string>

namespace dom {

bool modcheck_run(const std::string &path);

} // namespace dom

#endif
