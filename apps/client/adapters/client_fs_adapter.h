#ifndef DOMINIUM_CLIENT_FS_ADAPTER_H
#define DOMINIUM_CLIENT_FS_ADAPTER_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

int client_fs_resolve_root(char* out_path, size_t out_cap);
int client_fs_resolve_world_dir(char* out_path, size_t out_cap);

#ifdef __cplusplus
}
#endif

#endif
