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

