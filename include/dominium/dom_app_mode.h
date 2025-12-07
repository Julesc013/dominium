#ifndef DOMINIUM_DOM_APP_MODE_H
#define DOMINIUM_DOM_APP_MODE_H

#include "dom_plat_sys.h"
#include "dom_plat_term.h"
#include "dom_plat_ui.h"

#ifdef __cplusplus
extern "C" {
#endif

enum dom_ui_mode {
    DOM_UI_MODE_HEADLESS = 0,
    DOM_UI_MODE_TERMINAL,
    DOM_UI_MODE_NATIVE_UI,
    DOM_UI_MODE_RENDERED
};

enum dom_ui_mode dom_choose_ui_mode(int argc, char** argv,
                                    const struct dom_sys_vtable* sys,
                                    const struct dom_term_vtable* term,
                                    const struct dom_ui_vtable* ui,
                                    int rendered_allowed);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_DOM_APP_MODE_H */
