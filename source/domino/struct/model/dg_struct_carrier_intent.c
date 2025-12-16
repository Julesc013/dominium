/*
FILE: source/domino/struct/model/dg_struct_carrier_intent.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/model/dg_struct_carrier_intent
RESPONSIBILITY: Implements `dg_struct_carrier_intent`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* STRUCT carrier intent authoring model (C89). */
#include "struct/model/dg_struct_carrier_intent.h"

#include <stdlib.h>
#include <string.h>

void dg_struct_carrier_intent_init(dg_struct_carrier_intent *c) {
    if (!c) return;
    memset(c, 0, sizeof(*c));
    dg_anchor_clear(&c->a0);
    dg_anchor_clear(&c->a1);
}

void dg_struct_carrier_intent_free(dg_struct_carrier_intent *c) {
    if (!c) return;
    if (c->params.ptr) {
        free(c->params.ptr);
        c->params.ptr = (unsigned char *)0;
        c->params.len = 0u;
    }
    dg_struct_carrier_intent_init(c);
}

void dg_struct_carrier_intent_clear(dg_struct_carrier_intent *c) {
    dg_struct_carrier_intent_free(c);
}

int dg_struct_carrier_intent_set_params_copy(dg_struct_carrier_intent *c, const unsigned char *bytes, u32 len) {
    unsigned char *buf;
    if (!c) return -1;
    if (c->params.ptr) {
        free(c->params.ptr);
        c->params.ptr = (unsigned char *)0;
        c->params.len = 0u;
    }
    if (!bytes || len == 0u) return 0;
    buf = (unsigned char *)malloc((size_t)len);
    if (!buf) return -2;
    memcpy(buf, bytes, (size_t)len);
    c->params.ptr = buf;
    c->params.len = len;
    return 0;
}

int dg_struct_carrier_intent_validate(const dg_struct_carrier_intent *c) {
    if (!c) return -1;
    if (c->id == 0u) return -2;
    if (c->kind != DG_STRUCT_CARRIER_BRIDGE &&
        c->kind != DG_STRUCT_CARRIER_VIADUCT &&
        c->kind != DG_STRUCT_CARRIER_TUNNEL &&
        c->kind != DG_STRUCT_CARRIER_CUT &&
        c->kind != DG_STRUCT_CARRIER_FILL) return -3;
    if (c->width < 0) return -4;
    if (c->height < 0) return -5;
    if (c->depth < 0) return -6;
    return 0;
}

