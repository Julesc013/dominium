cmake_minimum_required(VERSION 3.16)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

dom_add_testx(NAME const_id_reuse_detection
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/id_reuse_detection.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME const_namespace_validation
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/namespace_validation.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME const_deterministic_ordering
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/deterministic_ordering_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME const_determinism_hardlocks
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/determinism_hardlock_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME const_legacy_header_parse
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/legacy_header_parse_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME const_refusal_code_stability
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/refusal_code_stability.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME const_unit_annotation_validation
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/unit_annotation_validation.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME const_no_raw_file_paths
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/no_raw_file_paths_lint.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME const_archive_presence
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/archive_presence_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME const_product_shell_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/product_shell/product_shell_contract_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME const_frozen_contract_hashes
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/frozen_contracts_guard.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME const_drp1_data_first_guard
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/drp1_data_first_guard.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME const_terrain_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/terrain_contract_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME const_srz_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/srz_contract_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME public_header_c89_compile
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/public_header_c89_compile.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME public_header_cpp98_compile
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/public_header_cpp98_compile.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME schema_roundtrip_unknown_preservation
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/schema_roundtrip_unknown_preservation.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME pack_scope_enforcement_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/pack_scope_enforcement_contracts.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME compat_report_presence_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/compat_report_presence_contracts.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME schema_change_notes_required
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/schema_change_notes_required.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME compliance_report_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/compliance_report_contracts.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME capability_gating_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/capability_gating_contracts.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME capability_matrix_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tests/testx/capability_matrix_contracts.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

set(DOM_CAPABILITY_MATRIX_SET_DIRS
    stage_0_nonbio
    stage_1_nonintelligent_life
    stage_2_intelligent_pre_tool
    stage_3_pre_tool_world
    stage_4_pre_industry
    stage_5_pre_present
    stage_6_future
)

set(DOM_CAPABILITY_MATRIX_SUITES
    test_load_and_validate
    test_command_surface
    test_pack_gating
    test_epistemics
    test_determinism_smoke
    test_replay_hash
)

foreach(capability_dir IN LISTS DOM_CAPABILITY_MATRIX_SET_DIRS)
    foreach(suite_name IN LISTS DOM_CAPABILITY_MATRIX_SUITES)
        dom_add_testx(NAME capability_matrix_${capability_dir}_${suite_name}
            COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tests/testx/stages/${capability_dir}/${suite_name}.py
            LABELS ${DOM_TESTX_LABEL_PORTABILITY}
        )
    endforeach()
endforeach()

set(DOM_CAPABILITY_MATRIX_REGRESSION
    test_no_life_without_capability
    test_no_tools_without_capability
    test_no_industry_without_capability
    test_no_future_without_capability
)

foreach(regression_name IN LISTS DOM_CAPABILITY_MATRIX_REGRESSION)
    dom_add_testx(NAME capability_regression_${regression_name}
        COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tests/testx/stage_regression/${regression_name}.py
        LABELS ${DOM_TESTX_LABEL_PORTABILITY}
    )
endforeach()
