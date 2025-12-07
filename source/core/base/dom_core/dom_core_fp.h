#ifndef DOM_CORE_FP_H
#define DOM_CORE_FP_H

#include "dom_core_types.h"

/* q16.16 operations */
dom_q16_16 dom_q16_from_int(dom_i32 v);
dom_i32    dom_q16_to_int_floor(dom_q16_16 v);
dom_q16_16 dom_q16_mul(dom_q16_16 a, dom_q16_16 b);
dom_q16_16 dom_q16_div(dom_q16_16 a, dom_q16_16 b);

/* q32.32 operations */
dom_q32_32 dom_q32_from_int(dom_i64 v);
dom_i64    dom_q32_to_int_floor(dom_q32_32 v);
dom_q32_32 dom_q32_mul(dom_q32_32 a, dom_q32_32 b);
dom_q32_32 dom_q32_div(dom_q32_32 a, dom_q32_32 b);

/* Clamp helpers */
dom_q16_16 dom_q16_clamp(dom_q16_16 v, dom_q16_16 lo, dom_q16_16 hi);
dom_q32_32 dom_q32_clamp(dom_q32_32 v, dom_q32_32 lo, dom_q32_32 hi);

#endif /* DOM_CORE_FP_H */
