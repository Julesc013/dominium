#ifndef DOM_SIM_EVENTS_H
#define DOM_SIM_EVENTS_H

#include "dom_core_types.h"
#include "dom_core_err.h"
#include "dom_core_id.h"

#define DOM_SIM_EVENT_PAYLOAD_BYTES 112
#define DOM_SIM_EVENT_QUEUE_SIZE    256

typedef dom_u16 DomSimMsgType;
typedef dom_u16 DomSimMsgFlags;

typedef struct DomSimMessageHeader {
    DomSimMsgType  type;
    DomSimMsgFlags flags;
    dom_u32        system_id;
    dom_entity_id  sender;
    dom_entity_id  receiver;
    dom_u64        tick_created;
} DomSimMessageHeader;

typedef struct DomSimMessage {
    DomSimMessageHeader header;
    dom_u8              payload[DOM_SIM_EVENT_PAYLOAD_BYTES];
} DomSimMessage;

dom_err_t dom_sim_events_init(void);
dom_err_t dom_sim_events_emit(const DomSimMessage *msg);
dom_err_t dom_sim_events_consume(DomSimMessage *out_msg);

#endif /* DOM_SIM_EVENTS_H */
