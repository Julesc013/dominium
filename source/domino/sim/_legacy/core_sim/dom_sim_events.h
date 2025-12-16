/*
FILE: source/domino/sim/_legacy/core_sim/dom_sim_events.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/_legacy/core_sim/dom_sim_events
RESPONSIBILITY: Implements `dom_sim_events`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SIM_EVENTS_H
#define DOM_SIM_EVENTS_H

#include "dom_core_types.h"
#include "dom_core_err.h"
#include "dom_core_id.h"
#include "dom_sim_tick.h"

#define DOM_SIM_MESSAGE_PAYLOAD_BYTES 112

typedef dom_u16 DomSimMsgType;
typedef dom_u16 DomSimMsgFlags;

typedef struct DomSimMessageHeader {
    DomSimMsgType  type;
    DomSimMsgFlags flags;
    dom_u32        system_id;
    dom_entity_id  sender;
    dom_entity_id  receiver;
    DomTickId      tick_created;
} DomSimMessageHeader;

typedef struct DomSimMessage {
    DomSimMessageHeader header;
    dom_u8              payload[DOM_SIM_MESSAGE_PAYLOAD_BYTES];
} DomSimMessage;

typedef dom_u16 DomCommandType;

typedef struct DomSimCommand {
    DomCommandType type;
    dom_entity_id  entity;
    dom_u32        param_a;
    dom_u32        param_b;
    dom_u64        data[2];
} DomSimCommand;

dom_err_t dom_sim_events_init(void);
void      dom_sim_events_reset(void);

dom_err_t dom_sim_events_local_emit(dom_entity_id entity, const DomSimMessage *msg);
dom_err_t dom_sim_events_local_consume(dom_entity_id entity, DomSimMessage *out_msg);

dom_err_t dom_sim_events_lane_emit(DomLaneId lane, const DomSimMessage *msg);
dom_err_t dom_sim_events_lane_consume(DomLaneId lane, DomSimMessage *out_msg);

dom_err_t dom_sim_events_cross_emit(DomLaneId target_lane, const DomSimMessage *msg);
dom_err_t dom_sim_events_global_emit(const DomSimMessage *msg);

void dom_sim_events_phase_pre_state(void);
void dom_sim_events_phase_merge(void);
void dom_sim_events_phase_finalize(void);

dom_err_t dom_sim_command_emit(DomLaneId lane, const DomSimCommand *cmd);
void      dom_sim_command_drain_for_lane(DomLaneId lane);

#endif /* DOM_SIM_EVENTS_H */
