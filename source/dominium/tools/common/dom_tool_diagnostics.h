/*
FILE: source/dominium/tools/common/dom_tool_diagnostics.h
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
#ifndef DOM_TOOL_DIAGNOSTICS_H
#define DOM_TOOL_DIAGNOSTICS_H

#include <string>
#include <vector>

namespace dom {
namespace tools {

enum DomToolSeverity {
    DOM_TOOL_WARNING = 0,
    DOM_TOOL_ERROR   = 1
};

struct DomToolMessage {
    DomToolSeverity severity;
    std::string text;
};

class DomToolDiagnostics {
public:
    void clear();
    void warn(const std::string &msg);
    void error(const std::string &msg);
    bool has_errors() const;
    const std::vector<DomToolMessage> &messages() const { return m_messages; }

private:
    std::vector<DomToolMessage> m_messages;
};

} // namespace tools
} // namespace dom

#endif /* DOM_TOOL_DIAGNOSTICS_H */

