add_executable(engine_smoke_test
    engine_smoke_test.c
)
target_link_libraries(engine_smoke_test PRIVATE engine::domino)
set_target_properties(engine_smoke_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_test(NAME engine_smoke COMMAND engine_smoke_test)

add_executable(engine_det_order_test
    engine_det_order_test.c
)
target_link_libraries(engine_det_order_test PRIVATE engine::domino)
target_include_directories(engine_det_order_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../modules
)
set_target_properties(engine_det_order_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_test(NAME engine_det_order COMMAND engine_det_order_test)

add_executable(engine_perf_no_modal_test
    engine_perf_no_modal_test.c
)
target_link_libraries(engine_perf_no_modal_test PRIVATE engine::domino)
set_target_properties(engine_perf_no_modal_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_test(NAME engine_perf_no_modal COMMAND engine_perf_no_modal_test)

add_executable(engine_due_sched_test
    engine_due_sched_test.c
)
target_link_libraries(engine_due_sched_test PRIVATE engine::domino)
set_target_properties(engine_due_sched_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_test(NAME engine_due_sched COMMAND engine_due_sched_test)

add_executable(engine_perf_budget_test
    engine_perf_budget_test.c
)
target_link_libraries(engine_perf_budget_test PRIVATE engine::domino)
target_include_directories(engine_perf_budget_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../modules
)
set_target_properties(engine_perf_budget_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

set(_dom_perf_run_root "${CMAKE_BINARY_DIR}/run_root_perf_budget")
add_test(NAME engine_perf_budget_fixture COMMAND engine_perf_budget_test)
set_tests_properties(engine_perf_budget_fixture PROPERTIES
    FIXTURES_SETUP perf_budget
    ENVIRONMENT "DOMINIUM_RUN_ROOT=${_dom_perf_run_root}"
)

add_test(NAME engine_perf_budget_check
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/ci/perf_budget_check.py
        --run-root ${_dom_perf_run_root}
        --budgets ${CMAKE_SOURCE_DIR}/docs/PERF_BUDGETS.md
)
set_tests_properties(engine_perf_budget_check PROPERTIES
    FIXTURES_REQUIRED perf_budget
    ENVIRONMENT "DOMINIUM_RUN_ROOT=${_dom_perf_run_root}"
)

add_executable(engine_data_validate_test
    engine_data_validate_test.c
)
target_link_libraries(engine_data_validate_test PRIVATE engine::domino)
set_target_properties(engine_data_validate_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_test(NAME engine_data_validate COMMAND engine_data_validate_test)

add_executable(execution_ir_tests
    execution_ir_tests.cpp
)
target_link_libraries(execution_ir_tests PRIVATE engine::domino)
set_target_properties(execution_ir_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME execution_ir COMMAND execution_ir_tests)

add_executable(execution_scheduler_ref_tests
    execution_scheduler_ref_tests.cpp
)
target_link_libraries(execution_scheduler_ref_tests PRIVATE engine::domino)
target_include_directories(execution_scheduler_ref_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../modules
)
set_target_properties(execution_scheduler_ref_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME execution_scheduler_ref COMMAND execution_scheduler_ref_tests)

add_executable(execution_scheduler_law_tests
    execution_scheduler_law_tests.cpp
)
target_link_libraries(execution_scheduler_law_tests PRIVATE engine::domino)
target_include_directories(execution_scheduler_law_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../modules
)
set_target_properties(execution_scheduler_law_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME execution_scheduler_law COMMAND execution_scheduler_law_tests)
