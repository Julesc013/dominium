/*
FILE: tests/domino_sys/test_input_trace.c
MODULE: Repository
LAYER / SUBSYSTEM: tests/domino_sys
RESPONSIBILITY: Verify deterministic input trace normalization across backend labels.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Normalization and hashing must be stable.
*/
#include <stdio.h>
#include <string.h>

#include "system/input/input_trace.h"

static d_sys_event make_key(d_sys_event_type type, d_sys_key key)
{
    d_sys_event ev;
    memset(&ev, 0, sizeof(ev));
    ev.type = type;
    ev.u.key.key = key;
    return ev;
}

static d_sys_event make_mouse_move(i32 x, i32 y)
{
    d_sys_event ev;
    memset(&ev, 0, sizeof(ev));
    ev.type = D_SYS_EVENT_MOUSE_MOVE;
    ev.u.mouse.x = x;
    ev.u.mouse.y = y;
    ev.u.mouse.button = 0;
    return ev;
}

static d_sys_event make_mouse_button(d_sys_event_type type, u8 button)
{
    d_sys_event ev;
    memset(&ev, 0, sizeof(ev));
    ev.type = type;
    ev.u.mouse.button = button;
    ev.u.mouse.x = 0;
    ev.u.mouse.y = 0;
    return ev;
}

static d_sys_event make_quit(void)
{
    d_sys_event ev;
    memset(&ev, 0, sizeof(ev));
    ev.type = D_SYS_EVENT_QUIT;
    return ev;
}

int main(void)
{
    d_sys_event stream_a[5];
    d_sys_event stream_b[5];
    d_sys_event out_a[8];
    d_sys_event out_b[8];
    d_sys_input_trace trace_a;
    d_sys_input_trace trace_b;
    u32 out_count_a = 0u;
    u32 out_count_b = 0u;
    u64 hash_a;
    u64 hash_b;

    stream_a[0] = make_mouse_move(10, 20);
    stream_a[1] = make_key(D_SYS_EVENT_KEY_DOWN, D_SYS_KEY_A);
    stream_a[2] = make_mouse_button(D_SYS_EVENT_MOUSE_BUTTON_DOWN, 1u);
    stream_a[3] = make_key(D_SYS_EVENT_KEY_UP, D_SYS_KEY_A);
    stream_a[4] = make_quit();

    stream_b[0] = make_key(D_SYS_EVENT_KEY_UP, D_SYS_KEY_A);
    stream_b[1] = make_mouse_button(D_SYS_EVENT_MOUSE_BUTTON_DOWN, 1u);
    stream_b[2] = make_mouse_move(10, 20);
    stream_b[3] = make_quit();
    stream_b[4] = make_key(D_SYS_EVENT_KEY_DOWN, D_SYS_KEY_A);

    d_sys_input_trace_clear(&trace_a);
    d_sys_input_trace_clear(&trace_b);

    if (!d_sys_input_trace_record(&trace_a, stream_a, 5u)) {
        fprintf(stderr, "input_trace: record stream_a failed\n");
        return 1;
    }
    if (!d_sys_input_trace_record(&trace_b, stream_b, 5u)) {
        fprintf(stderr, "input_trace: record stream_b failed\n");
        return 1;
    }

    if (!d_sys_input_trace_play(&trace_a, "win32", out_a, 8u, &out_count_a)) {
        fprintf(stderr, "input_trace: play win32 failed\n");
        return 1;
    }
    if (!d_sys_input_trace_play(&trace_b, "null", out_b, 8u, &out_count_b)) {
        fprintf(stderr, "input_trace: play null failed\n");
        return 1;
    }

    if (out_count_a != out_count_b) {
        fprintf(stderr, "input_trace: count mismatch (%u vs %u)\n",
                (unsigned)out_count_a,
                (unsigned)out_count_b);
        return 1;
    }

    hash_a = d_sys_input_trace_hash(out_a, out_count_a);
    hash_b = d_sys_input_trace_hash(out_b, out_count_b);
    if (hash_a != hash_b) {
        fprintf(stderr, "input_trace: hash mismatch (%llu vs %llu)\n",
                (unsigned long long)hash_a,
                (unsigned long long)hash_b);
        return 1;
    }

    return 0;
}
