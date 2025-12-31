cmake_minimum_required(VERSION 3.16)

add_library(core_tlv STATIC
    core_tlv_stream.cpp
    core_tlv_framed_reader.cpp
    core_tlv_framed_writer.cpp
    core_tlv_framed_validate.cpp
)
target_include_directories(core_tlv
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}
)
target_link_libraries(core_tlv
    PUBLIC
        core_err
)
set_target_properties(core_tlv PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_library(core_audit STATIC
    core_audit.cpp
)
target_include_directories(core_audit
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}
)
target_link_libraries(core_audit
    PUBLIC
        core_tlv
        core_err
)
set_target_properties(core_audit PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
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

add_library(core_tlv_schema STATIC
    core_tlv_schema.c
)
target_include_directories(core_tlv_schema
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}
)
target_link_libraries(core_tlv_schema
    PUBLIC
        core_err
)

add_library(core_log STATIC
    core_log.c
)
target_include_directories(core_log
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}
)

add_library(core_caps STATIC
    core_caps.c
)
target_include_directories(core_caps
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}
)

add_library(core_solver STATIC
    core_solver.c
)
target_include_directories(core_solver
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}
)

add_library(core_job STATIC
    core_job.c
    core_job_schema.c
)
target_include_directories(core_job
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}
)
target_link_libraries(core_job
    PUBLIC
        core_tlv_schema
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
