if(NOT DEFINED DOM_DIST_ROOT OR DOM_DIST_ROOT STREQUAL "")
    message(FATAL_ERROR "dominium_dist_meta: DOM_DIST_ROOT is required")
endif()

if(NOT EXISTS "${DOM_DIST_ROOT}")
    message(FATAL_ERROR "dominium_dist_meta: dist root does not exist: ${DOM_DIST_ROOT}")
endif()

file(MAKE_DIRECTORY "${DOM_DIST_ROOT}/meta")

set(_os "${DOM_DIST_OS}")
set(_arch "${DOM_DIST_ARCH}")
set(_variant "${DOM_DIST_VARIANT}")
set(_config "${DOM_DIST_CONFIG}")
set(_generator "${DOM_DIST_GENERATOR}")
set(_project "${DOM_DIST_PROJECT}")
set(_build_id "${DOM_BUILD_ID}")
set(_toolchain "${DOM_TOOLCHAIN_ID}")
set(_git "${DOM_GIT_HASH}")
set(_version "${DOM_PROJECT_SEMVER}")

if(_generator STREQUAL "")
    set(_generator "unknown")
endif()
if(_project STREQUAL "")
    set(_project "DominiumDomino")
endif()
if(_build_id STREQUAL "")
    set(_build_id "unknown")
endif()
if(_toolchain STREQUAL "")
    set(_toolchain "unknown")
endif()
if(_git STREQUAL "")
    set(_git "unknown")
endif()
if(_version STREQUAL "")
    set(_version "0.0.0")
endif()

file(GLOB_RECURSE _all_rel RELATIVE "${DOM_DIST_ROOT}" "${DOM_DIST_ROOT}/*")
set(_files "")
foreach(_rel IN LISTS _all_rel)
    if(IS_DIRECTORY "${DOM_DIST_ROOT}/${_rel}")
        continue()
    endif()
    if(_rel MATCHES "^meta/")
        continue()
    endif()
    file(TO_CMAKE_PATH "${_rel}" _rel_norm)
    list(APPEND _files "${_rel_norm}")
endforeach()
list(SORT _files)

set(_json_entries "")
set(_hash_lines "")
foreach(_rel IN LISTS _files)
    set(_abs "${DOM_DIST_ROOT}/${_rel}")
    file(SIZE "${_abs}" _size)
    file(SHA256 "${_abs}" _sha)
    list(APPEND _json_entries "    {\"path\":\"${_rel}\",\"size\":${_size},\"sha256\":\"${_sha}\"}")
    list(APPEND _hash_lines "${_sha}  ${_rel}")
endforeach()

if(_json_entries)
    string(JOIN ",\n" _json_body ${_json_entries})
else()
    set(_json_body "")
endif()

set(_files_json "{\n  \"schema\": 1,\n  \"files\": [\n${_json_body}\n  ]\n}\n")
file(WRITE "${DOM_DIST_ROOT}/meta/files.json" "${_files_json}")

if(_hash_lines)
    string(JOIN "\n" _hash_text ${_hash_lines})
    file(WRITE "${DOM_DIST_ROOT}/meta/hash.txt" "${_hash_text}\n")
else()
    file(WRITE "${DOM_DIST_ROOT}/meta/hash.txt" "")
endif()

set(_dist_json "{\n  \"schema\": 1,\n  \"generator\": \"cmake\",\n  \"project\": \"${_project}\",\n  \"build\": {\n    \"id\": \"${_build_id}\",\n    \"toolchain\": \"${_toolchain}\",\n    \"generator\": \"${_generator}\",\n    \"config\": \"${_config}\",\n    \"os\": \"${_os}\",\n    \"arch\": \"${_arch}\",\n    \"variant\": \"${_variant}\"\n  }\n}\n")
file(WRITE "${DOM_DIST_ROOT}/meta/dist.json" "${_dist_json}")

set(_targets_json "{\n  \"schema\": 1,\n  \"targets\": [\n    {\"os\":\"${_os}\",\"arch\":\"${_arch}\",\"variant\":\"${_variant}\",\"config\":\"${_config}\"}\n  ]\n}\n")
file(WRITE "${DOM_DIST_ROOT}/meta/targets.json" "${_targets_json}")

set(_build_txt
    "toolchain=${_toolchain}\n"
    "generator=${_generator}\n"
    "config=${_config}\n"
    "build_id=${_build_id}\n"
    "git=${_git}\n"
)
file(WRITE "${DOM_DIST_ROOT}/meta/build.txt" "${_build_txt}")

file(WRITE "${DOM_DIST_ROOT}/meta/ver.txt" "${_version}\n")

set(_rules_txt
    "dist_root=dist\n"
    "charset=a-z0-9_.-\n"
    "no_spaces=1\n"
    "no_build_config_dirs=1\n"
    "symbols_root=dist/sym\n"
    "runtime_root=dist/sys\n"
    "max_depth=16\n"
    "no_version_in_filenames=1\n"
)
file(WRITE "${DOM_DIST_ROOT}/meta/rules.txt" "${_rules_txt}")
