/*
FILE: source/dominium/game/core/client/input/dom_input_mapping.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/core/client/input/dom_input_mapping
RESPONSIBILITY: Implements `dom_input_mapping`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_INPUT_MAPPING_H
#define DOM_INPUT_MAPPING_H

#ifdef __cplusplus
extern "C" {
#endif

#include "dom_input_actions.h"

struct DomPlatformInputFrame;

typedef enum dom_input_context_e {
    DOM_INPUT_CONTEXT_GLOBAL = 0,
    DOM_INPUT_CONTEXT_GAMEPLAY,
    DOM_INPUT_CONTEXT_UI,
    DOM_INPUT_CONTEXT_MAP,
    DOM_INPUT_CONTEXT_EDITOR,
    DOM_INPUT_CONTEXT_LAUNCHER,
    DOM_INPUT_CONTEXT_COUNT
} dom_input_context;

#define DOM_INPUT_MOUSE_LEFT   0
#define DOM_INPUT_MOUSE_RIGHT  1
#define DOM_INPUT_MOUSE_MIDDLE 2

void dom_input_mapping_init(void);
void dom_input_mapping_shutdown(void);
int  dom_input_mapping_load_defaults(const char *path);

void dom_input_mapping_set_context_enabled(dom_input_context ctx, int enabled);
void dom_input_mapping_set_active_context_mask(unsigned mask);
unsigned dom_input_mapping_active_context_mask(void);

void dom_input_mapping_begin_frame(void);
void dom_input_mapping_apply_frame(const struct DomPlatformInputFrame *frame);

void dom_input_on_key_event(int keycode, int pressed);
void dom_input_on_mouse_button(int button, int pressed);
void dom_input_on_mouse_wheel(int delta);

int dom_input_action_was_triggered(dom_input_action action);
int dom_input_action_is_down(dom_input_action action);

void dom_input_mapping_debug_dump_binding(dom_input_action action);

#ifdef __cplusplus
}
#endif

#endif /* DOM_INPUT_MAPPING_H */
