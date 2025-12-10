#ifndef DOMINIUM_LAUNCHER_INSTANCES_H
#define DOMINIUM_LAUNCHER_INSTANCES_H

#include "domino/mod.h"
#include "dominium_launcher_view_registry.h"

typedef struct dominium_launcher_context dominium_launcher_context;
typedef struct dominium_launcher_instances_service dominium_launcher_instances_service;

/* Lifecycle */
int dominium_launcher_instances_create(dominium_launcher_context* lctx,
                                       dominium_launcher_instances_service** out_svc);
void dominium_launcher_instances_destroy(dominium_launcher_instances_service* svc);

/* Rescan instances from disk (called by launcher core) */
int dominium_launcher_instances_reload(dominium_launcher_instances_service* svc);

/* Instance operations (you can stub some of these initially) */
int dominium_launcher_instances_create_instance(dominium_launcher_instances_service* svc,
                                                const domino_instance_desc* tmpl);
int dominium_launcher_instances_delete_instance(dominium_launcher_instances_service* svc,
                                                const char* id);

/* Register one or more views into the view registry */
int dominium_launcher_instances_register_views(dominium_launcher_instances_service* svc,
                                               dominium_launcher_view_registry* vreg);

#endif /* DOMINIUM_LAUNCHER_INSTANCES_H */
