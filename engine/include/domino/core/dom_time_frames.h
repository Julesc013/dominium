/*
FILE: include/domino/core/dom_time_frames.h
MODULE: Domino
RESPONSIBILITY: Derived time frame conversion (ACT -> BST/GCT/CPT).
NOTES: Pure C90 header; frame conversion is deterministic and stateless.
*/
#ifndef DOMINO_CORE_DOM_TIME_FRAMES_H
#define DOMINO_CORE_DOM_TIME_FRAMES_H

#include "domino/core/dom_time_core.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Converts ACT into the requested frame; pure and deterministic. */
int dom_time_frame_convert(dom_time_frame_id frame, dom_act_time_t act, dom_act_time_t *out_frame_act);

int dom_time_act_to_bst(dom_act_time_t act, dom_act_time_t *out_bst);
int dom_time_act_to_gct(dom_act_time_t act, dom_act_time_t *out_gct);
int dom_time_act_to_cpt(dom_act_time_t act, dom_act_time_t *out_cpt);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CORE_DOM_TIME_FRAMES_H */
