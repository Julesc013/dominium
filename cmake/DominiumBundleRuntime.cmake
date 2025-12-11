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

    add_custom_command(TARGET ${target_name} POST_BUILD
        COMMAND ${CMAKE_COMMAND}
            -DINPUT=$<TARGET_FILE:${target_name}>
            -DOUTPUT_DIR=$<TARGET_FILE_DIR:${target_name}>
            -DSEARCH_DIRS=${DOMINIUM_RUNTIME_SEARCH_DIRS}
            -P "${CMAKE_SOURCE_DIR}/cmake/CopyRuntimeDeps.cmake"
        VERBATIM
    )
endfunction()
