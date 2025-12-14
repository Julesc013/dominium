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

