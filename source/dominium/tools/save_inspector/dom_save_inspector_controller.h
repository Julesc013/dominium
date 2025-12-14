#ifndef DOM_SAVE_INSPECTOR_CONTROLLER_H
#define DOM_SAVE_INSPECTOR_CONTROLLER_H

#include "dominium/tools/common/dom_tool_app.h"

#include <string>
#include <vector>

extern "C" {
#include "world/d_world.h"
}

namespace dom {
namespace tools {

class DomSaveInspectorController : public DomToolController {
public:
    DomSaveInspectorController();
    virtual ~DomSaveInspectorController();

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
    bool load_game_save_blob(const std::vector<unsigned char> &data, std::string &status);

private:
    d_world *m_world;
    unsigned long long m_hash;
    std::string m_format;
};

} // namespace tools
} // namespace dom

#endif /* DOM_SAVE_INSPECTOR_CONTROLLER_H */

