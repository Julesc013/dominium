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
# Build toggles
# --------------------------------------------------------------------
option(DOM_BUILD_LAUNCHER "Build dom_launcher multi-mode launcher" ON)
option(DOM_BUILD_SETUP "Build dom_setup install/repair tool" ON)

# --------------------------------------------------------------------
# MinGW static runtime (avoid libstdc++/libgcc DLL dependency)
# --------------------------------------------------------------------
if(MINGW)
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -static -static-libstdc++ -static-libgcc -Wl,-Bstatic -lwinpthread -Wl,-Bdynamic")
    # Helper to copy MinGW runtime DLLs next to executables (fallback if static link is ineffective)
    get_filename_component(_CXX_DIR "${CMAKE_CXX_COMPILER}" DIRECTORY)
    set(_STDCPP_DLL "${_CXX_DIR}/libstdc++-6.dll")
    set(_GCC_DLL_SEH "${_CXX_DIR}/libgcc_s_seh-1.dll")
    set(_GCC_DLL_DW2 "${_CXX_DIR}/libgcc_s_dw2-1.dll")
    set(_WINPTHREAD_DLL "${_CXX_DIR}/libwinpthread-1.dll")
    function(dom_copy_mingw_runtime target_name)
        if(EXISTS "${_STDCPP_DLL}")
            add_custom_command(TARGET ${target_name} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy_if_different "${_STDCPP_DLL}" $<TARGET_FILE_DIR:${target_name}>
                COMMENT "Copying libstdc++ runtime for ${target_name}")
        endif()
        if(EXISTS "${_GCC_DLL_SEH}")
            add_custom_command(TARGET ${target_name} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy_if_different "${_GCC_DLL_SEH}" $<TARGET_FILE_DIR:${target_name}>
                COMMENT "Copying libgcc (seh) runtime for ${target_name}")
        elseif(EXISTS "${_GCC_DLL_DW2}")
            add_custom_command(TARGET ${target_name} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy_if_different "${_GCC_DLL_DW2}" $<TARGET_FILE_DIR:${target_name}>
                COMMENT "Copying libgcc (dw2) runtime for ${target_name}")
        endif()
        if(EXISTS "${_WINPTHREAD_DLL}")
            add_custom_command(TARGET ${target_name} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy_if_different "${_WINPTHREAD_DLL}" $<TARGET_FILE_DIR:${target_name}>
                COMMENT "Copying winpthread runtime for ${target_name}")
        endif()
    endfunction()
endif()

# --------------------------------------------------------------------
# Subdirectories
# --------------------------------------------------------------------
add_subdirectory(shared)
add_subdirectory(engine)
add_subdirectory(runtime)
if(DOM_BUILD_SETUP)
    add_subdirectory(setup)
endif()
if(DOM_BUILD_LAUNCHER)
    add_subdirectory(launcher)
endif()
add_subdirectory(tools)
add_subdirectory(tests)

message(STATUS "Dominium core build configured")
