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

add_executable(dsys_stub_tests
    domino_sys/test_dsys_stub.c
)
target_link_libraries(dsys_stub_tests PRIVATE domino_sys)
add_test(NAME dsys_stub COMMAND dsys_stub_tests)

add_executable(domino_gfx_tests
    domino_gfx/test_gfx_soft.c
)
target_link_libraries(domino_gfx_tests PRIVATE domino_gfx domino_sys)
add_test(NAME domino_gfx_soft COMMAND domino_gfx_tests)

add_executable(domino_core_smoke
    domino_core/test_dom_core_smoke.c
)
target_link_libraries(domino_core_smoke PRIVATE
    -Wl,--start-group
    domino_engine
    dominium_rules
    domino_mod
    domino_sim
    domino_core
    domino_gfx
    domino_sys
    -Wl,--end-group
)
add_test(NAME domino_core_smoke COMMAND domino_core_smoke)

add_executable(domino_sim_tests test_stub.c)
target_link_libraries(domino_sim_tests PRIVATE domino_sim)
add_test(NAME domino_sim_stub COMMAND domino_sim_tests)

add_executable(domino_mod_tests test_stub.c)
target_link_libraries(domino_mod_tests PRIVATE domino_mod)
add_test(NAME domino_mod_stub COMMAND domino_mod_tests)

add_executable(dominium_integration_tests test_stub.c)
target_link_libraries(dominium_integration_tests PRIVATE
    -Wl,--start-group
    dominium_rules
    domino_engine
    domino_mod
    domino_sim
    domino_core
    domino_gfx
    domino_sys
    -Wl,--end-group
)
add_test(NAME dominium_integration_stub COMMAND dominium_integration_tests)

add_executable(domino_sim_dominium_tests
    domino_sim/test_domino_dominium_sim.c
)
target_link_libraries(domino_sim_dominium_tests PRIVATE
    -Wl,--start-group
    domino_engine
    dominium_rules
    domino_mod
    domino_sim
    domino_core
    domino_gfx
    domino_sys
    -Wl,--end-group
)
add_test(NAME domino_sim_dominium COMMAND domino_sim_dominium_tests)

add_executable(domino_canvas_tests
    domino_gfx/test_domino_canvas_build.c
)
target_link_libraries(domino_canvas_tests PRIVATE
    -Wl,--start-group
    domino_engine
    dominium_rules
    domino_mod
    domino_sim
    domino_core
    domino_gfx
    domino_sys
    -Wl,--end-group
)
add_test(NAME domino_canvas_build COMMAND domino_canvas_tests)

if(DOMINO_USE_X11_BACKEND)
    add_executable(dsys_x11_tests
        domino_sys/test_dsys_x11.c
    )
    target_link_libraries(dsys_x11_tests PRIVATE domino_engine)
    if(TARGET X11::X11)
        target_link_libraries(dsys_x11_tests PRIVATE X11::X11)
    elseif(X11_LIBRARIES)
        target_link_libraries(dsys_x11_tests PRIVATE ${X11_LIBRARIES})
    endif()
    add_test(NAME dsys_x11 COMMAND dsys_x11_tests)
endif()
