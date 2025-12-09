cmake_minimum_required(VERSION 3.16)

if(NOT WIN32)
    return()
endif()

option(DOMINIUM_BUILD_MSI "Build Windows MSI installer" ON)
option(DOMINIUM_BUILD_BUNDLE "Build Windows bootstrapper" ON)

set(DOMINIUM_VERSION "1.0.0" CACHE STRING "Dominium product version for installers")
set(DOMINIUM_DIST_DIR "${CMAKE_BINARY_DIR}/dist" CACHE PATH "Staging directory with dominium-setup-cli.exe and payload")
set(DOMINIUM_INSTALLER_DIR "${CMAKE_BINARY_DIR}/dist/installers/windows" CACHE PATH "Output directory for Windows installers")
set(DOMINIUM_MANUFACTURER "Dominium" CACHE STRING "Manufacturer string for installers")
set(DOMINIUM_LICENSE_FILE "${CMAKE_CURRENT_SOURCE_DIR}/license.rtf" CACHE FILEPATH "License RTF for MSI/Burn UI")
set(DOMINIUM_BUNDLE_ICON "" CACHE FILEPATH "Optional .ico for the Burn bootstrapper")
set(DOMINIUM_BUNDLE_LOGO "" CACHE FILEPATH "Optional logo (BMP/PNG) for the Burn bootstrapper UI")

set(DOMINIUM_MSI_NAME "Dominium-${DOMINIUM_VERSION}.msi" CACHE STRING "MSI file name")
set(DOMINIUM_BUNDLE_NAME "Dominium-${DOMINIUM_VERSION}-Setup.exe" CACHE STRING "Bootstrapper EXE name")

find_program(WIX_CANDLE_EXECUTABLE candle)
find_program(WIX_LIGHT_EXECUTABLE light)

if(DOMINIUM_BUILD_MSI)
    if(NOT WIX_CANDLE_EXECUTABLE OR NOT WIX_LIGHT_EXECUTABLE)
        message(WARNING "WiX candle/light not found; dominium_msi target disabled")
    else()
        file(MAKE_DIRECTORY "${DOMINIUM_INSTALLER_DIR}")

        set(_wixobj "${DOMINIUM_INSTALLER_DIR}/Dominium.wixobj")
        add_custom_command(
            OUTPUT "${_wixobj}"
            COMMAND "${WIX_CANDLE_EXECUTABLE}"
                -dDistDir="${DOMINIUM_DIST_DIR}"
                -dProductVersion="${DOMINIUM_VERSION}"
                -dManufacturer="${DOMINIUM_MANUFACTURER}"
                -dLicenseFile="${DOMINIUM_LICENSE_FILE}"
                -out "${_wixobj}"
                "${CMAKE_CURRENT_SOURCE_DIR}/Dominium.wxs"
            DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/Dominium.wxs"
            WORKING_DIRECTORY "${DOMINIUM_INSTALLER_DIR}"
            COMMENT "WiX candle Dominium.wxs"
        )

        set(_msi_path "${DOMINIUM_INSTALLER_DIR}/${DOMINIUM_MSI_NAME}")
        add_custom_command(
            OUTPUT "${_msi_path}"
            COMMAND "${WIX_LIGHT_EXECUTABLE}"
                -ext WixUIExtension
                -out "${_msi_path}"
                "${_wixobj}"
            DEPENDS "${_wixobj}"
            WORKING_DIRECTORY "${DOMINIUM_INSTALLER_DIR}"
            COMMENT "WiX light -> ${DOMINIUM_MSI_NAME}"
        )

        add_custom_target(dominium_msi
            DEPENDS "${_msi_path}"
        )
    endif()
endif()

if(DOMINIUM_BUILD_BUNDLE)
    if(NOT WIX_CANDLE_EXECUTABLE OR NOT WIX_LIGHT_EXECUTABLE)
        message(WARNING "WiX candle/light not found; dominium_bundle target disabled")
    else()
        file(MAKE_DIRECTORY "${DOMINIUM_INSTALLER_DIR}")

        set(_bundle_wixobj "${DOMINIUM_INSTALLER_DIR}/bootstrapper.wixobj")
        add_custom_command(
            OUTPUT "${_bundle_wixobj}"
            COMMAND "${WIX_CANDLE_EXECUTABLE}"
                -dProductVersion="${DOMINIUM_VERSION}"
                -dManufacturer="${DOMINIUM_MANUFACTURER}"
                -dLicenseFile="${DOMINIUM_LICENSE_FILE}"
                -dBundleIcon="${DOMINIUM_BUNDLE_ICON}"
                -dBundleLogo="${DOMINIUM_BUNDLE_LOGO}"
                -dMsiPath="${DOMINIUM_INSTALLER_DIR}/${DOMINIUM_MSI_NAME}"
                -out "${_bundle_wixobj}"
                "${CMAKE_CURRENT_SOURCE_DIR}/bootstrapper.wxs"
            DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/bootstrapper.wxs" "${DOMINIUM_INSTALLER_DIR}/${DOMINIUM_MSI_NAME}"
            WORKING_DIRECTORY "${DOMINIUM_INSTALLER_DIR}"
            COMMENT "WiX candle bootstrapper.wxs"
        )

        set(_bundle_path "${DOMINIUM_INSTALLER_DIR}/${DOMINIUM_BUNDLE_NAME}")
        add_custom_command(
            OUTPUT "${_bundle_path}"
            COMMAND "${WIX_LIGHT_EXECUTABLE}"
                -ext WixBalExtension
                -out "${_bundle_path}"
                "${_bundle_wixobj}"
            DEPENDS "${_bundle_wixobj}"
            WORKING_DIRECTORY "${DOMINIUM_INSTALLER_DIR}"
            COMMENT "WiX light -> ${DOMINIUM_BUNDLE_NAME}"
        )

        add_custom_target(dominium_bundle
            DEPENDS "${_bundle_path}"
        )
    endif()
endif()
