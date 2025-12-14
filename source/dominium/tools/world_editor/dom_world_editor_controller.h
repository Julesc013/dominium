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

