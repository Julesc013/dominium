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

