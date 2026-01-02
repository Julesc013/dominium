option(DOMINIUM_BUNDLE_RUNTIME_DEPS "Bundle runtime DLLs next to built executables" ON)

set(DOMINIUM_RUNTIME_SEARCH_DIRS "" CACHE STRING "Hint directories to search for runtime DLLs")

function(dominium_bundle_runtime target_name)
    if(NOT DOMINIUM_BUNDLE_RUNTIME_DEPS)
        return()
    endif()
    if(NOT WIN32)
        return()
    endif()
    if(NOT TARGET ${target_name})
        return()
    endif()

    set(_dom_runtime_search_dirs "${DOMINIUM_RUNTIME_SEARCH_DIRS}")
    if(WIN32 AND _dom_runtime_search_dirs STREQUAL "")
        if(CMAKE_CXX_COMPILER)
            get_filename_component(_dom_runtime_search_dirs "${CMAKE_CXX_COMPILER}" DIRECTORY)
        elseif(CMAKE_C_COMPILER)
            get_filename_component(_dom_runtime_search_dirs "${CMAKE_C_COMPILER}" DIRECTORY)
        endif()
    endif()

    add_custom_command(TARGET ${target_name} POST_BUILD
        COMMAND ${CMAKE_COMMAND}
            -DINPUT=$<TARGET_FILE:${target_name}>
            -DOUTPUT_DIR=$<TARGET_FILE_DIR:${target_name}>
            -DSEARCH_DIRS=${_dom_runtime_search_dirs}
            -P "${CMAKE_SOURCE_DIR}/cmake/CopyRuntimeDeps.cmake"
        VERBATIM
    )
endfunction()
