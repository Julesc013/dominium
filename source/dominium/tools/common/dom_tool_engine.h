#ifndef DOM_TOOL_ENGINE_H
#define DOM_TOOL_ENGINE_H

namespace dom {
namespace tools {

/* Initializes shared engine registries used by tools (schemas, content tables). */
void ensure_engine_content_initialized();

} // namespace tools
} // namespace dom

#endif /* DOM_TOOL_ENGINE_H */

