if(NOT DEFINED DOM_DIST_ROOT OR DOM_DIST_ROOT STREQUAL "")
    message(FATAL_ERROR "validate_dist: DOM_DIST_ROOT is required")
endif()
if(NOT EXISTS "${DOM_DIST_ROOT}")
    message(FATAL_ERROR "validate_dist: dist root does not exist: ${DOM_DIST_ROOT}")
endif()
if(NOT DEFINED DOM_DIST_LEAF OR DOM_DIST_LEAF STREQUAL "")
    message(FATAL_ERROR "validate_dist: DOM_DIST_LEAF is required")
endif()

set(_required_top
    "${DOM_DIST_ROOT}/meta"
    "${DOM_DIST_ROOT}/docs"
    "${DOM_DIST_ROOT}/res"
    "${DOM_DIST_ROOT}/cfg"
    "${DOM_DIST_ROOT}/sys"
    "${DOM_DIST_ROOT}/pkg"
    "${DOM_DIST_ROOT}/redist"
    "${DOM_DIST_ROOT}/sym"
)
foreach(_dir IN LISTS _required_top)
    if(NOT EXISTS "${_dir}")
        message(FATAL_ERROR "validate_dist: missing required dir: ${_dir}")
    endif()
endforeach()

set(_required_meta
    "${DOM_DIST_ROOT}/meta/dist.json"
    "${DOM_DIST_ROOT}/meta/targets.json"
    "${DOM_DIST_ROOT}/meta/files.json"
    "${DOM_DIST_ROOT}/meta/build.txt"
    "${DOM_DIST_ROOT}/meta/ver.txt"
    "${DOM_DIST_ROOT}/meta/hash.txt"
    "${DOM_DIST_ROOT}/meta/rules.txt"
)
foreach(_file IN LISTS _required_meta)
    if(NOT EXISTS "${_file}")
        message(FATAL_ERROR "validate_dist: missing required meta file: ${_file}")
    endif()
endforeach()

set(_required_leaf_dirs
    "${DOM_DIST_LEAF}/bin/launch"
    "${DOM_DIST_LEAF}/bin/game"
    "${DOM_DIST_LEAF}/bin/engine"
    "${DOM_DIST_LEAF}/bin/rend"
    "${DOM_DIST_LEAF}/bin/tools"
    "${DOM_DIST_LEAF}/bin/share"
    "${DOM_DIST_LEAF}/lib"
    "${DOM_DIST_LEAF}/etc"
    "${DOM_DIST_LEAF}/man"
)
foreach(_dir IN LISTS _required_leaf_dirs)
    if(NOT EXISTS "${_dir}")
        message(FATAL_ERROR "validate_dist: missing leaf dir: ${_dir}")
    endif()
endforeach()

set(_required_leaf_files
    "${DOM_DIST_LEAF}/etc/leaf.json"
    "${DOM_DIST_LEAF}/man/readme.txt"
)
foreach(_file IN LISTS _required_leaf_files)
    if(NOT EXISTS "${_file}")
        message(FATAL_ERROR "validate_dist: missing leaf file: ${_file}")
    endif()
endforeach()

function(_dom_check_segment seg rel_path)
    if("${seg}" STREQUAL "")
        return()
    endif()
    if("${seg}" MATCHES "[^a-z0-9_.-]")
        message(FATAL_ERROR "validate_dist: forbidden character in path: ${rel_path}")
    endif()
    if("${seg}" MATCHES "^-")
        message(FATAL_ERROR "validate_dist: leading '-' in path: ${rel_path}")
    endif()
    if("${seg}" MATCHES "\\.$")
        message(FATAL_ERROR "validate_dist: trailing '.' in path: ${rel_path}")
    endif()
    string(TOLOWER "${seg}" _seg_lower)
    if(NOT _seg_lower STREQUAL "${seg}")
        message(FATAL_ERROR "validate_dist: uppercase character in path: ${rel_path}")
    endif()
    if(_seg_lower MATCHES "^(con|prn|aux|nul|com[1-9]|lpt[1-9])$")
        message(FATAL_ERROR "validate_dist: forbidden dos device name in path: ${rel_path}")
    endif()
endfunction()

file(GLOB_RECURSE _all_paths LIST_DIRECTORIES true "${DOM_DIST_ROOT}/*")
foreach(_path IN LISTS _all_paths)
    file(RELATIVE_PATH _rel_raw "${DOM_DIST_ROOT}" "${_path}")
    file(TO_CMAKE_PATH "${_rel_raw}" _rel)
    if(_rel STREQUAL "" OR _rel STREQUAL ".")
        continue()
    endif()
    if(_rel MATCHES " ")
        message(FATAL_ERROR "validate_dist: space in path: ${_rel}")
    endif()

    string(REPLACE "/" ";" _parts "${_rel}")
    list(LENGTH _parts _depth)
    if(_depth GREATER 16)
        message(FATAL_ERROR "validate_dist: path depth exceeds 16: ${_rel}")
    endif()
    foreach(_seg IN LISTS _parts)
        _dom_check_segment("${_seg}" "${_rel}")
    endforeach()
endforeach()

set(_files_manifest "${DOM_DIST_ROOT}/meta/files.json")
if(EXISTS "${_files_manifest}")
    file(READ "${_files_manifest}" _manifest_text)
    string(REGEX MATCHALL "\"path\"[ \t]*:[ \t]*\"[^\"]+\"" _path_matches "${_manifest_text}")
    foreach(_match IN LISTS _path_matches)
        string(REGEX REPLACE "^.*\"([^\"]+)\"$" "\\1" _rel_path "${_match}")
        if(NOT EXISTS "${DOM_DIST_ROOT}/${_rel_path}")
            message(FATAL_ERROR "validate_dist: files.json entry missing on disk: ${_rel_path}")
        endif()
    endforeach()
endif()
