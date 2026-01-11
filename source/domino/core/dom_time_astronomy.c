/*
FILE: source/domino/core/dom_time_astronomy.c
MODULE: Domino
RESPONSIBILITY: Astronomy hooks for time queries (sunrise/sunset/ephemeris).
*/
#include "domino/core/dom_time_astronomy.h"

int dom_time_astronomy_sunrise(const dom_time_astronomy *astro, dom_act_time_t act, dom_act_time_t *out_act) {
    if (!out_act) {
        return DOM_TIME_INVALID;
    }
    if (!astro || !astro->sunrise) {
        return DOM_TIME_NO_DATA;
    }
    return astro->sunrise(astro->user, act, out_act);
}

int dom_time_astronomy_sunset(const dom_time_astronomy *astro, dom_act_time_t act, dom_act_time_t *out_act) {
    if (!out_act) {
        return DOM_TIME_INVALID;
    }
    if (!astro || !astro->sunset) {
        return DOM_TIME_NO_DATA;
    }
    return astro->sunset(astro->user, act, out_act);
}

int dom_time_astronomy_rotation_crossing(const dom_time_astronomy *astro, dom_act_time_t act, dom_act_time_t *out_act) {
    if (!out_act) {
        return DOM_TIME_INVALID;
    }
    if (!astro || !astro->rotation_crossing) {
        return DOM_TIME_NO_DATA;
    }
    return astro->rotation_crossing(astro->user, act, out_act);
}

int dom_time_astronomy_ephemeris_eval(const dom_time_astronomy *astro, dom_act_time_t act, void *out_blob, u32 out_bytes) {
    if (!out_blob || out_bytes == 0u) {
        return DOM_TIME_INVALID;
    }
    if (!astro || !astro->ephemeris_eval) {
        return DOM_TIME_NO_DATA;
    }
    return astro->ephemeris_eval(astro->user, act, out_blob, out_bytes);
}
