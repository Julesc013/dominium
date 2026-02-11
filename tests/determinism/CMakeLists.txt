cmake_minimum_required(VERSION 3.16)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

dom_add_testx(NAME determinism_thread_count_invariance
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/determinism_thread_count_invariance.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME determinism_replay_hash_invariance
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/determinism_replay_hash_invariance.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME determinism_ordering_invariance
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/determinism_ordering_invariance.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME determinism_srz
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/srz_determinism_tests.py
        --tool $<TARGET_FILE:dom_tool_srz>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME test_determinism_thread
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/testx_determinism_envelope_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --case thread
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME test_determinism_srz
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/testx_determinism_envelope_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --case srz
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME test_determinism_budget
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/testx_determinism_envelope_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --case budget
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME test_rng_stream_consistency
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/testx_determinism_envelope_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --case rng
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)
