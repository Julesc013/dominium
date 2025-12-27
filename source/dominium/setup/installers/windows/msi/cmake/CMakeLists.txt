cmake_minimum_required(VERSION 3.16)

if(NOT WIN32)
    return()
endif()

option(DOMINIUM_ENABLE_SETUP_MSI "Enable MSI build targets (msi-x86/msi-x64)" ON)
if(NOT DOMINIUM_ENABLE_SETUP_MSI)
    return()
endif()

find_program(WIX_CANDLE_EXECUTABLE candle)
find_program(WIX_LIGHT_EXECUTABLE light)
find_program(DOMINIUM_PYTHON NAMES python3 python)

if(NOT WIX_CANDLE_EXECUTABLE OR NOT WIX_LIGHT_EXECUTABLE)
    message(WARNING "WiX candle/light not found; MSI targets disabled")
    return()
endif()
if(NOT DOMINIUM_PYTHON)
    message(WARNING "python not found; MSI targets disabled")
    return()
endif()

set(DOMINIUM_MSI_VERSION "${DOM_PROJECT_SEMVER}" CACHE STRING "MSI ProductVersion (x.y.z)")
if(DOMINIUM_MSI_VERSION STREQUAL "" OR DOMINIUM_MSI_VERSION STREQUAL "unknown")
    set(DOMINIUM_MSI_VERSION "0.0.0" CACHE STRING "MSI ProductVersion (x.y.z)" FORCE)
endif()

set(DOMINIUM_MSI_MANUFACTURER "Dominium" CACHE STRING "MSI Manufacturer")
set(DOMINIUM_MSI_UPGRADE_CODE "{5E6234E6-0C7F-4D37-8DE8-4B79CF6C9445}" CACHE STRING "MSI UpgradeCode (stable)")
set(DOMINIUM_MSI_OUTPUT_DIR "${CMAKE_BINARY_DIR}/dist/installers/windows/msi" CACHE PATH "Output directory for MSI builds")
set(DOMINIUM_MSI_BUILD_DIR_X86 "" CACHE PATH "CMake build dir for x86 MSI inputs")
set(DOMINIUM_MSI_BUILD_DIR_X64 "" CACHE PATH "CMake build dir for x64 MSI inputs")
set(DOMINIUM_MSI_CA_X86 "" CACHE FILEPATH "InvokeSetupCore DLL for x86 MSI")
set(DOMINIUM_MSI_CA_X64 "" CACHE FILEPATH "InvokeSetupCore DLL for x64 MSI")

set(_dom_msi_root "${CMAKE_CURRENT_LIST_DIR}/..")
get_filename_component(_dom_msi_root_abs "${_dom_msi_root}" ABSOLUTE)
set(_dom_msi_wix_dir "${_dom_msi_root_abs}/wix")
set(_dom_msi_res_dir "${_dom_msi_root_abs}/resources")
set(_dom_msi_script "${CMAKE_CURRENT_LIST_DIR}/generate_msi_wix.py")
set(_dom_msi_verify "${CMAKE_CURRENT_LIST_DIR}/verify_msi.cmake")

if(CMAKE_SIZEOF_VOID_P EQUAL 4 AND DOMINIUM_MSI_BUILD_DIR_X86 STREQUAL "")
    set(DOMINIUM_MSI_BUILD_DIR_X86 "${CMAKE_BINARY_DIR}" CACHE PATH "CMake build dir for x86 MSI inputs" FORCE)
endif()
if(CMAKE_SIZEOF_VOID_P EQUAL 8 AND DOMINIUM_MSI_BUILD_DIR_X64 STREQUAL "")
    set(DOMINIUM_MSI_BUILD_DIR_X64 "${CMAKE_BINARY_DIR}" CACHE PATH "CMake build dir for x64 MSI inputs" FORCE)
endif()

add_library(dominium_msi_ca SHARED
    "${_dom_msi_root_abs}/InvokeSetupCore.c"
)
target_include_directories(dominium_msi_ca PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../core/include"
    "${CMAKE_SOURCE_DIR}/source/dominium/setup/core/include"
)
target_link_libraries(dominium_msi_ca PRIVATE dsu_core)
target_link_libraries(dominium_msi_ca PRIVATE msi)
set_target_properties(dominium_msi_ca PROPERTIES
    OUTPUT_NAME "DominiumSetupCA"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

function(_dom_msi_guid out_var seed)
    string(MD5 _hash "${seed}")
    string(SUBSTRING "${_hash}" 0 8 _g1)
    string(SUBSTRING "${_hash}" 8 4 _g2)
    string(SUBSTRING "${_hash}" 12 4 _g3)
    string(SUBSTRING "${_hash}" 16 4 _g4)
    string(SUBSTRING "${_hash}" 20 12 _g5)
    set(${out_var} "{${_g1}-${_g2}-${_g3}-${_g4}-${_g5}}" PARENT_SCOPE)
endfunction()

function(_dom_msi_add_target arch platform build_dir ca_hint)
    if(build_dir STREQUAL "")
        add_custom_target(msi-${arch}
            COMMAND ${CMAKE_COMMAND} -E echo "msi-${arch} skipped: build dir not configured (DOMINIUM_MSI_BUILD_DIR_${arch})"
        )
        return()
    endif()

    if(ca_hint STREQUAL "")
        add_custom_target(msi-${arch}
            COMMAND ${CMAKE_COMMAND} -E echo "msi-${arch} skipped: InvokeSetupCore DLL not configured (DOMINIUM_MSI_CA_${arch})"
        )
        return()
    endif()

    set(_arch_dir "${CMAKE_BINARY_DIR}/dist/msi/${arch}")
    set(_artifact_dir "${_arch_dir}/artifact_root")
    set(_artifact_stamp "${_artifact_dir}/.artifact_stamp")
    set(_manifest_json "${_arch_dir}/manifest.json")
    set(_gen_dir "${_arch_dir}/wixgen")
    set(_features_wxi "${_gen_dir}/Features.generated.wxi")
    set(_components_wxs "${_gen_dir}/InstallerFiles.generated.wxs")
    set(_build_deps "")
    if(build_dir STREQUAL CMAKE_BINARY_DIR)
        list(APPEND _build_deps dominium-setup)
    endif()

    file(MAKE_DIRECTORY "${_arch_dir}")
    file(MAKE_DIRECTORY "${_gen_dir}")
    file(MAKE_DIRECTORY "${DOMINIUM_MSI_OUTPUT_DIR}")

    _dom_msi_guid(_product_code "dominium-msi-${DOMINIUM_MSI_VERSION}-${arch}")
    _dom_msi_guid(_package_code "dominium-msi-${DOMINIUM_MSI_VERSION}-${arch}-${DOM_BUILD_ID}")

    add_custom_command(
        OUTPUT "${_artifact_stamp}"
        COMMAND "${DOMINIUM_PYTHON}" "${CMAKE_SOURCE_DIR}/scripts/packaging/pipeline.py"
            assemble
            --build-dir "${build_dir}"
            --out "${_artifact_dir}"
            --version "${DOMINIUM_MSI_VERSION}"
            --manifest-template "${CMAKE_SOURCE_DIR}/assets/setup/manifests/product.template.json"
            --reproducible
        COMMAND "${CMAKE_COMMAND}" -E touch "${_artifact_stamp}"
        DEPENDS
            ${_build_deps}
            "${CMAKE_SOURCE_DIR}/scripts/packaging/pipeline.py"
            "${CMAKE_SOURCE_DIR}/assets/setup/manifests/product.template.json"
        COMMENT "Assembling artifact_root for MSI (${arch})"
        VERBATIM
    )

    add_custom_command(
        OUTPUT "${_manifest_json}"
        COMMAND "${_artifact_dir}/setup/dominium-setup.exe"
            manifest dump
            --in "${_artifact_dir}/setup/manifests/product.dsumanifest"
            --out "${_manifest_json}"
            --format json
            --deterministic 1
        DEPENDS "${_artifact_stamp}"
        COMMENT "Dumping manifest JSON for MSI (${arch})"
        VERBATIM
    )

    add_custom_command(
        OUTPUT "${_features_wxi}" "${_components_wxs}"
        COMMAND "${DOMINIUM_PYTHON}" "${_dom_msi_script}"
            --artifact-dir "${_artifact_dir}"
            --manifest-json "${_manifest_json}"
            --features-out "${_features_wxi}"
            --components-out "${_components_wxs}"
        DEPENDS "${_manifest_json}" "${_dom_msi_script}"
        COMMENT "Generating WiX feature/component fragments (${arch})"
        VERBATIM
    )

    set(_wixobj "${DOMINIUM_MSI_OUTPUT_DIR}/DominiumSetup-${DOMINIUM_MSI_VERSION}-${arch}.wixobj")
    set(_msi_path "${DOMINIUM_MSI_OUTPUT_DIR}/DominiumSetup-${DOMINIUM_MSI_VERSION}-${arch}.msi")
    set(_msi_ok "${DOMINIUM_MSI_OUTPUT_DIR}/DominiumSetup-${DOMINIUM_MSI_VERSION}-${arch}.ok")

    add_custom_command(
        OUTPUT "${_wixobj}"
        COMMAND "${WIX_CANDLE_EXECUTABLE}"
            -dProductVersion="${DOMINIUM_MSI_VERSION}"
            -dManufacturer="${DOMINIUM_MSI_MANUFACTURER}"
            -dProductCode="${_product_code}"
            -dUpgradeCode="${DOMINIUM_MSI_UPGRADE_CODE}"
            -dPackageCode="${_package_code}"
            -dDsuPlatform="${platform}"
            -dWixBannerBmp="${_dom_msi_res_dir}/banner.bmp"
            -dWixDialogBmp="${_dom_msi_res_dir}/dialog.bmp"
            -dInvokeSetupCorePath="${ca_hint}"
            -dArtifactDir="${_artifact_dir}"
            -I "${_gen_dir}"
            -out "${_wixobj}"
            "${_dom_msi_wix_dir}/Product.wxs"
            "${_dom_msi_wix_dir}/Properties.wxs"
            "${_dom_msi_wix_dir}/Directories.wxs"
            "${_dom_msi_wix_dir}/Features.wxs"
            "${_dom_msi_wix_dir}/CustomActions.wxs"
            "${_dom_msi_wix_dir}/UI.wxs"
            "${_components_wxs}"
        DEPENDS
            "${_features_wxi}"
            "${_components_wxs}"
            dominium_msi_ca
            "${_dom_msi_wix_dir}/Product.wxs"
            "${_dom_msi_wix_dir}/Properties.wxs"
            "${_dom_msi_wix_dir}/Directories.wxs"
            "${_dom_msi_wix_dir}/Features.wxs"
            "${_dom_msi_wix_dir}/CustomActions.wxs"
            "${_dom_msi_wix_dir}/UI.wxs"
            "${_dom_msi_res_dir}/banner.bmp"
            "${_dom_msi_res_dir}/dialog.bmp"
        COMMENT "WiX candle -> ${_wixobj}"
        VERBATIM
    )

    add_custom_command(
        OUTPUT "${_msi_path}"
        COMMAND "${WIX_LIGHT_EXECUTABLE}"
            -ext WixUIExtension
            -out "${_msi_path}"
            "${_wixobj}"
        DEPENDS "${_wixobj}"
        COMMENT "WiX light -> ${_msi_path}"
        VERBATIM
    )

    add_custom_command(
        OUTPUT "${_msi_ok}"
        COMMAND "${CMAKE_COMMAND}" -DMSI_PATH="${_msi_path}" -P "${_dom_msi_verify}"
        COMMAND "${CMAKE_COMMAND}" -E touch "${_msi_ok}"
        DEPENDS "${_msi_path}" "${_dom_msi_verify}"
        COMMENT "Verifying MSI (${arch})"
        VERBATIM
    )

    add_custom_target(msi-${arch} DEPENDS "${_msi_ok}")
endfunction()

set(_msi_ca_x86 "${DOMINIUM_MSI_CA_X86}")
set(_msi_ca_x64 "${DOMINIUM_MSI_CA_X64}")
if(CMAKE_SIZEOF_VOID_P EQUAL 4)
    set(_msi_ca_x86 "$<TARGET_FILE:dominium_msi_ca>")
endif()
if(CMAKE_SIZEOF_VOID_P EQUAL 8)
    set(_msi_ca_x64 "$<TARGET_FILE:dominium_msi_ca>")
endif()

_dom_msi_add_target("x86" "win32-x86" "${DOMINIUM_MSI_BUILD_DIR_X86}" "${_msi_ca_x86}")
_dom_msi_add_target("x64" "win64-x64" "${DOMINIUM_MSI_BUILD_DIR_X64}" "${_msi_ca_x64}")
