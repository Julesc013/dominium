/*
Stub setup core implementation.
*/
#include "dsk/dsk_setup.h"
#include "dom_contracts/version.h"

const char* dsk_setup_version(void)
{
    return DOMINIUM_SETUP_VERSION;
}

int dsk_setup_status(void)
{
    return 0;
}
