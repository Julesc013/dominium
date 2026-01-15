cmake_minimum_required(VERSION 3.16)

if(NOT WIN32)
    return()
endif()

option(DOMINIUM_BUILD_MSI "Build Windows MSI installer (per-user, no services)" ON)
option(DOMINIUM_BUILD_BUNDLE "Build Windows bootstrapper EXE (Burn)" ON)

# Note: MSI ProductVersion must be numeric (x.y.z[.w]).
set(DOMINIUM_VERSION "0.0.0" CACHE STRING "Dominium product version for MSI/Burn (numeric)")
set(DOMINIUM_DIST_DIR "${CMAKE_BINARY_DIR}/dist/stage" CACHE PATH "Staging directory containing the portable bundle root")
set(DOMINIUM_INSTALLER_DIR "${CMAKE_BINARY_DIR}/dist/installers/windows" CACHE PATH "Output directory for Windows installers")
set(DOMINIUM_MANUFACTURER "Dominium" CACHE STRING "Manufacturer string for installers")
set(DOMINIUM_LICENSE_FILE "${CMAKE_CURRENT_SOURCE_DIR}/license.rtf" CACHE FILEPATH "License RTF for MSI/Burn UI")

# Stable upgrade codes (do not change once published).
set(DOMINIUM_UPGRADE_CODE "{6BA5C836-8F7E-4C48-BC07-7AD1C0C83E74}" CACHE STRING "MSI UpgradeCode GUID")
set(DOMINIUM_BUNDLE_UPGRADE_CODE "{5DD3A6BD-4F3B-4E0C-B5D1-0B2C879C98E3}" CACHE STRING "Burn UpgradeCode GUID")

set(DOMINIUM_MSI_NAME "Dominium-${DOMINIUM_VERSION}.msi" CACHE STRING "MSI file name")
set(DOMINIUM_BUNDLE_NAME "Dominium-${DOMINIUM_VERSION}-Setup.exe" CACHE STRING "Bootstrapper EXE name")

set(DOMINIUM_BUNDLE_ICON "" CACHE FILEPATH "Optional .ico for the Burn bootstrapper")
set(DOMINIUM_BUNDLE_LOGO "" CACHE FILEPATH "Optional logo (BMP/PNG) for the Burn bootstrapper UI")

find_program(WIX_CANDLE_EXECUTABLE candle)
find_program(WIX_LIGHT_EXECUTABLE light)

if(NOT DOMINIUM_PYTHON)
    find_program(DOMINIUM_PYTHON NAMES python3 python)
endif()

if(DOMINIUM_BUILD_MSI)
    if(NOT WIX_CANDLE_EXECUTABLE OR NOT WIX_LIGHT_EXECUTABLE)
        message(WARNING "WiX candle/light not found; dominium_msi target disabled")
    elseif(NOT DOMINIUM_PYTHON)
        message(WARNING "python not found; dominium_msi target disabled")
    else()
        file(MAKE_DIRECTORY "${DOMINIUM_INSTALLER_DIR}")

        string(MD5 _dom_msi_md5 "dominium-msi-${DOMINIUM_VERSION}")
        string(SUBSTRING "${_dom_msi_md5}" 0 8 _g1)
        string(SUBSTRING "${_dom_msi_md5}" 8 4 _g2)
        string(SUBSTRING "${_dom_msi_md5}" 12 4 _g3)
        string(SUBSTRING "${_dom_msi_md5}" 16 4 _g4)
        string(SUBSTRING "${_dom_msi_md5}" 20 12 _g5)
        set(DOMINIUM_PRODUCT_CODE "{${_g1}-${_g2}-${_g3}-${_g4}-${_g5}}")

        set(_stage_stamp "${DOMINIUM_DIST_DIR}/.stage_stamp")
        set(_gen_wxs "${DOMINIUM_INSTALLER_DIR}/Dominium.generated.wxs")
        add_custom_command(
            OUTPUT "${_gen_wxs}"
            COMMAND "${CMAKE_COMMAND}" -E make_directory "${DOMINIUM_INSTALLER_DIR}"
            COMMAND "${DOMINIUM_PYTHON}" "${CMAKE_CURRENT_SOURCE_DIR}/generate_dominium_wxs.py"
                --stage-dir "${DOMINIUM_DIST_DIR}"
                --out "${_gen_wxs}"
                --product-version "${DOMINIUM_VERSION}"
                --manufacturer "${DOMINIUM_MANUFACTURER}"
                --product-code "${DOMINIUM_PRODUCT_CODE}"
                --upgrade-code "${DOMINIUM_UPGRADE_CODE}"
                --license-file "${DOMINIUM_LICENSE_FILE}"
            DEPENDS "${_stage_stamp}" "${CMAKE_CURRENT_SOURCE_DIR}/generate_dominium_wxs.py"
            COMMENT "Generating WiX .wxs from stage directory"
            VERBATIM
        )

        set(_wixobj "${DOMINIUM_INSTALLER_DIR}/Dominium.wixobj")
        add_custom_command(
            OUTPUT "${_wixobj}"
            COMMAND "${WIX_CANDLE_EXECUTABLE}"
                -dDistDir="${DOMINIUM_DIST_DIR}"
                -out "${_wixobj}"
                "${_gen_wxs}"
            DEPENDS "${_gen_wxs}"
            WORKING_DIRECTORY "${DOMINIUM_INSTALLER_DIR}"
            COMMENT "WiX candle -> Dominium.wixobj"
            VERBATIM
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
            VERBATIM
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

        string(MD5 _dom_bundle_md5 "dominium-bundle-${DOMINIUM_VERSION}")
        string(SUBSTRING "${_dom_bundle_md5}" 0 8 _b1)
        string(SUBSTRING "${_dom_bundle_md5}" 8 4 _b2)
        string(SUBSTRING "${_dom_bundle_md5}" 12 4 _b3)
        string(SUBSTRING "${_dom_bundle_md5}" 16 4 _b4)
        string(SUBSTRING "${_dom_bundle_md5}" 20 12 _b5)
        set(DOMINIUM_BUNDLE_CODE "{${_b1}-${_b2}-${_b3}-${_b4}-${_b5}}")

        set(_bundle_wixobj "${DOMINIUM_INSTALLER_DIR}/bootstrapper.wixobj")
        add_custom_command(
            OUTPUT "${_bundle_wixobj}"
            COMMAND "${WIX_CANDLE_EXECUTABLE}"
                -dProductVersion="${DOMINIUM_VERSION}"
                -dManufacturer="${DOMINIUM_MANUFACTURER}"
                -dLicenseFile="${DOMINIUM_LICENSE_FILE}"
                -dBundleIcon="${DOMINIUM_BUNDLE_ICON}"
                -dBundleLogo="${DOMINIUM_BUNDLE_LOGO}"
                -dBundleCode="${DOMINIUM_BUNDLE_CODE}"
                -dBundleUpgradeCode="${DOMINIUM_BUNDLE_UPGRADE_CODE}"
                -dMsiPath="${DOMINIUM_INSTALLER_DIR}/${DOMINIUM_MSI_NAME}"
                -out "${_bundle_wixobj}"
                "${CMAKE_CURRENT_SOURCE_DIR}/bootstrapper.wxs"
            DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/bootstrapper.wxs" "${DOMINIUM_INSTALLER_DIR}/${DOMINIUM_MSI_NAME}"
            WORKING_DIRECTORY "${DOMINIUM_INSTALLER_DIR}"
            COMMENT "WiX candle -> bootstrapper.wixobj"
            VERBATIM
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
            VERBATIM
        )

        add_custom_target(dominium_bundle
            DEPENDS "${_bundle_path}"
        )
    endif()
endif()

