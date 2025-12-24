if(NOT DEFINED DOM_DIST_ROOT OR DOM_DIST_ROOT STREQUAL "")
    message(FATAL_ERROR "validate_dist: DOM_DIST_ROOT is required")
endif()
if(NOT EXISTS "${DOM_DIST_ROOT}")
    message(FATAL_ERROR "validate_dist: dist root does not exist: ${DOM_DIST_ROOT}")
endif()
if(NOT DEFINED DOM_DIST_LEAF OR DOM_DIST_LEAF STREQUAL "")
    message(FATAL_ERROR "validate_dist: DOM_DIST_LEAF is required")
endif()
if(NOT DEFINED DOM_DIST_VARIANT)
    set(DOM_DIST_VARIANT "")
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

file(GLOB _top_entries RELATIVE "${DOM_DIST_ROOT}" "${DOM_DIST_ROOT}/*")
set(_allowed_top meta docs res cfg sys pkg redist sym)
foreach(_entry IN LISTS _top_entries)
    if(_entry STREQUAL "")
        continue()
    endif()
    list(FIND _allowed_top "${_entry}" _idx)
    if(_idx EQUAL -1)
        message(FATAL_ERROR "validate_dist: unexpected top-level entry: ${_entry}")
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

function(_dom_check_segment seg rel_path is_file)
    if("${seg}" STREQUAL "")
        return()
    endif()
    if(is_file)
        set(_pattern "^[a-z0-9_.-]+$")
    else()
        set(_pattern "^[a-z0-9_]+$")
    endif()
    if(NOT "${seg}" MATCHES "${_pattern}")
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
    if(is_file)
        string(REGEX REPLACE "\\..*$" "" _base "${_seg_lower}")
    else()
        set(_base "${_seg_lower}")
    endif()
    if(_base MATCHES "^(con|prn|aux|nul|com[1-9]|lpt[1-9])$")
        message(FATAL_ERROR "validate_dist: forbidden dos device name in path: ${rel_path}")
    endif()
    set(_banned_segments debug release relwithdebinfo minsizerel cmake cmakefiles ninja msbuild msvc msys2)
    list(FIND _banned_segments "${_seg_lower}" _seg_banned)
    if(_seg_banned GREATER_EQUAL 0)
        if(NOT "${DOM_DIST_VARIANT}" STREQUAL "${_seg_lower}")
            message(FATAL_ERROR "validate_dist: build-system segment in path: ${rel_path}")
        endif()
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
    if(IS_DIRECTORY "${_path}")
        foreach(_seg IN LISTS _parts)
            _dom_check_segment("${_seg}" "${_rel}" FALSE)
        endforeach()
    else()
        list(LENGTH _parts _part_count)
        math(EXPR _dir_count "${_part_count} - 1")
        if(_dir_count GREATER 0)
            list(SUBLIST _parts 0 ${_dir_count} _dir_parts)
        else()
            set(_dir_parts "")
        endif()
        list(GET _parts -1 _file_seg)
        foreach(_seg IN LISTS _dir_parts)
            if(NOT _seg STREQUAL "")
                _dom_check_segment("${_seg}" "${_rel}" FALSE)
            endif()
        endforeach()
        _dom_check_segment("${_file_seg}" "${_rel}" TRUE)
    endif()

    if(NOT IS_DIRECTORY "${_path}")
        get_filename_component(_name "${_path}" NAME)
        string(TOLOWER "${_name}" _name_lower)
        get_filename_component(_ext "${_name_lower}" EXT)
        if(_ext STREQUAL ".pdb")
            if(NOT _rel MATCHES "^sym/")
                message(FATAL_ERROR "validate_dist: pdb outside sym: ${_rel}")
            endif()
        endif()
        set(_banned_ext .obj .o .pch .ipch .ilk .tlog .idb .iobj .ipdb)
        list(FIND _banned_ext "${_ext}" _ext_banned)
        if(_ext_banned GREATER_EQUAL 0)
            message(FATAL_ERROR "validate_dist: intermediate file in dist: ${_rel}")
        endif()
        set(_banned_names cmakecache.txt cmake_install.cmake build.ninja makefile .ninja_deps .ninja_log)
        list(FIND _banned_names "${_name_lower}" _name_banned)
        if(_name_banned GREATER_EQUAL 0)
            message(FATAL_ERROR "validate_dist: build system file in dist: ${_rel}")
        endif()
    endif()
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

message(STATUS "expected dist subtree (winnt/x64):")
message(STATUS "  dist/sys/winnt/x64/bin/launch/launch_dominium.exe")
message(STATUS "  dist/sys/winnt/x64/bin/game/game_dominium.exe")
message(STATUS "  dist/sys/winnt/x64/bin/engine/eng_domino.dll")
message(STATUS "  dist/sys/winnt/x64/bin/share/core_dominium.dll")
message(STATUS "  dist/sys/winnt/x64/bin/rend/rend_<backend>.dll")
message(STATUS "  dist/sys/winnt/x64/bin/tools/tool_<name>.exe")
message(STATUS "  dist/sys/winnt/x64/etc/leaf.json")
message(STATUS "  dist/sys/winnt/x64/man/readme.txt")
message(STATUS "  dist/sym/winnt/x64/bin/launch/launch_dominium.pdb")
