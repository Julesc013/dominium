set(DOMINO_GFX_SOURCES
    api/domino_gfx_core.c
    api/domino_gfx_internal.h
    soft/soft_gfx.c
    soft/soft_raster.c
    soft/soft_blit.c
    soft/soft_config.c
    soft/core/domino_soft_core.c
    soft/soft_internal.h
    soft/targets/null/soft_target_null.c
    gl2/gl2_gfx.c
)

option(DOMINO_GFX_ENABLE_VK1 "Enable Vulkan 1.0 renderer backend (vk1)" OFF)
option(DOMINIUM_GFX_CGA "Enable CGA renderer backend (cga)" ON)
option(DOMINIUM_GFX_HERC "Enable Hercules renderer backend (herc)" ON)
option(DOMINIUM_GFX_MDA "Enable MDA renderer backend (mda)" ON)
option(DOMINIUM_GFX_EGA "Enable EGA renderer backend (ega)" ON)
option(DOMINIUM_GFX_VGA "Enable VGA renderer backend (vga)" ON)
option(DOMINIUM_GFX_XGA "Enable XGA renderer backend (xga)" ON)
option(DOMINIUM_GFX_VESA "Enable VESA BIOS renderer backend (vesa)" ON)

if(WIN32)
    list(APPEND DOMINO_GFX_SOURCES
        soft/targets/win32/soft_target_win32.c
        dx9/dx9_gfx.c
        dx11/dx11_gfx.c
        gdi/gdi_gfx.c
    )
endif()
if(APPLE)
    list(APPEND DOMINO_GFX_SOURCES
        quickdraw/quickdraw_gfx.c
        quartz/quartz_gfx.c
        metal/metal_gfx.c
        metal/metal_backend.mm
    )
endif()

if(DOMINIUM_GFX_CGA)
    list(APPEND DOMINO_GFX_SOURCES
        cga/cga_gfx.c
        cga/cga_hw.c
    )
endif()
if(DOMINIUM_GFX_HERC)
    list(APPEND DOMINO_GFX_SOURCES
        herc/herc_gfx.c
        herc/herc_hw.c
    )
endif()

if(DOMINIUM_GFX_MDA)
    list(APPEND DOMINO_GFX_SOURCES
        mda/mda_gfx.c
        mda/mda_hw.c
    )
endif()

if(DOMINIUM_GFX_EGA)
    list(APPEND DOMINO_GFX_SOURCES
        ega/ega_gfx.c
        ega/ega_hw.c
    )
endif()

if(DOMINIUM_GFX_VGA)
    list(APPEND DOMINO_GFX_SOURCES
        vga/vga_gfx.c
        vga/vga_hw.c
    )
endif()

if(DOMINIUM_GFX_XGA)
    list(APPEND DOMINO_GFX_SOURCES
        xga/xga_gfx.c
        xga/xga_hw.c
    )
endif()

if(DOMINIUM_GFX_VESA)
    list(APPEND DOMINO_GFX_SOURCES
        vesa/vesa_gfx.c
        vesa/vesa_bios.c
    )
endif()

if(DOMINO_GFX_ENABLE_VK1)
    list(APPEND DOMINO_GFX_SOURCES vk1/vk1_gfx.c)
endif()

add_library(domino_gfx STATIC ${DOMINO_GFX_SOURCES})
target_include_directories(domino_gfx
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/api
        ${CMAKE_CURRENT_SOURCE_DIR}/soft
        ${CMAKE_CURRENT_SOURCE_DIR}/soft/core
        ${CMAKE_CURRENT_SOURCE_DIR}/soft/targets/null
        ${CMAKE_CURRENT_SOURCE_DIR}/soft/targets/win32
        ${CMAKE_CURRENT_SOURCE_DIR}/dx9
        ${CMAKE_CURRENT_SOURCE_DIR}/dx11
        ${CMAKE_CURRENT_SOURCE_DIR}/gl2
        ${CMAKE_CURRENT_SOURCE_DIR}/gdi
        ${CMAKE_CURRENT_SOURCE_DIR}/quickdraw
        ${CMAKE_CURRENT_SOURCE_DIR}/quartz
        ${CMAKE_CURRENT_SOURCE_DIR}/cga
        ${CMAKE_CURRENT_SOURCE_DIR}/herc
        ${CMAKE_CURRENT_SOURCE_DIR}/mda
        ${CMAKE_CURRENT_SOURCE_DIR}/ega
        ${CMAKE_CURRENT_SOURCE_DIR}/vga
        ${CMAKE_CURRENT_SOURCE_DIR}/xga
        ${CMAKE_CURRENT_SOURCE_DIR}/vesa
        ${CMAKE_CURRENT_SOURCE_DIR}/metal
        ${CMAKE_CURRENT_SOURCE_DIR}/vk1
)
target_link_libraries(domino_gfx PUBLIC domino_sys)
target_compile_features(domino_gfx PRIVATE c_std_90)
if(WIN32)
    target_link_libraries(domino_gfx PRIVATE gdi32 user32 d3d9 d3d11 dxgi dxguid opengl32)
endif()
if(APPLE)
    target_compile_definitions(domino_gfx PRIVATE DOMINIUM_GFX_QUICKDRAW DOMINIUM_GFX_QUARTZ)
    target_link_libraries(domino_gfx PRIVATE
        "-framework Carbon"
        "-framework CoreGraphics"
        "-framework CoreFoundation"
        "-framework Metal"
        "-framework QuartzCore"
        "-framework AppKit"
        "-framework OpenGL"
    )
endif()
if(NOT WIN32 AND NOT APPLE)
    target_link_libraries(domino_gfx PRIVATE GL)
endif()

if(DOMINIUM_GFX_CGA)
    target_compile_definitions(domino_gfx PRIVATE DOMINIUM_GFX_CGA)
endif()
if(DOMINIUM_GFX_HERC)
    target_compile_definitions(domino_gfx PRIVATE DOMINIUM_GFX_HERC DGFX_BACKEND_HERC=1)
endif()

if(DOMINIUM_GFX_MDA)
    target_compile_definitions(domino_gfx PRIVATE DGFX_BACKEND_MDA=1 DOMINIUM_GFX_MDA)
endif()

if(DOMINIUM_GFX_EGA)
    target_compile_definitions(domino_gfx PRIVATE DGFX_BACKEND_EGA=1)
endif()

if(DOMINIUM_GFX_VGA)
    target_compile_definitions(domino_gfx PRIVATE DOMINIUM_GFX_VGA)
endif()

if(DOMINIUM_GFX_XGA)
    target_compile_definitions(domino_gfx PRIVATE DOMINIUM_GFX_XGA DGFX_BACKEND_XGA=1)
endif()
if(DOMINIUM_GFX_VESA)
    target_compile_definitions(domino_gfx PRIVATE DGFX_BACKEND_VESA=1)
endif()

if(DOMINO_GFX_ENABLE_VK1)
    find_package(Vulkan REQUIRED)
    target_compile_definitions(domino_gfx PRIVATE DGFX_HAS_VK1)
    target_include_directories(domino_gfx PRIVATE ${Vulkan_INCLUDE_DIRS})
    target_link_libraries(domino_gfx PRIVATE Vulkan::Vulkan)
endif()
