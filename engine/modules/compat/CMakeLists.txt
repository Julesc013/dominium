cmake_minimum_required(VERSION 3.16)

add_library(domino_compat STATIC
    compat_core.c
)

target_include_directories(domino_compat
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)

target_compile_features(domino_compat PRIVATE c_std_90)
