#ifndef DOM_REPLAY_VIEWER_CONTROLLER_H
#define DOM_REPLAY_VIEWER_CONTROLLER_H

#include "dominium/tools/common/dom_tool_app.h"

#include <string>
#include <vector>

extern "C" {
#include "replay/d_replay.h"
}

namespace dom {
namespace tools {

class DomReplayViewerController : public DomToolController {
public:
    DomReplayViewerController();
    virtual ~DomReplayViewerController();

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
    d_replay_context m_ctx;
    bool m_loaded;
    u32 m_last_tick;
};

} // namespace tools
} // namespace dom

#endif /* DOM_REPLAY_VIEWER_CONTROLLER_H */

