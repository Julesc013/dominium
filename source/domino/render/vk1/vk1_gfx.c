#include <stdlib.h>
#include <string.h>

#include "vk1_gfx.h"
#include "domino/sys.h"

#define VK1_MAX_PHYSICAL_DEVICES 8

typedef struct vk1_camera_ubo_t {
    float view[16];
    float proj[16];
    float world[16];
} vk1_camera_ubo_t;

vk1_state_t g_vk1;

static bool      vk1_init(const dgfx_desc* desc);
static void      vk1_shutdown(void);
static dgfx_caps vk1_get_caps(void);
static void      vk1_resize(int width, int height);
static void      vk1_begin_frame(void);
static void      vk1_execute(const dgfx_cmd_buffer* cmd_buf);
static void      vk1_end_frame(void);

static void vk1_build_caps(void);

static bool vk1_create_instance(void);
static bool vk1_create_surface(void);
static bool vk1_pick_physical_device(void);
static bool vk1_create_logical_device(void);
static bool vk1_create_swapchain(void);
static bool vk1_create_render_pass(void);
static bool vk1_create_framebuffers(void);
static bool vk1_create_command_pool_and_buffers(void);
static bool vk1_create_sync_objects(void);
static bool vk1_create_camera_resources(void);
static bool vk1_create_pipelines(void);

static void vk1_cmd_clear(const uint8_t* payload, size_t size);
static void vk1_cmd_set_viewport(const uint8_t* payload);
static void vk1_cmd_set_camera(const uint8_t* payload);
static void vk1_cmd_set_pipeline(const uint8_t* payload);
static void vk1_cmd_set_texture(const uint8_t* payload);
static void vk1_cmd_draw_sprites(const uint8_t* payload, size_t size);
static void vk1_cmd_draw_lines(const uint8_t* payload, size_t size);
static void vk1_cmd_draw_meshes(const uint8_t* payload, size_t size);
static void vk1_cmd_draw_text(const uint8_t* payload, size_t size);

static const dgfx_backend_vtable g_vk1_vtable = {
    vk1_init,
    vk1_shutdown,
    vk1_get_caps,
    vk1_resize,
    vk1_begin_frame,
    vk1_execute,
    vk1_end_frame
};

const dgfx_backend_vtable* dgfx_vk1_get_vtable(void)
{
    return &g_vk1_vtable;
}

static void vk1_build_caps(void)
{
    memset(&g_vk1.caps, 0, sizeof(g_vk1.caps));
    g_vk1.caps.name = "vk1";
    g_vk1.caps.supports_2d = true;
    g_vk1.caps.supports_3d = true;
    g_vk1.caps.supports_text = false;
    g_vk1.caps.supports_rt = true;
    g_vk1.caps.supports_alpha = true;
    g_vk1.caps.max_texture_size = 16384;
}

static bool vk1_init(const dgfx_desc* desc)
{
    if (!desc || !desc->window) {
        return false;
    }

    memset(&g_vk1, 0, sizeof(g_vk1));

    g_vk1.native_window = dsys_window_get_native_handle(desc->window);
    if (!g_vk1.native_window) {
        return false;
    }

    g_vk1.width = (desc->width > 0) ? desc->width : 800;
    g_vk1.height = (desc->height > 0) ? desc->height : 600;
    g_vk1.fullscreen = 0;
    g_vk1.vsync = desc->vsync ? 1 : 0;

    if (!vk1_create_instance()) {
        vk1_shutdown();
        return false;
    }

    if (!vk1_create_surface()) {
        vk1_shutdown();
        return false;
    }

    if (!vk1_pick_physical_device()) {
        vk1_shutdown();
        return false;
    }

    if (!vk1_create_logical_device()) {
        vk1_shutdown();
        return false;
    }

    if (!vk1_create_swapchain()) {
        vk1_shutdown();
        return false;
    }

    if (!vk1_create_render_pass()) {
        vk1_shutdown();
        return false;
    }

    if (!vk1_create_framebuffers()) {
        vk1_shutdown();
        return false;
    }

    if (!vk1_create_command_pool_and_buffers()) {
        vk1_shutdown();
        return false;
    }

    if (!vk1_create_sync_objects()) {
        vk1_shutdown();
        return false;
    }

    if (!vk1_create_camera_resources()) {
        vk1_shutdown();
        return false;
    }

    if (!vk1_create_pipelines()) {
        vk1_shutdown();
        return false;
    }

    vk1_build_caps();
    g_vk1.frame_in_progress = 0;
    g_vk1.current_image_index = 0;
    return true;
}

static void vk1_shutdown(void)
{
    if (g_vk1.device != VK_NULL_HANDLE) {
        vkDeviceWaitIdle(g_vk1.device);
    }

    if (g_vk1.pipeline_2d) {
        vkDestroyPipeline(g_vk1.device, g_vk1.pipeline_2d, NULL);
    }
    if (g_vk1.pipeline_layout_2d) {
        vkDestroyPipelineLayout(g_vk1.device, g_vk1.pipeline_layout_2d, NULL);
    }
    if (g_vk1.pipeline_3d) {
        vkDestroyPipeline(g_vk1.device, g_vk1.pipeline_3d, NULL);
    }
    if (g_vk1.pipeline_layout_3d) {
        vkDestroyPipelineLayout(g_vk1.device, g_vk1.pipeline_layout_3d, NULL);
    }
    if (g_vk1.pipeline_lines) {
        vkDestroyPipeline(g_vk1.device, g_vk1.pipeline_lines, NULL);
    }
    if (g_vk1.pipeline_layout_lines) {
        vkDestroyPipelineLayout(g_vk1.device, g_vk1.pipeline_layout_lines, NULL);
    }

    if (g_vk1.camera_buffer != VK_NULL_HANDLE) {
        vkDestroyBuffer(g_vk1.device, g_vk1.camera_buffer, NULL);
    }
    if (g_vk1.camera_buffer_memory != VK_NULL_HANDLE) {
        vkFreeMemory(g_vk1.device, g_vk1.camera_buffer_memory, NULL);
    }
    if (g_vk1.descriptor_pool) {
        vkDestroyDescriptorPool(g_vk1.device, g_vk1.descriptor_pool, NULL);
    }
    if (g_vk1.descriptor_set_layout_camera) {
        vkDestroyDescriptorSetLayout(g_vk1.device, g_vk1.descriptor_set_layout_camera, NULL);
    }

    if (g_vk1.framebuffers) {
        uint32_t i;
        for (i = 0; i < g_vk1.swapchain_image_count; ++i) {
            if (g_vk1.framebuffers[i] != VK_NULL_HANDLE) {
                vkDestroyFramebuffer(g_vk1.device, g_vk1.framebuffers[i], NULL);
            }
        }
        free(g_vk1.framebuffers);
    }

    if (g_vk1.render_pass) {
        vkDestroyRenderPass(g_vk1.device, g_vk1.render_pass, NULL);
    }

    if (g_vk1.swapchain_image_views) {
        uint32_t i;
        for (i = 0; i < g_vk1.swapchain_image_count; ++i) {
            if (g_vk1.swapchain_image_views[i] != VK_NULL_HANDLE) {
                vkDestroyImageView(g_vk1.device, g_vk1.swapchain_image_views[i], NULL);
            }
        }
        free(g_vk1.swapchain_image_views);
    }

    if (g_vk1.swapchain_images) {
        free(g_vk1.swapchain_images);
    }

    if (g_vk1.swapchain) {
        vkDestroySwapchainKHR(g_vk1.device, g_vk1.swapchain, NULL);
    }

    if (g_vk1.image_available_semaphore) {
        vkDestroySemaphore(g_vk1.device, g_vk1.image_available_semaphore, NULL);
    }
    if (g_vk1.render_finished_semaphore) {
        vkDestroySemaphore(g_vk1.device, g_vk1.render_finished_semaphore, NULL);
    }
    if (g_vk1.in_flight_fence) {
        vkDestroyFence(g_vk1.device, g_vk1.in_flight_fence, NULL);
    }

    if (g_vk1.command_pool) {
        vkDestroyCommandPool(g_vk1.device, g_vk1.command_pool, NULL);
    }
    if (g_vk1.command_buffers) {
        free(g_vk1.command_buffers);
    }

    if (g_vk1.device) {
        vkDestroyDevice(g_vk1.device, NULL);
    }

    if (g_vk1.surface) {
        vkDestroySurfaceKHR(g_vk1.instance, g_vk1.surface, NULL);
    }

    if (g_vk1.instance) {
        vkDestroyInstance(g_vk1.instance, NULL);
    }

    memset(&g_vk1, 0, sizeof(g_vk1));
}

static dgfx_caps vk1_get_caps(void)
{
    return g_vk1.caps;
}

static void vk1_resize(int width, int height)
{
    if (!g_vk1.device || !g_vk1.swapchain) {
        return;
    }
    if (width <= 0 || height <= 0) {
        return;
    }
    if ((uint32_t)width == g_vk1.swapchain_extent.width &&
        (uint32_t)height == g_vk1.swapchain_extent.height) {
        return;
    }

    vkDeviceWaitIdle(g_vk1.device);

    g_vk1.width = width;
    g_vk1.height = height;

    if (g_vk1.framebuffers) {
        uint32_t i;
        for (i = 0; i < g_vk1.swapchain_image_count; ++i) {
            if (g_vk1.framebuffers[i] != VK_NULL_HANDLE) {
                vkDestroyFramebuffer(g_vk1.device, g_vk1.framebuffers[i], NULL);
            }
        }
        free(g_vk1.framebuffers);
        g_vk1.framebuffers = NULL;
    }
    if (g_vk1.swapchain_image_views) {
        uint32_t i;
        for (i = 0; i < g_vk1.swapchain_image_count; ++i) {
            if (g_vk1.swapchain_image_views[i] != VK_NULL_HANDLE) {
                vkDestroyImageView(g_vk1.device, g_vk1.swapchain_image_views[i], NULL);
            }
        }
        free(g_vk1.swapchain_image_views);
        g_vk1.swapchain_image_views = NULL;
    }
    if (g_vk1.swapchain) {
        vkDestroySwapchainKHR(g_vk1.device, g_vk1.swapchain, NULL);
        g_vk1.swapchain = VK_NULL_HANDLE;
    }

    if (!vk1_create_swapchain()) {
        return;
    }
    vk1_create_framebuffers();
}

static void vk1_begin_frame(void)
{
    VkResult res;

    if (!g_vk1.device || !g_vk1.swapchain || !g_vk1.command_buffers) {
        return;
    }

    vkWaitForFences(g_vk1.device, 1, &g_vk1.in_flight_fence, VK_TRUE, UINT64_MAX);
    vkResetFences(g_vk1.device, 1, &g_vk1.in_flight_fence);

    res = vkAcquireNextImageKHR(
        g_vk1.device,
        g_vk1.swapchain,
        UINT64_MAX,
        g_vk1.image_available_semaphore,
        VK_NULL_HANDLE,
        &g_vk1.current_image_index);
    if (res != VK_SUCCESS) {
        return;
    }

    {
        VkCommandBuffer cmd = g_vk1.command_buffers[g_vk1.current_image_index];
        VkCommandBufferBeginInfo begin_info;
        VkRenderPassBeginInfo rp_info;
        VkClearValue clear_values[2];

        memset(&begin_info, 0, sizeof(begin_info));
        begin_info.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;
        begin_info.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;

        vkBeginCommandBuffer(cmd, &begin_info);

        memset(clear_values, 0, sizeof(clear_values));
        clear_values[0].color.float32[0] = 0.0f;
        clear_values[0].color.float32[1] = 0.0f;
        clear_values[0].color.float32[2] = 0.0f;
        clear_values[0].color.float32[3] = 1.0f;
        clear_values[1].depthStencil.depth = 1.0f;
        clear_values[1].depthStencil.stencil = 0;

        memset(&rp_info, 0, sizeof(rp_info));
        rp_info.sType = VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO;
        rp_info.renderPass = g_vk1.render_pass;
        rp_info.framebuffer = g_vk1.framebuffers[g_vk1.current_image_index];
        rp_info.renderArea.offset.x = 0;
        rp_info.renderArea.offset.y = 0;
        rp_info.renderArea.extent = g_vk1.swapchain_extent;
        rp_info.clearValueCount = 2;
        rp_info.pClearValues = clear_values;

        vkCmdBeginRenderPass(cmd, &rp_info, VK_SUBPASS_CONTENTS_INLINE);

        /* Default viewport/scissor covering the full target. */
        vk1_cmd_set_viewport(NULL);
    }

    g_vk1.frame_in_progress = 1;
}

static void vk1_end_frame(void)
{
    VkSubmitInfo submit_info;
    VkPresentInfoKHR present_info;

    if (!g_vk1.device || !g_vk1.swapchain || !g_vk1.frame_in_progress) {
        return;
    }

    {
        VkCommandBuffer cmd = g_vk1.command_buffers[g_vk1.current_image_index];
        vkCmdEndRenderPass(cmd);
        vkEndCommandBuffer(cmd);
    }

    memset(&submit_info, 0, sizeof(submit_info));
    submit_info.sType = VK_STRUCTURE_TYPE_SUBMIT_INFO;

    {
        VkSemaphore wait_semaphores[1];
        VkPipelineStageFlags wait_stages[1];
        wait_semaphores[0] = g_vk1.image_available_semaphore;
        wait_stages[0] = VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT;
        submit_info.waitSemaphoreCount = 1;
        submit_info.pWaitSemaphores = wait_semaphores;
        submit_info.pWaitDstStageMask = wait_stages;
    }

    submit_info.commandBufferCount = 1;
    submit_info.pCommandBuffers = &g_vk1.command_buffers[g_vk1.current_image_index];

    {
        VkSemaphore signal_semaphores[1];
        signal_semaphores[0] = g_vk1.render_finished_semaphore;
        submit_info.signalSemaphoreCount = 1;
        submit_info.pSignalSemaphores = signal_semaphores;
    }

    vkQueueSubmit(g_vk1.graphics_queue, 1, &submit_info, g_vk1.in_flight_fence);

    memset(&present_info, 0, sizeof(present_info));
    present_info.sType = VK_STRUCTURE_TYPE_PRESENT_INFO_KHR;
    present_info.waitSemaphoreCount = 1;
    present_info.pWaitSemaphores = &g_vk1.render_finished_semaphore;
    present_info.swapchainCount = 1;
    present_info.pSwapchains = &g_vk1.swapchain;
    present_info.pImageIndices = &g_vk1.current_image_index;
    present_info.pResults = NULL;

    vkQueuePresentKHR(g_vk1.graphics_queue, &present_info);

    g_vk1.frame_in_progress = 0;
}

static bool vk1_create_instance(void)
{
    VkApplicationInfo app_info;
    VkInstanceCreateInfo create_info;
    VkResult res;

    memset(&app_info, 0, sizeof(app_info));
    app_info.sType = VK_STRUCTURE_TYPE_APPLICATION_INFO;
    app_info.pApplicationName = "Dominium";
    app_info.applicationVersion = VK_MAKE_VERSION(1, 0, 0);
    app_info.pEngineName = "Domino";
    app_info.engineVersion = VK_MAKE_VERSION(1, 0, 0);
    app_info.apiVersion = VK_API_VERSION_1_0;

    memset(&create_info, 0, sizeof(create_info));
    create_info.sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO;
    create_info.pApplicationInfo = &app_info;

    /* TODO: fill enabledExtensionCount / ppEnabledExtensionNames based
       on platform surface extension requirements. For now, assume they
       are provided by helper functions or compile-time configuration. */

    res = vkCreateInstance(&create_info, NULL, &g_vk1.instance);
    if (res != VK_SUCCESS) {
        return false;
    }
    return true;
}

static bool vk1_create_surface(void)
{
    VkResult res;
    (void)res;

    /* TODO: implement per platform:
       - For Win32: use VkWin32SurfaceCreateInfoKHR with HWND/HINSTANCE.
       - For X11: VkXlibSurfaceCreateInfoKHR with Display* and Window.
       - For macOS: VK_EXT_metal_surface / VK_MVK_macos_surface and CAMetalLayer.

       For now, assume a helper exists or this is filled later. */

    return false; /* placeholder until platform surface creation is wired */
}

static bool vk1_pick_physical_device(void)
{
    uint32_t device_count = 0;
    VkResult res;

    res = vkEnumeratePhysicalDevices(g_vk1.instance, &device_count, NULL);
    if (res != VK_SUCCESS || device_count == 0) {
        return false;
    }

    if (device_count > VK1_MAX_PHYSICAL_DEVICES) {
        device_count = VK1_MAX_PHYSICAL_DEVICES;
    }

    {
        VkPhysicalDevice devices[VK1_MAX_PHYSICAL_DEVICES];
        uint32_t i;

        res = vkEnumeratePhysicalDevices(g_vk1.instance, &device_count, devices);
        if (res != VK_SUCCESS) {
            return false;
        }

        g_vk1.physical_device = VK_NULL_HANDLE;
        for (i = 0; i < device_count; ++i) {
            /* TODO: query queue family support and surface presentation. */
            g_vk1.physical_device = devices[i];
            g_vk1.graphics_queue_family = 0;
            break;
        }
    }

    return (g_vk1.physical_device != VK_NULL_HANDLE);
}

static bool vk1_create_logical_device(void)
{
    VkDeviceQueueCreateInfo queue_info;
    VkDeviceCreateInfo create_info;
    float queue_priority = 1.0f;
    VkResult res;

    if (g_vk1.physical_device == VK_NULL_HANDLE) {
        return false;
    }

    memset(&queue_info, 0, sizeof(queue_info));
    queue_info.sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO;
    queue_info.queueFamilyIndex = g_vk1.graphics_queue_family;
    queue_info.queueCount = 1;
    queue_info.pQueuePriorities = &queue_priority;

    memset(&create_info, 0, sizeof(create_info));
    create_info.sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO;
    create_info.queueCreateInfoCount = 1;
    create_info.pQueueCreateInfos = &queue_info;

    /* TODO: enable swapchain extension and optional features */

    res = vkCreateDevice(g_vk1.physical_device, &create_info, NULL, &g_vk1.device);
    if (res != VK_SUCCESS) {
        return false;
    }

    vkGetDeviceQueue(g_vk1.device, g_vk1.graphics_queue_family, 0, &g_vk1.graphics_queue);
    return true;
}

static bool vk1_create_swapchain(void)
{
    VkResult res;
    VkSwapchainCreateInfoKHR create_info;

    if (g_vk1.device == VK_NULL_HANDLE || g_vk1.surface == VK_NULL_HANDLE) {
        return false;
    }

    /* TODO: query VkSurfaceCapabilitiesKHR, VkSurfaceFormatKHR, VkPresentModeKHR. */

    memset(&create_info, 0, sizeof(create_info));
    create_info.sType = VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR;
    create_info.surface = g_vk1.surface;
    create_info.minImageCount = 2;
    create_info.imageFormat = VK_FORMAT_B8G8R8A8_UNORM;
    create_info.imageColorSpace = VK_COLOR_SPACE_SRGB_NONLINEAR_KHR;
    create_info.imageExtent.width = (uint32_t)g_vk1.width;
    create_info.imageExtent.height = (uint32_t)g_vk1.height;
    create_info.imageArrayLayers = 1;
    create_info.imageUsage = VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT;
    create_info.imageSharingMode = VK_SHARING_MODE_EXCLUSIVE;
    create_info.preTransform = VK_SURFACE_TRANSFORM_IDENTITY_BIT_KHR;
    create_info.compositeAlpha = VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR;
    create_info.presentMode = VK_PRESENT_MODE_FIFO_KHR;
    create_info.clipped = VK_TRUE;
    create_info.oldSwapchain = VK_NULL_HANDLE;

    res = vkCreateSwapchainKHR(g_vk1.device, &create_info, NULL, &g_vk1.swapchain);
    if (res != VK_SUCCESS) {
        return false;
    }

    res = vkGetSwapchainImagesKHR(g_vk1.device, g_vk1.swapchain, &g_vk1.swapchain_image_count, NULL);
    if (res != VK_SUCCESS || g_vk1.swapchain_image_count == 0) {
        return false;
    }

    g_vk1.swapchain_images = (VkImage*)malloc(sizeof(VkImage) * g_vk1.swapchain_image_count);
    if (!g_vk1.swapchain_images) {
        return false;
    }

    res = vkGetSwapchainImagesKHR(
        g_vk1.device,
        g_vk1.swapchain,
        &g_vk1.swapchain_image_count,
        g_vk1.swapchain_images);
    if (res != VK_SUCCESS) {
        return false;
    }

    g_vk1.swapchain_image_views = (VkImageView*)malloc(sizeof(VkImageView) * g_vk1.swapchain_image_count);
    if (!g_vk1.swapchain_image_views) {
        return false;
    }

    {
        uint32_t i;
        for (i = 0; i < g_vk1.swapchain_image_count; ++i) {
            VkImageViewCreateInfo view_info;
            memset(&view_info, 0, sizeof(view_info));
            view_info.sType = VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO;
            view_info.image = g_vk1.swapchain_images[i];
            view_info.viewType = VK_IMAGE_VIEW_TYPE_2D;
            view_info.format = create_info.imageFormat;
            view_info.components.r = VK_COMPONENT_SWIZZLE_IDENTITY;
            view_info.components.g = VK_COMPONENT_SWIZZLE_IDENTITY;
            view_info.components.b = VK_COMPONENT_SWIZZLE_IDENTITY;
            view_info.components.a = VK_COMPONENT_SWIZZLE_IDENTITY;
            view_info.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
            view_info.subresourceRange.baseMipLevel = 0;
            view_info.subresourceRange.levelCount = 1;
            view_info.subresourceRange.baseArrayLayer = 0;
            view_info.subresourceRange.layerCount = 1;
            res = vkCreateImageView(g_vk1.device, &view_info, NULL, &g_vk1.swapchain_image_views[i]);
            if (res != VK_SUCCESS) {
                return false;
            }
        }
    }

    g_vk1.swapchain_format = create_info.imageFormat;
    g_vk1.swapchain_extent = create_info.imageExtent;
    return true;
}

static bool vk1_create_render_pass(void)
{
    VkAttachmentDescription attachments[1];
    VkAttachmentReference color_ref;
    VkSubpassDescription subpass;
    VkRenderPassCreateInfo rp_info;
    VkResult res;

    memset(attachments, 0, sizeof(attachments));
    attachments[0].format = g_vk1.swapchain_format;
    attachments[0].samples = VK_SAMPLE_COUNT_1_BIT;
    attachments[0].loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR;
    attachments[0].storeOp = VK_ATTACHMENT_STORE_OP_STORE;
    attachments[0].stencilLoadOp = VK_ATTACHMENT_LOAD_OP_DONT_CARE;
    attachments[0].stencilStoreOp = VK_ATTACHMENT_STORE_OP_DONT_CARE;
    attachments[0].initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
    attachments[0].finalLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR;

    memset(&color_ref, 0, sizeof(color_ref));
    color_ref.attachment = 0;
    color_ref.layout = VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL;

    memset(&subpass, 0, sizeof(subpass));
    subpass.pipelineBindPoint = VK_PIPELINE_BIND_POINT_GRAPHICS;
    subpass.colorAttachmentCount = 1;
    subpass.pColorAttachments = &color_ref;

    memset(&rp_info, 0, sizeof(rp_info));
    rp_info.sType = VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO;
    rp_info.attachmentCount = 1;
    rp_info.pAttachments = attachments;
    rp_info.subpassCount = 1;
    rp_info.pSubpasses = &subpass;

    res = vkCreateRenderPass(g_vk1.device, &rp_info, NULL, &g_vk1.render_pass);
    return (res == VK_SUCCESS);
}

static bool vk1_create_framebuffers(void)
{
    uint32_t i;

    if (!g_vk1.swapchain_image_views || g_vk1.render_pass == VK_NULL_HANDLE) {
        return false;
    }

    g_vk1.framebuffers = (VkFramebuffer*)malloc(sizeof(VkFramebuffer) * g_vk1.swapchain_image_count);
    if (!g_vk1.framebuffers) {
        return false;
    }

    for (i = 0; i < g_vk1.swapchain_image_count; ++i) {
        VkFramebufferCreateInfo fb_info;
        VkImageView attachments[1];
        VkResult res;

        attachments[0] = g_vk1.swapchain_image_views[i];

        memset(&fb_info, 0, sizeof(fb_info));
        fb_info.sType = VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO;
        fb_info.renderPass = g_vk1.render_pass;
        fb_info.attachmentCount = 1;
        fb_info.pAttachments = attachments;
        fb_info.width = g_vk1.swapchain_extent.width;
        fb_info.height = g_vk1.swapchain_extent.height;
        fb_info.layers = 1;

        res = vkCreateFramebuffer(g_vk1.device, &fb_info, NULL, &g_vk1.framebuffers[i]);
        if (res != VK_SUCCESS) {
            return false;
        }
    }

    return true;
}

static bool vk1_create_command_pool_and_buffers(void)
{
    VkCommandPoolCreateInfo pool_info;
    VkCommandBufferAllocateInfo alloc_info;
    VkResult res;

    if (g_vk1.device == VK_NULL_HANDLE) {
        return false;
    }

    memset(&pool_info, 0, sizeof(pool_info));
    pool_info.sType = VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO;
    pool_info.queueFamilyIndex = g_vk1.graphics_queue_family;
    pool_info.flags = VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;

    res = vkCreateCommandPool(g_vk1.device, &pool_info, NULL, &g_vk1.command_pool);
    if (res != VK_SUCCESS) {
        return false;
    }

    g_vk1.command_buffers = (VkCommandBuffer*)malloc(sizeof(VkCommandBuffer) * g_vk1.swapchain_image_count);
    if (!g_vk1.command_buffers) {
        return false;
    }

    memset(&alloc_info, 0, sizeof(alloc_info));
    alloc_info.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO;
    alloc_info.commandPool = g_vk1.command_pool;
    alloc_info.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
    alloc_info.commandBufferCount = g_vk1.swapchain_image_count;

    res = vkAllocateCommandBuffers(g_vk1.device, &alloc_info, g_vk1.command_buffers);
    return (res == VK_SUCCESS);
}

static bool vk1_create_sync_objects(void)
{
    VkSemaphoreCreateInfo sem_info;
    VkFenceCreateInfo fence_info;
    VkResult res;

    if (g_vk1.device == VK_NULL_HANDLE) {
        return false;
    }

    memset(&sem_info, 0, sizeof(sem_info));
    sem_info.sType = VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO;

    res = vkCreateSemaphore(g_vk1.device, &sem_info, NULL, &g_vk1.image_available_semaphore);
    if (res != VK_SUCCESS) {
        return false;
    }

    res = vkCreateSemaphore(g_vk1.device, &sem_info, NULL, &g_vk1.render_finished_semaphore);
    if (res != VK_SUCCESS) {
        return false;
    }

    memset(&fence_info, 0, sizeof(fence_info));
    fence_info.sType = VK_STRUCTURE_TYPE_FENCE_CREATE_INFO;
    fence_info.flags = VK_FENCE_CREATE_SIGNALED_BIT;

    res = vkCreateFence(g_vk1.device, &fence_info, NULL, &g_vk1.in_flight_fence);
    return (res == VK_SUCCESS);
}

static bool vk1_create_camera_resources(void)
{
    /* TODO: create a host-visible uniform buffer for camera/world matrices. */
    g_vk1.camera_buffer = VK_NULL_HANDLE;
    g_vk1.camera_buffer_memory = VK_NULL_HANDLE;
    g_vk1.descriptor_set_layout_camera = VK_NULL_HANDLE;
    g_vk1.descriptor_pool = VK_NULL_HANDLE;
    g_vk1.descriptor_set_camera = VK_NULL_HANDLE;
    return true;
}

static bool vk1_create_pipelines(void)
{
    /* TODO: create descriptor set layouts, pipeline layouts, shader modules, and pipelines. */
    g_vk1.pipeline_2d = VK_NULL_HANDLE;
    g_vk1.pipeline_layout_2d = VK_NULL_HANDLE;
    g_vk1.pipeline_3d = VK_NULL_HANDLE;
    g_vk1.pipeline_layout_3d = VK_NULL_HANDLE;
    g_vk1.pipeline_lines = VK_NULL_HANDLE;
    g_vk1.pipeline_layout_lines = VK_NULL_HANDLE;
    return true;
}

static void vk1_cmd_clear(const uint8_t* payload, size_t size)
{
    (void)payload;
    (void)size;
    if (!g_vk1.frame_in_progress) {
        return;
    }

    /* For now, rely on the begin-frame clear values. */
}

static void vk1_cmd_set_viewport(const uint8_t* payload)
{
    VkCommandBuffer cmd;
    VkViewport vp;
    VkRect2D scissor;

    (void)payload;
    if (!g_vk1.frame_in_progress) {
        return;
    }

    cmd = g_vk1.command_buffers[g_vk1.current_image_index];

    vp.x = 0.0f;
    vp.y = 0.0f;
    vp.width = (float)g_vk1.swapchain_extent.width;
    vp.height = (float)g_vk1.swapchain_extent.height;
    vp.minDepth = 0.0f;
    vp.maxDepth = 1.0f;

    vkCmdSetViewport(cmd, 0, 1, &vp);

    scissor.offset.x = 0;
    scissor.offset.y = 0;
    scissor.extent = g_vk1.swapchain_extent;
    vkCmdSetScissor(cmd, 0, 1, &scissor);
}

static void vk1_cmd_set_camera(const uint8_t* payload)
{
    VkDevice device = g_vk1.device;
    VkDeviceMemory mem = g_vk1.camera_buffer_memory;
    vk1_camera_ubo_t* ubo;
    VkResult res;
    int i;

    (void)payload;
    if (device == VK_NULL_HANDLE || mem == VK_NULL_HANDLE) {
        return;
    }

    res = vkMapMemory(device, mem, 0, sizeof(*ubo), 0, (void**)&ubo);
    if (res != VK_SUCCESS) {
        return;
    }

    for (i = 0; i < 16; ++i) {
        ubo->view[i] = 0.0f;
        ubo->proj[i] = 0.0f;
        ubo->world[i] = 0.0f;
    }
    ubo->view[0] = ubo->view[5] = ubo->view[10] = ubo->view[15] = 1.0f;
    ubo->proj[0] = ubo->proj[5] = ubo->proj[10] = ubo->proj[15] = 1.0f;
    ubo->world[0] = ubo->world[5] = ubo->world[10] = ubo->world[15] = 1.0f;

    vkUnmapMemory(device, mem);
}

static void vk1_cmd_set_pipeline(const uint8_t* payload)
{
    VkCommandBuffer cmd;

    (void)payload;
    if (!g_vk1.frame_in_progress) {
        return;
    }

    cmd = g_vk1.command_buffers[g_vk1.current_image_index];

    if (g_vk1.pipeline_3d != VK_NULL_HANDLE && g_vk1.pipeline_layout_3d != VK_NULL_HANDLE) {
        vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_GRAPHICS, g_vk1.pipeline_3d);
        vkCmdBindDescriptorSets(
            cmd,
            VK_PIPELINE_BIND_POINT_GRAPHICS,
            g_vk1.pipeline_layout_3d,
            0,
            1,
            &g_vk1.descriptor_set_camera,
            0,
            NULL);
    }
}

static void vk1_cmd_set_texture(const uint8_t* payload)
{
    (void)payload;
    /* Texture binding will be added when texture IR is available. */
}

static void vk1_cmd_draw_sprites(const uint8_t* payload, size_t size)
{
    VkCommandBuffer cmd;

    (void)payload;
    (void)size;
    if (!g_vk1.frame_in_progress) {
        return;
    }

    cmd = g_vk1.command_buffers[g_vk1.current_image_index];

    if (g_vk1.pipeline_2d != VK_NULL_HANDLE && g_vk1.pipeline_layout_2d != VK_NULL_HANDLE) {
        vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_GRAPHICS, g_vk1.pipeline_2d);
        vkCmdBindDescriptorSets(
            cmd,
            VK_PIPELINE_BIND_POINT_GRAPHICS,
            g_vk1.pipeline_layout_2d,
            0,
            1,
            &g_vk1.descriptor_set_camera,
            0,
            NULL);
    }

    /* TODO: upload quad vertices and issue vkCmdDraw. */
}

static void vk1_cmd_draw_lines(const uint8_t* payload, size_t size)
{
    VkCommandBuffer cmd;

    (void)payload;
    (void)size;
    if (!g_vk1.frame_in_progress) {
        return;
    }

    cmd = g_vk1.command_buffers[g_vk1.current_image_index];

    if (g_vk1.pipeline_lines != VK_NULL_HANDLE && g_vk1.pipeline_layout_lines != VK_NULL_HANDLE) {
        vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_GRAPHICS, g_vk1.pipeline_lines);
        vkCmdBindDescriptorSets(
            cmd,
            VK_PIPELINE_BIND_POINT_GRAPHICS,
            g_vk1.pipeline_layout_lines,
            0,
            1,
            &g_vk1.descriptor_set_camera,
            0,
            NULL);
    }

    /* TODO: upload line vertices and issue vkCmdDraw. */
}

static void vk1_cmd_draw_meshes(const uint8_t* payload, size_t size)
{
    VkCommandBuffer cmd;

    (void)payload;
    (void)size;
    if (!g_vk1.frame_in_progress) {
        return;
    }

    cmd = g_vk1.command_buffers[g_vk1.current_image_index];

    if (g_vk1.pipeline_3d != VK_NULL_HANDLE && g_vk1.pipeline_layout_3d != VK_NULL_HANDLE) {
        vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_GRAPHICS, g_vk1.pipeline_3d);
        vkCmdBindDescriptorSets(
            cmd,
            VK_PIPELINE_BIND_POINT_GRAPHICS,
            g_vk1.pipeline_layout_3d,
            0,
            1,
            &g_vk1.descriptor_set_camera,
            0,
            NULL);
    }

    /* TODO: parse mesh payload, bind buffers, and issue vkCmdDrawIndexed. */
}

static void vk1_cmd_draw_text(const uint8_t* payload, size_t size)
{
    (void)payload;
    (void)size;
    /* Text rendering is not implemented in the vk1 backend MVP. */
}

static void vk1_execute(const dgfx_cmd_buffer* cmd_buf)
{
    const uint8_t* ptr;
    const uint8_t* end;
    size_t header_size;

    if (!cmd_buf || !cmd_buf->data || cmd_buf->size == 0u) {
        return;
    }
    if (!g_vk1.frame_in_progress) {
        return;
    }

    header_size = sizeof(dgfx_cmd);
    ptr = cmd_buf->data;
    end = cmd_buf->data + cmd_buf->size;

    while (ptr + header_size <= end) {
        const dgfx_cmd* cmd;
        const uint8_t* payload;
        size_t payload_size;
        size_t total_size;

        cmd = (const dgfx_cmd*)ptr;
        payload_size = cmd->payload_size;
        total_size = header_size + payload_size;
        if (ptr + total_size > end) {
            break;
        }
        payload = ptr + header_size;

        switch (cmd->op) {
        case DGFX_CMD_CLEAR:
            vk1_cmd_clear(payload, payload_size);
            break;
        case DGFX_CMD_SET_VIEWPORT:
            vk1_cmd_set_viewport(payload);
            break;
        case DGFX_CMD_SET_CAMERA:
            vk1_cmd_set_camera(payload);
            break;
        case DGFX_CMD_SET_PIPELINE:
            vk1_cmd_set_pipeline(payload);
            break;
        case DGFX_CMD_SET_TEXTURE:
            vk1_cmd_set_texture(payload);
            break;
        case DGFX_CMD_DRAW_SPRITES:
            vk1_cmd_draw_sprites(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_MESHES:
            vk1_cmd_draw_meshes(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_LINES:
            vk1_cmd_draw_lines(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_TEXT:
            vk1_cmd_draw_text(payload, payload_size);
            break;
        default:
            break;
        }

        ptr += total_size;
    }
}
