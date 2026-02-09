#include "client_fs_adapter.h"

#include <stdlib.h>
#include <string.h>
#include <stdio.h>

int client_fs_resolve_root(char* out_path, size_t out_cap)
{
    const char* data_root = 0;
    if (!out_path || out_cap == 0u) {
        return 0;
    }
    out_path[0] = '\0';
    data_root = getenv("DOM_DATA_ROOT");
    if (!data_root || !data_root[0]) {
        data_root = "data";
    }
    if (strlen(data_root) >= out_cap) {
        return 0;
    }
    strcpy(out_path, data_root);
    return 1;
}

int client_fs_resolve_world_dir(char* out_path, size_t out_cap)
{
    char root[256];
    if (!out_path || out_cap == 0u) {
        return 0;
    }
    if (!client_fs_resolve_root(root, sizeof(root))) {
        return 0;
    }
    if (snprintf(out_path, out_cap, "%s/saves", root) < 0) {
        return 0;
    }
    return 1;
}
