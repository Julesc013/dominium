/* TODO: legacy CLI entrypoint; not yet wired into dominium_setup target. */
#include "dominium/dom_app_mode.h"
#include "dominium/dom_plat_sys.h"
#include "dominium/dom_plat_term.h"
#include "dominium/dom_plat_ui.h"
#include "dominium/dom_version.h"
#include "dominium/dom_core.h"

int main(int argc, char** argv)
{
    const struct dom_sys_vtable* sys = dom_plat_sys_choose_best();
    const struct dom_term_vtable* term = dom_plat_term_probe(sys);
    const struct dom_ui_vtable* ui = dom_plat_ui_probe(sys);
    enum dom_ui_mode mode = dom_choose_ui_mode(argc, argv, sys, term, ui, 0);
    (void)sys; (void)term; (void)ui;
    dom_log(DOM_LOG_INFO, "setup", "Dominium setup stub");
    dom_log(DOM_LOG_INFO, "setup", (mode == DOM_UI_MODE_HEADLESS) ? "mode=headless" :
                                 (mode == DOM_UI_MODE_TERMINAL) ? "mode=terminal" :
                                 (mode == DOM_UI_MODE_NATIVE_UI) ? "mode=native" : "mode=unknown");
    dom_log(DOM_LOG_INFO, "setup", "Version " DOM_VERSION_SEMVER);
    return 0;
}
