#ifndef DOM_TOOL_SESSION_H
#define DOM_TOOL_SESSION_H

#include <string>

extern "C" {
#include "ui/d_ui.h"
#include "world/d_world.h"
}

namespace dom {
namespace tools {

class DomContentRegistry;
class DomPackRegistry;

struct DomToolSession {
    std::string tool_id;                /* "world_editor", "tech_editor", etc */
    DomContentRegistry *content;        /* loaded content (items/materials/processes/...) */
    DomPackRegistry    *packs;          /* loaded packs/mods metadata (if any) */
    d_world            *preview_world;  /* optional preview world (static view) */
    dui_context        *ui;             /* DUI root context */

    DomToolSession()
        : tool_id(),
          content(0),
          packs(0),
          preview_world(0),
          ui(0) {}
};

} // namespace tools
} // namespace dom

#endif /* DOM_TOOL_SESSION_H */

