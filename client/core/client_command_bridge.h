#ifndef DOMINIUM_CLIENT_COMMAND_BRIDGE_H
#define DOMINIUM_CLIENT_COMMAND_BRIDGE_H

#include <stddef.h>

#include "client_commands_registry.h"
#include "client_state_machine.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum client_command_bridge_result_e {
    CLIENT_COMMAND_BRIDGE_NOT_CANONICAL = 0,
    CLIENT_COMMAND_BRIDGE_REWRITTEN = 1,
    CLIENT_COMMAND_BRIDGE_SYNTHETIC_OK = 2,
    CLIENT_COMMAND_BRIDGE_REFUSED = 3
} client_command_bridge_result;

client_command_bridge_result client_command_bridge_prepare(const char* raw_cmd,
                                                           char* out_cmd,
                                                           size_t out_cap,
                                                           char* out_message,
                                                           size_t out_message_cap,
                                                           const char* const* capability_ids,
                                                           u32 capability_count,
                                                           client_state_machine* state_machine);

#ifdef __cplusplus
}
#endif

#endif
