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

