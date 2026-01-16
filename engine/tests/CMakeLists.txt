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
