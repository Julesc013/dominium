#ifndef DOMINO_MOD_H_INCLUDED
#define DOMINO_MOD_H_INCLUDED

#include <stdint.h>
#include <stddef.h>
#include "domino/core.h"
#include "domino/inst.h"
#include "domino/version.h"
#include "domino/sys.h"
#include "domino/canvas.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_mod_vtable {
    uint32_t api_version;
    void (*on_load)(dom_core* core);
    void (*on_unload)(void);
    void (*on_tick)(dom_core* core, double dt);
} dom_mod_vtable;

typedef bool (*dom_mod_get_vtable_fn)(dom_mod_vtable* out);

bool dom_mod_load_all(dom_core* core, dom_instance_id inst);
void dom_mod_unload_all(dom_core* core, dom_instance_id inst);

/*------------------------------------------------------------
 * Launcher extensions (opt-in from mods/packs)
 *------------------------------------------------------------*/
typedef struct dom_launcher_ext_v1 {
    uint32_t struct_size;
    uint32_t struct_version;

    void (*on_launcher_start)(dom_core* core);
    void (*on_register_views)(dom_core* core);
    int  (*on_action)(dom_core* core, const char* action_id, const char* payload);
    bool (*on_build_canvas)(dom_core* core,
                            dom_instance_id inst,
                            const char* canvas_id,
                            dom_gfx_buffer* out);
} dom_launcher_ext_v1;

typedef const dom_launcher_ext_v1* (*dom_mod_get_launcher_ext_fn)(void);
uint32_t dom_launcher_ext_count(dom_core* core);
const dom_launcher_ext_v1* dom_launcher_ext_get(dom_core* core, uint32_t index);
bool dom_launcher_ext_register(dom_core* core, const dom_launcher_ext_v1* ext);

/*------------------------------------------------------------
 * Legacy registry/instance API (kept for compatibility)
 *------------------------------------------------------------*/
typedef enum {
    DOMINO_PACKAGE_KIND_UNKNOWN = 0,
    DOMINO_PACKAGE_KIND_MOD,
    DOMINO_PACKAGE_KIND_PACK
} domino_package_kind;

typedef struct domino_package_id {
    char value[64];
} domino_package_id;

typedef struct domino_package_desc {
    char               id[64];
    domino_semver      version;
    domino_package_kind kind;
    char               path[260];
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

/* Legacy mod host stubs */
typedef struct dm_mod_context dm_mod_context;

struct dm_mod_context {
    uint32_t placeholder;
};

dm_mod_context* dm_mod_create(void);
void            dm_mod_destroy(dm_mod_context* ctx);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_MOD_H_INCLUDED */
