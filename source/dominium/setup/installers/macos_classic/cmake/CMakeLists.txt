cmake_minimum_required(VERSION 3.16)

option(DOMINIUM_ENABLE_CLASSIC "Enable Classic Mac OS legacy installer sources" ON)

if(DOMINIUM_ENABLE_CLASSIC)
    if(NOT TARGET dsu_legacy_core)
        message(FATAL_ERROR "dsu_legacy_core target missing; enable legacy core build before Classic installer sources.")
    endif()

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
