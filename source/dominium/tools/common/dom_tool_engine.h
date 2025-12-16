/*
FILE: source/dominium/tools/common/dom_tool_engine.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/common/dom_tool_engine
RESPONSIBILITY: Defines internal contract for `dom_tool_engine`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_TOOL_ENGINE_H
#define DOM_TOOL_ENGINE_H

namespace dom {
namespace tools {

/* Initializes shared engine registries used by tools (schemas, content tables). */
void ensure_engine_content_initialized();

} // namespace tools
} // namespace dom

#endif /* DOM_TOOL_ENGINE_H */

