/*
FILE: source/domino/net/d_net.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / net/d_net
RESPONSIBILITY: Implements `d_net`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>
#include <string.h>

#include "d_net.h"
#include "d_net_cmd.h"
#include "d_net_schema.h"
#include "core/d_subsystem.h"
#include "world/d_world.h"

static int g_net_registered = 0;

static void d_net_tick_stub(d_world *w, u32 ticks) {
    (void)w;
    (void)ticks;
}

static int d_net_save_instance_stub(d_world *w, d_tlv_blob *out) {
    (void)w;
    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    return 0;
}

static int d_net_load_instance_stub(d_world *w, const d_tlv_blob *in) {
    (void)w;
    (void)in;
    return 0;
}

static void d_net_register_models_stub(void) {
}

static void d_net_load_protos_stub(const d_tlv_blob *blob) {
    (void)blob;
}

void d_net_register_subsystem(void) {
    d_subsystem_desc desc;
    const d_subsystem_desc *existing;
    int rc;

    if (g_net_registered) {
        return;
    }

    /* Schema registry is global; safe to call repeatedly. */
    d_net_register_schemas();
    (void)d_net_cmd_queue_init();

    existing = d_subsystem_get_by_id(D_SUBSYS_NET);
    if (existing) {
        g_net_registered = 1;
        return;
    }

    desc.subsystem_id = D_SUBSYS_NET;
    desc.name = "net";
    desc.version = 1u;
    desc.register_models = d_net_register_models_stub;
    desc.load_protos = d_net_load_protos_stub;
    desc.init_instance = (void (*)(d_world *))0;
    desc.tick = d_net_tick_stub;
    desc.save_chunk = (int (*)(d_world *, d_chunk *, d_tlv_blob *))0;
    desc.load_chunk = (int (*)(d_world *, d_chunk *, const d_tlv_blob *))0;
    desc.save_instance = d_net_save_instance_stub;
    desc.load_instance = d_net_load_instance_stub;

    rc = d_subsystem_register(&desc);
    if (rc == 0) {
        g_net_registered = 1;
    }
}

int d_net_init(d_net_context *ctx, d_net_profile_id profile_id) {
    if (!ctx) {
        return -1;
    }

    d_net_register_subsystem();

    memset(ctx, 0, sizeof(*ctx));
    ctx->profile_id = profile_id;
    ctx->local_player_id = 0u;
    ctx->peer_count = 0u;
    return 0;
}

void d_net_shutdown(d_net_context *ctx) {
    if (!ctx) {
        return;
    }
    ctx->profile_id = 0u;
    ctx->local_player_id = 0u;
    ctx->peer_count = 0u;
    d_net_cmd_queue_shutdown();
}

int d_net_step_lockstep(
    d_net_context           *ctx,
    const d_net_input_frame *local_inputs,
    u32                      local_input_count,
    d_net_input_frame       *out_frames,
    u32                     *in_out_frame_count
) {
    u32 copy_count;
    u32 i;
    if (!ctx || !in_out_frame_count) {
        return -1;
    }
    if (local_input_count > 0u && !local_inputs) {
        return -2;
    }

    copy_count = local_input_count;
    if (*in_out_frame_count < copy_count) {
        copy_count = *in_out_frame_count;
    }
    if (copy_count > 0u && !out_frames) {
        return -3;
    }

    for (i = 0u; i < copy_count; ++i) {
        out_frames[i] = local_inputs[i];
    }

    *in_out_frame_count = copy_count;
    (void)ctx;
    return 0;
}
