#ifndef DOMINO_INPUT_H_INCLUDED
#define DOMINO_INPUT_H_INCLUDED

#include "domino/baseline.h"
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_INPUT_MAX_KEYS              256
#define DOM_INPUT_MAX_MOUSE_BUTTONS     8
#define DOM_INPUT_MAX_GAMEPADS          4
#define DOM_INPUT_MAX_GAMEPAD_BUTTONS   16
#define DOM_INPUT_MAX_GAMEPAD_AXES      8

typedef struct dom_input_state {
    bool    keys[DOM_INPUT_MAX_KEYS];
    bool    mouse_buttons[DOM_INPUT_MAX_MOUSE_BUTTONS];
    int32_t mouse_x;
    int32_t mouse_y;
    int32_t mouse_dx;
    int32_t mouse_dy;
    int32_t mouse_wheel_x;
    int32_t mouse_wheel_y;
    bool    gamepad_buttons[DOM_INPUT_MAX_GAMEPADS][DOM_INPUT_MAX_GAMEPAD_BUTTONS];
    float   gamepad_axes[DOM_INPUT_MAX_GAMEPADS][DOM_INPUT_MAX_GAMEPAD_AXES];
} dom_input_state;

void dom_input_reset(dom_input_state* st);
void dom_input_consume_event(dom_input_state* st, const dsys_event* ev);
float dom_input_axis(const char* name);
bool  dom_input_action(const char* name);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_INPUT_H_INCLUDED */
