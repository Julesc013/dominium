/*
FILE: source/dominium/tools/world_editor/dom_world_editor_controller.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/world_editor/dom_world_editor_controller
RESPONSIBILITY: Implements `dom_world_editor_controller`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_WORLD_EDITOR_CONTROLLER_H
#define DOM_WORLD_EDITOR_CONTROLLER_H

#include "dominium/tools/common/dom_tool_app.h"

#include <string>

extern "C" {
#include "world/d_world.h"
}

namespace dom {
namespace tools {

class DomWorldEditorController : public DomToolController {
public:
    DomWorldEditorController();
    virtual ~DomWorldEditorController();

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
    d_world *m_world;
    unsigned m_checksum;
};

} // namespace tools
} // namespace dom

#endif /* DOM_WORLD_EDITOR_CONTROLLER_H */

