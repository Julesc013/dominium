#include "valid_c17_header.h"

int main(void)
{
    domino_test_config_t config;
    config.struct_size = (unsigned int)sizeof(config);
    config.api_version = 1u;
    config.user = 0;
    return config.struct_size == 0u;
}
