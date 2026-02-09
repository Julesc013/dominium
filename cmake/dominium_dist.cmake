include_guard(GLOBAL)

function(_dominium_dist_normalize_token out_var in_value)
    string(TOLOWER "${in_value}" _value)
    if(_value STREQUAL "")
        set(${out_var} "" PARENT_SCOPE)
        return()
    endif()
    string(REGEX MATCH "^[a-z0-9_]+$" _ok "${_value}")
    if(NOT _ok)
        message(FATAL_ERROR "dominium_dist: token '${in_value}' contains forbidden characters; use [a-z0-9_]")
    endif()
    set(${out_var} "${_value}" PARENT_SCOPE)
endfunction()

function(_dominium_dist_detect_os out_var)
    if(WIN32)
        set(_os "winnt")
    elseif(APPLE)
        set(_os "macosx")
    elseif(CMAKE_SYSTEM_NAME STREQUAL "Emscripten")
        set(_os "web")
    elseif(ANDROID OR CMAKE_SYSTEM_NAME STREQUAL "Android")
        set(_os "android")
    elseif(IOS OR CMAKE_SYSTEM_NAME STREQUAL "iOS")
        set(_os "ios")
    elseif(CMAKE_SYSTEM_NAME MATCHES ".*BSD")
        set(_os "bsd")
    elseif(CMAKE_SYSTEM_NAME STREQUAL "Linux")
        set(_os "linux")
    else()
        string(TOLOWER "${CMAKE_SYSTEM_NAME}" _os)
    endif()
    set(${out_var} "${_os}" PARENT_SCOPE)
endfunction()

function(_dominium_dist_detect_arch out_var)
    set(_arch_raw "${CMAKE_SYSTEM_PROCESSOR}")
    if(_arch_raw STREQUAL "")
        set(_arch_raw "${CMAKE_HOST_SYSTEM_PROCESSOR}")
    endif()
    string(TOLOWER "${_arch_raw}" _arch)
    if(_arch MATCHES "^(amd64|x86_64|x64)$")
        set(_arch "x64")
    elseif(_arch MATCHES "^(i[3-6]86|x86)$")
        set(_arch "x86")
    elseif(_arch MATCHES "^(aarch64|arm64)$")
        set(_arch "arm64")
    elseif(_arch MATCHES "^(wasm32)$")
        set(_arch "wasm")
    endif()
    set(${out_var} "${_arch}" PARENT_SCOPE)
endfunction()

function(dominium_dist_init)
    cmake_parse_arguments(DIST "" "DIST_ROOT;DIST_OS;DIST_ARCH;DIST_VARIANT" "" ${ARGN})

    if(DIST_DIST_ROOT)
        set(_root "${DIST_DIST_ROOT}")
    else()
        set(_root "${CMAKE_SOURCE_DIR}/dist")
    endif()
    get_filename_component(_root_abs "${_root}" ABSOLUTE)

    _dominium_dist_normalize_token(_os_override "${DIST_DIST_OS}")
    _dominium_dist_normalize_token(_arch_override "${DIST_DIST_ARCH}")
    _dominium_dist_normalize_token(_variant_norm "${DIST_DIST_VARIANT}")

    if(_os_override STREQUAL "")
        _dominium_dist_detect_os(_os_detected)
        set(_os "${_os_detected}")
    else()
        set(_os "${_os_override}")
    endif()

    if(_arch_override STREQUAL "")
        _dominium_dist_detect_arch(_arch_detected)
        set(_arch "${_arch_detected}")
    else()
        set(_arch "${_arch_override}")
    endif()

    if(_arch STREQUAL "wasm" AND NOT _os STREQUAL "web")
        set(_os "web")
    endif()

    _dominium_dist_normalize_token(_os_norm "${_os}")
    _dominium_dist_normalize_token(_arch_norm "${_arch}")
    set(_os "${_os_norm}")
    set(_arch "${_arch_norm}")

    if(_os STREQUAL "")
        message(FATAL_ERROR "dominium_dist_init: unable to resolve dist os token")
    endif()
    if(_arch STREQUAL "")
        message(FATAL_ERROR "dominium_dist_init: unable to resolve dist arch token")
    endif()

    set(_leaf "${_root_abs}/sys/${_os}/${_arch}")
    set(_sym_leaf "${_root_abs}/sym/${_os}/${_arch}")
    if(NOT _variant_norm STREQUAL "")
        set(_leaf "${_leaf}/${_variant_norm}")
        set(_sym_leaf "${_sym_leaf}/${_variant_norm}")
    endif()

    set(_bin_root "${_leaf}/bin")
    set(_bin_launch "${_bin_root}/launch")
    set(_bin_game "${_bin_root}/game")
    set(_bin_engine "${_bin_root}/engine")
    set(_bin_rend "${_bin_root}/rend")
    set(_bin_tools "${_bin_root}/tools")
    set(_bin_share "${_bin_root}/share")

    set(_lib_dir "${_leaf}/lib")
    set(_etc_dir "${_leaf}/etc")
    set(_man_dir "${_leaf}/man")

    set(_sym_bin_root "${_sym_leaf}/bin")
    set(_sym_lib_dir "${_sym_leaf}/lib")

    set(_required_dirs
        "${_root_abs}/meta"
        "${_root_abs}/docs"
        "${_root_abs}/res"
        "${_root_abs}/res/common"
        "${_root_abs}/res/locale"
        "${_root_abs}/res/packs"
        "${_root_abs}/cfg"
        "${_root_abs}/cfg/default"
        "${_root_abs}/cfg/profiles"
        "${_root_abs}/cfg/schemas"
        "${_root_abs}/sys"
        "${_leaf}"
        "${_bin_launch}"
        "${_bin_game}"
        "${_bin_engine}"
        "${_bin_rend}"
        "${_bin_tools}"
        "${_bin_share}"
        "${_lib_dir}"
        "${_etc_dir}"
        "${_man_dir}"
        "${_root_abs}/pkg"
        "${_root_abs}/pkg/winnt"
        "${_root_abs}/pkg/win9x"
        "${_root_abs}/pkg/win16"
        "${_root_abs}/pkg/dos"
        "${_root_abs}/pkg/macosx"
        "${_root_abs}/pkg/macclassic"
        "${_root_abs}/pkg/linux"
        "${_root_abs}/pkg/android"
        "${_root_abs}/pkg/ios"
        "${_root_abs}/pkg/web"
        "${_root_abs}/redist"
        "${_root_abs}/redist/msvc"
        "${_root_abs}/redist/dx"
        "${_root_abs}/redist/other"
        "${_root_abs}/sym"
        "${_sym_leaf}"
        "${_sym_bin_root}/launch"
        "${_sym_bin_root}/game"
        "${_sym_bin_root}/engine"
        "${_sym_bin_root}/rend"
        "${_sym_bin_root}/tools"
        "${_sym_bin_root}/share"
        "${_sym_lib_dir}"
    )
    file(MAKE_DIRECTORY ${_required_dirs})

    set(_leaf_json "{\n  \"schema\": 1,\n  \"os\": \"${_os}\",\n  \"arch\": \"${_arch}\",\n  \"variant\": \"${_variant_norm}\"\n}\n")
    file(WRITE "${_etc_dir}/leaf.json" "${_leaf_json}")
    file(WRITE "${_man_dir}/readme.txt"
        "dominium dist leaf\nos: ${_os}\narch: ${_arch}\nvariant: ${_variant_norm}\n")

    file(WRITE "${_root_abs}/docs/readme.txt"
        "dominium dist\n"
        "purpose: final post-link outputs only\n"
        "intermediates: stay in build/*\n"
        "how to build:\n"
        "  cmake --preset msvc-debug\n"
        "  cmake --build --preset msvc-debug\n"
        "  cmake --preset msys2-debug\n"
        "  cmake --build --preset msys2-debug\n"
        "runtime seed (portable/user/system):\n"
        "  dist/sys/<os>/<arch>/.dsu/installed_state.dsustate\n"
        "  dist/sys/<os>/<arch>/dominium_install.json\n"
        "  dist/sys/<os>/<arch>/repo/{products,packs,mods}\n"
        "  dist/sys/<os>/<arch>/{instances,artifacts,audit,exports,temp}\n"
        "seed target:\n"
        "  cmake --build <builddir> --target dist_seed\n"
        "seed options:\n"
        "  -DDOM_DIST_INSTALL_TYPE=portable|user|system\n"
        "  -DDOM_DIST_BUILD_CHANNEL=dev|beta|stable\n"
        "what ships:\n"
        "  dist/sys/<os>/<arch>/bin/*\n"
        "  dist/sys/<os>/<arch>/lib/*\n"
        "  dist/sym/<os>/<arch>/* (symbols)\n"
        "  dist/meta/* (metadata)\n"
        "repo docs: docs/BUILD_DIST.md, docs/build_output.md\n")

    if(EXISTS "${CMAKE_SOURCE_DIR}/LICENSE")
        file(READ "${CMAKE_SOURCE_DIR}/LICENSE" _license_text)
        file(WRITE "${_root_abs}/docs/licenses.txt" "${_license_text}")
    else()
        file(WRITE "${_root_abs}/docs/licenses.txt" "license file missing\n")
    endif()
    file(WRITE "${_root_abs}/docs/notes.txt" "release notes\n")

    set(DOM_DIST_ROOT "${_root_abs}" PARENT_SCOPE)
    set(DOM_DIST_OS "${_os}" PARENT_SCOPE)
    set(DOM_DIST_ARCH "${_arch}" PARENT_SCOPE)
    set(DOM_DIST_VARIANT "${_variant_norm}" PARENT_SCOPE)
    set(DOM_DIST_LEAF "${_leaf}" PARENT_SCOPE)
    set(DOM_DIST_SYM_LEAF "${_sym_leaf}" PARENT_SCOPE)
    set(DOM_DIST_BIN_LAUNCH "${_bin_launch}" PARENT_SCOPE)
    set(DOM_DIST_BIN_GAME "${_bin_game}" PARENT_SCOPE)
    set(DOM_DIST_BIN_ENGINE "${_bin_engine}" PARENT_SCOPE)
    set(DOM_DIST_BIN_REND "${_bin_rend}" PARENT_SCOPE)
    set(DOM_DIST_BIN_TOOLS "${_bin_tools}" PARENT_SCOPE)
    set(DOM_DIST_BIN_SHARE "${_bin_share}" PARENT_SCOPE)
    set(DOM_DIST_LIB "${_lib_dir}" PARENT_SCOPE)
    set(DOM_DIST_ETC "${_etc_dir}" PARENT_SCOPE)
    set(DOM_DIST_MAN "${_man_dir}" PARENT_SCOPE)
endfunction()

function(_dominium_dist_apply_output_dirs target runtime_dir sym_dir)
    if(NOT TARGET "${target}")
        message(FATAL_ERROR "dominium_dist_set_role: unknown target '${target}'")
    endif()

    set_target_properties("${target}" PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${runtime_dir}"
        LIBRARY_OUTPUT_DIRECTORY "${runtime_dir}"
        ARCHIVE_OUTPUT_DIRECTORY "${DOM_DIST_LIB}"
    )

    if(CMAKE_CONFIGURATION_TYPES)
        foreach(_cfg IN LISTS CMAKE_CONFIGURATION_TYPES)
            string(TOUPPER "${_cfg}" _cfg_upper)
            set_target_properties("${target}" PROPERTIES
                "RUNTIME_OUTPUT_DIRECTORY_${_cfg_upper}" "${runtime_dir}"
                "LIBRARY_OUTPUT_DIRECTORY_${_cfg_upper}" "${runtime_dir}"
                "ARCHIVE_OUTPUT_DIRECTORY_${_cfg_upper}" "${DOM_DIST_LIB}"
            )
        endforeach()
    endif()

    if(MSVC)
        set_target_properties("${target}" PROPERTIES
            PDB_OUTPUT_DIRECTORY "${sym_dir}"
            COMPILE_PDB_OUTPUT_DIRECTORY "${DOM_DIST_SYM_LEAF}/lib"
        )
        if(CMAKE_CONFIGURATION_TYPES)
            foreach(_cfg IN LISTS CMAKE_CONFIGURATION_TYPES)
                string(TOUPPER "${_cfg}" _cfg_upper)
                set_target_properties("${target}" PROPERTIES
                    "PDB_OUTPUT_DIRECTORY_${_cfg_upper}" "${sym_dir}"
                    "COMPILE_PDB_OUTPUT_DIRECTORY_${_cfg_upper}" "${DOM_DIST_SYM_LEAF}/lib"
                )
            endforeach()
        endif()
    endif()
endfunction()

function(dominium_dist_set_role target)
    cmake_parse_arguments(DIST "" "ROLE;NAME" "" ${ARGN})
    if(NOT DIST_ROLE)
        message(FATAL_ERROR "dominium_dist_set_role: ROLE is required")
    endif()

    string(TOLOWER "${DIST_ROLE}" _role)
    if(_role STREQUAL "launch")
        set(_runtime_dir "${DOM_DIST_BIN_LAUNCH}")
    elseif(_role STREQUAL "game")
        set(_runtime_dir "${DOM_DIST_BIN_GAME}")
    elseif(_role STREQUAL "engine")
        set(_runtime_dir "${DOM_DIST_BIN_ENGINE}")
    elseif(_role STREQUAL "rend")
        set(_runtime_dir "${DOM_DIST_BIN_REND}")
    elseif(_role STREQUAL "tools")
        set(_runtime_dir "${DOM_DIST_BIN_TOOLS}")
    elseif(_role STREQUAL "share")
        set(_runtime_dir "${DOM_DIST_BIN_SHARE}")
    else()
        message(FATAL_ERROR "dominium_dist_set_role: unknown role '${DIST_ROLE}'")
    endif()

    if(DIST_NAME)
        set_target_properties("${target}" PROPERTIES OUTPUT_NAME "${DIST_NAME}")
    endif()

    set(_sym_dir "${DOM_DIST_SYM_LEAF}/bin/${_role}")
    _dominium_dist_apply_output_dirs("${target}" "${_runtime_dir}" "${_sym_dir}")

    set_property(TARGET "${target}" PROPERTY DOM_DIST_ROLE "${_role}")
    set_property(GLOBAL APPEND PROPERTY DOM_DIST_ROLE_TARGETS "${target}")
endfunction()
