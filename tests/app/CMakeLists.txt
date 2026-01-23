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
