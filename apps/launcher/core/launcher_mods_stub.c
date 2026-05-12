/*
Stub launcher mods API.
*/
#include "launcher/launcher_mods.h"

#include <string.h>

int launcher_mods_scan(const char* path)
{
    (void)path;
    return 0;
}

int launcher_mods_get(int index, launcher_mod_meta* out)
{
    (void)index;
    if (out) {
        memset(out, 0, sizeof(*out));
    }
    return -1;
}

int launcher_mods_count(void)
{
    return 0;
}

int launcher_mods_set_enabled(const char* id, int enabled)
{
    (void)id;
    (void)enabled;
    return -1;
}

int launcher_mods_resolve_order(void)
{
    return 0;
}
