set(DOMINO_GFX_SOURCES
    api/domino_gfx_core.c
    api/domino_gfx_internal.h
    soft/core/domino_soft_core.c
    soft/soft_internal.h
    soft/targets/null/soft_target_null.c
    gl2/gl2_gfx.c
)

option(DOMINO_GFX_ENABLE_VK1 "Enable Vulkan 1.0 renderer backend (vk1)" OFF)

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

if(DOMINO_GFX_ENABLE_VK1)
    find_package(Vulkan REQUIRED)
    target_compile_definitions(domino_gfx PRIVATE DGFX_HAS_VK1)
    target_include_directories(domino_gfx PRIVATE ${Vulkan_INCLUDE_DIRS})
    target_link_libraries(domino_gfx PRIVATE Vulkan::Vulkan)
endif()
