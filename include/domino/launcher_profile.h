#ifndef DOMINO_LAUNCHER_PROFILE_H_INCLUDED
#define DOMINO_LAUNCHER_PROFILE_H_INCLUDED

#include <stdint.h>
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct launcher_profile {
    char id[64];
    char name[96];
    char install_path[260];
    char modset[128];
} launcher_profile;

int   launcher_profile_load_all(void);
const launcher_profile* launcher_profile_get(int index);
int   launcher_profile_count(void);
int   launcher_profile_save(const launcher_profile* p);
int   launcher_profile_set_active(int index);
int   launcher_profile_get_active(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_LAUNCHER_PROFILE_H_INCLUDED */
