/*
FILE: source/dominium/game/cli/game_cli.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/cli/game_cli
RESPONSIBILITY: Implements `game_cli`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* TODO: legacy CLI entrypoint; not yet wired into dominium_game target. */
#include "dominium/dom_app_mode.h"
#include "dominium/dom_plat_sys.h"
#include "dominium/dom_plat_term.h"
#include "dominium/dom_plat_ui.h"
#include "dominium/dom_rend.h"
#include "dominium/dom_version.h"
#include "dominium/dom_core.h"

int main(int argc, char** argv)
{
    const struct dom_sys_vtable* sys = dom_plat_sys_choose_best();
    const struct dom_term_vtable* term = dom_plat_term_probe(sys);
    const struct dom_ui_vtable* ui = dom_plat_ui_probe(sys);
    const struct dom_rend_vtable* rend = dom_rend_choose_best();
    enum dom_ui_mode mode = dom_choose_ui_mode(argc, argv, sys, term, ui, 1);
    (void)rend;
    dom_log(DOM_LOG_INFO, "game", "Dominium game stub");
    dom_log(DOM_LOG_INFO, "game", (mode == DOM_UI_MODE_HEADLESS) ? "mode=headless" :
                                 (mode == DOM_UI_MODE_TERMINAL) ? "mode=terminal" :
                                 (mode == DOM_UI_MODE_NATIVE_UI) ? "mode=native" :
                                 (mode == DOM_UI_MODE_RENDERED) ? "mode=rendered" : "mode=unknown");
    dom_log(DOM_LOG_INFO, "game", "Version " DOM_VERSION_SEMVER);
    return 0;
}
