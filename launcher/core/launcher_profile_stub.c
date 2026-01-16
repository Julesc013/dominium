/*
Stub launcher profile storage.
*/
#include "launcher/launcher_profile.h"

#include <string.h>

int launcher_profile_load_all(void)
{
    return 0;
}

const launcher_profile* launcher_profile_get(int index)
{
    (void)index;
    return (const launcher_profile*)0;
}

int launcher_profile_count(void)
{
    return 0;
}

int launcher_profile_save(const launcher_profile* p)
{
    (void)p;
    return -1;
}

int launcher_profile_set_active(int index)
{
    (void)index;
    return -1;
}

int launcher_profile_get_active(void)
{
    return -1;
}
