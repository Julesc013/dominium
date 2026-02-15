/*
FILE: client/presentation/ui_host_v1.c
MODULE: Dominium
LAYER / SUBSYSTEM: Client / presentation
RESPONSIBILITY: Minimal descriptor-driven tool UI host implementation.
ALLOWED DEPENDENCIES: ui_host_v1.h only.
FORBIDDEN DEPENDENCIES: TruthModel headers and direct authoritative mutation APIs.
DETERMINISM: Output intent IDs and process IDs are stable for identical action requests.
*/
#include "ui_host_v1.h"

static const char* dom_ui_default_payload_json(void)
{
    return "{}";
}

int dom_ui_host_build_snapshot_v1(const dom_perceived_model_v1* perceived,
                                  const dom_render_model_v1* render_model,
                                  dom_ui_host_snapshot_v1* out_snapshot)
{
    (void)render_model;
    if (!perceived || !out_snapshot) {
        return -1;
    }
    out_snapshot->schema_version = "1.0.0";
    out_snapshot->windows = 0;
    out_snapshot->window_count = 0u;
    return 0;
}

int dom_ui_host_emit_intent_v1(const dom_ui_action_request_v1* request,
                               dom_ui_intent_v1* out_intent)
{
    if (!request || !out_intent) {
        return -1;
    }
    out_intent->intent_id = request->window_id ? request->window_id : "";
    out_intent->process_id = request->widget_id ? request->widget_id : "";
    out_intent->payload_json = dom_ui_default_payload_json();
    return 0;
}
