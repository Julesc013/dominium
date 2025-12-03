#include "dom_core_fp.h"

dom_q16_16 dom_q16_from_int(dom_i32 v)            { return (dom_q16_16)(v << 16); }
dom_i32    dom_q16_to_int_floor(dom_q16_16 v)     { return (dom_i32)(v >> 16); }
dom_q16_16 dom_q16_mul(dom_q16_16 a, dom_q16_16 b){ return (dom_q16_16)((((dom_i64)a) * b) >> 16); }
dom_q16_16 dom_q16_div(dom_q16_16 a, dom_q16_16 b){ return (b == 0) ? 0 : (dom_q16_16)((((dom_i64)a) << 16) / b); }

dom_q32_32 dom_q32_from_int(dom_i64 v)            { return (dom_q32_32)(v << 32); }
dom_i64    dom_q32_to_int_floor(dom_q32_32 v)     { return (dom_i64)(v >> 32); }
dom_q32_32 dom_q32_mul(dom_q32_32 a, dom_q32_32 b){ return (dom_q32_32)((((dom_i64)a) * b) >> 32); }
dom_q32_32 dom_q32_div(dom_q32_32 a, dom_q32_32 b){ return (b == 0) ? 0 : (dom_q32_32)((((dom_i64)a) << 32) / b); }

dom_q16_16 dom_q16_clamp(dom_q16_16 v, dom_q16_16 lo, dom_q16_16 hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

dom_q32_32 dom_q32_clamp(dom_q32_32 v, dom_q32_32 lo, dom_q32_32 hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}
