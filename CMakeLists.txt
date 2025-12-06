cmake_minimum_required(VERSION 3.15)

project(Dominium
    VERSION 0.1.0
    LANGUAGES C CXX
)

# --------------------------------------------------------------------
# Language standards (C89 core, C++98 runtime/tooling)
# --------------------------------------------------------------------
set(CMAKE_C_STANDARD 90)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

set(CMAKE_CXX_STANDARD 98)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# --------------------------------------------------------------------
# Warning policy (portable across MSVC 2010 / GCC 4.x era)
# --------------------------------------------------------------------
if(MSVC)
    set(_dom_warning_flags
        /W4
        /WX-
        /D_CRT_SECURE_NO_WARNINGS
        /permissive-
        $<$<COMPILE_LANGUAGE:CXX>:/GR->
        $<$<COMPILE_LANGUAGE:CXX>:/D_HAS_EXCEPTIONS=0>
    )
else()
    set(_dom_warning_flags
        -Wall
        -Wextra
        -Wpedantic
        -Wno-unused-parameter
        $<$<COMPILE_LANGUAGE:C>:-Wdeclaration-after-statement>
        $<$<COMPILE_LANGUAGE:C>:-Wvla>
        $<$<COMPILE_LANGUAGE:C>:-Wlong-long>
        $<$<AND:$<COMPILE_LANGUAGE:C>,$<C_COMPILER_ID:Clang>>:-Wc99-extensions>
        $<$<COMPILE_LANGUAGE:CXX>:-Wlong-long>
        $<$<AND:$<COMPILE_LANGUAGE:CXX>,$<CXX_COMPILER_ID:Clang>>:-Wc++98-compat-pedantic>
        $<$<COMPILE_LANGUAGE:CXX>:-fno-exceptions>
        $<$<COMPILE_LANGUAGE:CXX>:-fno-rtti>
    )
endif()

add_compile_options(${_dom_warning_flags})

# --------------------------------------------------------------------
# Subdirectories
# --------------------------------------------------------------------
add_subdirectory(engine)
add_subdirectory(runtime)
add_subdirectory(launcher)
add_subdirectory(tools)
add_subdirectory(tests)

message(STATUS "Dominium core build configured")
