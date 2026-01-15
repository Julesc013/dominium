/*
FILE: include/domino/mod.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / mod
RESPONSIBILITY: Defines the public contract for `mod` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_MOD_H_INCLUDED
#define DOMINO_MOD_H_INCLUDED

#include <stddef.h>
#include "domino/baseline.h"
#include "domino/core.h"
#include "domino/inst.h"
#include "domino/version.h"
#include "domino/sys.h"
#include "domino/canvas.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_mod_vtable: Public type used by `mod`. */
typedef struct dom_mod_vtable {
    uint32_t api_version;
    void (*on_load)(dom_core* core);
    void (*on_unload)(void);
    void (*on_tick)(dom_core* core, double dt);
} dom_mod_vtable;

/* out: Public type used by `mod`. */
typedef bool (*dom_mod_get_vtable_fn)(dom_mod_vtable* out);

/* Purpose: Load all.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dom_mod_load_all(dom_core* core, dom_instance_id inst);
/* Purpose: Unload all.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
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

/* void: Public type used by `mod`. */
typedef const dom_launcher_ext_v1* (*dom_mod_get_launcher_ext_fn)(void);
/* Purpose: Count dom launcher ext.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
uint32_t dom_launcher_ext_count(dom_core* core);
/* Purpose: Get launcher ext.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const dom_launcher_ext_v1* dom_launcher_ext_get(dom_core* core, uint32_t index);
/* Purpose: Register launcher ext.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dom_launcher_ext_register(dom_core* core, const dom_launcher_ext_v1* ext);

/*------------------------------------------------------------
 * Legacy registry/instance API (kept for compatibility)
 *------------------------------------------------------------*/
typedef enum {
    DOMINO_PACKAGE_KIND_UNKNOWN = 0,
    DOMINO_PACKAGE_KIND_MOD,
    DOMINO_PACKAGE_KIND_PACK
} domino_package_kind;

/* domino_package_id: Public type used by `mod`. */
typedef struct domino_package_id {
    char value[64];
} domino_package_id;

/* domino_package_desc: Public type used by `mod`. */
typedef struct domino_package_desc {
    char               id[64];
    domino_semver      version;
    domino_package_kind kind;
    char               path[260];
} domino_package_desc;

/* domino_package_registry: Public type used by `mod`. */
typedef struct domino_package_registry domino_package_registry;

typedef int (*domino_package_visit_fn)(const domino_package_desc* desc,
                                       void* user);

#define DOMINO_MAX_INSTANCE_MODS  32
#define DOMINO_MAX_INSTANCE_PACKS 32

/* domino_instance_desc: Public type used by `mod`. */
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

/* domino_resolve_error: Public type used by `mod`. */
typedef struct domino_resolve_error {
    char message[256];
} domino_resolve_error;

/* Purpose: Create package registry.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
domino_package_registry* domino_package_registry_create(void);
/* Purpose: Destroy package registry.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void domino_package_registry_destroy(domino_package_registry* reg);
/* Purpose: Sys domino package registry set.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void domino_package_registry_set_sys(domino_package_registry* reg,
                                     domino_sys_context* sys);
/* Purpose: Roots domino package registry scan.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int  domino_package_registry_scan_roots(domino_package_registry* reg,
                                        const char* const* roots,
                                        unsigned int root_count);
/* Purpose: Visit domino package registry.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int  domino_package_registry_visit(domino_package_registry* reg,
                                   domino_package_visit_fn fn,
                                   void* user);
/* Purpose: Find package registry.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const domino_package_desc* domino_package_registry_find(domino_package_registry* reg,
                                                        const char* id);

/* Purpose: File domino manifest load from.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int domino_manifest_load_from_file(const char* path,
                                   domino_package_desc* out);

/* Purpose: Load instance.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int domino_instance_load(const char* path, domino_instance_desc* out);
/* Purpose: Save instance.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int domino_instance_save(const char* path, const domino_instance_desc* inst);
/* Purpose: Resolve domino instance.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int domino_instance_resolve(domino_package_registry* reg,
                            const domino_instance_desc* inst,
                            domino_resolve_error* out_err);

/* Legacy mod host stubs */
typedef struct dm_mod_context dm_mod_context;

struct dm_mod_context {
    uint32_t placeholder;
};

/* Purpose: Create mod.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
dm_mod_context* dm_mod_create(void);
/* Purpose: Destroy mod.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void            dm_mod_destroy(dm_mod_context* ctx);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_MOD_H_INCLUDED */
