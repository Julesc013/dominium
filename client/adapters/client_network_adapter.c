#include "client_network_adapter.h"

client_discovery_provider_status client_network_provider_saved(void)
{
    return CLIENT_DISCOVERY_PROVIDER_OK;
}

client_discovery_provider_status client_network_provider_manual(void)
{
    return CLIENT_DISCOVERY_PROVIDER_OK;
}

client_discovery_provider_status client_network_provider_lan(void)
{
    return CLIENT_DISCOVERY_PROVIDER_REFUSED;
}

client_discovery_provider_status client_network_provider_directory_official(void)
{
    return CLIENT_DISCOVERY_PROVIDER_REFUSED;
}

client_discovery_provider_status client_network_provider_directory_custom(void)
{
    return CLIENT_DISCOVERY_PROVIDER_REFUSED;
}

const char* client_network_provider_refusal_code(client_discovery_provider_status status)
{
    return status == CLIENT_DISCOVERY_PROVIDER_OK ? "ok" : "REFUSE_PROVIDER_UNAVAILABLE";
}
