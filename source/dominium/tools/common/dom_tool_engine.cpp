#include "dom_tool_engine.h"

extern "C" {
#include "content/d_content.h"
}

namespace dom {
namespace tools {

void ensure_engine_content_initialized() {
    static bool s_init = false;
    if (s_init) {
        return;
    }
    d_content_register_schemas();
    d_content_init();
    s_init = true;
}

} // namespace tools
} // namespace dom

