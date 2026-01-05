/*
FILE: source/dominium/game/runtime/dom_frames.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/frames
RESPONSIBILITY: Reference frame registry scaffolding (tree + transform stubs).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_FRAMES_H
#define DOM_FRAMES_H

#include "domino/core/spacetime.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_FRAMES_OK = 0,
    DOM_FRAMES_ERR = -1,
    DOM_FRAMES_INVALID_ARGUMENT = -2,
    DOM_FRAMES_DUPLICATE_ID = -3,
    DOM_FRAMES_NOT_FOUND = -4,
    DOM_FRAMES_INVALID_TREE = -5,
    DOM_FRAMES_NOT_IMPLEMENTED = -6
};

typedef u64 dom_frame_id;

typedef struct dom_frame_desc {
    dom_frame_id id;
    dom_frame_id parent_id;
} dom_frame_desc;

typedef struct dom_frames dom_frames;

dom_frames *dom_frames_create(void);
void dom_frames_destroy(dom_frames *frames);

int dom_frames_register(dom_frames *frames, const dom_frame_desc *desc);
int dom_frames_validate(const dom_frames *frames);

int dom_frames_transform_pos(const dom_frames *frames,
                             dom_frame_id src_frame,
                             dom_frame_id dst_frame,
                             const dom_posseg_q16 *pos,
                             dom_tick tick,
                             dom_posseg_q16 *out_pos);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_FRAMES_H */
