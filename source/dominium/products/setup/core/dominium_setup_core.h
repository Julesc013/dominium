#ifndef DOMINIUM_SETUP_CORE_H
#define DOMINIUM_SETUP_CORE_H

#include "domino/version.h"

typedef enum {
    DOMINIUM_SETUP_MODE_INSTALL,
    DOMINIUM_SETUP_MODE_REPAIR,
    DOMINIUM_SETUP_MODE_UNINSTALL
} dominium_setup_mode;

typedef struct dominium_setup_plan {
    dominium_setup_mode mode;

    char install_root[260];

    char product_id[64];
    domino_semver product_version;
} dominium_setup_plan;

int dominium_setup_execute(const dominium_setup_plan* plan);

#endif
