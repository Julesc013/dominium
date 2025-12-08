#include "domino/input.h"

#include <string.h>

void dom_input_reset(dom_input_state* st)
{
    if (!st) {
        return;
    }
    memset(st, 0, sizeof(*st));
}

void dom_input_consume_event(dom_input_state* st, const dsys_event* ev)
{
    int32_t key;
    int32_t button;
    int32_t gamepad;
    int32_t axis;

    if (!st || !ev) {
        return;
    }

    switch (ev->type) {
    case DSYS_EVENT_KEY_DOWN:
    case DSYS_EVENT_KEY_UP:
        key = ev->payload.key.key;
        if (key >= 0 && key < DOM_INPUT_MAX_KEYS) {
            st->keys[key] = (ev->type == DSYS_EVENT_KEY_DOWN) ? true : false;
        }
        break;
    case DSYS_EVENT_MOUSE_MOVE:
        st->mouse_x = ev->payload.mouse_move.x;
        st->mouse_y = ev->payload.mouse_move.y;
        st->mouse_dx += ev->payload.mouse_move.dx;
        st->mouse_dy += ev->payload.mouse_move.dy;
        break;
    case DSYS_EVENT_MOUSE_BUTTON:
        button = ev->payload.mouse_button.button;
        if (button >= 0 && button < DOM_INPUT_MAX_MOUSE_BUTTONS) {
            st->mouse_buttons[button] = ev->payload.mouse_button.pressed;
        }
        break;
    case DSYS_EVENT_MOUSE_WHEEL:
        st->mouse_wheel_x += ev->payload.mouse_wheel.delta_x;
        st->mouse_wheel_y += ev->payload.mouse_wheel.delta_y;
        break;
    case DSYS_EVENT_GAMEPAD_BUTTON:
        button = ev->payload.gamepad_button.button;
        gamepad = ev->payload.gamepad_button.gamepad;
        if (gamepad >= 0 && gamepad < DOM_INPUT_MAX_GAMEPADS &&
            button >= 0 && button < DOM_INPUT_MAX_GAMEPAD_BUTTONS) {
            st->gamepad_buttons[gamepad][button] = ev->payload.gamepad_button.pressed;
        }
        break;
    case DSYS_EVENT_GAMEPAD_AXIS:
        axis = ev->payload.gamepad_axis.axis;
        gamepad = ev->payload.gamepad_axis.gamepad;
        if (gamepad >= 0 && gamepad < DOM_INPUT_MAX_GAMEPADS &&
            axis >= 0 && axis < DOM_INPUT_MAX_GAMEPAD_AXES) {
            st->gamepad_axes[gamepad][axis] = ev->payload.gamepad_axis.value;
        }
        break;
    default:
        break;
    }
}

float dom_input_axis(const char* name)
{
    (void)name;
    return 0.0f;
}

bool dom_input_action(const char* name)
{
    (void)name;
    return false;
}
