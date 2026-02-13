cmake_minimum_required(VERSION 3.16)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

dom_add_testx(NAME test_future_case_stress_suite
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test_future_case_stress_suite.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME test_profile_switch_requires_restart
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/profile_bundle_stress_suite.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --case profile_switch_requires_restart
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME test_remove_optional_bundle_core_boots
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/profile_bundle_stress_suite.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --case remove_optional_bundle_core_boots
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME test_survival_to_creative_transition
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/profile_bundle_stress_suite.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --case survival_to_creative_transition
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME test_survival_hardcore_delta_only
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/profile_bundle_stress_suite.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --case survival_hardcore_delta_only
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME test_bundle_not_installed_refusal
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/profile_bundle_stress_suite.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --case bundle_not_installed_refusal
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)
