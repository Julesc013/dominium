cmake_minimum_required(VERSION 3.16)

option(DOMINIUM_ENABLE_WINDOWS_LEGACY "Enable legacy Windows installers (DOS/Win16/Win9x)" ON)
if(NOT DEFINED DOMINIUM_PUBLISH_INSTALLERS_TO_DIST)
    option(DOMINIUM_PUBLISH_INSTALLERS_TO_DIST "Copy built installers into repo dist/ for convenience" ON)
endif()
if(NOT DEFINED DOMINIUM_LEGACY_PUBLISH_DIR)
    set(DOMINIUM_LEGACY_PUBLISH_DIR "${CMAKE_SOURCE_DIR}/dist/legacy/windows" CACHE PATH "Publish legacy installers into repo dist")
endif()

set(_dom_legacy_root "${CMAKE_CURRENT_LIST_DIR}/..")
get_filename_component(_dom_legacy_root_abs "${_dom_legacy_root}" ABSOLUTE)
set(_dom_legacy_core_dir "${_dom_legacy_root_abs}/legacy_core")

if(DOMINIUM_ENABLE_WINDOWS_LEGACY AND NOT TARGET dsu_legacy_core)
    add_library(dsu_legacy_core
        "${_dom_legacy_core_dir}/src/legacy_fs_win32_9x.c"
        "${_dom_legacy_core_dir}/src/legacy_invocation.c"
        "${_dom_legacy_core_dir}/src/legacy_log.c"
        "${_dom_legacy_core_dir}/src/legacy_manifest.c"
        "${_dom_legacy_core_dir}/src/legacy_state.c"
        "${_dom_legacy_core_dir}/src/legacy_txn.c"
        "${_dom_legacy_core_dir}/src/legacy_uninstall.c"
        "${_dom_legacy_core_dir}/src/legacy_verify.c"
    )

    target_include_directories(dsu_legacy_core PUBLIC
        "${_dom_legacy_core_dir}/include"
    )

    set_target_properties(dsu_legacy_core PROPERTIES
        C_STANDARD 90
        C_STANDARD_REQUIRED ON
        C_EXTENSIONS OFF
    )
endif()

if(DOMINIUM_ENABLE_WINDOWS_LEGACY)
    add_custom_target(dominium-setup-legacy-sources
        SOURCES
            "${_dom_legacy_root_abs}/dos/src/dos_main.c"
            "${_dom_legacy_root_abs}/dos/src/dos_tui.c"
            "${_dom_legacy_root_abs}/dos/src/dos_extract.c"
            "${_dom_legacy_root_abs}/win16/src/win16_main.c"
            "${_dom_legacy_root_abs}/win16/src/win16_gui.c"
            "${_dom_legacy_root_abs}/win16/src/win16_resources.rc"
            "${_dom_legacy_root_abs}/win9x/src/win9x_main.c"
            "${_dom_legacy_root_abs}/win9x/src/win9x_gui.c"
            "${_dom_legacy_root_abs}/win9x/src/win9x_tui.c"
            "${_dom_legacy_root_abs}/win9x/src/win9x_cli.c"
            "${_dom_legacy_root_abs}/win9x/src/win9x_resources.rc"
    )

    if(WIN32)
        add_executable(dominium-setup-win9x
            "${_dom_legacy_root_abs}/win9x/src/win9x_main.c"
            "${_dom_legacy_root_abs}/win9x/src/win9x_gui.c"
            "${_dom_legacy_root_abs}/win9x/src/win9x_tui.c"
            "${_dom_legacy_root_abs}/win9x/src/win9x_cli.c"
            "${_dom_legacy_root_abs}/win9x/src/win9x_resources.rc"
        )

        target_include_directories(dominium-setup-win9x PRIVATE
            "${_dom_legacy_core_dir}/include"
        )

        target_link_libraries(dominium-setup-win9x PRIVATE
            dsu_legacy_core
            user32
            shell32
            ole32
        )

        set_target_properties(dominium-setup-win9x PROPERTIES
            OUTPUT_NAME "DominiumSetup-win9x"
            C_STANDARD 90
            C_STANDARD_REQUIRED ON
            C_EXTENSIONS OFF
        )

        add_custom_target(legacy_win9x_installer DEPENDS dominium-setup-win9x)
        if(DOMINIUM_PUBLISH_INSTALLERS_TO_DIST)
            set(_win9x_publish "${DOMINIUM_LEGACY_PUBLISH_DIR}/DominiumSetup-win9x.exe")
            add_custom_command(
                OUTPUT "${_win9x_publish}"
                COMMAND "${CMAKE_COMMAND}" -E make_directory "${DOMINIUM_LEGACY_PUBLISH_DIR}"
                COMMAND "${CMAKE_COMMAND}" -E copy_if_different "$<TARGET_FILE:dominium-setup-win9x>" "${_win9x_publish}"
                DEPENDS dominium-setup-win9x
                COMMENT "Publishing Win9x installer -> ${_win9x_publish}"
                VERBATIM
            )
            add_custom_target(legacy_win9x_publish DEPENDS "${_win9x_publish}")
            add_dependencies(legacy_win9x_installer legacy_win9x_publish)
        endif()
    endif()

    add_custom_target(legacy_dos_installer
        COMMAND ${CMAKE_COMMAND} -E echo "Use scripts/legacy/build_legacy_windows.bat dos to build DOS installer."
    )

    add_custom_target(legacy_win16_installer
        COMMAND ${CMAKE_COMMAND} -E echo "Use scripts/legacy/build_legacy_windows.bat win16 to build Win16 installer."
    )
endif()
