cmake_minimum_required(VERSION 3.16)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

dom_add_testx(NAME app_cli_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/app_cli_contracts.py
        --client $<TARGET_FILE:dominium_client>
        --server $<TARGET_FILE:dominium_server>
        --launcher $<TARGET_FILE:launcher_cli>
        --setup $<TARGET_FILE:setup_cli>
        --tools $<TARGET_FILE:dominium-tools>
        --temp-root ${CMAKE_BINARY_DIR}/tests/app_cli
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)
dom_register_product_cli_tests(client app_cli_contracts app_cli_contracts app_cli_contracts)
dom_register_product_cli_tests(server app_cli_contracts app_cli_contracts app_cli_contracts)
dom_register_product_cli_tests(launcher app_cli_contracts app_cli_contracts app_cli_contracts)
dom_register_product_cli_tests(setup app_cli_contracts app_cli_contracts app_cli_contracts)
dom_register_product_cli_tests(tools app_cli_contracts app_cli_contracts app_cli_contracts)

dom_add_testx(NAME app_ui_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/app_ui_contracts.py
        --client $<TARGET_FILE:dominium_client>
        --launcher $<TARGET_FILE:launcher_cli>
        --tools $<TARGET_FILE:dominium-tools>
        --temp-root ${CMAKE_BINARY_DIR}/tests/app_ui
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME slice0_flow_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/slice0_flow_tests.py
        --client $<TARGET_FILE:dominium_client>
        --temp-root ${CMAKE_BINARY_DIR}/tests/slice0_flow
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME slice0_hardcoded_ids
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/slice0_hardcoded_ids.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME world_definition_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/ci/validate_world_definition.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME app_observability
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/app_observability_tests.py
        --client $<TARGET_FILE:dominium_client>
        --tools $<TARGET_FILE:dominium-tools>
)

dom_add_testx(NAME app_buildmeta
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/app_buildmeta_tests.py
        --tool $<TARGET_FILE:dom_tool_artifactmeta>
        --input $<TARGET_FILE:dominium-tools>
        --temp-root ${CMAKE_BINARY_DIR}/tests/app_buildmeta
    LABELS ${DOM_TESTX_LABEL_BUILDMETA}
)

dom_add_testx(NAME build_include_sanity
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/verify_includes_sanity.py
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME build_abi_boundaries
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/verify_abi_boundaries.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME build_arch_checks
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/ci/arch_checks.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)
