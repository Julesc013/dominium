cmake_minimum_required(VERSION 3.16)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

dom_add_testx(NAME playtest_scenario_parity
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/playtest_scenario_parity_tests.py
        --client $<TARGET_FILE:dominium_client>
        --repo-root ${CMAKE_SOURCE_DIR}
        --temp-root ${CMAKE_BINARY_DIR}/tests/playtest_scenario_parity
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME playtest_variant_replay
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/playtest_variant_replay_tests.py
        --client $<TARGET_FILE:dominium_client>
        --repo-root ${CMAKE_SOURCE_DIR}
        --temp-root ${CMAKE_BINARY_DIR}/tests/playtest_variant_replay
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME playtest_replay_regression
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/playtest_replay_regression_tests.py
        --client $<TARGET_FILE:dominium_client>
        --repo-root ${CMAKE_SOURCE_DIR}
        --temp-root ${CMAKE_BINARY_DIR}/tests/playtest_replay_regression
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME playtest_mode_parity
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/playtest_mode_parity_tests.py
        --client $<TARGET_FILE:dominium_client>
        --repo-root ${CMAKE_SOURCE_DIR}
        --temp-root ${CMAKE_BINARY_DIR}/tests/playtest_mode_parity
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)
