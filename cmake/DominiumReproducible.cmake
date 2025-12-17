option(DOMINIUM_ENABLE_REPRODUCIBLE_BUILD "Enable best-effort reproducible-build flags where supported" ON)

if(NOT DOMINIUM_ENABLE_REPRODUCIBLE_BUILD)
    return()
endif()

# MSVC: /Brepro requests deterministic compilation and linking.
if(MSVC)
    add_compile_options(/Brepro)
    add_link_options(/Brepro)
endif()

# GCC/Clang: avoid embedding absolute paths in debug info and macros where supported.
include(CheckCCompilerFlag)
include(CheckCXXCompilerFlag)

function(dominium__add_compile_flag_if_supported flag)
    check_c_compiler_flag("${flag}" _dom_c_ok)
    if(_dom_c_ok)
        add_compile_options("$<$<COMPILE_LANGUAGE:C>:${flag}>")
    endif()
    check_cxx_compiler_flag("${flag}" _dom_cxx_ok)
    if(_dom_cxx_ok)
        add_compile_options("$<$<COMPILE_LANGUAGE:CXX>:${flag}>")
    endif()
endfunction()

if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang" OR CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    # Map source/build roots to stable prefixes for reproducibility.
    dominium__add_compile_flag_if_supported("-ffile-prefix-map=${CMAKE_SOURCE_DIR}=.")
    dominium__add_compile_flag_if_supported("-ffile-prefix-map=${CMAKE_BINARY_DIR}=.")
    dominium__add_compile_flag_if_supported("-fdebug-prefix-map=${CMAKE_SOURCE_DIR}=.")
    dominium__add_compile_flag_if_supported("-fdebug-prefix-map=${CMAKE_BINARY_DIR}=.")
    dominium__add_compile_flag_if_supported("-fmacro-prefix-map=${CMAKE_SOURCE_DIR}=.")
    dominium__add_compile_flag_if_supported("-fmacro-prefix-map=${CMAKE_BINARY_DIR}=.")
endif()

