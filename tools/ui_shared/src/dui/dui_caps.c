/*
FILE: source/domino/dui/dui_caps.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dui/dui_caps
RESPONSIBILITY: Registers DUI backends into the central capability registry (presentation-only).
ALLOWED DEPENDENCIES: `include/domino/**`, `include/dui/**`, `source/domino/**`.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: No internal synchronization; register during startup only.
ERROR MODEL: Returns `dom_caps_result`.
DETERMINISM: Presentation-only backends; determinism grade is UI-only.
VERSIONING / ABI / DATA FORMAT NOTES: Uses `dom_backend_desc` and `get_api` hook.
EXTENSION POINTS: Add new backends by registering additional descriptors.
*/
#include "domino/caps.h"

#include "dui/dui_api_v1.h"

/* Backend API providers (defined by backend modules). */
const void* dom_dui_null_get_api(u32 requested_abi);
const void* dom_dui_dgfx_get_api(u32 requested_abi);
const void* dom_dui_win32_get_api(u32 requested_abi);
const void* dom_dui_gtk_get_api(u32 requested_abi);
const void* dom_dui_macos_get_api(u32 requested_abi);

static dom_caps_result dui_register_one(const char* name,
                                       u32 prio,
                                       u32 required_hw,
                                       dom_caps_get_api_fn get_api)
{
    dom_backend_desc d;
    if (!name || !name[0] || !get_api) {
        return DOM_CAPS_ERR_BAD_DESC;
    }
    d.abi_version = DOM_CAPS_ABI_VERSION;
    d.struct_size = (u32)sizeof(dom_backend_desc);
    d.subsystem_id = DOM_SUBSYS_DUI;
    d.subsystem_name = "ui";
    d.backend_name = name;
    d.backend_priority = prio;
    d.required_hw_flags = required_hw;
    d.subsystem_flags = 0u;
    d.backend_flags = DOM_CAPS_BACKEND_PRESENTATION_ONLY;
    d.determinism = DOM_DET_D2_BEST_EFFORT;
    d.perf_class = DOM_CAPS_PERF_BASELINE;
    d.get_api = get_api;
    d.probe = 0;
    return dom_caps_register_backend(&d);
}

dom_caps_result dom_dui_register_caps_backends(void)
{
    dom_caps_result r;

    /* Null backend is always available (headless). */
    r = dui_register_one("null", 10u, 0u, dom_dui_null_get_api);
    if (r != DOM_CAPS_OK && r != DOM_CAPS_ERR_DUPLICATE) {
        return r;
    }

    /* DGFX fallback (software renderer path). */
    r = dui_register_one("dgfx", 50u, 0u, dom_dui_dgfx_get_api);
    if (r != DOM_CAPS_OK && r != DOM_CAPS_ERR_DUPLICATE) {
        return r;
    }

#if defined(_WIN32)
    r = dui_register_one("win32", 100u, DOM_HW_OS_WIN32, dom_dui_win32_get_api);
    if (r != DOM_CAPS_OK && r != DOM_CAPS_ERR_DUPLICATE) {
        return r;
    }
#endif

#if defined(__APPLE__)
    r = dui_register_one("macos", 100u, DOM_HW_OS_APPLE, dom_dui_macos_get_api);
    if (r != DOM_CAPS_OK && r != DOM_CAPS_ERR_DUPLICATE) {
        return r;
    }
#endif

#if defined(__unix__) || defined(__unix) || defined(__linux__)
    r = dui_register_one("gtk", 100u, DOM_HW_OS_UNIX, dom_dui_gtk_get_api);
    if (r != DOM_CAPS_OK && r != DOM_CAPS_ERR_DUPLICATE) {
        return r;
    }
#endif

    return DOM_CAPS_OK;
}
