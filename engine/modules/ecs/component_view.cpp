/*
FILE: engine/modules/ecs/component_view.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino / ecs
RESPONSIBILITY: ComponentView helpers.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside ecs.
DETERMINISM: Stable view properties only.
*/
#include "domino/ecs/ecs_component_view.h"

dom_component_view dom_component_view_invalid(void)
{
    dom_component_view view;
    view.component_id = 0u;
    view.field_id = 0u;
    view.element_type = 0u;
    view.element_size = 0u;
    view.stride = 0u;
    view.count = 0u;
    view.access_mode = 0u;
    view.view_flags = DOM_ECS_VIEW_DENIED;
    view.reserved = 0u;
    view.backend_token = 0u;
    return view;
}

d_bool dom_component_view_is_valid(const dom_component_view* view)
{
    if (!view) {
        return D_FALSE;
    }
    return (view->view_flags & DOM_ECS_VIEW_VALID) ? D_TRUE : D_FALSE;
}

d_bool dom_component_view_has_index(const dom_component_view* view, u32 index)
{
    if (!dom_component_view_is_valid(view)) {
        return D_FALSE;
    }
    return (index < view->count) ? D_TRUE : D_FALSE;
}
