#ifndef DOMINO_LAUNCHER_H_INCLUDED
#define DOMINO_LAUNCHER_H_INCLUDED

#include "domino/launcher_config.h"
#include "domino/launcher_profile.h"
#include "domino/launcher_mods.h"
#include "domino/launcher_process.h"

#ifdef __cplusplus
extern "C" {
#endif

int launcher_init(const launcher_config* cfg);
int launcher_run(void);
void launcher_shutdown(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_LAUNCHER_H_INCLUDED */
