/*
FILE: source/dominium/game/core/client/input/dom_input_actions.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/core/client/input/dom_input_actions
RESPONSIBILITY: Defines internal contract for `dom_input_actions`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_INPUT_ACTIONS_H
#define DOM_INPUT_ACTIONS_H

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_input_action_e {
    ACTION_NONE = 0,

    /* Function key actions */
    ACTION_HELP_OVERLAY,
    ACTION_SCREENSHOT_CAPTURE,
    ACTION_DEBUG_OVERLAY_CYCLE,
    ACTION_VIEW_DIMENSION_TOGGLE,
    ACTION_VIEW_RENDER_MODE_CYCLE,
    ACTION_QUICK_SAVE,
    ACTION_QUICK_LOAD,
    ACTION_REPLAY_PANEL,
    ACTION_TOOLS_PANEL,
    ACTION_WORLD_MAP,
    ACTION_SETTINGS_MENU,
    ACTION_FULLSCREEN_TOGGLE,
    ACTION_DEV_CONSOLE,

    /* Movement / camera */
    ACTION_MOVE_FORWARD,
    ACTION_MOVE_BACKWARD,
    ACTION_MOVE_LEFT,
    ACTION_MOVE_RIGHT,
    ACTION_CAMERA_ROTATE_CCW,
    ACTION_CAMERA_ROTATE_CW,
    ACTION_CAMERA_ALT_UP,
    ACTION_CAMERA_ALT_DOWN,

    /* Selection/UI */
    ACTION_PRIMARY_SELECT,
    ACTION_SECONDARY_SELECT,
    ACTION_UI_BACK,
    ACTION_LAYER_CYCLE,

    /* Quickbar */
    ACTION_QUICKBAR_SLOT_1,
    ACTION_QUICKBAR_SLOT_2,
    ACTION_QUICKBAR_SLOT_3,
    ACTION_QUICKBAR_SLOT_4,
    ACTION_QUICKBAR_SLOT_5,
    ACTION_QUICKBAR_SLOT_6,
    ACTION_QUICKBAR_SLOT_7,
    ACTION_QUICKBAR_SLOT_8,
    ACTION_QUICKBAR_SLOT_9,

    /* Overlays / diagnostics */
    ACTION_PROFILER_OVERLAY,
    ACTION_HIGHLIGHT_INTERACTIVES,

    ACTION_COUNT
} dom_input_action;

#ifdef __cplusplus
}
#endif

#endif /* DOM_INPUT_ACTIONS_H */
