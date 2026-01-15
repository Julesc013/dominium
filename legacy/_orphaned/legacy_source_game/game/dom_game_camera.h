/*
FILE: source/dominium/game/dom_game_camera.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/dom_game_camera
RESPONSIBILITY: Defines internal contract for `dom_game_camera`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_CAMERA_H
#define DOM_GAME_CAMERA_H

extern "C" {
#include "view/d_view.h"
#include "system/d_system_input.h"
}

namespace dom {

struct GameCamera {
    float cx;
    float cy;
    float zoom;
    float move_speed;

    bool move_up;
    bool move_down;
    bool move_left;
    bool move_right;
    bool zoom_in;
    bool zoom_out;

    GameCamera();
    void reset();

    void handle_input(const d_sys_event &ev);
    void tick(float tick_dt);
    void apply_to_view(d_view_desc &view) const;
};

} // namespace dom

#endif
