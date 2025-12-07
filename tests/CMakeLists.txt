enable_testing()

add_executable(domino_sys_tests test_stub.c)
target_link_libraries(domino_sys_tests PRIVATE domino_sys)
add_test(NAME domino_sys_stub COMMAND domino_sys_tests)

add_executable(domino_gfx_tests test_stub.c)
target_link_libraries(domino_gfx_tests PRIVATE domino_gfx)
add_test(NAME domino_gfx_stub COMMAND domino_gfx_tests)

add_executable(domino_sim_tests test_stub.c)
target_link_libraries(domino_sim_tests PRIVATE domino_sim)
add_test(NAME domino_sim_stub COMMAND domino_sim_tests)

add_executable(domino_mod_tests test_stub.c)
target_link_libraries(domino_mod_tests PRIVATE domino_mod)
add_test(NAME domino_mod_stub COMMAND domino_mod_tests)

add_executable(dominium_integration_tests test_stub.c)
target_link_libraries(dominium_integration_tests PRIVATE dominium_rules domino_sys)
add_test(NAME dominium_integration_stub COMMAND dominium_integration_tests)
