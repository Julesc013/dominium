#ifndef DOMINIUM_METAL_GFX_H
#define DOMINIUM_METAL_GFX_H

#include <stdint.h>

#include "domino/gfx.h"
#include "domino/canvas.h"

/* Opaque Objective-C types are viewed as void* here to keep the C interface. */
typedef void* MetalDeviceRef;           /* id<MTLDevice> */
typedef void* MetalCommandQueueRef;     /* id<MTLCommandQueue> */
typedef void* MetalCommandBufferRef;    /* id<MTLCommandBuffer> */
typedef void* MetalRenderPassDescRef;   /* MTLRenderPassDescriptor* */
typedef void* MetalRenderPipelineRef;   /* id<MTLRenderPipelineState> */
typedef void* MetalDepthStencilStateRef;
typedef void* MetalDrawableRef;         /* id<CAMetalDrawable> */
typedef void* MetalLayerRef;            /* CAMetalLayer* */
typedef void* MetalBufferRef;           /* id<MTLBuffer> */
typedef void* MetalTextureRef;          /* id<MTLTexture> */

typedef struct metal_state_t {
    void*   ns_window; /* from dsys_window_get_native_handle */

    int     width;
    int     height;
    int     fullscreen;
    int     vsync;

    MetalDeviceRef           device;
    MetalCommandQueueRef     cmd_queue;
    MetalLayerRef            layer;

    MetalCommandBufferRef    current_cmd_buffer;
    MetalRenderPassDescRef   current_rp_desc;
    MetalRenderPipelineRef   pipeline_2d;
    MetalRenderPipelineRef   pipeline_3d;
    MetalRenderPipelineRef   pipeline_lines;
    MetalDepthStencilStateRef depth_state_default;

    MetalBufferRef           vbo_sprites;
    MetalBufferRef           vbo_lines;
    MetalBufferRef           vbo_mesh;
    MetalBufferRef           ibo_mesh;

    MetalDrawableRef         current_drawable;
    MetalTextureRef          depth_target;

    dgfx_caps                caps;
    int                      frame_in_progress;
    int                      current_pipeline; /* 0=none, 1=2D, 2=3D, 3=lines */

    float                    view[16];
    float                    proj[16];
    float                    world[16];
} metal_state_t;

extern metal_state_t g_metal;

const dgfx_backend_vtable* dgfx_metal_get_vtable(void);

#endif /* DOMINIUM_METAL_GFX_H */
