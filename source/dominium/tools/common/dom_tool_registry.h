#ifndef DOM_TOOL_REGISTRY_H
#define DOM_TOOL_REGISTRY_H

#include <stddef.h>

namespace dom {
namespace tools {

struct DomToolDesc {
    const char *id;          /* "world_editor", "tech_editor", ... */
    const char *name;        /* "World Editor" */
    const char *description; /* short human description */
    const char *exe_name;    /* executable base name (no extension), e.g. "dominium-world-editor" */
};

const DomToolDesc *tool_list(size_t *out_count);
const DomToolDesc *find_tool(const char *id);

} // namespace tools
} // namespace dom

#endif /* DOM_TOOL_REGISTRY_H */

