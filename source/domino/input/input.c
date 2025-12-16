/*
FILE: source/domino/input/input.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / input/input
RESPONSIBILITY: Implements `input`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/input/input.h"
#include "domino/sys.h"

#include <string.h>

#define D_INPUT_QUEUE_CAPACITY 256u
#define D_INPUT_IME_CAPACITY   32u

static d_input_event g_event_queue[D_INPUT_QUEUE_CAPACITY];
static u32 g_event_head = 0u;
static u32 g_event_tail = 0u;

static d_ime_event g_ime_queue[D_INPUT_IME_CAPACITY];
static u32 g_ime_ids[D_INPUT_IME_CAPACITY];
static u32 g_ime_head = 0u;
static u32 g_ime_tail = 0u;
static u32 g_ime_seq = 1u;

static void d_input_clear_events(void) {
    u32 i;
    g_event_head = 0u;
    g_event_tail = 0u;
    for (i = 0u; i < D_INPUT_QUEUE_CAPACITY; ++i) {
        memset(&g_event_queue[i], 0, sizeof(g_event_queue[i]));
    }
}

static void d_input_clear_ime(void) {
    u32 i;
    g_ime_head = 0u;
    g_ime_tail = 0u;
    for (i = 0u; i < D_INPUT_IME_CAPACITY; ++i) {
        memset(&g_ime_queue[i], 0, sizeof(g_ime_queue[i]));
        g_ime_ids[i] = 0u;
    }
}

static void d_input_push_event(const d_input_event* ev) {
    u32 slot;
    if (!ev) {
        return;
    }
    if ((g_event_tail - g_event_head) >= D_INPUT_QUEUE_CAPACITY) {
        return; /* drop oldest if full to keep determinism */
    }
    slot = g_event_tail % D_INPUT_QUEUE_CAPACITY;
    g_event_queue[slot] = *ev;
    g_event_tail += 1u;
}

static void d_input_push_ime_event(d_input_event_type type, u32 id) {
    d_input_event ev;
    memset(&ev, 0, sizeof(ev));
    ev.type = type;
    ev.param1 = (i32)id;
    d_input_push_event(&ev);
}

static void d_input_map_raw(const dsys_input_event* raw) {
    d_input_event ev;
    if (!raw) {
        return;
    }
    memset(&ev, 0, sizeof(ev));

    switch (raw->type) {
    case DSYS_INPUT_EVENT_KEY_DOWN:
        ev.type = D_INPUT_KEYDOWN;
        ev.param1 = raw->payload.key.keycode;
        ev.param2 = raw->payload.key.repeat;
        d_input_push_event(&ev);
        if (raw->payload.key.translated) {
            d_input_event ch;
            memset(&ch, 0, sizeof(ch));
            ch.type = D_INPUT_CHAR;
            ch.param1 = raw->payload.key.translated & 0xFF;
            d_input_push_event(&ch);
        }
        break;
    case DSYS_INPUT_EVENT_KEY_UP:
        ev.type = D_INPUT_KEYUP;
        ev.param1 = raw->payload.key.keycode;
        d_input_push_event(&ev);
        break;
    case DSYS_INPUT_EVENT_TEXT:
        ev.type = D_INPUT_CHAR;
        ev.param1 = (i32)(unsigned char)raw->payload.text.text[0];
        ev.param2 = (i32)strlen(raw->payload.text.text);
        d_input_push_event(&ev);
        break;
    case DSYS_INPUT_EVENT_MOUSE_MOVE:
        ev.type = D_INPUT_MOUSEMOVE;
        ev.param1 = raw->payload.mouse_move.x;
        ev.param2 = raw->payload.mouse_move.y;
        ev.param3 = raw->payload.mouse_move.dx;
        ev.param4 = raw->payload.mouse_move.dy;
        d_input_push_event(&ev);
        break;
    case DSYS_INPUT_EVENT_MOUSE_BUTTON:
        ev.type = raw->payload.mouse_button.pressed ? D_INPUT_MOUSEDOWN : D_INPUT_MOUSEUP;
        ev.param1 = raw->payload.mouse_button.button;
        ev.param2 = raw->payload.mouse_button.x;
        ev.param3 = raw->payload.mouse_button.y;
        ev.param4 = raw->payload.mouse_button.clicks;
        d_input_push_event(&ev);
        break;
    case DSYS_INPUT_EVENT_MOUSE_WHEEL:
        ev.type = D_INPUT_MOUSEWHEEL;
        ev.param1 = raw->payload.mouse_wheel.delta_x;
        ev.param2 = raw->payload.mouse_wheel.delta_y;
        d_input_push_event(&ev);
        break;
    case DSYS_INPUT_EVENT_CONTROLLER_BUTTON:
    case DSYS_INPUT_EVENT_CONTROLLER_AXIS:
        ev.type = D_INPUT_CONTROLLER;
        ev.param1 = raw->payload.controller.gamepad;
        ev.param2 = raw->payload.controller.control;
        ev.param3 = raw->payload.controller.value;
        ev.param4 = raw->payload.controller.is_axis;
        d_input_push_event(&ev);
        break;
    default:
        break;
    }
}

static void d_input_collect_raw(void) {
    dsys_input_event raw;
    while ((g_event_tail - g_event_head) < D_INPUT_QUEUE_CAPACITY) {
        if (!dsys_input_poll_raw(&raw)) {
            break;
        }
        d_input_map_raw(&raw);
    }
}

static void d_input_collect_ime(void) {
    d_ime_event ime;
    while ((g_ime_tail - g_ime_head) < D_INPUT_IME_CAPACITY) {
        u32 slot;
        u32 id;
        if (!d_ime_poll(&ime)) {
            break;
        }
        slot = g_ime_tail % D_INPUT_IME_CAPACITY;
        g_ime_queue[slot] = ime;
        id = g_ime_seq++;
        g_ime_ids[slot] = id;
        g_ime_tail += 1u;
        if (ime.has_commit) {
            d_input_push_ime_event(D_INPUT_IME_TEXT, id);
        }
        if (ime.has_composition) {
            d_input_push_ime_event(D_INPUT_IME_COMPOSITION, id);
        }
    }
}

void d_input_init(void) {
    d_input_clear_events();
    d_input_clear_ime();
}

void d_input_shutdown(void) {
    d_input_clear_events();
    d_input_clear_ime();
}

void d_input_begin_frame(void) {
    d_input_clear_events();
    d_input_clear_ime();
    d_input_collect_raw();
    d_input_collect_ime();
}

void d_input_end_frame(void) {
    /* placeholder for future frame finalization */
}

u32 d_input_poll(d_input_event* out_event) {
    u32 slot;
    if (g_event_head == g_event_tail) {
        if (out_event) {
            memset(out_event, 0, sizeof(*out_event));
        }
        return 0u;
    }
    slot = g_event_head % D_INPUT_QUEUE_CAPACITY;
    if (out_event) {
        *out_event = g_event_queue[slot];
    }
    g_event_head += 1u;
    return 1u;
}

u32 d_input_get_ime_event(u32 id, d_ime_event* out_event) {
    u32 idx;
    if (out_event) {
        memset(out_event, 0, sizeof(*out_event));
    }
    for (idx = g_ime_head; idx < g_ime_tail; ++idx) {
        u32 slot = idx % D_INPUT_IME_CAPACITY;
        if (g_ime_ids[slot] == id) {
            if (out_event) {
                *out_event = g_ime_queue[slot];
            }
            return 1u;
        }
    }
    return 0u;
}
