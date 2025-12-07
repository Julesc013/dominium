#ifndef DOMINO_MOD_H
#define DOMINO_MOD_H

#include <stdint.h>
#include <stddef.h>
#include "domino/version.h"
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    DOMINO_PACKAGE_KIND_UNKNOWN = 0,
    DOMINO_PACKAGE_KIND_MOD,
    DOMINO_PACKAGE_KIND_PACK
} domino_package_kind;

typedef struct domino_package_id {
    char value[64];
} domino_package_id;

typedef struct domino_package_desc {
    char              id[64];
    domino_semver     version;
    domino_package_kind kind;
    char              path[260];
} domino_package_desc;

typedef struct domino_package_registry domino_package_registry;

typedef int (*domino_package_visit_fn)(const domino_package_desc* desc,
                                       void* user);

#define DOMINO_MAX_INSTANCE_MODS  32
#define DOMINO_MAX_INSTANCE_PACKS 32

typedef struct domino_instance_desc {
    char          id[64];
    char          label[128];
    char          product_id[64];
    domino_semver product_version;
    char          root_path[260];

    unsigned int  mod_count;
    char          mods_enabled[DOMINO_MAX_INSTANCE_MODS][64];

    unsigned int  pack_count;
    char          packs_enabled[DOMINO_MAX_INSTANCE_PACKS][64];
} domino_instance_desc;

typedef struct domino_resolve_error {
    char message[256];
} domino_resolve_error;

domino_package_registry* domino_package_registry_create(void);
void domino_package_registry_destroy(domino_package_registry* reg);
void domino_package_registry_set_sys(domino_package_registry* reg,
                                     domino_sys_context* sys);
int  domino_package_registry_scan_roots(domino_package_registry* reg,
                                        const char* const* roots,
                                        unsigned int root_count);
int  domino_package_registry_visit(domino_package_registry* reg,
                                   domino_package_visit_fn fn,
                                   void* user);
const domino_package_desc* domino_package_registry_find(domino_package_registry* reg,
                                                        const char* id);

int domino_manifest_load_from_file(const char* path,
                                   domino_package_desc* out);

int domino_instance_load(const char* path, domino_instance_desc* out);
int domino_instance_save(const char* path, const domino_instance_desc* inst);
int domino_instance_resolve(domino_package_registry* reg,
                            const domino_instance_desc* inst,
                            domino_resolve_error* out_err);

/* Legacy mod host stubs (kept for compatibility) */
typedef struct dm_mod_context dm_mod_context;

struct dm_mod_context {
    uint32_t placeholder;
};

dm_mod_context* dm_mod_create(void);
void            dm_mod_destroy(dm_mod_context* ctx);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_MOD_H */
