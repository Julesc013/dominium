#include "sim/lod/dg_rep.h"

d_bool dg_rep_state_is_valid(dg_rep_state s) {
    return (s >= DG_REP_R0_FULL && s < DG_REP_COUNT) ? D_TRUE : D_FALSE;
}

const char *dg_rep_state_name(dg_rep_state s) {
    switch (s) {
        case DG_REP_R0_FULL: return "R0_FULL";
        case DG_REP_R1_LITE: return "R1_LITE";
        case DG_REP_R2_AGG: return "R2_AGG";
        case DG_REP_R3_DORMANT: return "R3_DORMANT";
        default: break;
    }
    return "R?_INVALID";
}

