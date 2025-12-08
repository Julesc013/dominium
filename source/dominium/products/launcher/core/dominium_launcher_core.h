#ifndef DOMINIUM_LAUNCHER_CORE_H
#define DOMINIUM_LAUNCHER_CORE_H

#include "domino/sys.h"
#include "domino/mod.h"
#include "domino/version.h"
#include "dominium_launcher_view_registry.h"

typedef struct dominium_launcher_context dominium_launcher_context;

#define DOMINIUM_LAUNCHER_MAX_INSTANCES 64

/* Lifecycle */
int  dominium_launcher_init(dominium_launcher_context** out_ctx);
void dominium_launcher_shutdown(dominium_launcher_context* ctx);

/* Reload registry and instances from disk */
int dominium_launcher_reload_registry(dominium_launcher_context* ctx);
int dominium_launcher_reload_instances(dominium_launcher_context* ctx);

/* Accessors for lower layers (read-only) */
domino_sys_context* dominium_launcher_get_sys(dominium_launcher_context* ctx);
const domino_package_registry* dominium_launcher_get_registry(dominium_launcher_context* ctx);
dominium_launcher_view_registry* dominium_launcher_get_view_registry(dominium_launcher_context* ctx);

/* Instance listing: copies currently loaded instance descriptors */
int dominium_launcher_list_instances(dominium_launcher_context* ctx,
                                     domino_instance_desc* out,
                                     unsigned int max_count,
                                     unsigned int* out_count);

/* Run an instance by id: resolves + spawns game process */
int dominium_launcher_run_instance(dominium_launcher_context* ctx,
                                   const char* instance_id);

/* Legacy compatibility helper retained for existing code paths */
int dominium_launcher_resolve_instance(dominium_launcher_context* ctx,
                                       const domino_instance_desc* inst,
                                       domino_resolve_error* err);

#endif /* DOMINIUM_LAUNCHER_CORE_H */
