cmake_minimum_required(VERSION 3.15)

# Internal tool libraries placeholder (assetc/packer/etc.).
add_library(dom_tools_support INTERFACE)
target_include_directories(dom_tools_support
    INTERFACE
        ${CMAKE_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/include/dom_priv
)

# TODO: populate src/tools/* with reusable logic for top-level tools/.

option(DOMINIUM_BUILD_DGFX_DEMO "Build dgfx demo tool" ON)

if(DOMINIUM_BUILD_DGFX_DEMO)
    add_executable(dgfx_demo
        dgfx_demo/dgfx_demo.c
        dgfx_demo/dgfx_demo.h
        dgfx_demo/dgfx_demo_main.c
    )
    target_include_directories(dgfx_demo PRIVATE ${DOMINIUM_INCLUDE_DIR})
    target_link_libraries(dgfx_demo PRIVATE domino_gfx domino_sys)
    if(NOT WIN32)
        target_link_libraries(dgfx_demo PRIVATE m)
    endif()
    target_compile_features(dgfx_demo PRIVATE c_std_90)
endif()
