#ifndef DOMINIUM_CLIENT_COMMANDS_REGISTRY_H
#define DOMINIUM_CLIENT_COMMANDS_REGISTRY_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define CLIENT_CMD_MODE_CLI 1u
#define CLIENT_CMD_MODE_TUI 2u
#define CLIENT_CMD_MODE_GUI 4u

typedef struct client_command_desc_t {
    const char* command_id;
    const char* const* required_capabilities;
    u32 required_capability_count;
    const char* epistemic_scope;
    const char* const* refusal_codes;
    u32 refusal_code_count;
    u32 mode_mask;
} client_command_desc;

const client_command_desc* client_command_registry(u32* out_count);
const client_command_desc* client_command_find(const char* command_id);
int client_command_mode_available(const client_command_desc* cmd, const char* mode_id);
int client_command_capabilities_allowed(const client_command_desc* cmd,
                                        const char* const* capability_ids,
                                        u32 capability_count);

#ifdef __cplusplus
}
#endif

#endif
