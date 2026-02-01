/*
FILE: source/domino/world/frame/dg_frame_graph.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/frame/dg_frame_graph
RESPONSIBILITY: Implements `dg_frame_graph`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>

#include "world/frame/dg_frame_graph.h"

void dg_frame_graph_init(dg_frame_graph *g, dg_frame_node *storage, u32 capacity) {
    if (!g) return;
    g->nodes = storage;
    g->count = 0u;
    g->capacity = capacity;
}

void dg_frame_graph_clear(dg_frame_graph *g) {
    if (!g) return;
    g->count = 0u;
}

int dg_frame_graph_add(dg_frame_graph *g, const dg_frame_node *node) {
    u32 i;
    if (!g || !node) return -1;
    if (!g->nodes || g->capacity == 0u) return -2;
    if (node->id == DG_FRAME_ID_WORLD) return -3;
    if (g->count >= g->capacity) return -4;

    for (i = 0u; i < g->count; ++i) {
        if (g->nodes[i].id == node->id) {
            return -5; /* duplicate */
        }
    }

    g->nodes[g->count] = *node;
    g->count += 1u;
    return 0;
}

int dg_frame_graph_find(const dg_frame_graph *g, dg_frame_id id, dg_frame_node *out_node) {
    u32 i;
    if (!g || !out_node) return -1;
    if (id == DG_FRAME_ID_WORLD) return -2;
    if (!g->nodes) return -3;
    for (i = 0u; i < g->count; ++i) {
        if (g->nodes[i].id == id) {
            *out_node = g->nodes[i];
            return 0;
        }
    }
    return -4;
}

u32 dg_frame_graph_count(const dg_frame_graph *g) {
    return g ? g->count : 0u;
}

const dg_frame_node *dg_frame_graph_at(const dg_frame_graph *g, u32 index) {
    if (!g || !g->nodes || index >= g->count) {
        return (const dg_frame_node *)0;
    }
    return &g->nodes[index];
}

