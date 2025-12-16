/*
FILE: source/domino/sim/lod/dg_accum.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/lod/dg_accum
RESPONSIBILITY: Implements `dg_accum`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>

#include "sim/lod/dg_accum.h"

static u64 dg_abs_i64_u64(i64 v) {
    if (v < 0) {
        return (u64)(0ULL - (u64)v);
    }
    return (u64)v;
}

static i64 dg_clamp_abs_i64(i64 v, u64 max_abs) {
    u64 mag = dg_abs_i64_u64(v);
    if (mag <= max_abs) {
        return v;
    }
    if (v < 0) {
        return -(i64)max_abs;
    }
    return (i64)max_abs;
}

static d_bool dg_accum_unit_is_zero(dg_accum_type type, const dg_accum_value *unit) {
    if (!unit) {
        return D_TRUE;
    }
    switch (type) {
        case DG_ACCUM_SCALAR_Q32_32: return (unit->scalar == 0) ? D_TRUE : D_FALSE;
        case DG_ACCUM_VEC3_Q32_32: return (unit->vec3.x == 0 && unit->vec3.y == 0 && unit->vec3.z == 0) ? D_TRUE : D_FALSE;
        case DG_ACCUM_COUNT_I64: return (unit->count == 0) ? D_TRUE : D_FALSE;
        default: break;
    }
    return D_TRUE;
}

void dg_accum_init_scalar(dg_accum *a, q32_32 unit) {
    if (!a) {
        return;
    }
    memset(a, 0, sizeof(*a));
    a->type = DG_ACCUM_SCALAR_Q32_32;
    a->unit.scalar = (unit < 0) ? (q32_32)(-unit) : unit;
}

void dg_accum_init_vec3(dg_accum *a, dg_accum_vec3_q32_32 unit) {
    if (!a) {
        return;
    }
    memset(a, 0, sizeof(*a));
    a->type = DG_ACCUM_VEC3_Q32_32;
    a->unit.vec3.x = (unit.x < 0) ? (q32_32)(-unit.x) : unit.x;
    a->unit.vec3.y = (unit.y < 0) ? (q32_32)(-unit.y) : unit.y;
    a->unit.vec3.z = (unit.z < 0) ? (q32_32)(-unit.z) : unit.z;
}

void dg_accum_init_count(dg_accum *a, i64 unit) {
    if (!a) {
        return;
    }
    memset(a, 0, sizeof(*a));
    a->type = DG_ACCUM_COUNT_I64;
    a->unit.count = (unit < 0) ? -unit : unit;
}

void dg_accum_clear(dg_accum *a) {
    if (!a) {
        return;
    }
    a->last_add_tick = 0u;
    memset(&a->owed, 0, sizeof(a->owed));
}

d_bool dg_accum_is_empty(const dg_accum *a) {
    if (!a) {
        return D_TRUE;
    }
    switch (a->type) {
        case DG_ACCUM_SCALAR_Q32_32: return (a->owed.scalar == 0) ? D_TRUE : D_FALSE;
        case DG_ACCUM_VEC3_Q32_32: return (a->owed.vec3.x == 0 && a->owed.vec3.y == 0 && a->owed.vec3.z == 0) ? D_TRUE : D_FALSE;
        case DG_ACCUM_COUNT_I64: return (a->owed.count == 0) ? D_TRUE : D_FALSE;
        default: break;
    }
    return D_TRUE;
}

void dg_accum_add(dg_accum *a, dg_accum_value delta, dg_tick tick) {
    if (!a) {
        return;
    }
    a->last_add_tick = tick;
    switch (a->type) {
        case DG_ACCUM_SCALAR_Q32_32:
            a->owed.scalar = (q32_32)(a->owed.scalar + delta.scalar);
            break;
        case DG_ACCUM_VEC3_Q32_32:
            a->owed.vec3.x = (q32_32)(a->owed.vec3.x + delta.vec3.x);
            a->owed.vec3.y = (q32_32)(a->owed.vec3.y + delta.vec3.y);
            a->owed.vec3.z = (q32_32)(a->owed.vec3.z + delta.vec3.z);
            break;
        case DG_ACCUM_COUNT_I64:
            a->owed.count = (i64)(a->owed.count + delta.count);
            break;
        default:
            break;
    }
}

u32 dg_accum_apply(dg_accum *a, dg_accum_apply_fn apply_fn, void *user_ctx, u32 max_units, u32 *budget_units) {
    u32 used = 0u;

    if (!a || !apply_fn || !budget_units) {
        return 0u;
    }
    if (max_units == 0u) {
        return 0u;
    }

    while (used < max_units && *budget_units > 0u) {
        dg_accum_value delta;
        d_bool unit_zero;

        if (dg_accum_is_empty(a)) {
            break;
        }

        memset(&delta, 0, sizeof(delta));
        unit_zero = dg_accum_unit_is_zero(a->type, &a->unit);

        if (unit_zero) {
            /* Apply everything in one unit. */
            delta = a->owed;
        } else {
            switch (a->type) {
                case DG_ACCUM_SCALAR_Q32_32: {
                    u64 max_abs = dg_abs_i64_u64((i64)a->unit.scalar);
                    delta.scalar = (q32_32)dg_clamp_abs_i64((i64)a->owed.scalar, max_abs);
                } break;
                case DG_ACCUM_VEC3_Q32_32: {
                    u64 max_abs_x = dg_abs_i64_u64((i64)a->unit.vec3.x);
                    u64 max_abs_y = dg_abs_i64_u64((i64)a->unit.vec3.y);
                    u64 max_abs_z = dg_abs_i64_u64((i64)a->unit.vec3.z);
                    delta.vec3.x = (q32_32)dg_clamp_abs_i64((i64)a->owed.vec3.x, max_abs_x);
                    delta.vec3.y = (q32_32)dg_clamp_abs_i64((i64)a->owed.vec3.y, max_abs_y);
                    delta.vec3.z = (q32_32)dg_clamp_abs_i64((i64)a->owed.vec3.z, max_abs_z);
                } break;
                case DG_ACCUM_COUNT_I64: {
                    u64 max_abs_c = dg_abs_i64_u64(a->unit.count);
                    delta.count = dg_clamp_abs_i64(a->owed.count, max_abs_c);
                } break;
                default:
                    delta = a->owed;
                    break;
            }
        }

        apply_fn(user_ctx, a->type, delta);

        /* Subtract what was applied (lossless; remainder stays). */
        switch (a->type) {
            case DG_ACCUM_SCALAR_Q32_32:
                a->owed.scalar = (q32_32)(a->owed.scalar - delta.scalar);
                break;
            case DG_ACCUM_VEC3_Q32_32:
                a->owed.vec3.x = (q32_32)(a->owed.vec3.x - delta.vec3.x);
                a->owed.vec3.y = (q32_32)(a->owed.vec3.y - delta.vec3.y);
                a->owed.vec3.z = (q32_32)(a->owed.vec3.z - delta.vec3.z);
                break;
            case DG_ACCUM_COUNT_I64:
                a->owed.count = (i64)(a->owed.count - delta.count);
                break;
            default:
                break;
        }

        *budget_units -= 1u;
        used += 1u;

        if (unit_zero) {
            /* Applied everything; done. */
            break;
        }
    }

    return used;
}

