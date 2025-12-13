#include "dom_game_camera.h"

extern "C" {
#include "domino/core/fixed.h"
}

namespace dom {

GameCamera::GameCamera()
{
    reset();
}

void GameCamera::reset()
{
    cx = 0.0f;
    cy = 0.0f;
    zoom = 50.0f;
    move_speed = 10.0f;
    move_up = move_down = move_left = move_right = false;
    zoom_in = zoom_out = false;
}

void GameCamera::handle_input(const d_sys_event &ev)
{
    if (ev.type == D_SYS_EVENT_KEY_DOWN || ev.type == D_SYS_EVENT_KEY_UP) {
        bool pressed = (ev.type == D_SYS_EVENT_KEY_DOWN);
        switch (ev.u.key.key) {
        case D_SYS_KEY_W:
        case D_SYS_KEY_UP:
            move_up = pressed;
            break;
        case D_SYS_KEY_S:
        case D_SYS_KEY_DOWN:
            move_down = pressed;
            break;
        case D_SYS_KEY_A:
        case D_SYS_KEY_LEFT:
            move_left = pressed;
            break;
        case D_SYS_KEY_D:
        case D_SYS_KEY_RIGHT:
            move_right = pressed;
            break;
        case D_SYS_KEY_Q:
            zoom_out = pressed;
            break;
        case D_SYS_KEY_E:
            zoom_in = pressed;
            break;
        default:
            break;
        }
    }
}

void GameCamera::tick(float tick_dt)
{
    float step = move_speed * zoom * tick_dt;
    if (move_up)    cy -= step;
    if (move_down)  cy += step;
    if (move_left)  cx -= step;
    if (move_right) cx += step;

    if (zoom_in) {
        zoom *= 0.98f;
    }
    if (zoom_out) {
        zoom *= 1.02f;
    }
    if (zoom < 5.0f)  zoom = 5.0f;
    if (zoom > 500.0f) zoom = 500.0f;
}

void GameCamera::apply_to_view(d_view_desc &view) const
{
    view.camera.pos_x = d_q16_16_from_double((double)cx);
    view.camera.pos_y = d_q16_16_from_double((double)zoom);
    view.camera.pos_z = d_q16_16_from_double((double)cy);
    view.camera.dir_x = d_q16_16_from_int(0);
    view.camera.dir_y = d_q16_16_from_int(-1);
    view.camera.dir_z = d_q16_16_from_int(0);
    view.camera.up_x = d_q16_16_from_int(0);
    view.camera.up_y = d_q16_16_from_int(0);
    view.camera.up_z = d_q16_16_from_int(1);
}

} // namespace dom
