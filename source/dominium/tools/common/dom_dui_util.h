#ifndef DOM_DUI_UTIL_H
#define DOM_DUI_UTIL_H

extern "C" {
#include "ui/d_ui.h"
}

namespace dom {
namespace tools {

void dui_clear_children(dui_context &ctx, dui_widget *parent);

dui_widget *dui_add_child_end(dui_context &ctx,
                              dui_widget *parent,
                              dui_widget_kind kind);

int dui_try_click(dui_context &ctx, int x, int y);

} // namespace tools
} // namespace dom

#endif /* DOM_DUI_UTIL_H */

