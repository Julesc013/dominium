/*
FILE: source/domino/system/input/input_trace.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/input/input_trace
RESPONSIBILITY: Implements deterministic input trace normalization and hashing.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Normalization and hashing must be stable across platforms.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
*/
#include "system/input/input_trace.h"

#include <string.h>

typedef struct d_sys_input_trace_item {
    d_sys_event ev;
    u32 index;
} d_sys_input_trace_item;

static void d_sys_input_trace_key(const d_sys_event* ev,
                                  u32* out_type,
                                  i32* out_a,
                                  i32* out_b,
                                  i32* out_c)
{
    u32 type = 0u;
    i32 a = 0;
    i32 b = 0;
    i32 c = 0;
    if (ev) {
        type = (u32)ev->type;
        switch (ev->type) {
        case D_SYS_EVENT_KEY_DOWN:
        case D_SYS_EVENT_KEY_UP:
            a = (i32)ev->u.key.key;
            break;
        case D_SYS_EVENT_MOUSE_MOVE:
            a = ev->u.mouse.x;
            b = ev->u.mouse.y;
            break;
        case D_SYS_EVENT_MOUSE_BUTTON_DOWN:
        case D_SYS_EVENT_MOUSE_BUTTON_UP:
            a = (i32)ev->u.mouse.button;
            b = ev->u.mouse.x;
            c = ev->u.mouse.y;
            break;
        default:
            break;
        }
    }
    if (out_type) *out_type = type;
    if (out_a) *out_a = a;
    if (out_b) *out_b = b;
    if (out_c) *out_c = c;
}

static int d_sys_input_trace_cmp(const d_sys_input_trace_item* a,
                                 const d_sys_input_trace_item* b)
{
    u32 ta;
    u32 tb;
    i32 aa;
    i32 ab;
    i32 ba;
    i32 bb;
    i32 ca;
    i32 cb;

    d_sys_input_trace_key(&a->ev, &ta, &aa, &ba, &ca);
    d_sys_input_trace_key(&b->ev, &tb, &ab, &bb, &cb);

    if (ta != tb) return (ta < tb) ? -1 : 1;
    if (aa != ab) return (aa < ab) ? -1 : 1;
    if (ba != bb) return (ba < bb) ? -1 : 1;
    if (ca != cb) return (ca < cb) ? -1 : 1;
    if (a->index != b->index) return (a->index < b->index) ? -1 : 1;
    return 0;
}

void d_sys_input_trace_normalize(d_sys_event* events, u32 count)
{
    d_sys_input_trace_item items[D_SYS_INPUT_TRACE_MAX_EVENTS];
    u32 i;
    if (!events || count < 2u) {
        return;
    }
    if (count > D_SYS_INPUT_TRACE_MAX_EVENTS) {
        count = D_SYS_INPUT_TRACE_MAX_EVENTS;
    }
    for (i = 0u; i < count; ++i) {
        items[i].ev = events[i];
        items[i].index = i;
    }
    for (i = 1u; i < count; ++i) {
        d_sys_input_trace_item key = items[i];
        u32 j = i;
        while (j > 0u && d_sys_input_trace_cmp(&key, &items[j - 1u]) < 0) {
            items[j] = items[j - 1u];
            --j;
        }
        items[j] = key;
    }
    for (i = 0u; i < count; ++i) {
        events[i] = items[i].ev;
    }
}

void d_sys_input_trace_clear(d_sys_input_trace* trace)
{
    if (!trace) {
        return;
    }
    memset(trace, 0, sizeof(*trace));
}

int d_sys_input_trace_record(d_sys_input_trace* trace,
                             const d_sys_event* events,
                             u32 count)
{
    u32 i;
    if (!trace) {
        return 0;
    }
    trace->count = 0u;
    if (!events || count == 0u) {
        return 1;
    }
    if (count > D_SYS_INPUT_TRACE_MAX_EVENTS) {
        count = D_SYS_INPUT_TRACE_MAX_EVENTS;
    }
    for (i = 0u; i < count; ++i) {
        trace->events[i] = events[i];
    }
    trace->count = count;
    return 1;
}

int d_sys_input_trace_play(const d_sys_input_trace* trace,
                           const char* backend_name,
                           d_sys_event* out_events,
                           u32 max_events,
                           u32* out_count)
{
    u32 i;
    u32 count;
    (void)backend_name;

    if (out_count) {
        *out_count = 0u;
    }
    if (!trace || !out_events || max_events == 0u) {
        return 0;
    }

    count = trace->count;
    if (count > max_events) {
        count = max_events;
    }
    for (i = 0u; i < count; ++i) {
        out_events[i] = trace->events[i];
    }

    d_sys_input_trace_normalize(out_events, count);
    if (out_count) {
        *out_count = count;
    }
    return 1;
}

static u64 d_sys_input_hash_u32(u64 hash, u32 v)
{
    u32 i;
    for (i = 0u; i < 4u; ++i) {
        hash ^= (u64)((v >> (i * 8u)) & 0xffu);
        hash *= 1099511628211ull;
    }
    return hash;
}

static u64 d_sys_input_hash_i32(u64 hash, i32 v)
{
    return d_sys_input_hash_u32(hash, (u32)v);
}

u64 d_sys_input_trace_hash(const d_sys_event* events, u32 count)
{
    u64 hash = 14695981039346656037ull;
    u32 i;
    if (!events) {
        return hash;
    }
    hash = d_sys_input_hash_u32(hash, count);
    for (i = 0u; i < count; ++i) {
        u32 type;
        i32 a;
        i32 b;
        i32 c;
        d_sys_input_trace_key(&events[i], &type, &a, &b, &c);
        hash = d_sys_input_hash_u32(hash, type);
        hash = d_sys_input_hash_i32(hash, a);
        hash = d_sys_input_hash_i32(hash, b);
        hash = d_sys_input_hash_i32(hash, c);
    }
    return hash;
}
