set(DOMINO_SYS_SOURCES
    core/sys_stub.c
    core/audio/dom_audio_api.c
    core/base/core_rng.c
    core/base/dom_core/dom_core_bits.c
    core/base/dom_core/dom_core_err.c
    core/base/dom_core/dom_core_fp.c
    core/base/dom_core/dom_core_id.c
    core/base/dom_core/dom_core_log.c
    core/base/dom_core/dom_core_mem.c
    core/base/dom_core/dom_core_rng.c
    core/base/dom_core/dom_core_types.c
    core/base/dom_core/dom_core_version.c
    core/base/shared/json.cpp
    core/base/shared/logging.cpp
    core/base/shared/manifest_install.cpp
    core/base/shared/os_paths.cpp
    core/base/shared/process.cpp
    core/base/shared/uuid.cpp
    plat/null/dom_plat_sys_stub.c
    plat/null/dom_plat_term_stub.c
    plat/null/dom_plat_ui_stub.c
)

add_library(domino_sys STATIC ${DOMINO_SYS_SOURCES})
target_include_directories(domino_sys
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
        ${DOMINIUM_INCLUDE_DIR}/dominium/_internal
        ${DOMINIUM_INCLUDE_DIR}/dominium/_internal/dom_priv
        ${CMAKE_CURRENT_SOURCE_DIR}/core/base
        ${CMAKE_CURRENT_SOURCE_DIR}/core/base/dom_core
        ${CMAKE_CURRENT_SOURCE_DIR}/core/base/shared
        ${CMAKE_CURRENT_SOURCE_DIR}/core/audio
        ${CMAKE_CURRENT_SOURCE_DIR}/core/math
)
target_compile_features(domino_sys PRIVATE c_std_90 cxx_std_98)
