#ifndef DOMINO_INPUT_INPUT_H
#define DOMINO_INPUT_INPUT_H

#include "domino/core/types.h"
#include "domino/input/ime.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum d_input_event_type {
    D_INPUT_KEYDOWN = 0,
    D_INPUT_KEYUP,
    D_INPUT_CHAR,
    D_INPUT_MOUSEMOVE,
    D_INPUT_MOUSEDOWN,
    D_INPUT_MOUSEUP,
    D_INPUT_MOUSEWHEEL,
    D_INPUT_IME_TEXT,
    D_INPUT_IME_COMPOSITION,
    D_INPUT_CONTROLLER
} d_input_event_type;

typedef struct d_input_event {
    d_input_event_type type;
    i32 param1;
    i32 param2;
    i32 param3;
    i32 param4;
} d_input_event;

void d_input_init(void);
void d_input_shutdown(void);
void d_input_begin_frame(void);
void d_input_end_frame(void);

u32  d_input_poll(d_input_event* out_event);

/* Retrieve IME payload for events that report an identifier in param1. */
u32  d_input_get_ime_event(u32 id, d_ime_event* out_event);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_INPUT_INPUT_H */
