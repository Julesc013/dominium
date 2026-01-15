/*
FILE: source/domino/render/vk1/d_gfx_vk1.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/vk1/d_gfx_vk1
RESPONSIBILITY: Implements `d_gfx_vk1`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "d_gfx_vk1.h"

#include <string.h>

#include <vulkan/vulkan.h>

static VkInstance g_vk1_instance = VK_NULL_HANDLE;

static int d_gfx_vk1_init(void)
{
    VkApplicationInfo app;
    VkInstanceCreateInfo ci;
    VkResult r;

    memset(&app, 0, sizeof(app));
    app.sType = VK_STRUCTURE_TYPE_APPLICATION_INFO;
    app.pApplicationName = "Domino";
    app.applicationVersion = 1u;
    app.pEngineName = "Domino";
    app.engineVersion = 1u;
    app.apiVersion = VK_API_VERSION_1_0;

    memset(&ci, 0, sizeof(ci));
    ci.sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO;
    ci.pApplicationInfo = &app;

    r = vkCreateInstance(&ci, (const VkAllocationCallbacks*)0, &g_vk1_instance);
    if (r != VK_SUCCESS) {
        g_vk1_instance = VK_NULL_HANDLE;
        return 0;
    }

    return 1;
}

static void d_gfx_vk1_shutdown(void)
{
    if (g_vk1_instance != VK_NULL_HANDLE) {
        vkDestroyInstance(g_vk1_instance, (const VkAllocationCallbacks*)0);
        g_vk1_instance = VK_NULL_HANDLE;
    }
}

static void d_gfx_vk1_submit(const d_gfx_cmd_buffer* buf)
{
    (void)buf;
}

static void d_gfx_vk1_present(void)
{
}

static d_gfx_backend_soft g_vk1_backend = {
    d_gfx_vk1_init,
    d_gfx_vk1_shutdown,
    d_gfx_vk1_submit,
    d_gfx_vk1_present
};

const d_gfx_backend_soft* d_gfx_vk1_register_backend(void)
{
    return &g_vk1_backend;
}

