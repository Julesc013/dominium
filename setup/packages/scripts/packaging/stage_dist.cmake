# Deterministic staging script for portable packages.
#
# Inputs (required):
#   - DIST_DIR: output staging root (bundle root / DOMINIUM_HOME).
#   - VERSION: version string for repo/products/<version>.
#   - LAUNCHER_BIN: full path to built dominium-launcher binary.
#   - GAME_BIN: full path to built dominium_game binary.
#   - SETUP_BIN: full path to built dominium-setup binary (optional tool).
#   - CONFIGURED_BIN_DIR: directory with configured wrapper scripts.
#   - SOURCE_DIR: repository root (for LICENSE, etc).

if(NOT DEFINED DIST_DIR OR DIST_DIR STREQUAL "")
    message(FATAL_ERROR "stage_dist.cmake: DIST_DIR is required")
endif()
if(NOT DEFINED VERSION OR VERSION STREQUAL "")
    message(FATAL_ERROR "stage_dist.cmake: VERSION is required")
endif()
if(NOT DEFINED LAUNCHER_BIN OR LAUNCHER_BIN STREQUAL "")
    message(FATAL_ERROR "stage_dist.cmake: LAUNCHER_BIN is required")
endif()
if(NOT DEFINED GAME_BIN OR GAME_BIN STREQUAL "")
    message(FATAL_ERROR "stage_dist.cmake: GAME_BIN is required")
endif()

set(_stage "${DIST_DIR}")
file(REMOVE_RECURSE "${_stage}")
file(MAKE_DIRECTORY "${_stage}")

file(MAKE_DIRECTORY
    "${_stage}/bin"
    "${_stage}/repo/products/game/${VERSION}/bin"
    "${_stage}/repo/mods"
    "${_stage}/repo/packs"
    "${_stage}/instances"
    "${_stage}/temp"
)

function(_dom_copy_sidecars src_exe dst_dir)
    if(NOT EXISTS "${src_exe}")
        message(FATAL_ERROR "stage_dist.cmake: missing source binary: ${src_exe}")
    endif()
    file(COPY "${src_exe}" DESTINATION "${dst_dir}")

    get_filename_component(_src_dir "${src_exe}" DIRECTORY)

    # Copy common runtime sidecars next to the executable when present.
    file(GLOB _dlls "${_src_dir}/*.dll")
    file(GLOB _dylibs "${_src_dir}/*.dylib")
    file(GLOB _sos "${_src_dir}/*.so" "${_src_dir}/*.so.*")

    foreach(_f IN LISTS _dlls _dylibs _sos)
        if(EXISTS "${_f}")
            file(COPY "${_f}" DESTINATION "${dst_dir}")
        endif()
    endforeach()
endfunction()

_dom_copy_sidecars("${LAUNCHER_BIN}" "${_stage}/bin")
_dom_copy_sidecars("${GAME_BIN}" "${_stage}/repo/products/game/${VERSION}/bin")

if(DEFINED SETUP_BIN AND NOT SETUP_BIN STREQUAL "" AND EXISTS "${SETUP_BIN}")
    _dom_copy_sidecars("${SETUP_BIN}" "${_stage}/bin")
endif()

# Wrapper scripts (portable entrypoints).
if(DEFINED CONFIGURED_BIN_DIR AND EXISTS "${CONFIGURED_BIN_DIR}")
    if(EXISTS "${CONFIGURED_BIN_DIR}/dominium.cmd")
        file(COPY "${CONFIGURED_BIN_DIR}/dominium.cmd" DESTINATION "${_stage}/bin")
    endif()
    if(EXISTS "${CONFIGURED_BIN_DIR}/dominium")
        file(COPY "${CONFIGURED_BIN_DIR}/dominium" DESTINATION "${_stage}/bin")
        file(CHMOD "${_stage}/bin/dominium"
            PERMISSIONS
                OWNER_READ OWNER_WRITE OWNER_EXECUTE
                GROUP_READ GROUP_EXECUTE
                WORLD_READ WORLD_EXECUTE)
    endif()
endif()

# Top-level docs/licenses.
if(DEFINED SOURCE_DIR AND EXISTS "${SOURCE_DIR}/LICENSE")
    file(COPY "${SOURCE_DIR}/LICENSE" DESTINATION "${_stage}")
endif()
if(DEFINED SOURCE_DIR AND EXISTS "${SOURCE_DIR}/README.md")
    file(COPY "${SOURCE_DIR}/README.md" DESTINATION "${_stage}")
endif()

file(WRITE "${_stage}/.stage_stamp" "dominium_stage=1\nversion=${VERSION}\n")

