#ifndef DOMINIUM_LAUNCHER_MODEL_H
#define DOMINIUM_LAUNCHER_MODEL_H

#include "domino/mod.h"
#include "dominium_launcher_core.h"

typedef struct dominium_launcher_instance_view {
    char id[64];
    char label[128];
    char product_id[64];
    domino_semver product_version;
    unsigned int mod_count;
    unsigned int pack_count;
    int compatible;
} dominium_launcher_instance_view;

int dominium_launcher_build_views(dominium_launcher_context* ctx,
                                  dominium_launcher_instance_view* out,
                                  unsigned int max_count,
                                  unsigned int* out_count);

#endif
