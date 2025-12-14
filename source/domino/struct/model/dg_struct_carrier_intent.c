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

