cmake_minimum_required(VERSION 3.16)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

dom_add_testx(NAME historical_blocker_tool_discovery
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/historical_blocker_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --case tool_discovery
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME historical_blocker_derived_nondeterminism
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/historical_blocker_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --case derived_nondeterminism
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME historical_blocker_direct_gate_invocation
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/historical_blocker_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --case direct_gate_invocation
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME historical_blocker_stage_token
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/historical_blocker_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --case stage_token
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME historical_blocker_identity_drift
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/historical_blocker_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --case identity_drift
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME test_identity_explanation_required
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/historical_blocker_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --case identity_explanation_required
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)
