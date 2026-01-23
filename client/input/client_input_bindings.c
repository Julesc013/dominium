/*
Client input bindings implementation (read-only).
*/
#include "client_input_bindings.h"

dom_client_action dom_client_input_translate(const dsys_event* ev)
{
    int key;
    if (!ev || ev->type != DSYS_EVENT_KEY_DOWN) {
        return DOM_CLIENT_ACTION_NONE;
    }
    key = ev->payload.key.key;
    if (key == 'h' || key == 'H') {
        return DOM_CLIENT_ACTION_TOGGLE_OVERLAY;
    }
    if (key == 'b' || key == 'B') {
        return DOM_CLIENT_ACTION_TOGGLE_BORDERLESS;
    }
    return DOM_CLIENT_ACTION_NONE;
}
