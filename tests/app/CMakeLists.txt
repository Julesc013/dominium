cmake_minimum_required(VERSION 3.16)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

add_test(NAME app_cli_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/app_cli_contracts.py
        --client $<TARGET_FILE:dominium_client>
        --server $<TARGET_FILE:dominium_server>
        --launcher $<TARGET_FILE:launcher_cli>
        --setup $<TARGET_FILE:setup_cli>
        --tools $<TARGET_FILE:dominium-tools>
        --temp-root ${CMAKE_BINARY_DIR}/tests/app_cli
)

add_test(NAME app_observability
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/app_observability_tests.py
        --client $<TARGET_FILE:dominium_client>
        --tools $<TARGET_FILE:dominium-tools>
)

add_test(NAME app_buildmeta
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/app_buildmeta_tests.py
        --tool $<TARGET_FILE:dom_tool_artifactmeta>
        --input $<TARGET_FILE:dominium-tools>
        --temp-root ${CMAKE_BINARY_DIR}/tests/app_buildmeta
)

add_test(NAME build_include_sanity
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/verify_includes_sanity.py
)

add_test(NAME build_abi_boundaries
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/verify_abi_boundaries.py
        --repo-root ${CMAKE_SOURCE_DIR}
)

add_test(NAME build_arch_checks
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/ci/arch_checks.py
        --repo-root ${CMAKE_SOURCE_DIR}
)
