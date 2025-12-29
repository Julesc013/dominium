cmake_minimum_required(VERSION 3.16)

add_subdirectory(common)
add_subdirectory(game)
add_subdirectory(launcher)
add_subdirectory(setup)
add_subdirectory(providers)
add_subdirectory(tools)

set(DOM_KERNEL_ALLOWED_LINK_LIBS
    core_tlv
    core_audit
    core_util
    core_err
    core_log
    core_job
)

function(dom_check_kernel_links target_name)
    if(NOT TARGET ${target_name})
        message(FATAL_ERROR "Kernel target '${target_name}' is missing")
    endif()
    get_target_property(_dom_kernel_links ${target_name} LINK_LIBRARIES)
    if(NOT _dom_kernel_links OR _dom_kernel_links STREQUAL "LINK_LIBRARIES-NOTFOUND")
        set(_dom_kernel_links "")
    endif()
    foreach(_lib IN LISTS _dom_kernel_links)
        if(_lib MATCHES "^\\$<")
            continue()
        endif()
        list(FIND DOM_KERNEL_ALLOWED_LINK_LIBS "${_lib}" _idx)
        if(_idx EQUAL -1)
            message(FATAL_ERROR "Kernel target '${target_name}' links forbidden library '${_lib}'")
        endif()
    endforeach()
endfunction()

dom_check_kernel_links(dominium_launcher_core)
dom_check_kernel_links(dsu_core)

find_program(DOMINIUM_PYTHON NAMES python3 python)
if(DOMINIUM_PYTHON)
    add_test(
        NAME dominium_layer_checks
        COMMAND ${DOMINIUM_PYTHON} ${CMAKE_SOURCE_DIR}/scripts/check_layers.py --build-dir ${CMAKE_BINARY_DIR}
    )
else()
    message(WARNING "Python not found; dominium_layer_checks disabled")
endif()
