#ifndef DOMINIUM_SETUP_MODEL_H
#define DOMINIUM_SETUP_MODEL_H

#include "domino/version.h"

typedef struct dominium_installed_product {
    char          id[64];
    domino_semver version;
    int           content_api;
} dominium_installed_product;

int dominium_setup_list_installed(dominium_installed_product* out,
                                  unsigned int max_count,
                                  unsigned int* out_count);

#endif
