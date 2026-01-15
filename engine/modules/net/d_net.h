/*
FILE: source/domino/net/d_net.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / net/d_net
RESPONSIBILITY: Defines internal contract for `d_net`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic networking stubs (C89). */
#ifndef D_NET_H
#define D_NET_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_net_profile_id;

typedef struct d_proto_net_profile {
    d_net_profile_id id;
    const char      *name;

    u32              mode;   /* LOCKSTEP, CLIENT_SERVER, etc. */
    u32              flags;  /* AUTH_REQUIRED, SECURE, etc. */

    d_tlv_blob       params; /* tick rate, max peers, etc. */
} d_proto_net_profile;

/* Input frame type – used for lockstep simulation. */
typedef struct d_net_input_frame {
    u32   tick_index;
    u32   player_id;
    u32   payload_size;
    u8   *payload;       /* pointer to opaque command data; encoded by higher layers */
} d_net_input_frame;

/*
 * High-level net API:
 * For this prompt, only a lockstep-friendly interface is implemented.
 */

typedef struct d_net_context {
    d_net_profile_id profile_id;
    u32              local_player_id;
    u32              peer_count;
    /* Implementation-private fields in d_net.c */
} d_net_context;

/* Initialize network context for a given profile. */
int d_net_init(d_net_context *ctx, d_net_profile_id profile_id);

/* Shutdown network context. */
void d_net_shutdown(d_net_context *ctx);

/*
 * Submit local inputs for a tick and retrieve the authoritative combined input frame list.
 * For a simple lockstep model, this echoes local input as authoritative in single-player.
 */
int d_net_step_lockstep(
    d_net_context           *ctx,
    const d_net_input_frame *local_inputs,
    u32                      local_input_count,
    d_net_input_frame       *out_frames,
    u32                     *in_out_frame_count
);

/* Register subsystem hooks (tick/serialize stubs). */
void d_net_register_subsystem(void);

#ifdef __cplusplus
}
#endif

#endif /* D_NET_H */
