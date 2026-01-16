/*
FILE: source/domino/core/dom_time_core.c
MODULE: Domino
RESPONSIBILITY: Authoritative engine time core (ACT storage + advancement).
*/
#include "domino/core/dom_time_core.h"

static int dom_time_add_checked(dom_act_time_t a, dom_time_delta_t b, dom_act_time_t *out_val) {
    if (!out_val) {
        return DOM_TIME_INVALID;
    }
    if (b > 0) {
        if (a > (DOM_TIME_ACT_MAX - b)) {
            return DOM_TIME_OVERFLOW;
        }
    } else if (b < 0) {
        if (a < (DOM_TIME_ACT_MIN - b)) {
            return DOM_TIME_OVERFLOW;
        }
    }
    *out_val = (dom_act_time_t)(a + b);
    return DOM_TIME_OK;
}

int dom_time_core_init(dom_time_core *core, dom_act_time_t start_act) {
    if (!core) {
        return DOM_TIME_INVALID;
    }
    core->current_act = start_act;
    return DOM_TIME_OK;
}

int dom_time_get_act(const dom_time_core *core, dom_act_time_t *out_act) {
    if (!core || !out_act) {
        return DOM_TIME_INVALID;
    }
    *out_act = core->current_act;
    return DOM_TIME_OK;
}

int dom_time_advance(dom_time_core *core, dom_time_delta_t delta) {
    dom_act_time_t next_act;
    int rc;

    if (!core) {
        return DOM_TIME_INVALID;
    }
    if (delta < 0) {
        return DOM_TIME_BACKWARDS;
    }
    rc = dom_time_add_checked(core->current_act, delta, &next_act);
    if (rc != DOM_TIME_OK) {
        return rc;
    }
    core->current_act = next_act;
    return DOM_TIME_OK;
}

int dom_time_advance_to(dom_time_core *core, dom_act_time_t target_act) {
    if (!core) {
        return DOM_TIME_INVALID;
    }
    if (target_act < core->current_act) {
        return DOM_TIME_BACKWARDS;
    }
    core->current_act = target_act;
    return DOM_TIME_OK;
}
