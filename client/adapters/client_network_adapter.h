#ifndef DOMINIUM_CLIENT_NETWORK_ADAPTER_H
#define DOMINIUM_CLIENT_NETWORK_ADAPTER_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum client_discovery_provider_status_e {
    CLIENT_DISCOVERY_PROVIDER_OK = 0,
    CLIENT_DISCOVERY_PROVIDER_REFUSED = 1
} client_discovery_provider_status;

client_discovery_provider_status client_network_provider_saved(void);
client_discovery_provider_status client_network_provider_manual(void);
client_discovery_provider_status client_network_provider_lan(void);
client_discovery_provider_status client_network_provider_directory_official(void);
client_discovery_provider_status client_network_provider_directory_custom(void);
const char* client_network_provider_refusal_code(client_discovery_provider_status status);

#ifdef __cplusplus
}
#endif

#endif
