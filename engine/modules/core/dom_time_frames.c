/*
FILE: source/domino/core/dom_time_frames.c
MODULE: Domino
RESPONSIBILITY: Derived time frame conversion (ACT -> BST/GCT/CPT).
*/
#include "domino/core/dom_time_frames.h"

static int dom_time_apply_offset(dom_act_time_t act, dom_act_time_t offset, dom_act_time_t *out_val) {
    if (!out_val) {
        return DOM_TIME_INVALID;
    }
    if (offset > 0 && act > (DOM_TIME_ACT_MAX - offset)) {
        return DOM_TIME_OVERFLOW;
    }
    if (offset < 0 && act < (DOM_TIME_ACT_MIN - offset)) {
        return DOM_TIME_OVERFLOW;
    }
    *out_val = (dom_act_time_t)(act + offset);
    return DOM_TIME_OK;
}

int dom_time_act_to_bst(dom_act_time_t act, dom_act_time_t *out_bst) {
    /* Placeholder: no frame offset until ephemeris data is available. */
    return dom_time_apply_offset(act, 0, out_bst);
}

int dom_time_act_to_gct(dom_act_time_t act, dom_act_time_t *out_gct) {
    /* Placeholder: no frame offset until galactic model is available. */
    return dom_time_apply_offset(act, 0, out_gct);
}

int dom_time_act_to_cpt(dom_act_time_t act, dom_act_time_t *out_cpt) {
    /* Placeholder: no frame offset until cosmological model is available. */
    return dom_time_apply_offset(act, 0, out_cpt);
}

int dom_time_frame_convert(dom_time_frame_id frame, dom_act_time_t act, dom_act_time_t *out_frame_act) {
    if (!out_frame_act) {
        return DOM_TIME_INVALID;
    }
    switch (frame) {
        case DOM_TIME_FRAME_ACT:
            *out_frame_act = act;
            return DOM_TIME_OK;
        case DOM_TIME_FRAME_BST:
            return dom_time_act_to_bst(act, out_frame_act);
        case DOM_TIME_FRAME_GCT:
            return dom_time_act_to_gct(act, out_frame_act);
        case DOM_TIME_FRAME_CPT:
            return dom_time_act_to_cpt(act, out_frame_act);
        default:
            return DOM_TIME_INVALID;
    }
}
