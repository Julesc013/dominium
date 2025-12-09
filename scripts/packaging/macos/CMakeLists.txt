cmake_minimum_required(VERSION 3.16)

if(NOT APPLE)
    return()
endif()

option(DOMINIUM_BUILD_MACOS_PKG "Build macOS .pkg and .dmg installers" ON)

set(DOMINIUM_VERSION "1.0.0" CACHE STRING "Dominium product version for macOS packaging")
set(DOMINIUM_DIST_DIR "${CMAKE_BINARY_DIR}/dist" CACHE PATH "Staging directory with macOS binaries/data")
set(DOMINIUM_INSTALLER_DIR "${CMAKE_BINARY_DIR}/dist/installers/macos" CACHE PATH "Output directory for macOS installers")
set(DOMINIUM_BUNDLE_IDENTIFIER "com.yourorg.dominium" CACHE STRING "CFBundleIdentifier for Dominium.app")
set(DOMINIUM_BUNDLE_EXECUTABLE "dominium-launcher" CACHE STRING "Executable name inside Dominium.app")
set(DOMINIUM_MACOS_MINIMUM_VERSION "10.13" CACHE STRING "Minimum macOS version supported by the app bundle")
set(DOMINIUM_MACOS_VOLUME_NAME "Dominium" CACHE STRING "Volume label for the generated DMG")
set(DOMINIUM_MACOS_APP_NAME "Dominium.app" CACHE STRING "App bundle name")

find_program(DOMINIUM_BASH_EXECUTABLE bash)

if(DOMINIUM_BUILD_MACOS_PKG)
    if(NOT DOMINIUM_BASH_EXECUTABLE)
        message(WARNING "bash not found; dominium_macos_pkg target disabled")
        return()
    endif()

    file(MAKE_DIRECTORY "${DOMINIUM_INSTALLER_DIR}")

    # Ensure postinstall script is executable for pkgbuild.
    file(CHMOD "${CMAKE_CURRENT_SOURCE_DIR}/postinstall"
        PERMISSIONS
            OWNER_READ OWNER_WRITE OWNER_EXECUTE
            GROUP_READ GROUP_EXECUTE
            WORLD_READ WORLD_EXECUTE)

    set(DOMINIUM_MACOS_APP_BUNDLE "${DOMINIUM_INSTALLER_DIR}/${DOMINIUM_MACOS_APP_NAME}")

    file(MAKE_DIRECTORY
        "${DOMINIUM_MACOS_APP_BUNDLE}/Contents"
        "${DOMINIUM_MACOS_APP_BUNDLE}/Contents/MacOS"
        "${DOMINIUM_MACOS_APP_BUNDLE}/Contents/Resources")

    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/Dominium.app/Contents/Info.plist.in"
        "${DOMINIUM_MACOS_APP_BUNDLE}/Contents/Info.plist"
        @ONLY
    )

    set(_bundle_stamp "${DOMINIUM_MACOS_APP_BUNDLE}/Contents/MacOS/.bundle-stamp")
    add_custom_command(
        OUTPUT "${_bundle_stamp}"
        COMMAND "${CMAKE_COMMAND}" -E make_directory "${DOMINIUM_MACOS_APP_BUNDLE}/Contents/MacOS"
        COMMAND "${CMAKE_COMMAND}" -E make_directory "${DOMINIUM_MACOS_APP_BUNDLE}/Contents/Resources"
        COMMAND "${CMAKE_COMMAND}" -E copy "${DOMINIUM_DIST_DIR}/dominium_launcher_cli" "${DOMINIUM_MACOS_APP_BUNDLE}/Contents/MacOS/${DOMINIUM_BUNDLE_EXECUTABLE}"
        COMMAND "${CMAKE_COMMAND}" -E copy_if_different "${DOMINIUM_DIST_DIR}/dominium-setup-cli" "${DOMINIUM_MACOS_APP_BUNDLE}/Contents/MacOS/dominium-setup-cli"
        COMMAND "${CMAKE_COMMAND}" -E touch "${_bundle_stamp}"
        DEPENDS "${DOMINIUM_DIST_DIR}/dominium_launcher_cli"
        COMMENT "Staging Dominium.app bundle"
    )

    set(_component_pkg "${DOMINIUM_INSTALLER_DIR}/Dominium-${DOMINIUM_VERSION}.pkg")
    set(_distribution_pkg "${DOMINIUM_INSTALLER_DIR}/Dominium-${DOMINIUM_VERSION}-installer.pkg")
    add_custom_command(
        OUTPUT "${_component_pkg}" "${_distribution_pkg}"
        COMMAND "${CMAKE_COMMAND}" -E env
            APP_BUNDLE="${DOMINIUM_MACOS_APP_BUNDLE}"
            IDENTIFIER="${DOMINIUM_BUNDLE_IDENTIFIER}"
            VERSION="${DOMINIUM_VERSION}"
            OUT_DIR="${DOMINIUM_INSTALLER_DIR}"
            SCRIPTS_DIR="${CMAKE_CURRENT_SOURCE_DIR}"
            "${DOMINIUM_BASH_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/build_pkg.sh"
        DEPENDS "${_bundle_stamp}" "${DOMINIUM_MACOS_APP_BUNDLE}/Contents/Info.plist"
        COMMENT "pkgbuild/productbuild Dominium macOS installer"
        WORKING_DIRECTORY "${DOMINIUM_INSTALLER_DIR}"
    )

    set(_dmg_path "${DOMINIUM_INSTALLER_DIR}/Dominium-${DOMINIUM_VERSION}.dmg")
    add_custom_command(
        OUTPUT "${_dmg_path}"
        COMMAND "${CMAKE_COMMAND}" -E env
            APP_BUNDLE="${DOMINIUM_MACOS_APP_BUNDLE}"
            OUTPUT_DMG="${_dmg_path}"
            VOLUME_NAME="${DOMINIUM_MACOS_VOLUME_NAME}"
            PKG_PATH="${_distribution_pkg}"
            "${DOMINIUM_BASH_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/build_dmg.sh"
        DEPENDS "${_distribution_pkg}"
        COMMENT "hdiutil create Dominium DMG"
        WORKING_DIRECTORY "${DOMINIUM_INSTALLER_DIR}"
    )

    add_custom_target(dominium_macos_app
        DEPENDS "${_bundle_stamp}"
    )

    add_custom_target(dominium_macos_pkg
        DEPENDS "${_distribution_pkg}"
    )

    add_custom_target(dominium_macos_dmg
        DEPENDS "${_dmg_path}"
    )
endif()
