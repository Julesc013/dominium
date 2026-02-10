cmake_minimum_required(VERSION 3.16)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

dom_add_testx(NAME tools_pack_validate
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools_pack_validate_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME tools_capability_inspect
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools_capability_inspect_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME tools_fab_diff
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools_fab_diff_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME tools_refusal_explain
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools_refusal_explain_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME tools_coverage_inspect
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools_coverage_inspect_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME tools_auditx
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools_auditx_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)
