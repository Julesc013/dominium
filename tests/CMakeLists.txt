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

add_executable(domino_lod_framework_tests
    domino_sim/test_dg_lod_framework.c
)
target_link_libraries(domino_lod_framework_tests PRIVATE domino_core)
add_test(NAME domino_lod_framework COMMAND domino_lod_framework_tests)

add_executable(domino_pose_anchor_tests
    domino_sim/test_dg_pose_anchor_quant.c
)
target_link_libraries(domino_pose_anchor_tests PRIVATE domino_core)
add_test(NAME domino_pose_anchor COMMAND domino_pose_anchor_tests)

add_executable(domino_domains_frames_prop_tests
    domino_sim/test_dg_domains_frames_prop.c
)
target_link_libraries(domino_domains_frames_prop_tests PRIVATE domino_core)
add_test(NAME domino_domains_frames_prop COMMAND domino_domains_frames_prop_tests)

add_executable(domino_trans_compile_tests
    domino_trans/test_dg_trans_compile_determinism.c
)
target_link_libraries(domino_trans_compile_tests PRIVATE domino_core)
add_test(NAME domino_trans_compile COMMAND domino_trans_compile_tests)

add_executable(domino_struct_compile_tests
    domino_struct/test_dg_struct_compile_determinism.c
)
target_link_libraries(domino_struct_compile_tests PRIVATE domino_core)
add_test(NAME domino_struct_compile COMMAND domino_struct_compile_tests)

add_executable(domino_decor_compile_tests
    domino_decor/test_dg_decor_compile_determinism.c
)
target_link_libraries(domino_decor_compile_tests PRIVATE domino_core)
add_test(NAME domino_decor_compile COMMAND domino_decor_compile_tests)

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

if(DOMINO_USE_POSIX_BACKEND)
    add_executable(dsys_posix_tests
        domino_sys/test_dsys_posix.c
    )
    target_link_libraries(dsys_posix_tests PRIVATE domino_engine)
    add_test(NAME dsys_posix COMMAND dsys_posix_tests)
endif()

add_executable(dominium_contract_tests
    contract/dominium_contract_tests.cpp
)
target_include_directories(dominium_contract_tests PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/dominium/launcher/core/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
)
target_compile_definitions(dominium_contract_tests PRIVATE
    DOM_TLV_VECTORS_DIR="${CMAKE_SOURCE_DIR}/tests/vectors/tlv"
)
target_link_libraries(dominium_contract_tests PRIVATE
    dominium_launcher_core
    launcher_services_impl_null
    dsk_kernel
    core_job
    core_tlv_schema
)
set_target_properties(dominium_contract_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if (MSVC)
    target_compile_options(dominium_contract_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_contract_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()
add_test(NAME dominium_contract_schema_vectors COMMAND dominium_contract_tests schema_vectors)
add_test(NAME dominium_contract_installed_state COMMAND dominium_contract_tests installed_state_contract)
add_test(NAME dominium_contract_handshake COMMAND dominium_contract_tests handshake_contract)
add_test(NAME dominium_contract_pack_resolver COMMAND dominium_contract_tests pack_resolver_contract)
add_test(NAME dominium_contract_selection_audit COMMAND dominium_contract_tests selection_audit_contract)
add_test(NAME dominium_contract_job_journal COMMAND dominium_contract_tests job_journal_contract)

add_executable(dominium_tlv_fuzz_tests
    contract/dominium_tlv_fuzz_tests.cpp
)
target_include_directories(dominium_tlv_fuzz_tests PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/dominium/launcher/core/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
)
target_compile_definitions(dominium_tlv_fuzz_tests PRIVATE
    DOM_TLV_VECTORS_DIR="${CMAKE_SOURCE_DIR}/tests/vectors/tlv"
)
target_link_libraries(dominium_tlv_fuzz_tests PRIVATE
    dominium_launcher_core
    dsk_kernel
    core_job
    core_tlv_schema
)
set_target_properties(dominium_tlv_fuzz_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if (MSVC)
    target_compile_options(dominium_tlv_fuzz_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_tlv_fuzz_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()
add_test(NAME dominium_tlv_fuzz COMMAND dominium_tlv_fuzz_tests)

add_test(NAME dominium_layer_checks
    COMMAND ${CMAKE_COMMAND} -E chdir ${CMAKE_SOURCE_DIR} python scripts/check_layers.py
)

add_subdirectory(setup2)
