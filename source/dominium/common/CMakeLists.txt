cmake_minimum_required(VERSION 3.16)

add_library(core_tlv INTERFACE)
target_include_directories(core_tlv INTERFACE
    ${DOMINIUM_INCLUDE_DIR}
)

add_library(core_audit INTERFACE)
target_include_directories(core_audit INTERFACE
    ${DOMINIUM_INCLUDE_DIR}
)

add_library(core_util INTERFACE)
target_include_directories(core_util INTERFACE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
)

add_library(core_err STATIC
    core_err.c
)
target_include_directories(core_err
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}
)

add_library(core_log STATIC
    core_log.c
)
target_include_directories(core_log
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}
)

add_library(dominium_common STATIC
    dominium_product_manifest.c
    dominium_version.c
    game_content_api.c
    dominium_product_info.c
    dmn_paths.c
    dmn_repo.c
    dmn_instance.c
    dom_paths.cpp
    dom_instance.cpp
    dom_packset.cpp
    dom_session.cpp
    dom_compat.cpp
    dom_profile_cli.cpp
)

target_include_directories(dominium_common
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
        ${CMAKE_SOURCE_DIR}/source/domino
        ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(dominium_common
    PUBLIC
        domino_core
)
