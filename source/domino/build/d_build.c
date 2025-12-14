/* Construction and placement API (C89).
 *
 * NOTE: In the refactor, BUILD is being converted to an anchor+pose contract:
 * authoritative placement is expressed as:
 *   - dg_anchor (parametric reference to authoring primitives)
 *   - dg_pose   local offset relative to the anchor
 *
 * No grid assumptions are permitted in engine logic.
 * No placement snapping lives here; snapping is UI-only.
 *
 * BUILD commit semantics are intentionally not implemented in this prompt.
 * This file only enforces schema expectations and participates in subsystem
 * registration/serialization scaffolding.
 */
#include "build/d_build.h"

#include <string.h>

#include "core/d_subsystem.h"
#include "core/dg_quant.h"

static int g_build_registered = 0;

static void dbuild_set_err(char *buf, u32 buf_size, const char *msg) {
    u32 i;
    if (!buf || buf_size == 0u) return;
    if (!msg) {
        buf[0] = '\0';
        return;
    }
    for (i = 0u; i + 1u < buf_size && msg[i] != '\0'; ++i) {
        buf[i] = msg[i];
    }
    buf[i] = '\0';
}

static d_bool dbuild_is_quantized(dg_q v, dg_q quantum) {
    if (quantum <= 0) return D_FALSE;
    return (((i64)v % (i64)quantum) == 0) ? D_TRUE : D_FALSE;
}

static d_bool dbuild_anchor_is_quantized(const dg_anchor *a) {
    if (!a) return D_FALSE;
    if (a->_pad32 != 0u) return D_FALSE;

    switch (a->kind) {
    case DG_ANCHOR_TERRAIN:
        return (dbuild_is_quantized(a->u.terrain.u, DG_QUANT_PARAM_DEFAULT_Q) &&
                dbuild_is_quantized(a->u.terrain.v, DG_QUANT_PARAM_DEFAULT_Q) &&
                dbuild_is_quantized(a->u.terrain.h, DG_QUANT_PARAM_DEFAULT_Q)) ? D_TRUE : D_FALSE;
    case DG_ANCHOR_CORRIDOR_TRANS:
        return (dbuild_is_quantized(a->u.corridor.s, DG_QUANT_PARAM_DEFAULT_Q) &&
                dbuild_is_quantized(a->u.corridor.t, DG_QUANT_PARAM_DEFAULT_Q) &&
                dbuild_is_quantized(a->u.corridor.h, DG_QUANT_PARAM_DEFAULT_Q) &&
                dbuild_is_quantized(a->u.corridor.roll, DG_QUANT_ANGLE_DEFAULT_Q)) ? D_TRUE : D_FALSE;
    case DG_ANCHOR_STRUCT_SURFACE:
        return (dbuild_is_quantized(a->u.struct_surface.u, DG_QUANT_PARAM_DEFAULT_Q) &&
                dbuild_is_quantized(a->u.struct_surface.v, DG_QUANT_PARAM_DEFAULT_Q) &&
                dbuild_is_quantized(a->u.struct_surface.offset, DG_QUANT_PARAM_DEFAULT_Q)) ? D_TRUE : D_FALSE;
    case DG_ANCHOR_ROOM_SURFACE:
        return (dbuild_is_quantized(a->u.room_surface.u, DG_QUANT_PARAM_DEFAULT_Q) &&
                dbuild_is_quantized(a->u.room_surface.v, DG_QUANT_PARAM_DEFAULT_Q) &&
                dbuild_is_quantized(a->u.room_surface.offset, DG_QUANT_PARAM_DEFAULT_Q)) ? D_TRUE : D_FALSE;
    case DG_ANCHOR_SOCKET:
        return dbuild_is_quantized(a->u.socket.param, DG_QUANT_PARAM_DEFAULT_Q);
    default:
        return D_FALSE;
    }
}

static d_bool dbuild_pose_is_quantized(const dg_pose *p) {
    if (!p) return D_FALSE;
    if (!dbuild_is_quantized(p->pos.x, DG_QUANT_POS_DEFAULT_Q)) return D_FALSE;
    if (!dbuild_is_quantized(p->pos.y, DG_QUANT_POS_DEFAULT_Q)) return D_FALSE;
    if (!dbuild_is_quantized(p->pos.z, DG_QUANT_POS_DEFAULT_Q)) return D_FALSE;

    /* Quaternion components are treated as quantized params. */
    if (!dbuild_is_quantized(p->rot.x, DG_QUANT_PARAM_DEFAULT_Q)) return D_FALSE;
    if (!dbuild_is_quantized(p->rot.y, DG_QUANT_PARAM_DEFAULT_Q)) return D_FALSE;
    if (!dbuild_is_quantized(p->rot.z, DG_QUANT_PARAM_DEFAULT_Q)) return D_FALSE;
    if (!dbuild_is_quantized(p->rot.w, DG_QUANT_PARAM_DEFAULT_Q)) return D_FALSE;

    if (!dbuild_is_quantized(p->incline, DG_QUANT_ANGLE_DEFAULT_Q)) return D_FALSE;
    if (!dbuild_is_quantized(p->roll, DG_QUANT_ANGLE_DEFAULT_Q)) return D_FALSE;
    return D_TRUE;
}

int d_build_validate(
    d_world               *w,
    const d_build_request *req,
    char                  *err_buf,
    u32                    err_buf_size
) {
    if (!w || !req) {
        dbuild_set_err(err_buf, err_buf_size, "invalid args");
        return -1;
    }

    if (req->kind != D_BUILD_KIND_STRUCTURE && req->kind != D_BUILD_KIND_SPLINE) {
        dbuild_set_err(err_buf, err_buf_size, "invalid kind");
        return -2;
    }

    if (req->anchor.kind == DG_ANCHOR_NONE) {
        dbuild_set_err(err_buf, err_buf_size, "missing anchor");
        return -3;
    }

    if (dbuild_anchor_is_quantized(&req->anchor) != D_TRUE ||
        dbuild_pose_is_quantized(&req->offset) != D_TRUE) {
        dbuild_set_err(err_buf, err_buf_size, "unquantized anchor/pose");
        return -4;
    }

    /* Semantic build validation is intentionally not implemented in this prompt. */
    dbuild_set_err(err_buf, err_buf_size, "");
    return 0;
}

int d_build_commit(
    d_world               *w,
    const d_build_request *req,
    u32                   *out_struct_eid
) {
    char err[128];
    if (out_struct_eid) *out_struct_eid = 0u;
    if (!w || !req) return -1;
    memset(err, 0, sizeof(err));
    if (d_build_validate(w, req, err, (u32)sizeof(err)) != 0) {
        return -2;
    }
    /* No authoritative BUILD commit in this prompt. */
    return -3;
}

int d_build_get_foundation_down(const d_world *w, u32 struct_id, q16_16 out_down[4]) {
    (void)w;
    (void)struct_id;
    if (out_down) {
        out_down[0] = 0;
        out_down[1] = 0;
        out_down[2] = 0;
        out_down[3] = 0;
    }
    return -1;
}

static int dbuild_save_chunk(d_world *w, d_chunk *chunk, d_tlv_blob *out) {
    (void)w;
    (void)chunk;
    if (!out) return -1;
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    return 0;
}

static int dbuild_load_chunk(d_world *w, d_chunk *chunk, const d_tlv_blob *in) {
    (void)w;
    (void)chunk;
    (void)in;
    return 0;
}

static int dbuild_save_instance(d_world *w, d_tlv_blob *out) {
    (void)w;
    if (!out) return -1;
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    return 0;
}

static int dbuild_load_instance(d_world *w, const d_tlv_blob *in) {
    (void)w;
    (void)in;
    return 0;
}

static void dbuild_register_models(void) { /* no-op */ }
static void dbuild_load_protos(const d_tlv_blob *blob) { (void)blob; }
static void dbuild_init_instance(d_world *w) { (void)w; }
static void dbuild_tick_stub(d_world *w, u32 ticks) { (void)w; (void)ticks; }

static const d_subsystem_desc g_build_subsystem = {
    D_SUBSYS_BUILD,
    "build",
    3u, /* bumped for anchor+pose contract */
    dbuild_register_models,
    dbuild_load_protos,
    dbuild_init_instance,
    dbuild_tick_stub,
    dbuild_save_chunk,
    dbuild_load_chunk,
    dbuild_save_instance,
    dbuild_load_instance
};

void d_build_register_subsystem(void) {
    if (g_build_registered) {
        return;
    }
    if (d_subsystem_register(&g_build_subsystem) == 0) {
        g_build_registered = 1;
    }
}

void d_build_shutdown(d_world *w) {
    (void)w;
}

