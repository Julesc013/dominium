/*
FILE: source/dominium/tools/common/dom_tool_registry.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/common/dom_tool_registry
RESPONSIBILITY: Defines internal contract for `dom_tool_registry`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_TOOL_REGISTRY_H
#define DOM_TOOL_REGISTRY_H

#include <stddef.h>

namespace dom {
namespace tools {

struct DomToolDesc {
    const char *id;          /* "world_editor", "tech_editor", ... */
    const char *name;        /* "World Editor" */
    const char *description; /* short human description */
    const char *exe_name;    /* executable base name (no extension), e.g. "dominium-world-editor" */
};

const DomToolDesc *tool_list(size_t *out_count);
const DomToolDesc *find_tool(const char *id);

} // namespace tools
} // namespace dom

#endif /* DOM_TOOL_REGISTRY_H */

