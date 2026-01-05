/*
FILE: include/domino/core/spacetime.h
MODULE: Domino
RESPONSIBILITY: Canonical spacetime types and deterministic conversions.
NOTES: Pure C90 header; no platform headers.
*/
#ifndef DOMINO_CORE_SPACETIME_H
#define DOMINO_CORE_SPACETIME_H

#include "domino/core/fixed.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_SPACETIME_OK = 0,
    DOM_SPACETIME_ERR = -1,
    DOM_SPACETIME_INVALID = -2,
    DOM_SPACETIME_OVERFLOW = -3
};

typedef u64 dom_tick;
typedef u32 dom_ups;

typedef struct dom_timebase {
    dom_tick tick_index;
    dom_ups ups;
} dom_timebase;

typedef struct dom_posseg_q16 {
    i32 seg[3];
    fix32 loc[3];
} dom_posseg_q16;

/* Validates a timebase; returns DOM_SPACETIME_OK or DOM_SPACETIME_INVALID. */
int dom_timebase_validate(const dom_timebase *tb);

/* Converts ticks to microseconds; returns OVERFLOW and sets *out_us=UINT64_MAX on overflow. */
int dom_ticks_to_us(dom_tick ticks, dom_ups ups, u64 *out_us);

/* Converts ticks to nanoseconds; returns OVERFLOW and sets *out_ns=UINT64_MAX on overflow. */
int dom_ticks_to_ns(dom_tick ticks, dom_ups ups, u64 *out_ns);

/* Computes FNV-1a 64-bit hash of a UTF-8 ID string. */
int dom_id_hash64(const char *bytes, u32 len, u64 *out_hash);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CORE_SPACETIME_H */
