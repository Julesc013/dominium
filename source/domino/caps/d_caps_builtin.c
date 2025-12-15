#include "domino/caps.h"

static u32 g_caps_builtins_registered = 0u;

dom_caps_result dom_dsys_register_caps_backends(void);
dom_caps_result dom_dgfx_register_caps_backends(void);

dom_caps_result dom_caps_register_builtin_backends(void)
{
    dom_caps_result r;

    if (g_caps_builtins_registered) {
        return DOM_CAPS_OK;
    }

    r = dom_dsys_register_caps_backends();
    if (r != DOM_CAPS_OK) {
        return r;
    }
    r = dom_dgfx_register_caps_backends();
    if (r != DOM_CAPS_OK) {
        return r;
    }

    g_caps_builtins_registered = 1u;
    return DOM_CAPS_OK;
}

