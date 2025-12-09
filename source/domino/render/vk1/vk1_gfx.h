#ifndef DOMINIUM_VK1_GFX_H
#define DOMINIUM_VK1_GFX_H

#include <stdint.h>

#include "domino/gfx.h"
#include "domino/canvas.h"

/* Vulkan headers */
#include <vulkan/vulkan.h>

/* vk1 renderer state */
typedef struct vk1_state_t {
    /* host window handle is platform-specific; dsys_window_get_native_handle
       returns a platform-dependent pointer. vk1 backend is responsible
       for bridging this to VkSurfaceKHR via platform-specific creation.
       For now store it as void*. */
    void                *native_window;

    int                  width;
    int                  height;
    int                  fullscreen;
    int                  vsync;

    VkInstance           instance;
    VkPhysicalDevice     physical_device;
    VkDevice             device;
    uint32_t             graphics_queue_family;
    VkQueue              graphics_queue;

    VkSurfaceKHR         surface;
    VkSwapchainKHR       swapchain;
    VkFormat             swapchain_format;
    VkExtent2D           swapchain_extent;

    VkImage             *swapchain_images;
    VkImageView         *swapchain_image_views;
    uint32_t             swapchain_image_count;

    VkRenderPass         render_pass;
    VkFramebuffer       *framebuffers;

    VkCommandPool        command_pool;
    VkCommandBuffer     *command_buffers;

    VkSemaphore          image_available_semaphore;
    VkSemaphore          render_finished_semaphore;
    VkFence              in_flight_fence;

    dgfx_caps            caps;

    int                  frame_in_progress;
    uint32_t             current_image_index;

    /* Basic pipelines and layouts */
    VkPipelineLayout     pipeline_layout_2d;
    VkPipeline           pipeline_2d;

    VkPipelineLayout     pipeline_layout_3d;
    VkPipeline           pipeline_3d;

    VkPipelineLayout     pipeline_layout_lines;
    VkPipeline           pipeline_lines;

    /* Descriptor set layout(s) / descriptor pool */
    VkDescriptorSetLayout descriptor_set_layout_camera;
    VkDescriptorPool      descriptor_pool;
    VkDescriptorSet       descriptor_set_camera;

    VkBuffer              camera_buffer;
    VkDeviceMemory        camera_buffer_memory;

    /* Optional: simple vertex buffers for immediate-mode style draws.
       For v1, you can use vkCmdDraw with push constants or
       staging buffers. Keep fields in place so they can be filled later.
    */

} vk1_state_t;

extern vk1_state_t g_vk1;

const dgfx_backend_vtable *dgfx_vk1_get_vtable(void);

#endif /* DOMINIUM_VK1_GFX_H */
