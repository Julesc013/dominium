cmake_minimum_required(VERSION 3.16)

get_filename_component(ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)

set(SCHEMA_FILES
    "${ROOT}/source/dominium/setup/kernel/include/dsk/dsk_contracts.h"
    "${ROOT}/source/dominium/setup/kernel/include/dsk/dsk_contract_plan.h"
    "${ROOT}/source/dominium/setup/kernel/include/dsk/dsk_audit.h"
    "${ROOT}/source/dominium/setup/kernel/include/dsk/dsk_jobs.h"
    "${ROOT}/source/dominium/setup/services/include/dss/dss_txn.h"
    "${ROOT}/include/dominium/core_installed_state.h"
)

set(ACCUM "")
foreach(FILE_PATH IN LISTS SCHEMA_FILES)
    if(NOT EXISTS "${FILE_PATH}")
        message(FATAL_ERROR "schema_freeze_check: missing file ${FILE_PATH}")
    endif()
    file(READ "${FILE_PATH}" FILE_CONTENT)
    set(ACCUM "${ACCUM}\n-- ${FILE_PATH} --\n${FILE_CONTENT}")
endforeach()

string(SHA256 SCHEMA_HASH "${ACCUM}")
string(TOLOWER "${SCHEMA_HASH}" SCHEMA_HASH)

if(DEFINED SCHEMA_FREEZE_PRINT_ONLY AND SCHEMA_FREEZE_PRINT_ONLY)
    message(STATUS "schema_freeze_hash=${SCHEMA_HASH}")
    return()
endif()

set(DOC_PATH "${ROOT}/docs/setup2/SCHEMA_FREEZE_V1.md")
if(NOT EXISTS "${DOC_PATH}")
    message(FATAL_ERROR "schema_freeze_check: missing ${DOC_PATH}")
endif()

file(READ "${DOC_PATH}" DOC_CONTENTS)
string(REGEX MATCH "schema_hash:[ \t]*([0-9a-fA-F]+)" MATCH "${DOC_CONTENTS}")
if(NOT MATCH)
    message(FATAL_ERROR "schema_freeze_check: missing schema_hash in SCHEMA_FREEZE_V1.md")
endif()
set(DOC_HASH "${CMAKE_MATCH_1}")
string(TOLOWER "${DOC_HASH}" DOC_HASH)

if(NOT SCHEMA_HASH STREQUAL DOC_HASH)
    message(FATAL_ERROR "schema_freeze_check: schema hash mismatch (doc=${DOC_HASH} actual=${SCHEMA_HASH})")
endif()

message(STATUS "schema_freeze_check: OK (${SCHEMA_HASH})")
