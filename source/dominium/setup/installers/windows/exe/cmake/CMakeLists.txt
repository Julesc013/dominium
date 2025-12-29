cmake_minimum_required(VERSION 3.16)

if(NOT WIN32)
    return()
endif()

option(DOMINIUM_BUILD_EXE_INSTALLERS "Build Windows EXE installer targets" ON)
if(NOT DOMINIUM_BUILD_EXE_INSTALLERS)
    return()
endif()

find_program(DOMINIUM_PYTHON NAMES python3 python)
if(NOT DOMINIUM_PYTHON)
    message(WARNING "python not found; setup_exe targets disabled")
    return()
endif()

set(EXE_ROOT "${CMAKE_CURRENT_LIST_DIR}/..")
get_filename_component(EXE_ROOT "${EXE_ROOT}" ABSOLUTE)

set(DOMINIUM_EXE_ARTIFACT_DIR "${CMAKE_BINARY_DIR}/dist/artifact_root" CACHE PATH "Artifact root for EXE packaging")
set(DOMINIUM_EXE_OUTPUT_DIR "${CMAKE_BINARY_DIR}/dist/windows" CACHE PATH "EXE output directory")
if(NOT DEFINED DOMINIUM_PUBLISH_INSTALLERS_TO_DIST)
    option(DOMINIUM_PUBLISH_INSTALLERS_TO_DIST "Copy built installers into repo dist/ for convenience" ON)
endif()
if(NOT DEFINED DOMINIUM_DIST_INSTALLERS_DIR)
    set(DOMINIUM_DIST_INSTALLERS_DIR "${CMAKE_SOURCE_DIR}/dist/installers" CACHE PATH "Repo dist/ installers root")
endif()
set(DOMINIUM_EXE_PUBLISH_DIR "${DOMINIUM_DIST_INSTALLERS_DIR}/windows/exe" CACHE PATH "Publish EXE installers into repo dist")
set(DOMINIUM_EXE_VERSION "${DOM_PROJECT_SEMVER}")
set(DOMINIUM_EXE_MANIFEST_TEMPLATE "${CMAKE_SOURCE_DIR}/assets/setup/manifests/product.template.json")

set(_exe_common_src
    "${EXE_ROOT}/common/src/archive.c"
    "${EXE_ROOT}/common/src/args_parse.c"
    "${EXE_ROOT}/common/src/bridge_core.c"
    "${EXE_ROOT}/common/src/capability.c"
    "${EXE_ROOT}/common/src/invocation_builder.c"
    "${EXE_ROOT}/common/src/log_forward.c"
    "${EXE_ROOT}/common/src/ui_contract.c"
    "${EXE_ROOT}/common/src/ui_strings.c"
)

set(_exe_win32_src
    "${EXE_ROOT}/win32/src/win32_entry.c"
    "${EXE_ROOT}/win32/src/win32_gui.c"
    "${EXE_ROOT}/win32/src/win32_tui.c"
    "${EXE_ROOT}/win32/src/win32_resources.rc"
)

add_executable(dominium_setup_exe_win32_stub
    ${_exe_common_src}
    ${_exe_win32_src}
    "${EXE_ROOT}/win32/src/win32_main.c"
)

target_include_directories(dominium_setup_exe_win32_stub PRIVATE
    "${EXE_ROOT}/common/include"
    "${EXE_ROOT}/win32/include"
    "${CMAKE_SOURCE_DIR}/source/dominium/setup/core/include"
    "${CMAKE_SOURCE_DIR}/include"
)

target_link_libraries(dominium_setup_exe_win32_stub PRIVATE
    setup_kernel
    setup_services_impl_platform
    shell32
    ole32
)

set_target_properties(dominium_setup_exe_win32_stub PROPERTIES
    OUTPUT_NAME "DominiumSetup-win32-stub"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_executable(dominium_setup_exe_win64_stub
    ${_exe_common_src}
    ${_exe_win32_src}
    "${EXE_ROOT}/win64/src/win64_main.c"
)

target_include_directories(dominium_setup_exe_win64_stub PRIVATE
    "${EXE_ROOT}/common/include"
    "${EXE_ROOT}/win32/include"
    "${CMAKE_SOURCE_DIR}/source/dominium/setup/core/include"
    "${CMAKE_SOURCE_DIR}/include"
)

target_link_libraries(dominium_setup_exe_win64_stub PRIVATE
    setup_kernel
    setup_services_impl_platform
    shell32
    ole32
)

set_target_properties(dominium_setup_exe_win64_stub PROPERTIES
    OUTPUT_NAME "DominiumSetup-win64-stub"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

set(_artifact_stamp "${DOMINIUM_EXE_ARTIFACT_DIR}/.artifact_stamp")
add_custom_command(
    OUTPUT "${_artifact_stamp}"
    COMMAND "${DOMINIUM_PYTHON}" "${CMAKE_SOURCE_DIR}/scripts/packaging/pipeline.py"
        assemble
        --build-dir "${CMAKE_BINARY_DIR}"
        --out "${DOMINIUM_EXE_ARTIFACT_DIR}"
        --version "${DOMINIUM_EXE_VERSION}"
        --manifest-template "${DOMINIUM_EXE_MANIFEST_TEMPLATE}"
    COMMAND "${CMAKE_COMMAND}" -E touch "${_artifact_stamp}"
    DEPENDS
        dominium-setup
        dominium-launcher
        dominium_game
        "${CMAKE_SOURCE_DIR}/scripts/packaging/pipeline.py"
        "${DOMINIUM_EXE_MANIFEST_TEMPLATE}"
    COMMENT "Assembling artifact_root for EXE installers"
    VERBATIM
)

set(_exe_win32 "${DOMINIUM_EXE_OUTPUT_DIR}/DominiumSetup-win32.exe")
add_custom_command(
    OUTPUT "${_exe_win32}"
    COMMAND "${CMAKE_COMMAND}" -E make_directory "${DOMINIUM_EXE_OUTPUT_DIR}"
    COMMAND "${DOMINIUM_PYTHON}" "${EXE_ROOT}/cmake/build_exe_archive.py"
        --stub "$<TARGET_FILE:dominium_setup_exe_win32_stub>"
        --input "${DOMINIUM_EXE_ARTIFACT_DIR}"
        --output "${_exe_win32}"
    DEPENDS
        dominium_setup_exe_win32_stub
        "${_artifact_stamp}"
        "${EXE_ROOT}/cmake/build_exe_archive.py"
    COMMENT "Embedding payloads into DominiumSetup-win32.exe"
    VERBATIM
)

set(_exe_win64 "${DOMINIUM_EXE_OUTPUT_DIR}/DominiumSetup-win64.exe")
add_custom_command(
    OUTPUT "${_exe_win64}"
    COMMAND "${CMAKE_COMMAND}" -E make_directory "${DOMINIUM_EXE_OUTPUT_DIR}"
    COMMAND "${DOMINIUM_PYTHON}" "${EXE_ROOT}/cmake/build_exe_archive.py"
        --stub "$<TARGET_FILE:dominium_setup_exe_win64_stub>"
        --input "${DOMINIUM_EXE_ARTIFACT_DIR}"
        --output "${_exe_win64}"
    DEPENDS
        dominium_setup_exe_win64_stub
        "${_artifact_stamp}"
        "${EXE_ROOT}/cmake/build_exe_archive.py"
    COMMENT "Embedding payloads into DominiumSetup-win64.exe"
    VERBATIM
)

add_custom_target(setup_exe_win32_nt DEPENDS "${_exe_win32}")
add_custom_target(setup_exe_win64 DEPENDS "${_exe_win64}")
if(DOMINIUM_PUBLISH_INSTALLERS_TO_DIST)
    set(_exe_win32_publish "${DOMINIUM_EXE_PUBLISH_DIR}/DominiumSetup-win32.exe")
    add_custom_command(
        OUTPUT "${_exe_win32_publish}"
        COMMAND "${CMAKE_COMMAND}" -E make_directory "${DOMINIUM_EXE_PUBLISH_DIR}"
        COMMAND "${CMAKE_COMMAND}" -E copy_if_different "${_exe_win32}" "${_exe_win32_publish}"
        DEPENDS "${_exe_win32}"
        COMMENT "Publishing EXE -> ${_exe_win32_publish}"
        VERBATIM
    )
    add_custom_target(setup_exe_win32_nt_publish DEPENDS "${_exe_win32_publish}")
    add_dependencies(setup_exe_win32_nt setup_exe_win32_nt_publish)

    set(_exe_win64_publish "${DOMINIUM_EXE_PUBLISH_DIR}/DominiumSetup-win64.exe")
    add_custom_command(
        OUTPUT "${_exe_win64_publish}"
        COMMAND "${CMAKE_COMMAND}" -E make_directory "${DOMINIUM_EXE_PUBLISH_DIR}"
        COMMAND "${CMAKE_COMMAND}" -E copy_if_different "${_exe_win64}" "${_exe_win64_publish}"
        DEPENDS "${_exe_win64}"
        COMMENT "Publishing EXE -> ${_exe_win64_publish}"
        VERBATIM
    )
    add_custom_target(setup_exe_win64_publish DEPENDS "${_exe_win64_publish}")
    add_dependencies(setup_exe_win64 setup_exe_win64_publish)
endif()

add_custom_target(setup_exe_win16
    COMMAND "${CMAKE_COMMAND}" -E echo "setup_exe_win16: requires external Win16 toolchain (see docs/setup/WINDOWS_LEGACY_SUPPORT.md)"
)
