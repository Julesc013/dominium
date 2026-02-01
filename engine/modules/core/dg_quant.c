/*
FILE: source/domino/core/dg_quant.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/dg_quant
RESPONSIBILITY: Implements `dg_quant`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic quantization helpers (C89). */
#include "core/dg_quant.h"

static u64 dg_abs_i64_u64(i64 v) {
    if (v < 0) {
        if (v == (i64)0x8000000000000000LL) {
            return ((u64)1) << 63;
        }
        return (u64)(-v);
    }
    return (u64)v;
}

static dg_q dg_quant_round_near(dg_q value_q, dg_q quantum_q) {
    dg_q q;
    dg_q r;
    dg_q base;
    u64 ar;
    u64 uq;

    if (quantum_q <= 0) {
        return value_q;
    }

    /* C89 division is truncating toward zero (enforced by det invariants). */
    q = (dg_q)((i64)value_q / (i64)quantum_q);
    r = (dg_q)((i64)value_q % (i64)quantum_q);

    /* base is the trunc-toward-zero multiple. */
    base = (dg_q)((q48_16)value_q - (q48_16)r);

    if (r == 0) {
        return base;
    }

    ar = dg_abs_i64_u64((i64)r);
    uq = (u64)quantum_q;

    /* If remainder is at least half the quantum, round away from zero. */
    if (ar >= (uq - ar)) {
        if (value_q >= 0) {
            return (dg_q)d_q48_16_add((q48_16)base, (q48_16)quantum_q);
        } else {
            return (dg_q)d_q48_16_sub((q48_16)base, (q48_16)quantum_q);
        }
    }

    return base;
}

dg_q dg_quant_pos(dg_q value_q, dg_q quantum_q) {
    return dg_quant_round_near(value_q, quantum_q);
}

dg_q dg_quant_angle(dg_q value_q, dg_q quantum_q) {
    return dg_quant_round_near(value_q, quantum_q);
}

dg_q dg_quant_param(dg_q value_q, dg_q quantum_q) {
    return dg_quant_round_near(value_q, quantum_q);
}

