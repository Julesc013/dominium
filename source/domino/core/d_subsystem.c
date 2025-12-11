#include <stdio.h>

#include "d_subsystem.h"

#define D_SUBSYSTEM_MAX 64u

static d_subsystem_desc g_subsystems[D_SUBSYSTEM_MAX];
static u32 g_subsystem_count = 0u;

int d_subsystem_register(const d_subsystem_desc *desc) {
    u32 i;
    if (!desc) {
        fprintf(stderr, "d_subsystem_register: NULL descriptor\n");
        return -1;
    }
    if (desc->subsystem_id == 0u) {
        fprintf(stderr, "d_subsystem_register: invalid id 0\n");
        return -2;
    }
    for (i = 0u; i < g_subsystem_count; ++i) {
        if (g_subsystems[i].subsystem_id == desc->subsystem_id) {
            fprintf(stderr, "d_subsystem_register: duplicate id %u\n", (unsigned int)desc->subsystem_id);
            return -3;
        }
    }
    if (g_subsystem_count >= D_SUBSYSTEM_MAX) {
        fprintf(stderr, "d_subsystem_register: registry full\n");
        return -4;
    }

    g_subsystems[g_subsystem_count] = *desc;
    g_subsystem_count += 1u;
    return 0;
}

u32 d_subsystem_count(void) {
    return g_subsystem_count;
}

const d_subsystem_desc *d_subsystem_get_by_index(u32 index) {
    if (index >= g_subsystem_count) {
        return (const d_subsystem_desc *)0;
    }
    return &g_subsystems[index];
}

const d_subsystem_desc *d_subsystem_get_by_id(d_subsystem_id id) {
    u32 i;
    for (i = 0u; i < g_subsystem_count; ++i) {
        if (g_subsystems[i].subsystem_id == id) {
            return &g_subsystems[i];
        }
    }
    return (const d_subsystem_desc *)0;
}
