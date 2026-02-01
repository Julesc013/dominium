/*
FILE: source/dominium/tools/net_inspector/dom_net_inspector_controller.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/net_inspector/dom_net_inspector_controller
RESPONSIBILITY: Defines internal contract for `dom_net_inspector_controller`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/architecture/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_NET_INSPECTOR_CONTROLLER_H
#define DOM_NET_INSPECTOR_CONTROLLER_H

#include "dominium/tools/common/dom_tool_app.h"

#include <string>
#include <vector>

namespace dom {
namespace tools {

class DomNetInspectorController : public DomToolController {
public:
    DomNetInspectorController();

    virtual const char *tool_id() const;
    virtual const char *tool_name() const;
    virtual const char *tool_description() const;

    virtual bool supports_demo() const;
    virtual std::string demo_path(const std::string &home) const;

    virtual bool load(const std::string &path, std::string &status);
    virtual bool validate(std::string &status);
    virtual bool save(const std::string &path, std::string &status);
    virtual void summary(std::string &out) const;

private:
    size_t m_bytes;
    size_t m_lines;
};

} // namespace tools
} // namespace dom

#endif /* DOM_NET_INSPECTOR_CONTROLLER_H */

