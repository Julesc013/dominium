/*
FILE: source/dominium/tools/common/dom_tool_diagnostics.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/common/dom_tool_diagnostics
RESPONSIBILITY: Implements `dom_tool_diagnostics`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_tool_diagnostics.h"

namespace dom {
namespace tools {

void DomToolDiagnostics::clear() {
    m_messages.clear();
}

void DomToolDiagnostics::warn(const std::string &msg) {
    DomToolMessage m;
    m.severity = DOM_TOOL_WARNING;
    m.text = msg;
    m_messages.push_back(m);
}

void DomToolDiagnostics::error(const std::string &msg) {
    DomToolMessage m;
    m.severity = DOM_TOOL_ERROR;
    m.text = msg;
    m_messages.push_back(m);
}

bool DomToolDiagnostics::has_errors() const {
    size_t i;
    for (i = 0u; i < m_messages.size(); ++i) {
        if (m_messages[i].severity == DOM_TOOL_ERROR) {
            return true;
        }
    }
    return false;
}

} // namespace tools
} // namespace dom

