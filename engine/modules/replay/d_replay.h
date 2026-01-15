/*
FILE: source/domino/replay/d_replay.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / replay/d_replay
RESPONSIBILITY: Defines internal contract for `d_replay`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic replay/record subsystem (C89). */
#ifndef D_REPLAY_H
#define D_REPLAY_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"
#include "net/d_net.h"
#include "sim/d_sim_hash.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_replay_id;

typedef struct dreplay_frame {
    u32 tick_index;
    u32 input_count;
    /* For now, directly reuse network input frames. */
    d_net_input_frame *inputs;
} dreplay_frame;

typedef enum dreplay_mode_e {
    DREPLAY_MODE_OFF = 0,
    DREPLAY_MODE_RECORD,
    DREPLAY_MODE_PLAYBACK
} dreplay_mode;

typedef struct d_replay_context {
    dreplay_mode mode;
    u32          determinism_mode; /* 0=off,1=record,2=playback,3=assert-only */
    d_world_hash last_hash;

    /* For RECORD: dynamic array of frames; for PLAYBACK: read-only pointer. */
    dreplay_frame *frames;
    u32            frame_count;
    u32            frame_capacity;

    u32            cursor;       /* current frame index for playback */
} d_replay_context;

/* Initialize a replay context in RECORD or PLAYBACK mode. */
int d_replay_init_record(d_replay_context *ctx, u32 initial_capacity);
int d_replay_init_playback(d_replay_context *ctx, dreplay_frame *frames, u32 frame_count);
void d_replay_shutdown(d_replay_context *ctx);

/* Record inputs for a tick. */
int d_replay_record_frame(
    d_replay_context        *ctx,
    u32                      tick_index,
    const d_net_input_frame *inputs,
    u32                      input_count
);

/* Get inputs for a tick during playback. */
int d_replay_get_frame(
    d_replay_context  *ctx,
    u32                tick_index,
    d_net_input_frame *out_inputs,
    u32               *in_out_input_count
);

/* Serialize replay to TLV and parse it back. */
int d_replay_serialize(
    const d_replay_context *ctx,
    d_tlv_blob             *out
);

int d_replay_deserialize(
    const d_tlv_blob *in,
    d_replay_context *out_ctx
);

/* Subsystem registration hook. */
void d_replay_register_subsystem(void);

#ifdef __cplusplus
}
#endif

#endif /* D_REPLAY_H */
