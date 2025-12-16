/*
FILE: source/dominium/setup/dom_setup_ops.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/dom_setup_ops
RESPONSIBILITY: Defines internal contract for `dom_setup_ops`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SETUP_OPS_H
#define DOM_SETUP_OPS_H

#include <string>

#include "dom_paths.h"

namespace dom {

bool setup_install(const Paths &paths, const std::string &source);
bool setup_repair(const Paths &paths, const std::string &product);
bool setup_uninstall(const Paths &paths, const std::string &product);
bool setup_import(const Paths &paths, const std::string &source);
bool setup_gc(const Paths &paths);
bool setup_validate(const Paths &paths, const std::string &target);

} // namespace dom

#endif
