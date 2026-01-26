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

add_executable(execution_contract_tests
    execution_contract_tests.cpp
)
target_link_libraries(execution_contract_tests PRIVATE engine::domino)
target_include_directories(execution_contract_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../modules
)
set_target_properties(execution_contract_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME execution_contract COMMAND execution_contract_tests)

add_executable(agent_foundation_contract_tests
    agent_foundation_contract_tests.cpp
)
target_link_libraries(agent_foundation_contract_tests PRIVATE engine::domino)
target_compile_definitions(agent_foundation_contract_tests PRIVATE
    DOMINIUM_REPO_ROOT="${CMAKE_SOURCE_DIR}"
)
set_target_properties(agent_foundation_contract_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME agent_foundation_contract COMMAND agent_foundation_contract_tests)

add_executable(agent_mvp_core_tests
    agent_mvp_core_tests.cpp
)
target_link_libraries(agent_mvp_core_tests PRIVATE engine::domino game::dominium)
set_target_properties(agent_mvp_core_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME agent_mvp_core COMMAND agent_mvp_core_tests)

add_executable(agent_mvp_social_tests
    agent_mvp_social_tests.cpp
)
target_link_libraries(agent_mvp_social_tests PRIVATE engine::domino game::dominium)
set_target_properties(agent_mvp_social_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME agent_mvp_social COMMAND agent_mvp_social_tests)

add_executable(physicalization_mvp_tests
    physicalization_mvp_tests.cpp
)
target_link_libraries(physicalization_mvp_tests PRIVATE engine::domino game::dominium)
set_target_properties(physicalization_mvp_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME physicalization_mvp COMMAND physicalization_mvp_tests)

add_executable(player_embodiment_tests
    player_embodiment_tests.cpp
)
target_link_libraries(player_embodiment_tests PRIVATE engine::domino game::dominium)
set_target_properties(player_embodiment_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME player_embodiment COMMAND player_embodiment_tests)

add_executable(execution_equivalence_tests
    execution_equivalence_tests.cpp
)
target_link_libraries(execution_equivalence_tests PRIVATE engine::domino)
target_include_directories(execution_equivalence_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../modules
)
set_target_properties(execution_equivalence_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME execution_equivalence COMMAND execution_equivalence_tests)

add_executable(ecs_storage_iface_tests
    ecs_storage_iface_tests.cpp
)
target_link_libraries(ecs_storage_iface_tests PRIVATE engine::domino)
set_target_properties(ecs_storage_iface_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME ecs_storage_iface COMMAND ecs_storage_iface_tests)

add_executable(ecs_soa_storage_tests
    ecs_soa_storage_tests.cpp
)
target_link_libraries(ecs_soa_storage_tests PRIVATE engine::domino)
target_include_directories(ecs_soa_storage_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../modules
)
set_target_properties(ecs_soa_storage_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME ecs_soa_storage COMMAND ecs_soa_storage_tests)

add_executable(ecs_packed_view_tests
    ecs_packed_view_tests.cpp
)
target_link_libraries(ecs_packed_view_tests PRIVATE engine::domino)
set_target_properties(ecs_packed_view_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME ecs_packed_view COMMAND ecs_packed_view_tests)

add_executable(kernel_iface_tests
    kernel_iface_tests.cpp
)
target_link_libraries(kernel_iface_tests PRIVATE engine::domino)
target_include_directories(kernel_iface_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../modules
)
set_target_properties(kernel_iface_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME kernel_iface COMMAND kernel_iface_tests)

add_executable(kernel_scalar_tests
    kernel_scalar_tests.cpp
)
target_link_libraries(kernel_scalar_tests PRIVATE engine::domino)
target_include_directories(kernel_scalar_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../modules
)
set_target_properties(kernel_scalar_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME kernel_scalar COMMAND kernel_scalar_tests)

add_executable(kernel_simd_equivalence_tests
    kernel_simd_equivalence_tests.cpp
)
target_link_libraries(kernel_simd_equivalence_tests PRIVATE engine::domino)
target_include_directories(kernel_simd_equivalence_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../modules
)
set_target_properties(kernel_simd_equivalence_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME kernel_simd_equivalence COMMAND kernel_simd_equivalence_tests)

add_executable(kernel_gpu_fallback_tests
    kernel_gpu_fallback_tests.cpp
)
target_link_libraries(kernel_gpu_fallback_tests PRIVATE engine::domino)
target_include_directories(kernel_gpu_fallback_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../modules
)
set_target_properties(kernel_gpu_fallback_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME kernel_gpu_fallback COMMAND kernel_gpu_fallback_tests)

add_executable(kernel_policy_tests
    kernel_policy_tests.cpp
)
target_link_libraries(kernel_policy_tests PRIVATE engine::domino)
target_include_directories(kernel_policy_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../modules
)
set_target_properties(kernel_policy_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME kernel_policy COMMAND kernel_policy_tests)

add_executable(sys_caps_tests
    sys_caps_tests.cpp
)
target_link_libraries(sys_caps_tests PRIVATE engine::domino)
set_target_properties(sys_caps_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME sys_caps COMMAND sys_caps_tests)

add_executable(execution_policy_tests
    execution_policy_tests.cpp
)
target_link_libraries(execution_policy_tests PRIVATE engine::domino)
set_target_properties(execution_policy_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME execution_policy COMMAND execution_policy_tests)

add_executable(budget_model_tests
    budget_model_tests.cpp
)
target_link_libraries(budget_model_tests PRIVATE engine::domino)
set_target_properties(budget_model_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME budget_model COMMAND budget_model_tests)

add_executable(domain_volume_tests
    domain_volume_tests.cpp
)
target_link_libraries(domain_volume_tests PRIVATE engine::domino)
set_target_properties(domain_volume_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME domain_volume COMMAND domain_volume_tests)

add_executable(visitability_contract_tests
    visitability_contract_tests.cpp
)
target_link_libraries(visitability_contract_tests PRIVATE engine::domino game::dominium)
set_target_properties(visitability_contract_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME visitability_contract COMMAND visitability_contract_tests)

add_executable(execution_perf_regression_tests
    execution_perf_regression_tests.cpp
)
target_link_libraries(execution_perf_regression_tests PRIVATE engine::domino)
target_include_directories(execution_perf_regression_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../modules
)
target_compile_definitions(execution_perf_regression_tests PRIVATE
    DOMINIUM_FIXTURES_DIR="${CMAKE_SOURCE_DIR}/game/tests/fixtures"
)
set_target_properties(execution_perf_regression_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME execution_perf_regression COMMAND execution_perf_regression_tests)

add_executable(render_prep_work_ir_tests
    render_prep_work_ir_tests.cpp
)
target_sources(render_prep_work_ir_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/client/presentation/frame_graph_builder.cpp
    ${CMAKE_SOURCE_DIR}/client/presentation/render_prep_system.cpp
)
target_link_libraries(render_prep_work_ir_tests PRIVATE engine::domino game::dominium)
target_include_directories(render_prep_work_ir_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../modules
    ${CMAKE_SOURCE_DIR}/client/presentation
)
set_target_properties(render_prep_work_ir_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME render_prep_work_ir COMMAND render_prep_work_ir_tests)

add_executable(streaming_work_ir_tests
    streaming_work_ir_tests.cpp
)
target_link_libraries(streaming_work_ir_tests PRIVATE engine::domino game::dominium)
target_include_directories(streaming_work_ir_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../modules
)
set_target_properties(streaming_work_ir_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME streaming_work_ir COMMAND streaming_work_ir_tests)
