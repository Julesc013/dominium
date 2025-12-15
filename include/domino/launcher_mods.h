#ifndef DOMINO_LAUNCHER_MODS_H_INCLUDED
#define DOMINO_LAUNCHER_MODS_H_INCLUDED

#include "domino/baseline.h"
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct launcher_mod_meta {
    char id[64];
    char name[96];
    char version[32];
    int  priority;
    int  enabled;
} launcher_mod_meta;

int launcher_mods_scan(const char* path);
int launcher_mods_get(int index, launcher_mod_meta* out);
int launcher_mods_count(void);
int launcher_mods_set_enabled(const char* id, int enabled);
int launcher_mods_resolve_order(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_LAUNCHER_MODS_H_INCLUDED */
