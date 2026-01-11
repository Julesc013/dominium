/*
FILE: include/domino/core/dom_time_astronomy.h
MODULE: Domino
RESPONSIBILITY: Astronomy hooks for time queries (sunrise/sunset/ephemeris).
NOTES: Pure C90 header; deterministic stubs until data providers exist.
*/
#ifndef DOMINO_CORE_DOM_TIME_ASTRONOMY_H
#define DOMINO_CORE_DOM_TIME_ASTRONOMY_H

#include "domino/core/dom_time_core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_time_astronomy {
    void *user;
    int (*sunrise)(void *user, dom_act_time_t act, dom_act_time_t *out_act);
    int (*sunset)(void *user, dom_act_time_t act, dom_act_time_t *out_act);
    int (*rotation_crossing)(void *user, dom_act_time_t act, dom_act_time_t *out_act);
    int (*ephemeris_eval)(void *user, dom_act_time_t act, void *out_blob, u32 out_bytes);
} dom_time_astronomy;

int dom_time_astronomy_sunrise(const dom_time_astronomy *astro, dom_act_time_t act, dom_act_time_t *out_act);
int dom_time_astronomy_sunset(const dom_time_astronomy *astro, dom_act_time_t act, dom_act_time_t *out_act);
int dom_time_astronomy_rotation_crossing(const dom_time_astronomy *astro, dom_act_time_t act, dom_act_time_t *out_act);
int dom_time_astronomy_ephemeris_eval(const dom_time_astronomy *astro, dom_act_time_t act, void *out_blob, u32 out_bytes);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CORE_DOM_TIME_ASTRONOMY_H */
