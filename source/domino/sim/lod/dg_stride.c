#include "sim/lod/dg_stride.h"

#include "core/dg_det_hash.h"

d_bool dg_stride_should_run(dg_tick tick, u64 stable_id, u32 stride) {
    u64 h;
    u64 s;
    if (stride <= 1u) {
        return D_TRUE;
    }
    h = dg_det_hash_u64(stable_id);
    s = (u64)stride;
    return (((tick + h) % s) == 0u) ? D_TRUE : D_FALSE;
}

