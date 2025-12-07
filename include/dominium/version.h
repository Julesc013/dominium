#ifndef DOMINIUM_VERSION_H
#define DOMINIUM_VERSION_H

#include "domino/version.h"

#define DOMINIUM_VERSION_MAJOR 0
#define DOMINIUM_VERSION_MINOR 1
#define DOMINIUM_VERSION_PATCH 0
#define DOMINIUM_VERSION_SEMVER "0.1.0"

/* Legacy compatibility macros */
#ifndef DOM_VERSION_SEMVER
#define DOM_VERSION_SEMVER DOMINIUM_VERSION_SEMVER
#endif
#define DOM_PRODUCT_LAUNCHER 1
#define DOM_PRODUCT_SETUP    2
#define DOM_PRODUCT_GAME     3

#define DOMINIUM_GAME_ID     "dominium.game"
#define DOMINIUM_LAUNCHER_ID "dominium.launcher"

#ifdef __cplusplus
extern "C" {
#endif

void dominium_game_get_version(domino_semver* out);
void dominium_launcher_get_version(domino_semver* out);

int dominium_game_get_content_api(void);
int dominium_launcher_get_content_api(void);
int dominium_launcher_get_ext_api(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_VERSION_H */
