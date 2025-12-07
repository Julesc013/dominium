cmake_minimum_required(VERSION 3.15)

# Internal tool libraries placeholder (assetc/packer/etc.).
add_library(dom_tools_support INTERFACE)
target_include_directories(dom_tools_support
    INTERFACE
        ${CMAKE_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/include/dom_priv
)

# TODO: populate src/tools/* with reusable logic for top-level tools/.
