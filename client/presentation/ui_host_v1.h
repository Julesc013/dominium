/*
FILE: client/presentation/ui_host_v1.h
MODULE: Dominium
LAYER / SUBSYSTEM: Client / presentation
RESPONSIBILITY: Descriptor-driven tool UI host contract bound to PerceivedModel-only data.
ALLOWED DEPENDENCIES: perceived_model_v1.h and render_model_v1.h.
FORBIDDEN DEPENDENCIES: domino/truth_model_v1.h.
DETERMINISM: Intent mapping from descriptor+selection+widget-state is deterministic.
*/
#ifndef DOMINIUM_CLIENT_PRESENTATION_UI_HOST_V1_H
#define DOMINIUM_CLIENT_PRESENTATION_UI_HOST_V1_H

#include "perceived_model_v1.h"
#include "render_model_v1.h"

typedef struct dom_ui_window_ref_v1 {
    const char* window_id;
    const char* title;
    const char* descriptor_path;
} dom_ui_window_ref_v1;

typedef struct dom_ui_intent_v1 {
    const char* intent_id;
    const char* process_id;
    const char* payload_json;
} dom_ui_intent_v1;

typedef struct dom_ui_action_request_v1 {
    const char* window_id;
    const char* widget_id;
    const char* selection_json;
    const char* widget_state_json;
    u32 action_sequence;
} dom_ui_action_request_v1;

typedef struct dom_ui_host_snapshot_v1 {
    const char* schema_version;
    const dom_ui_window_ref_v1* windows;
    u32 window_count;
} dom_ui_host_snapshot_v1;

int dom_ui_host_build_snapshot_v1(const dom_perceived_model_v1* perceived,
                                  const dom_render_model_v1* render_model,
                                  dom_ui_host_snapshot_v1* out_snapshot);

int dom_ui_host_emit_intent_v1(const dom_ui_action_request_v1* request,
                               dom_ui_intent_v1* out_intent);

#endif /* DOMINIUM_CLIENT_PRESENTATION_UI_HOST_V1_H */
