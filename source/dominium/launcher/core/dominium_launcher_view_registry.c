/*
FILE: source/dominium/launcher/core/dominium_launcher_view_registry.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core/dominium_launcher_view_registry
RESPONSIBILITY: Implements `dominium_launcher_view_registry`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dominium_launcher_view_registry.h"

#include <stdlib.h>
#include <string.h>

struct dominium_launcher_view_registry {
    dominium_launcher_view_desc views[64];
    unsigned int count;
    unsigned int sorted;
};

static int dominium_launcher_view_compare(const void* a, const void* b)
{
    const dominium_launcher_view_desc* va = (const dominium_launcher_view_desc*)a;
    const dominium_launcher_view_desc* vb = (const dominium_launcher_view_desc*)b;
    if (va->priority < vb->priority) return -1;
    if (va->priority > vb->priority) return 1;
    return strcmp(va->id, vb->id);
}

dominium_launcher_view_registry* dominium_launcher_view_registry_create(void)
{
    dominium_launcher_view_registry* reg =
        (dominium_launcher_view_registry*)malloc(sizeof(dominium_launcher_view_registry));
    if (!reg) return NULL;
    memset(reg, 0, sizeof(*reg));
    return reg;
}

void dominium_launcher_view_registry_destroy(dominium_launcher_view_registry* reg)
{
    if (!reg) return;
    free(reg);
}

int dominium_launcher_view_register(dominium_launcher_view_registry* reg,
                                    const dominium_launcher_view_desc* desc)
{
    if (!reg || !desc) return -1;
    if (reg->count >= (sizeof(reg->views) / sizeof(reg->views[0]))) {
        return -1; /* TODO: grow dynamically */
    }
    reg->views[reg->count++] = *desc;
    reg->sorted = 0;
    return 0;
}

int dominium_launcher_view_list(const dominium_launcher_view_registry* reg,
                                const dominium_launcher_view_desc** out_array,
                                unsigned int* out_count)
{
    dominium_launcher_view_registry* mut_reg;
    if (!reg || !out_array || !out_count) return -1;
    mut_reg = (dominium_launcher_view_registry*)reg; /* sorting is internal; registry owns the array */
    if (!mut_reg->sorted && mut_reg->count > 1) {
        qsort(mut_reg->views,
              mut_reg->count,
              sizeof(mut_reg->views[0]),
              dominium_launcher_view_compare);
        mut_reg->sorted = 1;
    }
    *out_array = mut_reg->views;
    *out_count = mut_reg->count;
    return 0;
}

const dominium_launcher_view_desc* dominium_launcher_view_find(
    const dominium_launcher_view_registry* reg,
    const char* id)
{
    unsigned int i;
    if (!reg || !id) return NULL;
    for (i = 0; i < reg->count; ++i) {
        if (strcmp(reg->views[i].id, id) == 0) {
            return &reg->views[i];
        }
    }
    return NULL;
}
