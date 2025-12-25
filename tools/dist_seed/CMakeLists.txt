cmake_minimum_required(VERSION 3.16)

add_executable(dominium_dist_seed
    dist_seed_state.c
)

set_target_properties(dominium_dist_seed PROPERTIES
    OUTPUT_NAME "dominium-dist-seed"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

if(DOM_DIST_SEED_RUNTIME)
    if(NOT DEFINED DOM_DIST_LEAF OR DOM_DIST_LEAF STREQUAL "")
        message(FATAL_ERROR "dominium_dist_seed: DOM_DIST_LEAF is required when DOM_DIST_SEED_RUNTIME=ON")
    endif()

    set(_install_type_raw "${DOM_DIST_INSTALL_TYPE}")
    if(_install_type_raw STREQUAL "")
        set(_install_type_raw "portable")
    endif()
    string(TOLOWER "${_install_type_raw}" _install_type)

    if(_install_type STREQUAL "portable")
        set(_seed_scope 0)
        set(_install_type_manifest "portable")
    elseif(_install_type STREQUAL "user" OR _install_type STREQUAL "per-user" OR _install_type STREQUAL "peruser")
        set(_seed_scope 1)
        set(_install_type_manifest "per-user")
    elseif(_install_type STREQUAL "system")
        set(_seed_scope 2)
        set(_install_type_manifest "system")
    else()
        message(FATAL_ERROR "dominium_dist_seed: unsupported DOM_DIST_INSTALL_TYPE '${_install_type_raw}' (use portable|user|system)")
    endif()

    if(NOT DEFINED DOM_DIST_OS OR DOM_DIST_OS STREQUAL "")
        message(FATAL_ERROR "dominium_dist_seed: DOM_DIST_OS is required")
    endif()
    if(NOT DEFINED DOM_DIST_ARCH OR DOM_DIST_ARCH STREQUAL "")
        message(FATAL_ERROR "dominium_dist_seed: DOM_DIST_ARCH is required")
    endif()

    set(_platform_os "any")
    if(DOM_DIST_OS STREQUAL "winnt")
        if(DOM_DIST_ARCH STREQUAL "x86")
            set(_platform_os "win32")
        else()
            set(_platform_os "win64")
        endif()
    elseif(DOM_DIST_OS STREQUAL "linux")
        set(_platform_os "linux")
    elseif(DOM_DIST_OS STREQUAL "macos")
        set(_platform_os "macos")
    else()
        set(_platform_os "any")
    endif()

    set(_platform_arch "any")
    if(DOM_DIST_ARCH STREQUAL "x86" OR DOM_DIST_ARCH STREQUAL "x64" OR DOM_DIST_ARCH STREQUAL "arm64")
        set(_platform_arch "${DOM_DIST_ARCH}")
    endif()

    set(_platform_triple "${_platform_os}-${_platform_arch}")

    set(_install_platform "linux")
    if(DOM_DIST_OS STREQUAL "winnt")
        set(_install_platform "win_nt")
    elseif(DOM_DIST_OS STREQUAL "macos")
        set(_install_platform "mac")
    elseif(DOM_DIST_OS STREQUAL "linux")
        set(_install_platform "linux")
    endif()

    set(_seed_build_channel "${DOM_DIST_BUILD_CHANNEL}")
    if(_seed_build_channel STREQUAL "")
        set(_seed_build_channel "dev")
    endif()

    set(_seed_version "${DOM_PROJECT_SEMVER}")
    if(_seed_version STREQUAL "")
        set(_seed_version "0.0.0")
    endif()

    file(TO_CMAKE_PATH "${DOM_DIST_LEAF}" _install_root_json)

    file(MAKE_DIRECTORY
        "${DOM_DIST_LEAF}/.dsu"
        "${DOM_DIST_LEAF}/repo"
        "${DOM_DIST_LEAF}/repo/products"
        "${DOM_DIST_LEAF}/repo/packs"
        "${DOM_DIST_LEAF}/repo/mods"
        "${DOM_DIST_LEAF}/instances"
        "${DOM_DIST_LEAF}/artifacts"
        "${DOM_DIST_LEAF}/audit"
        "${DOM_DIST_LEAF}/exports"
        "${DOM_DIST_LEAF}/temp"
    )

    set(_install_json
        "{\n"
        "  \"schema_version\": 1,\n"
        "  \"install_id\": \"00000000-0000-0000-0000-000000000000\",\n"
        "  \"install_type\": \"${_install_type_manifest}\",\n"
        "  \"platform\": \"${_install_platform}\",\n"
        "  \"version\": \"${_seed_version}\",\n"
        "  \"root_path\": \"${_install_root_json}\",\n"
        "  \"created_at\": \"1970-01-01T00:00:00Z\",\n"
        "  \"created_by\": \"dist-seed\"\n"
        "}\n"
    )
    file(WRITE "${DOM_DIST_LEAF}/dominium_install.json" "${_install_json}")

    set(_state_file "${DOM_DIST_LEAF}/.dsu/installed_state.dsustate")
    add_custom_command(
        OUTPUT "${_state_file}"
        COMMAND ${CMAKE_COMMAND} -E make_directory "${DOM_DIST_LEAF}/.dsu"
        COMMAND $<TARGET_FILE:dominium_dist_seed>
            --out "${_state_file}"
            --install-root "${_install_root_json}"
            --product-id "dominium"
            --product-version "${_seed_version}"
            --build-channel "${_seed_build_channel}"
            --platform "${_platform_triple}"
            --scope "${_seed_scope}"
        DEPENDS dominium_dist_seed
        COMMENT "Seeding dist installed state"
        VERBATIM
    )
    add_custom_target(dist_seed ALL DEPENDS "${_state_file}")
endif()
