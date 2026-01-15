cmake_minimum_required(VERSION 3.16)

if(NOT DEFINED ARTIFACT_ROOT)
    message(FATAL_ERROR "ARTIFACT_ROOT is required")
endif()
if(NOT DEFINED OUT_DIR)
    message(FATAL_ERROR "OUT_DIR is required")
endif()
if(NOT DEFINED VERSION)
    message(FATAL_ERROR "VERSION is required")
endif()
if(NOT DEFINED ARCH)
    message(FATAL_ERROR "ARCH is required")
endif()

if(NOT DEFINED REPO_ROOT)
    get_filename_component(REPO_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../../../../../.." ABSOLUTE)
endif()

if(NOT DEFINED PYTHON_EXECUTABLE)
    find_program(PYTHON_EXECUTABLE NAMES python3 python)
endif()
if(NOT PYTHON_EXECUTABLE)
    message(FATAL_ERROR "python3/python not found")
endif()

file(MAKE_DIRECTORY "${OUT_DIR}")

set(_tar_name "Dominium-linux-${ARCH}-${VERSION}.tar.gz")
set(_tar_path "${OUT_DIR}/${_tar_name}")
set(_archive_script "${REPO_ROOT}/scripts/packaging/make_deterministic_archive.py")

execute_process(
    COMMAND "${PYTHON_EXECUTABLE}" "${_archive_script}"
        --format tar.gz
        --input "${ARTIFACT_ROOT}"
        --output "${_tar_path}"
        --root-name artifact_root
    RESULT_VARIABLE _tar_rc
)
if(NOT _tar_rc EQUAL 0)
    message(FATAL_ERROR "tarball packaging failed (${_tar_rc})")
endif()

# Dry-run apply validation (sandboxed).
set(_cli "${ARTIFACT_ROOT}/setup/dominium-setup")
set(_manifest "${ARTIFACT_ROOT}/setup/manifests/product.dsumanifest")
set(_dry_root "${OUT_DIR}/_dry_run_${ARCH}")
set(_inv "${_dry_root}/dry_run.dsuinv")
set(_plan "${_dry_root}/dry_run.dsuplan")
set(_install_root "${_dry_root}/install_root")

if(NOT EXISTS "${_cli}")
    message(FATAL_ERROR "missing Setup Core CLI: ${_cli}")
endif()
if(NOT EXISTS "${_manifest}")
    message(FATAL_ERROR "missing manifest: ${_manifest}")
endif()

file(REMOVE_RECURSE "${_dry_root}")
file(MAKE_DIRECTORY "${_install_root}")

execute_process(
    COMMAND "${CMAKE_COMMAND}" -E chdir "${ARTIFACT_ROOT}"
        "${_cli}"
        --deterministic 1
        export-invocation
        --manifest "setup/manifests/product.dsumanifest"
        --op install
        --scope portable
        --install-root "${_install_root}"
        --ui-mode cli
        --frontend-id linux-cmake
        --out "${_inv}"
    RESULT_VARIABLE _inv_rc
)
if(NOT _inv_rc EQUAL 0)
    message(FATAL_ERROR "dry-run export-invocation failed (${_inv_rc})")
endif()

execute_process(
    COMMAND "${CMAKE_COMMAND}" -E chdir "${ARTIFACT_ROOT}"
        "${_cli}"
        --deterministic 1
        plan
        --manifest "setup/manifests/product.dsumanifest"
        --invocation "${_inv}"
        --out "${_plan}"
    RESULT_VARIABLE _plan_rc
)
if(NOT _plan_rc EQUAL 0)
    message(FATAL_ERROR "dry-run plan failed (${_plan_rc})")
endif()

execute_process(
    COMMAND "${CMAKE_COMMAND}" -E chdir "${ARTIFACT_ROOT}"
        "${_cli}"
        --deterministic 1
        apply
        --plan "${_plan}"
        --dry-run
    RESULT_VARIABLE _apply_rc
)
if(NOT _apply_rc EQUAL 0)
    message(FATAL_ERROR "dry-run apply failed (${_apply_rc})")
endif()

message(STATUS "wrote ${_tar_path}")
