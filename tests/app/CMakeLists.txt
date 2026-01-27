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

dom_add_testx(NAME slice1_physical_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/slice1_physical_tests.py
        --client $<TARGET_FILE:dominium_client>
        --temp-root ${CMAKE_BINARY_DIR}/tests/slice1_physical
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME slice1_hardcoded_constants
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/slice1_hardcoded_constants.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME slice2_coordination_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/slice2_coordination_tests.py
        --client $<TARGET_FILE:dominium_client>
        --temp-root ${CMAKE_BINARY_DIR}/tests/slice2_coordination
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME slice2_hardcoded_roles
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/slice2_hardcoded_roles.py
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

dom_add_testx(NAME semantic_stability_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/semantic_stability_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME pack_resolution_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/pack_resolution_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME save_pipeline_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/save_pipeline_contract_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME refusal_budget_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/refusal_budget_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME namespace_unit_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/namespace_unit_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME mod_ecosystem_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/mod_ecosystem_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME harden1_docs_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/harden1_docs_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME scale0_collapse_expand_equivalence
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/scale0_contract_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --family collapse_expand_equivalence
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME scale0_invariant_conservation
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/scale0_contract_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --family invariant_conservation
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME scale0_tolerance_bound
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/scale0_contract_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --family tolerance_bound
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME scale0_interest_pattern_invariance
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/scale0_contract_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --family interest_pattern_invariance
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME scale0_cross_thread_determinism
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/scale0_contract_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --family cross_thread_determinism
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME scale0_replay_equivalence
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/scale0_contract_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --family replay_equivalence
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME baseline_sku_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/baseline_sku_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME path_hygiene_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/path_hygiene_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME modpack_workspace_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/modpack_workspace_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME legacy_header_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/legacy_header_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME determinism_hash_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/determinism_hash_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)
