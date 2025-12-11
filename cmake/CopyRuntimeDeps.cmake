# This script runs at build-time to copy runtime DLL dependencies next to an executable.

if(NOT DEFINED INPUT OR NOT DEFINED OUTPUT_DIR)
    message(FATAL_ERROR "CopyRuntimeDeps.cmake: INPUT and OUTPUT_DIR must be defined")
endif()

set(_search_dirs "")
if(DEFINED SEARCH_DIRS)
    set(_search_dirs ${SEARCH_DIRS})
endif()

file(GET_RUNTIME_DEPENDENCIES
    EXECUTABLES "${INPUT}"
    RESOLVED_DEPENDENCIES_VAR _resolved
    UNRESOLVED_DEPENDENCIES_VAR _unresolved
    DIRECTORIES ${_search_dirs}
    POST_EXCLUDE_REGEXES ".*[Ss]ystem32/.*" ".*[Ww]indows/.*"
)

foreach(dep IN LISTS _resolved)
    if(NOT EXISTS "${dep}")
        continue()
    endif()
    get_filename_component(dep_name "${dep}" NAME)
    file(COPY "${dep}" DESTINATION "${OUTPUT_DIR}")
endforeach()

if(_unresolved)
    message(WARNING "Unresolved runtime dependencies for ${INPUT}: ${_unresolved}")
endif()
