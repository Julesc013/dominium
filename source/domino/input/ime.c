#include "domino/input/ime.h"
#include "domino/sys.h"

#include <string.h>

#define D_IME_QUEUE_CAPACITY 16u

static d_ime_event g_ime_queue[D_IME_QUEUE_CAPACITY];
static u32 g_ime_head = 0u;
static u32 g_ime_tail = 0u;
static u32 g_ime_enabled = 0u;

static void d_ime_reset_queue(void) {
    u32 i;
    g_ime_head = 0u;
    g_ime_tail = 0u;
    for (i = 0u; i < D_IME_QUEUE_CAPACITY; ++i) {
        memset(&g_ime_queue[i], 0, sizeof(g_ime_queue[i]));
    }
}

static void d_ime_collect(void) {
    dsys_ime_event raw;

    if (!g_ime_enabled) {
        return;
    }

    while ((g_ime_tail - g_ime_head) < D_IME_QUEUE_CAPACITY) {
        u32 slot;
        if (!dsys_ime_poll(&raw)) {
            break;
        }
        slot = g_ime_tail % D_IME_QUEUE_CAPACITY;
        memset(&g_ime_queue[slot], 0, sizeof(g_ime_queue[slot]));
        g_ime_queue[slot].has_composition = (u8)(raw.has_composition ? 1u : 0u);
        g_ime_queue[slot].has_commit = (u8)(raw.has_commit ? 1u : 0u);
        if (raw.has_composition) {
            strncpy(g_ime_queue[slot].composition, raw.composition,
                    sizeof(g_ime_queue[slot].composition) - 1u);
            g_ime_queue[slot].composition[sizeof(g_ime_queue[slot].composition) - 1u] = '\0';
        }
        if (raw.has_commit) {
            strncpy(g_ime_queue[slot].committed, raw.committed,
                    sizeof(g_ime_queue[slot].committed) - 1u);
            g_ime_queue[slot].committed[sizeof(g_ime_queue[slot].committed) - 1u] = '\0';
        }
        g_ime_tail += 1u;
    }
}

void d_ime_init(void) {
    g_ime_enabled = 0u;
    d_ime_reset_queue();
}

void d_ime_shutdown(void) {
    d_ime_disable();
    d_ime_reset_queue();
}

void d_ime_enable(void) {
    if (g_ime_enabled) {
        return;
    }
    g_ime_enabled = 1u;
    dsys_ime_start();
}

void d_ime_disable(void) {
    if (!g_ime_enabled) {
        return;
    }
    dsys_ime_stop();
    g_ime_enabled = 0u;
    d_ime_reset_queue();
}

u32 d_ime_poll(d_ime_event* out) {
    u32 slot;
    d_ime_collect();
    if (g_ime_head == g_ime_tail) {
        if (out) {
            memset(out, 0, sizeof(*out));
        }
        return 0u;
    }
    slot = g_ime_head % D_IME_QUEUE_CAPACITY;
    if (out) {
        *out = g_ime_queue[slot];
    }
    g_ime_head += 1u;
    return 1u;
}
