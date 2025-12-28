cmake_minimum_required(VERSION 3.16)

option(DOMINIUM_ENABLE_CLASSIC "Enable Classic Mac OS legacy installer sources" ON)

if(DOMINIUM_ENABLE_CLASSIC)
    add_library(dsu_legacy_core
        ${CMAKE_CURRENT_LIST_DIR}/../core_legacy/src/legacy_fs.c
        ${CMAKE_CURRENT_LIST_DIR}/../core_legacy/src/legacy_invocation.c
        ${CMAKE_CURRENT_LIST_DIR}/../core_legacy/src/legacy_log.c
        ${CMAKE_CURRENT_LIST_DIR}/../core_legacy/src/legacy_manifest.c
        ${CMAKE_CURRENT_LIST_DIR}/../core_legacy/src/legacy_state.c
        ${CMAKE_CURRENT_LIST_DIR}/../core_legacy/src/legacy_txn.c
        ${CMAKE_CURRENT_LIST_DIR}/../core_legacy/src/legacy_uninstall.c
        ${CMAKE_CURRENT_LIST_DIR}/../core_legacy/src/legacy_verify.c
    )

    target_include_directories(dsu_legacy_core PUBLIC
        ${CMAKE_CURRENT_LIST_DIR}/../core_legacy/include
    )

    set_target_properties(dsu_legacy_core PROPERTIES
        C_STANDARD 90
        C_STANDARD_REQUIRED ON
        C_EXTENSIONS OFF
    )

    add_custom_target(dominium-setup-classic-sources
        SOURCES
            ${CMAKE_CURRENT_LIST_DIR}/../gui/classic_installer_app/src/main.c
            ${CMAKE_CURRENT_LIST_DIR}/../gui/classic_installer_app/src/dialogs.c
            ${CMAKE_CURRENT_LIST_DIR}/../gui/classic_installer_app/src/dialogs.h
            ${CMAKE_CURRENT_LIST_DIR}/../gui/classic_installer_app/src/resources.r
    )

    if(APPLE)
        add_custom_target(package-macos-classic
            COMMAND ${CMAKE_COMMAND} -E env
                OUT_DIR=${CMAKE_BINARY_DIR}/dist/macos_classic
                bash ${CMAKE_CURRENT_LIST_DIR}/../packaging/sit_or_img/build_image.sh
            WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}/../packaging/sit_or_img
            COMMENT "Packaging Classic Mac OS disk image"
            VERBATIM
        )
    endif()
endif()
