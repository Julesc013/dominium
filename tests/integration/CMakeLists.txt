cmake_minimum_required(VERSION 3.16)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

file(MAKE_DIRECTORY "${CMAKE_BINARY_DIR}/tests")
set(_dom_gui_deps_report "${CMAKE_BINARY_DIR}/tests/gui_deps_report.txt")

set(_dom_gui_forbidden_tokens
    "SDL2::SDL2"
    "SDL2"
    "OpenGL::GL"
    "OpenGL::OpenGL"
    "opengl32"
    "GLU"
    "EGL"
    "GLESv2"
    "Vulkan::Vulkan"
    "vulkan-1"
    "vulkan"
    "d3d9"
    "d3d11"
    "dxgi"
    "X11"
    "Xrandr"
    "Xinerama"
    "Xcursor"
    "Xi"
    "wayland-client"
    "wayland-egl"
    "AppKit"
    "Cocoa"
    "UIKit"
    "Metal"
    "QuartzCore"
    "dom_render_backend_"
    "dom_platform_backend_"
    "dui"
    "dgui"
)

get_property(_dom_all_targets GLOBAL PROPERTY TARGETS)
set(_dom_test_targets "")
file(TO_CMAKE_PATH "${CMAKE_SOURCE_DIR}" _dom_repo_root)
string(REGEX REPLACE "([][+.*()^$?{}|\\\\])" "\\\\\\1" _dom_repo_root_regex "${_dom_repo_root}")
foreach(_dom_target IN LISTS _dom_all_targets)
    get_target_property(_dom_type ${_dom_target} TYPE)
    if(NOT _dom_type STREQUAL "EXECUTABLE")
        continue()
    endif()
    get_target_property(_dom_src_dir ${_dom_target} SOURCE_DIR)
    if(NOT _dom_src_dir OR _dom_src_dir STREQUAL "SOURCE_DIR-NOTFOUND")
        continue()
    endif()
    file(TO_CMAKE_PATH "${_dom_src_dir}" _dom_src_dir_norm)
    if(_dom_src_dir_norm MATCHES "^${_dom_repo_root_regex}/(tests|engine/tests|game/tests)(/|$)")
        list(APPEND _dom_test_targets ${_dom_target})
    endif()
endforeach()

file(WRITE "${_dom_gui_deps_report}" "report_version=1\n")
foreach(_dom_target IN LISTS _dom_test_targets)
    get_target_property(_dom_links ${_dom_target} LINK_LIBRARIES)
    if(_dom_links STREQUAL "LINK_LIBRARIES-NOTFOUND")
        set(_dom_links "")
    endif()
    set(_dom_links_clean "")
    foreach(_dom_link IN LISTS _dom_links)
        if(_dom_link STREQUAL "debug" OR _dom_link STREQUAL "optimized" OR _dom_link STREQUAL "general")
            continue()
        endif()
        list(APPEND _dom_links_clean "${_dom_link}")
        foreach(_dom_token IN LISTS _dom_gui_forbidden_tokens)
            string(FIND "${_dom_link}" "${_dom_token}" _dom_idx)
            if(NOT _dom_idx EQUAL -1)
                file(APPEND "${_dom_gui_deps_report}" "violation=${_dom_target}|${_dom_link}|${_dom_token}\n")
            endif()
        endforeach()
    endforeach()
    string(REPLACE ";" "," _dom_links_text "${_dom_links_clean}")
    file(APPEND "${_dom_gui_deps_report}" "target=${_dom_target}\n")
    file(APPEND "${_dom_gui_deps_report}" "links=${_dom_links_text}\n")
endforeach()

dom_add_testx(NAME build_test_gui_deps
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test_gui_deps.py
        --report ${_dom_gui_deps_report}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)
