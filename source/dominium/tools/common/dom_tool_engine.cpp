/*
FILE: source/dominium/tools/common/dom_tool_engine.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/common/dom_tool_engine
RESPONSIBILITY: Implements `dom_tool_engine`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_tool_engine.h"

extern "C" {
#include "content/d_content.h"
}

namespace dom {
namespace tools {

void ensure_engine_content_initialized() {
    static bool s_init = false;
    if (s_init) {
        return;
    }
    d_content_register_schemas();
    d_content_init();
    s_init = true;
}

} // namespace tools
} // namespace dom

