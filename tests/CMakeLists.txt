enable_testing()

add_executable(domino_sys_probe_tests
    domino_sys/test_platform_probe.c
)
target_link_libraries(domino_sys_probe_tests PRIVATE domino_sys)
add_test(NAME domino_sys_probe COMMAND domino_sys_probe_tests)

add_executable(domino_sys_dynarray_tests
    domino_sys/test_dynarray.c
)
target_link_libraries(domino_sys_dynarray_tests PRIVATE domino_sys)
add_test(NAME domino_sys_dynarray COMMAND domino_sys_dynarray_tests)

add_executable(domino_gfx_tests
    domino_gfx/test_gfx_soft.c
)
target_link_libraries(domino_gfx_tests PRIVATE domino_gfx domino_sys)
add_test(NAME domino_gfx_soft COMMAND domino_gfx_tests)

add_executable(domino_sim_tests test_stub.c)
target_link_libraries(domino_sim_tests PRIVATE domino_sim)
add_test(NAME domino_sim_stub COMMAND domino_sim_tests)

add_executable(domino_mod_tests test_stub.c)
target_link_libraries(domino_mod_tests PRIVATE domino_mod)
add_test(NAME domino_mod_stub COMMAND domino_mod_tests)

add_executable(dominium_integration_tests test_stub.c)
target_link_libraries(dominium_integration_tests PRIVATE dominium_rules domino_sys)
add_test(NAME dominium_integration_stub COMMAND dominium_integration_tests)
