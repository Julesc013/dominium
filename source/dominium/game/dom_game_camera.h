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
