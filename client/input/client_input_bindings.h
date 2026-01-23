/*
Client input bindings (read-only action mapping).
*/
#ifndef DOMINIUM_CLIENT_INPUT_BINDINGS_H
#define DOMINIUM_CLIENT_INPUT_BINDINGS_H

#include "domino/system/dsys.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_client_action {
    DOM_CLIENT_ACTION_NONE = 0,
    DOM_CLIENT_ACTION_TOGGLE_OVERLAY,
    DOM_CLIENT_ACTION_TOGGLE_BORDERLESS
} dom_client_action;

dom_client_action dom_client_input_translate(const dsys_event* ev);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_CLIENT_INPUT_BINDINGS_H */
