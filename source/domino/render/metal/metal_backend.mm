#if defined(__APPLE__)
#import <Metal/Metal.h>
#import <QuartzCore/CAMetalLayer.h>
#import <AppKit/AppKit.h>
#include <CoreFoundation/CoreFoundation.h>
#include <TargetConditionals.h>
#include <stddef.h>
#include <string.h>

#include "metal_gfx.h"
#include "domino/sys.h"

extern metal_state_t g_metal;

typedef struct metal_cmd_clear_payload_t {
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;
} metal_cmd_clear_payload_t;

typedef struct metal_lines_header_t {
    uint16_t vertex_count;
    uint16_t reserved;
} metal_lines_header_t;

typedef struct metal_line_vertex_t {
    float    x;
    float    y;
    float    z;
    uint32_t color;
} metal_line_vertex_t;

typedef struct metal_sprite_vertex_t {
    float    x;
    float    y;
    float    z;
    float    u;
    float    v;
    uint32_t color;
} metal_sprite_vertex_t;

typedef struct metal_mesh_vertex_t {
    float x;
    float y;
    float z;
    float nx;
    float ny;
    float nz;
    float u;
    float v;
} metal_mesh_vertex_t;

static bool metal_backend_create_pipelines(void);
static bool metal_backend_create_buffers(void);
static void metal_backend_init_state(void);
static void metal_backend_build_caps(void);
static id<MTLRenderCommandEncoder> metal_begin_encoder(void);
static void metal_end_encoder(id<MTLRenderCommandEncoder> enc);
static id<MTLTexture> metal_ensure_depth_texture(void);

static void metal_cmd_clear(const uint8_t* payload, size_t payload_size);
static void metal_cmd_set_viewport(const uint8_t* payload);
static void metal_cmd_set_camera(const uint8_t* payload, size_t payload_size);
static void metal_cmd_set_pipeline(const uint8_t* payload);
static void metal_cmd_set_texture(const uint8_t* payload);
static void metal_cmd_draw_sprites(const uint8_t* payload, size_t payload_size);
static void metal_cmd_draw_lines(const uint8_t* payload, size_t payload_size);
static void metal_cmd_draw_meshes(const uint8_t* payload, size_t payload_size);
static void metal_cmd_draw_text(const uint8_t* payload, size_t payload_size);

static void metal_release(void** obj)
{
    if (obj && *obj) {
        CFRelease((CFTypeRef)*obj);
        *obj = NULL;
    }
}

static NSString* metal_shader_source(void)
{
    static NSString* src = nil;
    if (!src) {
        src =
        @"#include <metal_stdlib>\n"
        "using namespace metal;\n"
        "struct VS2DIn { float3 pos [[attribute(0)]]; float2 uv [[attribute(1)]]; uchar4 color [[attribute(2)]]; };\n"
        "struct VSLineIn { float3 pos [[attribute(0)]]; uchar4 color [[attribute(1)]]; };\n"
        "struct VS3DIn { float3 pos [[attribute(0)]]; float3 nrm [[attribute(1)]]; float2 uv [[attribute(2)]]; };\n"
        "struct VSOut { float4 position [[position]]; float2 uv; float4 color; };\n"
        "vertex VSOut vs_2d(VS2DIn in [[stage_in]]) {\n"
        "    VSOut o; o.position = float4(in.pos, 1.0); o.uv = in.uv; o.color = float4(in.color) / 255.0; return o; }\n"
        "fragment float4 fs_2d(VSOut in [[stage_in]]) { return in.color; }\n"
        "vertex VSOut vs_lines(VSLineIn in [[stage_in]]) { VSOut o; o.position = float4(in.pos, 1.0); o.uv=float2(0.0); o.color=float4(in.color)/255.0; return o; }\n"
        "fragment float4 fs_lines(VSOut in [[stage_in]]) { return in.color; }\n"
        "vertex VSOut vs_3d(VS3DIn in [[stage_in]]) { VSOut o; o.position = float4(in.pos, 1.0); o.uv=in.uv; o.color=float4(1.0); return o; }\n"
        "fragment float4 fs_3d(VSOut in [[stage_in]]) { return float4(1.0,1.0,1.0,1.0); }\n";
    }
    return src;
}

static id<MTLLibrary> metal_make_library(id<MTLDevice> dev)
{
    NSError* err;
    NSString* src;

    if (!dev) {
        return nil;
    }
    err = nil;
    src = metal_shader_source();
    return [dev newLibraryWithSource:src options:nil error:&err];
}

static id<MTLRenderPipelineState> metal_create_pipeline(id<MTLDevice> dev,
                                                        id<MTLLibrary> lib,
                                                        NSString* vs_name,
                                                        NSString* fs_name,
                                                        MTLVertexDescriptor* vd,
                                                        BOOL enable_depth)
{
    MTLRenderPipelineDescriptor* desc;
    NSError* err;
    id<MTLFunction> vs;
    id<MTLFunction> fs;

    if (!dev || !lib || !vs_name || !fs_name) {
        return nil;
    }

    vs = [lib newFunctionWithName:vs_name];
    fs = [lib newFunctionWithName:fs_name];
    if (!vs || !fs) {
        return nil;
    }

    desc = [[MTLRenderPipelineDescriptor alloc] init];
    desc.vertexFunction = vs;
    desc.fragmentFunction = fs;
    if (vd) {
        desc.vertexDescriptor = vd;
    }
    desc.colorAttachments[0].pixelFormat = MTLPixelFormatBGRA8Unorm;
    desc.colorAttachments[0].blendingEnabled = YES;
    desc.colorAttachments[0].rgbBlendOperation = MTLBlendOperationAdd;
    desc.colorAttachments[0].alphaBlendOperation = MTLBlendOperationAdd;
    desc.colorAttachments[0].sourceRGBBlendFactor = MTLBlendFactorSourceAlpha;
    desc.colorAttachments[0].destinationRGBBlendFactor = MTLBlendFactorOneMinusSourceAlpha;
    desc.colorAttachments[0].sourceAlphaBlendFactor = MTLBlendFactorOne;
    desc.colorAttachments[0].destinationAlphaBlendFactor = MTLBlendFactorOneMinusSourceAlpha;
    if (enable_depth) {
        desc.depthAttachmentPixelFormat = MTLPixelFormatDepth32Float;
    }

    err = nil;
    return [dev newRenderPipelineStateWithDescriptor:desc error:&err];
}

bool metal_backend_init(const dgfx_desc* desc)
{
    NSWindow* window;
    NSView* content;
    CAMetalLayer* layer;
    id<MTLDevice> device;
    id<MTLCommandQueue> queue;
    CGFloat scale;

    if (!desc || !desc->window) {
        return false;
    }

    memset(&g_metal, 0, sizeof(g_metal));
    g_metal.ns_window = dsys_window_get_native_handle(desc->window);
    if (!g_metal.ns_window) {
        return false;
    }

    g_metal.width = (desc->width > 0) ? desc->width : 1280;
    g_metal.height = (desc->height > 0) ? desc->height : 720;
    g_metal.fullscreen = 0;
    g_metal.vsync = desc->vsync ? 1 : 0;

    window = (__bridge NSWindow*)g_metal.ns_window;
    content = [window contentView];
    if (!content) {
        return false;
    }

    device = MTLCreateSystemDefaultDevice();
    if (!device) {
        return false;
    }
    g_metal.device = (__bridge_retained void*)device;

    queue = [device newCommandQueue];
    if (!queue) {
        metal_backend_shutdown();
        return false;
    }

    g_metal.cmd_queue = (__bridge_retained void*)queue;

    layer = nil;
    if ([[content layer] isKindOfClass:[CAMetalLayer class]]) {
        layer = (CAMetalLayer*)[content layer];
    } else {
        layer = [CAMetalLayer layer];
        [content setWantsLayer:YES];
        [content setLayer:layer];
    }
    if (!layer) {
        metal_backend_shutdown();
        return false;
    }

    scale = 1.0;
#if TARGET_OS_OSX
    scale = [window backingScaleFactor];
#endif

    layer.device = device;
    layer.pixelFormat = MTLPixelFormatBGRA8Unorm;
    layer.framebufferOnly = YES;
    layer.contentsScale = scale;
    layer.drawableSize = CGSizeMake((CGFloat)g_metal.width, (CGFloat)g_metal.height);

    g_metal.layer = (__bridge_retained void*)layer;

    if (!metal_backend_create_pipelines()) {
        metal_backend_shutdown();
        return false;
    }
    if (!metal_backend_create_buffers()) {
        metal_backend_shutdown();
        return false;
    }

    metal_backend_init_state();
    metal_backend_build_caps();
    g_metal.frame_in_progress = 0;
    g_metal.current_pipeline = 0;

    return true;
}

void metal_backend_shutdown(void)
{
    metal_release(&g_metal.current_rp_desc);
    metal_release(&g_metal.current_cmd_buffer);
    metal_release(&g_metal.current_drawable);

    metal_release(&g_metal.pipeline_2d);
    metal_release(&g_metal.pipeline_3d);
    metal_release(&g_metal.pipeline_lines);
    metal_release(&g_metal.depth_state_default);

    metal_release(&g_metal.vbo_sprites);
    metal_release(&g_metal.vbo_lines);
    metal_release(&g_metal.vbo_mesh);
    metal_release(&g_metal.ibo_mesh);
    metal_release(&g_metal.depth_target);

    metal_release(&g_metal.cmd_queue);
    metal_release(&g_metal.layer);
    metal_release(&g_metal.device);

    memset(&g_metal, 0, sizeof(g_metal));
}

dgfx_caps metal_backend_get_caps(void)
{
    return g_metal.caps;
}

static id<MTLTexture> metal_ensure_depth_texture(void)
{
    id<MTLTexture> depth;
    id<MTLDevice> dev;
    BOOL recreate;

    dev = (__bridge id<MTLDevice>)g_metal.device;
    if (!dev) {
        return nil;
    }

    depth = (__bridge id<MTLTexture>)g_metal.depth_target;
    recreate = NO;
    if (!depth) {
        recreate = YES;
    } else if ((int)[depth width] != g_metal.width ||
               (int)[depth height] != g_metal.height) {
        recreate = YES;
    }

    if (recreate) {
        MTLTextureDescriptor* td;
        td = [MTLTextureDescriptor texture2DDescriptorWithPixelFormat:MTLPixelFormatDepth32Float
                                                                width:(NSUInteger)g_metal.width
                                                               height:(NSUInteger)g_metal.height
                                                            mipmapped:NO];
        td.storageMode = MTLStorageModePrivate;
        td.usage = MTLTextureUsageRenderTarget;
        depth = [dev newTextureWithDescriptor:td];
        metal_release(&g_metal.depth_target);
        if (depth) {
            g_metal.depth_target = (__bridge_retained void*)depth;
        }
    }

    return depth;
}

void metal_backend_resize(int width, int height)
{
    CAMetalLayer* layer;

    if (width <= 0 || height <= 0) {
        return;
    }
    g_metal.width = width;
    g_metal.height = height;

    layer = (__bridge CAMetalLayer*)g_metal.layer;
    if (layer) {
        layer.drawableSize = CGSizeMake((CGFloat)width, (CGFloat)height);
    }
    metal_release(&g_metal.depth_target);
}

void metal_backend_begin_frame(void)
{
    id<MTLCommandQueue> queue;
    CAMetalLayer* layer;
    id<CAMetalDrawable> drawable;
    id<MTLCommandBuffer> cmd;
    MTLRenderPassDescriptor* rp;
    id<MTLTexture> depth;

    if (g_metal.frame_in_progress) {
        return;
    }

    queue = (__bridge id<MTLCommandQueue>)g_metal.cmd_queue;
    layer = (__bridge CAMetalLayer*)g_metal.layer;
    if (!queue || !layer) {
        return;
    }

    drawable = [layer nextDrawable];
    if (!drawable) {
        return;
    }

    depth = metal_ensure_depth_texture();

    cmd = [queue commandBuffer];
    rp = [MTLRenderPassDescriptor renderPassDescriptor];
    rp.colorAttachments[0].texture = drawable.texture;
    rp.colorAttachments[0].loadAction = MTLLoadActionClear;
    rp.colorAttachments[0].storeAction = MTLStoreActionStore;
    rp.colorAttachments[0].clearColor = MTLClearColorMake(0.0, 0.0, 0.0, 1.0);
    if (depth) {
        rp.depthAttachment.texture = depth;
        rp.depthAttachment.loadAction = MTLLoadActionClear;
        rp.depthAttachment.storeAction = MTLStoreActionDontCare;
        rp.depthAttachment.clearDepth = 1.0;
    }

    g_metal.current_drawable = (__bridge_retained void*)drawable;
    g_metal.current_cmd_buffer = (__bridge_retained void*)cmd;
    g_metal.current_rp_desc = (__bridge_retained void*)rp;
    g_metal.frame_in_progress = 1;
}

void metal_backend_end_frame(void)
{
    id<MTLCommandBuffer> cmd;
    id<CAMetalDrawable> drawable;

    if (!g_metal.frame_in_progress) {
        return;
    }

    cmd = (__bridge id<MTLCommandBuffer>)g_metal.current_cmd_buffer;
    drawable = (__bridge id<CAMetalDrawable>)g_metal.current_drawable;

    if (cmd && drawable) {
        [cmd presentDrawable:drawable];
        [cmd commit];
    }

    metal_release(&g_metal.current_rp_desc);
    metal_release(&g_metal.current_cmd_buffer);
    metal_release(&g_metal.current_drawable);
    g_metal.frame_in_progress = 0;
}

static id<MTLRenderCommandEncoder> metal_begin_encoder(void)
{
    id<MTLCommandBuffer> cmd;
    MTLRenderPassDescriptor* rp;

    cmd = (__bridge id<MTLCommandBuffer>)g_metal.current_cmd_buffer;
    rp = (__bridge MTLRenderPassDescriptor*)g_metal.current_rp_desc;
    if (!cmd || !rp) {
        return nil;
    }
    /* Only clear on the first encoder; subsequent encoders load previous contents. */
    id<MTLRenderCommandEncoder> enc;
    enc = [cmd renderCommandEncoderWithDescriptor:rp];
    rp.colorAttachments[0].loadAction = MTLLoadActionLoad;
    if (rp.depthAttachment.texture) {
        rp.depthAttachment.loadAction = MTLLoadActionLoad;
    }
    return enc;
}

static void metal_end_encoder(id<MTLRenderCommandEncoder> enc)
{
    if (enc) {
        [enc endEncoding];
    }
}

static bool metal_backend_create_pipelines(void)
{
    id<MTLDevice> dev;
    id<MTLLibrary> lib;
    id<MTLRenderPipelineState> p2d;
    id<MTLRenderPipelineState> p3d;
    id<MTLRenderPipelineState> plines;
    id<MTLDepthStencilState> ds;
    MTLVertexDescriptor* vd2d;
    MTLVertexDescriptor* vdline;
    MTLVertexDescriptor* vdmesh;

    dev = (__bridge id<MTLDevice>)g_metal.device;
    if (!dev) {
        return false;
    }

    lib = metal_make_library(dev);
    if (!lib) {
        return false;
    }

    vd2d = [MTLVertexDescriptor vertexDescriptor];
    vd2d.attributes[0].format = MTLVertexFormatFloat3;
    vd2d.attributes[0].offset = 0;
    vd2d.attributes[0].bufferIndex = 0;
    vd2d.attributes[1].format = MTLVertexFormatFloat2;
    vd2d.attributes[1].offset = (NSUInteger)offsetof(metal_sprite_vertex_t, u);
    vd2d.attributes[1].bufferIndex = 0;
    vd2d.attributes[2].format = MTLVertexFormatUChar4Normalized;
    vd2d.attributes[2].offset = (NSUInteger)offsetof(metal_sprite_vertex_t, color);
    vd2d.attributes[2].bufferIndex = 0;
    vd2d.layouts[0].stride = sizeof(metal_sprite_vertex_t);
    vd2d.layouts[0].stepFunction = MTLVertexStepFunctionPerVertex;

    vdline = [MTLVertexDescriptor vertexDescriptor];
    vdline.attributes[0].format = MTLVertexFormatFloat3;
    vdline.attributes[0].offset = 0;
    vdline.attributes[0].bufferIndex = 0;
    vdline.attributes[1].format = MTLVertexFormatUChar4Normalized;
    vdline.attributes[1].offset = (NSUInteger)offsetof(metal_line_vertex_t, color);
    vdline.attributes[1].bufferIndex = 0;
    vdline.layouts[0].stride = sizeof(metal_line_vertex_t);
    vdline.layouts[0].stepFunction = MTLVertexStepFunctionPerVertex;

    vdmesh = [MTLVertexDescriptor vertexDescriptor];
    vdmesh.attributes[0].format = MTLVertexFormatFloat3;
    vdmesh.attributes[0].offset = 0;
    vdmesh.attributes[0].bufferIndex = 0;
    vdmesh.attributes[1].format = MTLVertexFormatFloat3;
    vdmesh.attributes[1].offset = (NSUInteger)offsetof(metal_mesh_vertex_t, nx);
    vdmesh.attributes[1].bufferIndex = 0;
    vdmesh.attributes[2].format = MTLVertexFormatFloat2;
    vdmesh.attributes[2].offset = (NSUInteger)offsetof(metal_mesh_vertex_t, u);
    vdmesh.attributes[2].bufferIndex = 0;
    vdmesh.layouts[0].stride = sizeof(metal_mesh_vertex_t);
    vdmesh.layouts[0].stepFunction = MTLVertexStepFunctionPerVertex;

    p2d = metal_create_pipeline(dev, lib, @"vs_2d", @"fs_2d", vd2d, NO);
    p3d = metal_create_pipeline(dev, lib, @"vs_3d", @"fs_3d", vdmesh, YES);
    plines = metal_create_pipeline(dev, lib, @"vs_lines", @"fs_lines", vdline, NO);
    if (!p2d || !p3d || !plines) {
        return false;
    }

    g_metal.pipeline_2d = (__bridge_retained void*)p2d;
    g_metal.pipeline_3d = (__bridge_retained void*)p3d;
    g_metal.pipeline_lines = (__bridge_retained void*)plines;

    {
        MTLDepthStencilDescriptor* ds_desc;
        ds_desc = [[MTLDepthStencilDescriptor alloc] init];
        ds_desc.depthCompareFunction = MTLCompareFunctionLessEqual;
        ds_desc.depthWriteEnabled = YES;
        ds = [dev newDepthStencilStateWithDescriptor:ds_desc];
        if (ds) {
            g_metal.depth_state_default = (__bridge_retained void*)ds;
        }
    }

    return true;
}

static bool metal_backend_create_buffers(void)
{
    id<MTLDevice> dev;
    id<MTLBuffer> vbo_sprites;
    id<MTLBuffer> vbo_lines;
    id<MTLBuffer> vbo_mesh;
    id<MTLBuffer> ibo_mesh;

    dev = (__bridge id<MTLDevice>)g_metal.device;
    if (!dev) {
        return false;
    }

    vbo_sprites = [dev newBufferWithLength:(NSUInteger)(64 * 1024)
                                   options:MTLResourceStorageModeShared];
    vbo_lines = [dev newBufferWithLength:(NSUInteger)(64 * 1024)
                                 options:MTLResourceStorageModeShared];
    vbo_mesh = [dev newBufferWithLength:(NSUInteger)(256 * 1024)
                                options:MTLResourceStorageModeShared];
    ibo_mesh = [dev newBufferWithLength:(NSUInteger)(256 * 1024)
                                options:MTLResourceStorageModeShared];

    if (!vbo_sprites || !vbo_lines || !vbo_mesh || !ibo_mesh) {
        return false;
    }

    g_metal.vbo_sprites = (__bridge_retained void*)vbo_sprites;
    g_metal.vbo_lines = (__bridge_retained void*)vbo_lines;
    g_metal.vbo_mesh = (__bridge_retained void*)vbo_mesh;
    g_metal.ibo_mesh = (__bridge_retained void*)ibo_mesh;

    return true;
}

static void metal_backend_init_state(void)
{
    int i;
    for (i = 0; i < 16; ++i) {
        g_metal.view[i] = 0.0f;
        g_metal.proj[i] = 0.0f;
        g_metal.world[i] = 0.0f;
    }
    g_metal.view[0] = g_metal.view[5] = g_metal.view[10] = g_metal.view[15] = 1.0f;
    g_metal.proj[0] = g_metal.proj[5] = g_metal.proj[10] = g_metal.proj[15] = 1.0f;
    g_metal.world[0] = g_metal.world[5] = g_metal.world[10] = g_metal.world[15] = 1.0f;
}

static void metal_backend_build_caps(void)
{
    memset(&g_metal.caps, 0, sizeof(g_metal.caps));
    g_metal.caps.name = "metal";
    g_metal.caps.supports_2d = true;
    g_metal.caps.supports_3d = true;
    g_metal.caps.supports_text = false;
    g_metal.caps.supports_rt = true;
    g_metal.caps.supports_alpha = true;
    g_metal.caps.max_texture_size = 16384;
}

static void metal_cmd_clear(const uint8_t* payload, size_t payload_size)
{
    metal_cmd_clear_payload_t clr;
    float r;
    float g;
    float b;
    float a;
    MTLRenderPassDescriptor* rp;
    id<MTLRenderCommandEncoder> enc;

    r = 0.0f;
    g = 0.0f;
    b = 0.0f;
    a = 1.0f;

    if (payload && payload_size >= sizeof(clr)) {
        memcpy(&clr, payload, sizeof(clr));
        r = (float)clr.r / 255.0f;
        g = (float)clr.g / 255.0f;
        b = (float)clr.b / 255.0f;
        a = (float)clr.a / 255.0f;
    }

    rp = (__bridge MTLRenderPassDescriptor*)g_metal.current_rp_desc;
    if (rp) {
        rp.colorAttachments[0].clearColor = MTLClearColorMake(r, g, b, a);
        enc = metal_begin_encoder();
        metal_end_encoder(enc);
        rp.colorAttachments[0].loadAction = MTLLoadActionLoad;
        if (rp.depthAttachment.texture) {
            rp.depthAttachment.loadAction = MTLLoadActionLoad;
        }
    }
}

static void metal_cmd_set_viewport(const uint8_t* payload)
{
    (void)payload;
    /* Default viewport covers the drawable; custom viewport wiring deferred. */
}

static void metal_cmd_set_camera(const uint8_t* payload, size_t payload_size)
{
    size_t expected;
    expected = sizeof(float) * 16u * 3u;
    if (payload && payload_size >= expected) {
        memcpy(g_metal.view, payload, sizeof(g_metal.view));
        memcpy(g_metal.proj, payload + sizeof(g_metal.view), sizeof(g_metal.proj));
        memcpy(g_metal.world, payload + sizeof(g_metal.view) + sizeof(g_metal.proj), sizeof(g_metal.world));
    } else {
        metal_backend_init_state();
    }
}

static void metal_cmd_set_pipeline(const uint8_t* payload)
{
    (void)payload;
    g_metal.current_pipeline = 2;
}

static void metal_cmd_set_texture(const uint8_t* payload)
{
    (void)payload;
    /* Texture binding will be added once the IR carries texture handles. */
}

static void metal_cmd_draw_sprites(const uint8_t* payload, size_t payload_size)
{
    id<MTLRenderCommandEncoder> enc;
    id<MTLRenderPipelineState> pso;
    id<MTLDepthStencilState> ds;
    id<MTLBuffer> vbo;
    metal_sprite_vertex_t verts[6];

    (void)payload;
    (void)payload_size;
    if (!g_metal.frame_in_progress) {
        return;
    }

    enc = metal_begin_encoder();
    if (!enc) {
        return;
    }

    pso = (__bridge id<MTLRenderPipelineState>)g_metal.pipeline_2d;
    ds = (__bridge id<MTLDepthStencilState>)g_metal.depth_state_default;
    vbo = (__bridge id<MTLBuffer>)g_metal.vbo_sprites;
    if (!pso || !vbo) {
        metal_end_encoder(enc);
        return;
    }

    verts[0].x = -0.5f; verts[0].y = -0.5f; verts[0].z = 0.0f;
    verts[0].u = 0.0f;  verts[0].v = 1.0f;  verts[0].color = 0xffffffffu;
    verts[1].x = -0.5f; verts[1].y =  0.5f; verts[1].z = 0.0f;
    verts[1].u = 0.0f;  verts[1].v = 0.0f;  verts[1].color = 0xffffffffu;
    verts[2].x =  0.5f; verts[2].y =  0.5f; verts[2].z = 0.0f;
    verts[2].u = 1.0f;  verts[2].v = 0.0f;  verts[2].color = 0xffffffffu;

    verts[3] = verts[0];
    verts[4] = verts[2];
    verts[5].x =  0.5f; verts[5].y = -0.5f; verts[5].z = 0.0f;
    verts[5].u = 1.0f;  verts[5].v = 1.0f;  verts[5].color = 0xffffffffu;

    memcpy([vbo contents], verts, sizeof(verts));
    [vbo didModifyRange:NSMakeRange(0, sizeof(verts))];

    [enc setRenderPipelineState:pso];
    if (ds) {
        [enc setDepthStencilState:ds];
    }
    [enc setVertexBuffer:vbo offset:0 atIndex:0];
    [enc drawPrimitives:MTLPrimitiveTypeTriangle vertexStart:0 vertexCount:6];

    metal_end_encoder(enc);
}

static void metal_cmd_draw_lines(const uint8_t* payload, size_t payload_size)
{
    metal_lines_header_t header;
    const metal_line_vertex_t* src;
    id<MTLRenderCommandEncoder> enc;
    id<MTLRenderPipelineState> pso;
    id<MTLDepthStencilState> ds;
    id<MTLBuffer> vbo;
    NSUInteger stride;
    NSUInteger max_count;
    NSUInteger count;

    if (!payload || payload_size < sizeof(header)) {
        return;
    }
    if (!g_metal.frame_in_progress) {
        return;
    }

    memcpy(&header, payload, sizeof(header));
    if (header.vertex_count == 0u) {
        return;
    }
    if (payload_size < sizeof(header) + ((size_t)header.vertex_count * sizeof(metal_line_vertex_t))) {
        return;
    }

    src = (const metal_line_vertex_t*)(payload + sizeof(header));
    vbo = (__bridge id<MTLBuffer>)g_metal.vbo_lines;
    if (!vbo) {
        return;
    }

    stride = (NSUInteger)sizeof(metal_line_vertex_t);
    max_count = [vbo length] / stride;
    count = header.vertex_count;
    if (count > max_count) {
        count = max_count;
    }
    if (count == 0u) {
        return;
    }

    memcpy([vbo contents], src, count * stride);
    [vbo didModifyRange:NSMakeRange(0, count * stride)];

    enc = metal_begin_encoder();
    if (!enc) {
        return;
    }

    pso = (__bridge id<MTLRenderPipelineState>)g_metal.pipeline_lines;
    ds = (__bridge id<MTLDepthStencilState>)g_metal.depth_state_default;
    if (!pso) {
        metal_end_encoder(enc);
        return;
    }

    [enc setRenderPipelineState:pso];
    if (ds) {
        [enc setDepthStencilState:ds];
    }
    [enc setVertexBuffer:vbo offset:0 atIndex:0];
    [enc drawPrimitives:MTLPrimitiveTypeLine vertexStart:0 vertexCount:count];

    metal_end_encoder(enc);
}

static void metal_cmd_draw_meshes(const uint8_t* payload, size_t payload_size)
{
    id<MTLRenderCommandEncoder> enc;
    id<MTLRenderPipelineState> pso;
    id<MTLDepthStencilState> ds;
    id<MTLBuffer> vbo;
    metal_mesh_vertex_t verts[3];

    (void)payload;
    (void)payload_size;
    if (!g_metal.frame_in_progress) {
        return;
    }

    enc = metal_begin_encoder();
    if (!enc) {
        return;
    }

    pso = (__bridge id<MTLRenderPipelineState>)g_metal.pipeline_3d;
    ds = (__bridge id<MTLDepthStencilState>)g_metal.depth_state_default;
    vbo = (__bridge id<MTLBuffer>)g_metal.vbo_mesh;
    if (!pso || !vbo) {
        metal_end_encoder(enc);
        return;
    }

    verts[0].x = 0.0f; verts[0].y = 0.5f;  verts[0].z = 0.0f;
    verts[0].nx = 0.0f; verts[0].ny = 0.0f; verts[0].nz = -1.0f;
    verts[0].u = 0.5f;  verts[0].v = 0.0f;
    verts[1].x = -0.5f; verts[1].y = -0.5f; verts[1].z = 0.0f;
    verts[1].nx = 0.0f; verts[1].ny = 0.0f; verts[1].nz = -1.0f;
    verts[1].u = 0.0f;  verts[1].v = 1.0f;
    verts[2].x = 0.5f;  verts[2].y = -0.5f; verts[2].z = 0.0f;
    verts[2].nx = 0.0f; verts[2].ny = 0.0f; verts[2].nz = -1.0f;
    verts[2].u = 1.0f;  verts[2].v = 1.0f;

    memcpy([vbo contents], verts, sizeof(verts));
    [vbo didModifyRange:NSMakeRange(0, sizeof(verts))];

    [enc setRenderPipelineState:pso];
    if (ds) {
        [enc setDepthStencilState:ds];
    }
    [enc setVertexBuffer:vbo offset:0 atIndex:0];
    [enc drawPrimitives:MTLPrimitiveTypeTriangle vertexStart:0 vertexCount:3];

    metal_end_encoder(enc);
}

static void metal_cmd_draw_text(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* Text rendering will be wired once a glyph atlas exists. */
}

void metal_backend_execute(const dgfx_cmd_buffer* cmd_buf)
{
    const uint8_t* ptr;
    const uint8_t* end;
    size_t header_size;

    if (!cmd_buf || !cmd_buf->data || cmd_buf->size == 0u) {
        return;
    }
    if (!g_metal.frame_in_progress) {
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
            metal_cmd_clear(payload, payload_size);
            break;
        case DGFX_CMD_SET_VIEWPORT:
            metal_cmd_set_viewport(payload);
            break;
        case DGFX_CMD_SET_CAMERA:
            metal_cmd_set_camera(payload, payload_size);
            break;
        case DGFX_CMD_SET_PIPELINE:
            metal_cmd_set_pipeline(payload);
            break;
        case DGFX_CMD_SET_TEXTURE:
            metal_cmd_set_texture(payload);
            break;
        case DGFX_CMD_DRAW_SPRITES:
            metal_cmd_draw_sprites(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_MESHES:
            metal_cmd_draw_meshes(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_LINES:
            metal_cmd_draw_lines(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_TEXT:
            metal_cmd_draw_text(payload, payload_size);
            break;
        default:
            break;
        }

        ptr += total_size;
    }
}

#else /* !__APPLE__ */

#include "metal_gfx.h"
#include <string.h>

/* Stub implementations to satisfy non-Apple builds if this file is compiled. */
bool metal_backend_init(const dgfx_desc* desc)               { (void)desc; return false; }
void metal_backend_shutdown(void)                            { }
dgfx_caps metal_backend_get_caps(void)                       { dgfx_caps c; memset(&c, 0, sizeof(c)); return c; }
void metal_backend_resize(int width, int height)             { (void)width; (void)height; }
void metal_backend_begin_frame(void)                         { }
void metal_backend_execute(const dgfx_cmd_buffer* cmd_buf)   { (void)cmd_buf; }
void metal_backend_end_frame(void)                           { }
#endif /* __APPLE__ */
bool metal_backend_init(const dgfx_desc* desc)               { (void)desc; return false; }
void metal_backend_shutdown(void)                            { }
dgfx_caps metal_backend_get_caps(void)                       { dgfx_caps c; memset(&c, 0, sizeof(c)); return c; }
void metal_backend_resize(int width, int height)             { (void)width; (void)height; }
void metal_backend_begin_frame(void)                         { }
void metal_backend_execute(const dgfx_cmd_buffer* cmd_buf)   { (void)cmd_buf; }
void metal_backend_end_frame(void)                           { }

#endif /* __APPLE__ */
