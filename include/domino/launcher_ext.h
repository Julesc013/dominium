#ifndef DOMINO_LAUNCHER_EXT_H_INCLUDED
#define DOMINO_LAUNCHER_EXT_H_INCLUDED

#include <stdint.h>
#include "domino/core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct launcher_ext_vtable {
    uint32_t api_version;
    void (*register_views)(dom_core* core);
    void (*register_actions)(dom_core* core);
} launcher_ext_vtable;

typedef bool (*launcher_ext_get_vtable_fn)(launcher_ext_vtable* out);

bool launcher_ext_load_all(dom_core* core);
void launcher_ext_unload_all(dom_core* core);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_LAUNCHER_EXT_H_INCLUDED */
