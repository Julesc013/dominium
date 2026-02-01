/*
FILE: source/dominium/tools/net_inspector/dom_net_inspector_controller.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/net_inspector/dom_net_inspector_controller
RESPONSIBILITY: Implements `dom_net_inspector_controller`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/architecture/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_net_inspector_controller.h"

#include <cstdio>

#include "dominium/tools/common/dom_tool_io.h"

namespace dom {
namespace tools {

DomNetInspectorController::DomNetInspectorController()
    : m_bytes(0u),
      m_lines(0u) {}

const char *DomNetInspectorController::tool_id() const { return "net_inspector"; }
const char *DomNetInspectorController::tool_name() const { return "Net Inspector"; }
const char *DomNetInspectorController::tool_description() const { return "Inspect network packet logs (stub)."; }

bool DomNetInspectorController::supports_demo() const { return false; }
std::string DomNetInspectorController::demo_path(const std::string &home) const { (void)home; return std::string(); }

bool DomNetInspectorController::load(const std::string &path, std::string &status) {
    std::vector<unsigned char> data;
    std::string err;
    size_t i;

    m_bytes = 0u;
    m_lines = 0u;

    if (!read_file(path, data, &err)) {
        status = err.empty() ? "Failed to read file." : err;
        return false;
    }

    m_bytes = data.size();
    for (i = 0u; i < data.size(); ++i) {
        if (data[i] == '\n') {
            m_lines += 1u;
        }
    }

    status = "Loaded.";
    return true;
}

bool DomNetInspectorController::validate(std::string &status) {
    status = "OK (no validators yet).";
    return true;
}

bool DomNetInspectorController::save(const std::string &path, std::string &status) {
    (void)path;
    status = "Read-only tool.";
    return false;
}

void DomNetInspectorController::summary(std::string &out) const {
    char buf[128];
    std::sprintf(buf, "bytes=%u lines=%u", (unsigned)m_bytes, (unsigned)m_lines);
    out = buf;
}

} // namespace tools
} // namespace dom

