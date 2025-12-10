#ifndef DOMINIUM_LAUNCHER_VIEW_REGISTRY_H
#define DOMINIUM_LAUNCHER_VIEW_REGISTRY_H

#include "dominium_launcher_view.h"

typedef struct dominium_launcher_view_registry dominium_launcher_view_registry;

/* Creation/destruction */
dominium_launcher_view_registry* dominium_launcher_view_registry_create(void);
void dominium_launcher_view_registry_destroy(dominium_launcher_view_registry* reg);

/* Register a view: copy desc inside registry; returns 0 if OK, non-zero on error */
int dominium_launcher_view_register(dominium_launcher_view_registry* reg,
                                    const dominium_launcher_view_desc* desc);

/* Get an array of all views sorted by (priority, id). The array pointer is owned by the registry. */
int dominium_launcher_view_list(const dominium_launcher_view_registry* reg,
                                const dominium_launcher_view_desc** out_array,
                                unsigned int* out_count);

/* Find by id; returns NULL if not found */
const dominium_launcher_view_desc* dominium_launcher_view_find(
    const dominium_launcher_view_registry* reg,
    const char* id);

#endif /* DOMINIUM_LAUNCHER_VIEW_REGISTRY_H */
