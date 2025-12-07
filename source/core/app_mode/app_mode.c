#include "dominium/dom_app_mode.h"

#include <string.h>

static enum dom_ui_mode parse_flag(const char* s, int rendered_allowed, enum dom_ui_mode fallback)
{
    if (!s) return fallback;
    if (strcmp(s, "--mode=headless") == 0) return DOM_UI_MODE_HEADLESS;
    if (strcmp(s, "--mode=terminal") == 0) return DOM_UI_MODE_TERMINAL;
    if (strcmp(s, "--mode=native") == 0) return DOM_UI_MODE_NATIVE_UI;
    if (rendered_allowed && strcmp(s, "--mode=rendered") == 0) return DOM_UI_MODE_RENDERED;
    return fallback;
}

enum dom_ui_mode dom_choose_ui_mode(int argc, char** argv,
                                    const struct dom_sys_vtable* sys,
                                    const struct dom_term_vtable* term,
                                    const struct dom_ui_vtable* ui,
                                    int rendered_allowed)
{
    enum dom_ui_mode mode = DOM_UI_MODE_HEADLESS;
    int i;
    for (i = 1; i < argc; ++i) {
        enum dom_ui_mode parsed = parse_flag(argv[i], rendered_allowed, mode);
        if (parsed != mode) {
            mode = parsed;
        }
    }

    /* Probe availability if not forced to rendered explicitly. */
    if (mode == DOM_UI_MODE_NATIVE_UI) {
        if (!ui) mode = DOM_UI_MODE_HEADLESS;
    } else if (mode == DOM_UI_MODE_TERMINAL) {
        if (!term) mode = DOM_UI_MODE_HEADLESS;
    } else if (mode == DOM_UI_MODE_HEADLESS) {
        if (ui) mode = DOM_UI_MODE_NATIVE_UI;
        else if (term) mode = DOM_UI_MODE_TERMINAL;
    } else if (mode == DOM_UI_MODE_RENDERED) {
        if (!rendered_allowed) mode = DOM_UI_MODE_HEADLESS;
    }

    (void)sys;
    return mode;
}
