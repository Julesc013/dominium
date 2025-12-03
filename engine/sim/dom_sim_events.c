#include "dom_sim_events.h"
#include <string.h>

static DomSimMessage g_queue[DOM_SIM_EVENT_QUEUE_SIZE];
static dom_u32 g_head = 0;
static dom_u32 g_tail = 0;
static dom_u32 g_count = 0;

dom_err_t dom_sim_events_init(void)
{
    g_head = g_tail = g_count = 0;
    memset(g_queue, 0, sizeof(g_queue));
    return DOM_OK;
}

dom_err_t dom_sim_events_emit(const DomSimMessage *msg)
{
    if (!msg) return DOM_ERR_INVALID_ARG;
    if (g_count >= DOM_SIM_EVENT_QUEUE_SIZE) return DOM_ERR_BOUNDS;
    g_queue[g_tail] = *msg;
    g_tail = (g_tail + 1) % DOM_SIM_EVENT_QUEUE_SIZE;
    g_count++;
    return DOM_OK;
}

dom_err_t dom_sim_events_consume(DomSimMessage *out_msg)
{
    if (!out_msg) return DOM_ERR_INVALID_ARG;
    if (g_count == 0) return DOM_ERR_NOT_FOUND;
    *out_msg = g_queue[g_head];
    g_head = (g_head + 1) % DOM_SIM_EVENT_QUEUE_SIZE;
    g_count--;
    return DOM_OK;
}
