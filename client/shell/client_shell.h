/*
Client shell core (world creation, save/load, navigation).
*/
#ifndef DOMINIUM_CLIENT_SHELL_H
#define DOMINIUM_CLIENT_SHELL_H

#include <stddef.h>
#include <stdint.h>

#include "dominium/app/ui_event_log.h"
#include "dominium/physical/local_processes.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_SHELL_MAX_TEMPLATES 8u
#define DOM_SHELL_MAX_TEMPLATE_ID 96u
#define DOM_SHELL_MAX_TEMPLATE_DESC 160u
#define DOM_SHELL_MAX_TEMPLATE_VERSION 16u

#define DOM_SHELL_MAX_POLICIES 8u
#define DOM_SHELL_POLICY_ID_MAX 64u

#define DOM_SHELL_STATUS_MAX 160u

#define DOM_SHELL_MAX_EVENTS 64u
#define DOM_SHELL_EVENT_MAX 160u

#define DOM_SHELL_WORLDDEF_MAX 65536u
#define DOM_SHELL_FIELD_MAX 8u
#define DOM_SHELL_FIELD_GRID_W 1u
#define DOM_SHELL_FIELD_GRID_H 1u
#define DOM_SHELL_INTENT_MAX 160u

#define DOM_SHELL_SAVE_HEADER "DOMINIUM_SAVE_V1"
#define DOM_SHELL_REPLAY_HEADER "DOMINIUM_REPLAY_V1"

#define DOM_SHELL_WORLDDEF_SCHEMA_ID "dominium.schema.world_definition"
#define DOM_SHELL_WORLDDEF_SCHEMA_VERSION 1u

#define DOM_SHELL_AUTH_POLICY "policy.authority.shell"
#define DOM_SHELL_MODE_FREE "policy.mode.nav.free"
#define DOM_SHELL_MODE_ORBIT "policy.mode.nav.orbit"
#define DOM_SHELL_MODE_SURFACE "policy.mode.nav.surface"

typedef struct dom_shell_policy_set {
    char items[DOM_SHELL_MAX_POLICIES][DOM_SHELL_POLICY_ID_MAX];
    uint32_t count;
} dom_shell_policy_set;

typedef struct dom_shell_template {
    char template_id[DOM_SHELL_MAX_TEMPLATE_ID];
    char version[DOM_SHELL_MAX_TEMPLATE_VERSION];
    char description[DOM_SHELL_MAX_TEMPLATE_DESC];
    char source[16];
} dom_shell_template;

typedef struct dom_shell_registry {
    dom_shell_template templates[DOM_SHELL_MAX_TEMPLATES];
    uint32_t count;
} dom_shell_registry;

typedef struct dom_shell_world_summary {
    char worlddef_id[DOM_SHELL_MAX_TEMPLATE_ID];
    char template_id[DOM_SHELL_MAX_TEMPLATE_ID];
    uint32_t schema_version;
    char spawn_node_id[DOM_SHELL_MAX_TEMPLATE_ID];
    char spawn_frame_id[DOM_SHELL_MAX_TEMPLATE_ID];
    double spawn_pos[3];
    double spawn_orient[3];
    dom_shell_policy_set movement;
    dom_shell_policy_set authority;
    dom_shell_policy_set mode;
    dom_shell_policy_set debug;
} dom_shell_world_summary;

typedef struct dom_shell_world_state {
    int active;
    char active_mode[DOM_SHELL_POLICY_ID_MAX];
    char current_node_id[DOM_SHELL_MAX_TEMPLATE_ID];
    double position[3];
    double orientation[3];
    uint64_t worlddef_hash;
    size_t worlddef_len;
    char worlddef_json[DOM_SHELL_WORLDDEF_MAX];
    dom_shell_world_summary summary;
} dom_shell_world_state;

typedef struct dom_shell_event_ring {
    char lines[DOM_SHELL_MAX_EVENTS][DOM_SHELL_EVENT_MAX];
    uint32_t head;
    uint32_t count;
    uint32_t seq;
} dom_shell_event_ring;

typedef struct dom_shell_field_state {
    dom_field_storage objective;
    dom_field_storage subjective;
    dom_field_layer objective_layers[DOM_SHELL_FIELD_MAX];
    dom_field_layer subjective_layers[DOM_SHELL_FIELD_MAX];
    i32 objective_values[DOM_SHELL_FIELD_MAX][DOM_SHELL_FIELD_GRID_W * DOM_SHELL_FIELD_GRID_H];
    i32 subjective_values[DOM_SHELL_FIELD_MAX][DOM_SHELL_FIELD_GRID_W * DOM_SHELL_FIELD_GRID_H];
    u32 field_ids[DOM_SHELL_FIELD_MAX];
    u32 field_count;
    u32 knowledge_mask;
    u32 confidence_q16;
    u32 uncertainty_q16;
} dom_shell_field_state;

typedef struct dom_shell_structure_state {
    dom_local_structure_state structure;
    dom_assembly assembly;
    dom_assembly_part parts[4];
    dom_assembly_connection connections[4];
    dom_volume_claim_registry claims;
    dom_volume_claim claim_storage[4];
    dom_network_graph network;
    dom_network_node nodes[4];
    dom_network_edge edges[4];
} dom_shell_structure_state;

typedef struct dom_client_shell {
    dom_shell_registry registry;
    dom_shell_world_state world;
    dom_shell_event_ring events;
    dom_shell_field_state fields;
    dom_shell_structure_state structure;
    dom_shell_policy_set create_movement;
    dom_shell_policy_set create_authority;
    dom_shell_policy_set create_mode;
    dom_shell_policy_set create_debug;
    uint32_t create_template_index;
    uint64_t create_seed;
    uint32_t tick;
    char last_status[DOM_SHELL_STATUS_MAX];
    char last_refusal_code[32];
    char last_refusal_detail[DOM_SHELL_STATUS_MAX];
    char last_intent[DOM_SHELL_INTENT_MAX];
    char last_plan[DOM_SHELL_INTENT_MAX];
    uint64_t next_intent_id;
    uint64_t rng_seed;
} dom_client_shell;

void dom_client_shell_init(dom_client_shell* shell);
void dom_client_shell_reset(dom_client_shell* shell);
void dom_client_shell_tick(dom_client_shell* shell);

const dom_shell_registry* dom_client_shell_registry(const dom_client_shell* shell);
const dom_shell_world_state* dom_client_shell_world(const dom_client_shell* shell);
const dom_shell_event_ring* dom_client_shell_events(const dom_client_shell* shell);

int dom_client_shell_set_create_seed(dom_client_shell* shell, uint64_t seed);
int dom_client_shell_set_create_template(dom_client_shell* shell, uint32_t index);
int dom_client_shell_set_create_policy(dom_client_shell* shell, const char* set_name, const char* csv);

int dom_client_shell_create_world(dom_client_shell* shell,
                                  dom_app_ui_event_log* log,
                                  char* status,
                                  size_t status_cap,
                                  int emit_text);
int dom_client_shell_save_world(dom_client_shell* shell,
                                const char* path,
                                dom_app_ui_event_log* log,
                                char* status,
                                size_t status_cap,
                                int emit_text);
int dom_client_shell_load_world(dom_client_shell* shell,
                                const char* path,
                                dom_app_ui_event_log* log,
                                char* status,
                                size_t status_cap,
                                int emit_text);
int dom_client_shell_inspect_replay(dom_client_shell* shell,
                                    const char* path,
                                    dom_app_ui_event_log* log,
                                    char* status,
                                    size_t status_cap,
                                    int emit_text);
int dom_client_shell_set_mode(dom_client_shell* shell,
                              const char* mode_id,
                              dom_app_ui_event_log* log,
                              char* status,
                              size_t status_cap,
                              int emit_text);
int dom_client_shell_move(dom_client_shell* shell, double dx, double dy, double dz,
                          dom_app_ui_event_log* log);

int dom_client_shell_execute(dom_client_shell* shell,
                             const char* cmdline,
                             dom_app_ui_event_log* log,
                             char* status,
                             size_t status_cap,
                             int emit_text);

void dom_client_shell_event_lines(const dom_shell_event_ring* ring,
                                  char* lines,
                                  size_t line_cap,
                                  size_t line_stride,
                                  int* out_count);

void dom_client_shell_policy_to_csv(const dom_shell_policy_set* set,
                                    char* out,
                                    size_t out_cap);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_CLIENT_SHELL_H */
