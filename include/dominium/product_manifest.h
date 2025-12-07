#ifndef DOMINIUM_PRODUCT_MANIFEST_H
#define DOMINIUM_PRODUCT_MANIFEST_H

#include "domino/version.h"

typedef struct dominium_product_desc {
    char          id[64];
    domino_semver version;
    int           content_api;
    int           launcher_content_api;
    int           launcher_ext_api;
} dominium_product_desc;

#ifdef __cplusplus
extern "C" {
#endif

/* Load from a TOML-like file on disk. Returns 0 on success. */
int dominium_product_load(const char* path, dominium_product_desc* out);

#ifdef __cplusplus
}
#endif

#endif
