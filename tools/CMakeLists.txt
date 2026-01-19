cmake_minimum_required(VERSION 3.16)

add_library(tools_shared STATIC
    _shared/tools_shared_stub.c
)
target_include_directories(tools_shared PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/_shared
)
target_link_libraries(tools_shared
    PUBLIC
        libs::contracts
)
set_target_properties(tools_shared PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_library(tools::shared ALIAS tools_shared)

add_executable(dominium-tools
    tools_host_main.c
)
target_link_libraries(dominium-tools PRIVATE tools::shared)
set_target_properties(dominium-tools PROPERTIES
    OUTPUT_NAME "tools"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_executable(coredata_compile
    coredata_compile_stub.c
)
set_target_properties(coredata_compile PROPERTIES
    OUTPUT_NAME "coredata_compile"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_executable(coredata_validate
    coredata_validate_stub.c
)
set_target_properties(coredata_validate PROPERTIES
    OUTPUT_NAME "coredata_validate"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_executable(data_validate
    data_validate/data_validate_main.c
)
target_link_libraries(data_validate PRIVATE domino_engine)
set_target_properties(data_validate PROPERTIES
    OUTPUT_NAME "data_validate"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_executable(validate_all
    validation/validate_all_main.cpp
    validation/validator_common.cpp
    validation/validator_reports.cpp
    validation/validators_registry.cpp
    validate/tool_validation.cpp
    validate/policy_validation.cpp
)
target_include_directories(validate_all PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
)
set_target_properties(validate_all PROPERTIES
    OUTPUT_NAME "validate_all"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_library(dominium_tools_inspect STATIC
    inspect/replay_inspector.cpp
    inspect/provenance_browser.cpp
    inspect/ledger_inspector.cpp
    inspect/event_timeline_view.cpp
)
target_include_directories(dominium_tools_inspect
    PUBLIC
        ${DOMINIUM_ENGINE_INCLUDE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}/inspect
)
set_target_properties(dominium_tools_inspect PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_executable(dominium_tool0_inspection_tests
    tests/tool0_inspection_tests.cpp
)
target_link_libraries(dominium_tool0_inspection_tests PRIVATE dominium_tools_inspect)
set_target_properties(dominium_tool0_inspection_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME dominium_tool0_inspection
    COMMAND $<TARGET_FILE:dominium_tool0_inspection_tests>
)

add_executable(mod_pack_builder
    modpack/mod_pack_builder.cpp
    validation/validator_common.cpp
)
target_include_directories(mod_pack_builder PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GAME_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
)
target_link_libraries(mod_pack_builder PRIVATE dominium_game)
set_target_properties(mod_pack_builder PROPERTIES
    OUTPUT_NAME "mod_pack_builder"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_executable(mod_pack_validator
    modpack/mod_pack_validator.cpp
    validation/validator_common.cpp
)
target_include_directories(mod_pack_validator PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GAME_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
)
target_link_libraries(mod_pack_validator PRIVATE dominium_game)
set_target_properties(mod_pack_validator PROPERTIES
    OUTPUT_NAME "mod_pack_validator"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_executable(tools::host ALIAS dominium-tools)
add_executable(tools::coredata_compile ALIAS coredata_compile)
add_executable(tools::coredata_validate ALIAS coredata_validate)
add_executable(tools::data_validate ALIAS data_validate)
add_executable(tools::validate_all ALIAS validate_all)

add_test(NAME dominium_validate_all_bad_fallback
    COMMAND $<TARGET_FILE:validate_all>
        --repo-root=${CMAKE_SOURCE_DIR}/tools/validation/fixtures/bad_fallback
        --strict=1
)
set_tests_properties(dominium_validate_all_bad_fallback PROPERTIES WILL_FAIL TRUE)

add_test(NAME dominium_validate_all_bad_float
    COMMAND $<TARGET_FILE:validate_all>
        --repo-root=${CMAKE_SOURCE_DIR}/tools/validation/fixtures/bad_float
        --strict=1
)
set_tests_properties(dominium_validate_all_bad_float PROPERTIES WILL_FAIL TRUE)

add_test(NAME dominium_validate_all_bad_unbounded
    COMMAND $<TARGET_FILE:validate_all>
        --repo-root=${CMAKE_SOURCE_DIR}/tools/validation/fixtures/bad_unbounded
        --strict=1
)
set_tests_properties(dominium_validate_all_bad_unbounded PROPERTIES WILL_FAIL TRUE)

add_test(NAME dominium_validate_all_bad_fabrication
    COMMAND $<TARGET_FILE:validate_all>
        --repo-root=${CMAKE_SOURCE_DIR}/tools/validation/fixtures/bad_fabrication
        --strict=1
)
set_tests_properties(dominium_validate_all_bad_fabrication PROPERTIES WILL_FAIL TRUE)

add_test(NAME dominium_validate_all_bad_ui
    COMMAND $<TARGET_FILE:validate_all>
        --repo-root=${CMAKE_SOURCE_DIR}/tools/validation/fixtures/bad_ui
        --strict=1
)
set_tests_properties(dominium_validate_all_bad_ui PROPERTIES WILL_FAIL TRUE)

add_test(NAME dominium_validate_all_bad_renderer
    COMMAND $<TARGET_FILE:validate_all>
        --repo-root=${CMAKE_SOURCE_DIR}/tools/validation/fixtures/bad_renderer
        --strict=1
)
set_tests_properties(dominium_validate_all_bad_renderer PROPERTIES WILL_FAIL TRUE)

add_test(NAME dominium_content1_sol_data
    COMMAND python ${CMAKE_SOURCE_DIR}/tools/ci/validate_sol_data.py
        --repo-root=${CMAKE_SOURCE_DIR}
)

add_test(NAME dominium_content2_earth_data
    COMMAND python ${CMAKE_SOURCE_DIR}/tools/ci/validate_earth_data.py
        --repo-root=${CMAKE_SOURCE_DIR}
)

add_test(NAME dominium_content3_milky_way_data
    COMMAND python ${CMAKE_SOURCE_DIR}/tools/ci/validate_milky_way_data.py
        --repo-root=${CMAKE_SOURCE_DIR}
)
