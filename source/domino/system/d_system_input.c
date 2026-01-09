/*
FILE: source/domino/system/d_system_input.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/d_system_input
RESPONSIBILITY: Implements `d_system_input`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "d_system_input.h"
#include "system/input/input_trace.h"

#include <string.h>
#include "domino/system/dsys.h"

#define D_SYS_INPUT_QUEUE_MAX 64

typedef struct d_sys_input_queue_s {
    d_sys_event events[D_SYS_INPUT_QUEUE_MAX];
    int         head;
    int         tail;
    int         count;
} d_sys_input_queue;

static d_sys_input_queue g_input_queue = { { { D_SYS_EVENT_NONE } }, 0, 0, 0 };

static d_sys_key d_system_map_keycode(int keycode) {
    switch (keycode) {
    case 27:  return D_SYS_KEY_ESCAPE;
    case 13:  return D_SYS_KEY_ENTER;
    case 32:  return D_SYS_KEY_SPACE;
    case 8:   return D_SYS_KEY_BACKSPACE;
    case 127: return D_SYS_KEY_BACKSPACE;
    case '0': return D_SYS_KEY_0;
    case '1': return D_SYS_KEY_1;
    case '2': return D_SYS_KEY_2;
    case '3': return D_SYS_KEY_3;
    case '4': return D_SYS_KEY_4;
    case '5': return D_SYS_KEY_5;
    case '6': return D_SYS_KEY_6;
    case '7': return D_SYS_KEY_7;
    case '8': return D_SYS_KEY_8;
    case '9': return D_SYS_KEY_9;
    case '.': return D_SYS_KEY_PERIOD;
    case 'w': case 'W': return D_SYS_KEY_W;
    case 'a': case 'A': return D_SYS_KEY_A;
    case 's': case 'S': return D_SYS_KEY_S;
    case 'd': case 'D': return D_SYS_KEY_D;
    case 'q': case 'Q': return D_SYS_KEY_Q;
    case 'e': case 'E': return D_SYS_KEY_E;
    /* SDL2 keycodes for arrows */
    case 1073741906: return D_SYS_KEY_UP;
    case 1073741905: return D_SYS_KEY_DOWN;
    case 1073741904: return D_SYS_KEY_LEFT;
    case 1073741903: return D_SYS_KEY_RIGHT;
    default:
        break;
    }
    return D_SYS_KEY_UNKNOWN;
}

static u8 d_system_map_mouse_button(int button) {
    /* SDL: 1=left,2=middle,3=right; map to 1=left,2=right,3=middle */
    if (button == 1) return 1;
    if (button == 3) return 2;
    if (button == 2) return 3;
    if (button == 0) return 1;
    return 0;
}

static void d_system_queue_clear(void) {
    memset(&g_input_queue, 0, sizeof(g_input_queue));
}

int d_system_input_enqueue(const d_sys_event *ev) {
    if (!ev) {
        return -1;
    }
    if (g_input_queue.count >= D_SYS_INPUT_QUEUE_MAX) {
        /* drop oldest to keep deterministic order, avoid overflow */
        g_input_queue.head = (g_input_queue.head + 1) % D_SYS_INPUT_QUEUE_MAX;
        g_input_queue.count -= 1;
    }
    g_input_queue.events[g_input_queue.tail] = *ev;
    g_input_queue.tail = (g_input_queue.tail + 1) % D_SYS_INPUT_QUEUE_MAX;
    g_input_queue.count += 1;
    return 0;
}

int d_system_poll_event(d_sys_event *out_ev) {
    if (out_ev) {
        memset(out_ev, 0, sizeof(*out_ev));
    }
    if (g_input_queue.count == 0) {
        return 0;
    }
    if (out_ev) {
        *out_ev = g_input_queue.events[g_input_queue.head];
    }
    g_input_queue.head = (g_input_queue.head + 1) % D_SYS_INPUT_QUEUE_MAX;
    g_input_queue.count -= 1;
    return 1;
}

int d_system_input_pump_dsys(void) {
    dsys_event ev;
    d_sys_event batch[D_SYS_INPUT_TRACE_MAX_EVENTS];
    u32 count = 0u;
    u32 i;
    while (dsys_poll_event(&ev)) {
        d_sys_event out;
        memset(&out, 0, sizeof(out));
        switch (ev.type) {
        case DSYS_EVENT_QUIT:
            out.type = D_SYS_EVENT_QUIT;
            break;
        case DSYS_EVENT_KEY_DOWN:
        case DSYS_EVENT_KEY_UP:
            out.type = (ev.type == DSYS_EVENT_KEY_DOWN) ? D_SYS_EVENT_KEY_DOWN : D_SYS_EVENT_KEY_UP;
            out.u.key.key = d_system_map_keycode(ev.payload.key.key);
            break;
        case DSYS_EVENT_MOUSE_MOVE:
            out.type = D_SYS_EVENT_MOUSE_MOVE;
            out.u.mouse.x = (i32)ev.payload.mouse_move.x;
            out.u.mouse.y = (i32)ev.payload.mouse_move.y;
            out.u.mouse.button = 0;
            break;
        case DSYS_EVENT_MOUSE_BUTTON:
            out.type = ev.payload.mouse_button.pressed ? D_SYS_EVENT_MOUSE_BUTTON_DOWN : D_SYS_EVENT_MOUSE_BUTTON_UP;
            out.u.mouse.x = 0;
            out.u.mouse.y = 0;
            out.u.mouse.button = d_system_map_mouse_button(ev.payload.mouse_button.button);
            break;
        default:
            break;
        }
        if (out.type != D_SYS_EVENT_NONE) {
            if (count >= D_SYS_INPUT_TRACE_MAX_EVENTS) {
                memmove(batch,
                        batch + 1,
                        (D_SYS_INPUT_TRACE_MAX_EVENTS - 1u) * sizeof(d_sys_event));
                count = D_SYS_INPUT_TRACE_MAX_EVENTS - 1u;
            }
            batch[count++] = out;
        }
    }
    if (count > 1u) {
        /* Canonicalize ordering to avoid backend-dependent event sequences. */
        d_sys_input_trace_normalize(batch, count);
    }
    for (i = 0u; i < count; ++i) {
        d_system_input_enqueue(&batch[i]);
    }
    return (int)count;
}
