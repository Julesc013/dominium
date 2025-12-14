#ifndef DOM_LAUNCHER_UI_H
#define DOM_LAUNCHER_UI_H

#include "ui/d_ui.h"
#include "dom_launcher_app.h"

namespace dom {

void dom_launcher_ui_build_root(dui_context &ctx, DomLauncherApp &app);
void dom_launcher_ui_update(dui_context &ctx, DomLauncherApp &app);
int  dom_launcher_ui_try_click(dui_context &ctx, int x, int y);

} // namespace dom

#endif
