cmake_minimum_required(VERSION 3.16)

enable_testing()

set(DG_DET_SCAN_FILES "")
foreach(dir IN ITEMS
    ${CMAKE_SOURCE_DIR}/source/domino/core
    ${CMAKE_SOURCE_DIR}/source/domino/agent
    ${CMAKE_SOURCE_DIR}/source/domino/decor
    ${CMAKE_SOURCE_DIR}/source/domino/sim
    ${CMAKE_SOURCE_DIR}/source/domino/struct
    ${CMAKE_SOURCE_DIR}/source/domino/trans
    ${CMAKE_SOURCE_DIR}/source/domino/world
)
    file(GLOB_RECURSE dir_files CONFIGURE_DEPENDS
        ${dir}/*.c
        ${dir}/*.h
    )
    list(APPEND DG_DET_SCAN_FILES ${dir_files})
endforeach()
list(SORT DG_DET_SCAN_FILES)

list(FILTER DG_DET_SCAN_FILES EXCLUDE REGEX "core_internal\\.h$")
list(FILTER DG_DET_SCAN_FILES EXCLUDE REGEX "fixed_debug\\.c$")
list(FILTER DG_DET_SCAN_FILES EXCLUDE REGEX "fs_util\\.c$")

set(DG_DET_SCAN_FILES_REL "")
foreach(abs IN LISTS DG_DET_SCAN_FILES)
    file(RELATIVE_PATH rel ${CMAKE_SOURCE_DIR} ${abs})
    string(REPLACE "\\" "/" rel ${rel})
    list(APPEND DG_DET_SCAN_FILES_REL ${rel})
endforeach()

set(DG_DET_SCAN_OUT_H ${CMAKE_CURRENT_BINARY_DIR}/dg_det_scan_files.h)
file(WRITE ${DG_DET_SCAN_OUT_H}
    "/* Generated: deterministic source scan file list. */\n"
    "#ifndef DG_DET_SCAN_FILES_H\n"
    "#define DG_DET_SCAN_FILES_H\n"
    "static const char *dg_det_scan_files[] = {\n"
)
foreach(rel IN LISTS DG_DET_SCAN_FILES_REL)
    file(APPEND ${DG_DET_SCAN_OUT_H} "    \"${rel}\",\n")
endforeach()
file(APPEND ${DG_DET_SCAN_OUT_H}
    "};\n"
    "static const unsigned dg_det_scan_file_count = (unsigned)(sizeof(dg_det_scan_files) / sizeof(dg_det_scan_files[0]));\n"
    "#endif /* DG_DET_SCAN_FILES_H */\n"
)

add_executable(domino_numeric_test
    numeric_test.c
)

target_include_directories(domino_numeric_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_numeric_test
    domino_core
)

set_target_properties(domino_numeric_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_numeric_test COMMAND domino_numeric_test)

add_executable(domino_pkt_determinism_test
    pkt_determinism_test.c
)

target_include_directories(domino_pkt_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_pkt_determinism_test
    domino_core
)

set_target_properties(domino_pkt_determinism_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_pkt_determinism_test COMMAND domino_pkt_determinism_test)

add_executable(domino_sched_determinism_test
    sched_determinism_test.c
)

target_include_directories(domino_sched_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_sched_determinism_test
    domino_core
)

set_target_properties(domino_sched_determinism_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_sched_determinism_test COMMAND domino_sched_determinism_test)

add_executable(domino_stimulus_determinism_test
    stimulus_determinism_test.c
)

target_include_directories(domino_stimulus_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_stimulus_determinism_test
    domino_core
)

set_target_properties(domino_stimulus_determinism_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_stimulus_determinism_test COMMAND domino_stimulus_determinism_test)

add_executable(domino_lod_framework_test
    lod_framework_test.c
)

target_include_directories(domino_lod_framework_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_lod_framework_test
    domino_core
)

set_target_properties(domino_lod_framework_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_lod_framework_test COMMAND domino_lod_framework_test)

add_executable(domino_pose_anchor_quant_test
    pose_anchor_quant_test.c
)

target_include_directories(domino_pose_anchor_quant_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_pose_anchor_quant_test
    domino_core
)

set_target_properties(domino_pose_anchor_quant_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_pose_anchor_quant_test COMMAND domino_pose_anchor_quant_test)

add_executable(domino_trans_compile_determinism_test
    ../../tests/domino_trans/test_dg_trans_compile_determinism.c
)

target_include_directories(domino_trans_compile_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_trans_compile_determinism_test
    domino_core
)

set_target_properties(domino_trans_compile_determinism_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_trans_compile_determinism_test COMMAND domino_trans_compile_determinism_test)

add_executable(domino_struct_compile_determinism_test
    ../../tests/domino_struct/test_dg_struct_compile_determinism.c
)

target_include_directories(domino_struct_compile_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_struct_compile_determinism_test
    domino_core
)

set_target_properties(domino_struct_compile_determinism_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_struct_compile_determinism_test COMMAND domino_struct_compile_determinism_test)

add_executable(domino_decor_compile_determinism_test
    ../../tests/domino_decor/test_dg_decor_compile_determinism.c
)

target_include_directories(domino_decor_compile_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_decor_compile_determinism_test
    domino_core
)

set_target_properties(domino_decor_compile_determinism_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_decor_compile_determinism_test COMMAND domino_decor_compile_determinism_test)

add_executable(domino_agent_behavior_determinism_test
    agent_behavior_determinism_test.c
)

target_include_directories(domino_agent_behavior_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_agent_behavior_determinism_test
    domino_core
)

set_target_properties(domino_agent_behavior_determinism_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_agent_behavior_determinism_test COMMAND domino_agent_behavior_determinism_test)

add_executable(domino_graph_toolkit_determinism_test
    graph_toolkit_determinism_test.c
)

target_include_directories(domino_graph_toolkit_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_graph_toolkit_determinism_test
    domino_core
)

set_target_properties(domino_graph_toolkit_determinism_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_graph_toolkit_determinism_test COMMAND domino_graph_toolkit_determinism_test)

add_executable(domino_domains_frames_prop_determinism_test
    domains_frames_prop_determinism_test.c
)

target_include_directories(domino_domains_frames_prop_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_domains_frames_prop_determinism_test
    domino_core
)

set_target_properties(domino_domains_frames_prop_determinism_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_domains_frames_prop_determinism_test COMMAND domino_domains_frames_prop_determinism_test)

add_executable(domino_det_regression_scan_test
    determinism_regression_scan_test.c
)

target_include_directories(domino_det_regression_scan_test PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}
)

set_target_properties(domino_det_regression_scan_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_regression_scan_test COMMAND domino_det_regression_scan_test)
set_tests_properties(domino_det_regression_scan_test PROPERTIES
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)

add_executable(domino_det_sched_test
    ../../tests/determinism/det_sched.c
)

target_include_directories(domino_det_sched_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_det_sched_test
    domino_core
)

set_target_properties(domino_det_sched_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_sched_test COMMAND domino_det_sched_test)

add_executable(domino_det_packets_test
    ../../tests/determinism/det_packets.c
)

target_include_directories(domino_det_packets_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_det_packets_test
    domino_core
)

set_target_properties(domino_det_packets_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_packets_test COMMAND domino_det_packets_test)

add_executable(domino_det_lod_test
    ../../tests/determinism/det_lod.c
)

target_include_directories(domino_det_lod_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_det_lod_test
    domino_core
)

set_target_properties(domino_det_lod_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_lod_test COMMAND domino_det_lod_test)

add_executable(domino_det_trans_test
    ../../tests/determinism/det_trans.c
)

target_include_directories(domino_det_trans_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_det_trans_test
    domino_core
)

set_target_properties(domino_det_trans_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_trans_test COMMAND domino_det_trans_test)

add_executable(domino_det_struct_test
    ../../tests/determinism/det_struct.c
)

target_include_directories(domino_det_struct_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_det_struct_test
    domino_core
)

set_target_properties(domino_det_struct_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_struct_test COMMAND domino_det_struct_test)

add_executable(domino_det_decor_test
    ../../tests/determinism/det_decor.c
)

target_include_directories(domino_det_decor_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_det_decor_test
    domino_core
)

set_target_properties(domino_det_decor_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_decor_test COMMAND domino_det_decor_test)

add_executable(domino_det_agents_test
    ../../tests/determinism/det_agents.c
)

target_include_directories(domino_det_agents_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_det_agents_test
    domino_core
)

set_target_properties(domino_det_agents_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_agents_test COMMAND domino_det_agents_test)

add_executable(domino_det_graph_test
    ../../tests/determinism/det_graph.c
)

target_include_directories(domino_det_graph_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_det_graph_test
    domino_core
)

set_target_properties(domino_det_graph_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_graph_test COMMAND domino_det_graph_test)

add_executable(domino_det_domains_test
    ../../tests/determinism/det_domains.c
)

target_include_directories(domino_det_domains_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_det_domains_test
    domino_core
)

set_target_properties(domino_det_domains_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_domains_test COMMAND domino_det_domains_test)

add_executable(domino_det_knowledge_test
    ../../tests/determinism/det_knowledge.c
)

target_include_directories(domino_det_knowledge_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_det_knowledge_test
    domino_core
)

set_target_properties(domino_det_knowledge_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_knowledge_test COMMAND domino_det_knowledge_test)

add_executable(dgfx_soft_hash_test
    ../../tests/domino_gfx/test_dgfx_soft_hash.c
    ../../external/xxhash/xxhash.c
)

target_include_directories(dgfx_soft_hash_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_CURRENT_SOURCE_DIR}/../../source/domino
    ${CMAKE_CURRENT_SOURCE_DIR}/../../external/xxhash
)

target_link_libraries(dgfx_soft_hash_test
    domino_core
)

set_target_properties(dgfx_soft_hash_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)

add_test(NAME dgfx_soft_hash_test COMMAND dgfx_soft_hash_test)

add_executable(domino_sys_smoke
    domino_sys_smoke.c
)

target_link_libraries(domino_sys_smoke
    domino_core
)

set_target_properties(domino_sys_smoke PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)

add_executable(domino_dui_smoke
    domino_dui_smoke.c
)

target_include_directories(domino_dui_smoke PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_dui_smoke
    domino_core
)

set_target_properties(domino_dui_smoke PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)

add_test(NAME domino_dui_smoke_null COMMAND domino_dui_smoke null)
add_test(NAME domino_dui_smoke_dgfx COMMAND domino_dui_smoke dgfx)
if(WIN32)
    add_test(NAME domino_dui_smoke_native COMMAND domino_dui_smoke win32)
endif()

add_executable(dominium_launcher_ui_backend_swap_test
    launcher_ui_backend_swap_test.c
)

target_include_directories(dominium_launcher_ui_backend_swap_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(dominium_launcher_ui_backend_swap_test
    domino_core
)

set_target_properties(dominium_launcher_ui_backend_swap_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)

add_test(NAME dominium_launcher_ui_backend_swap_test COMMAND dominium_launcher_ui_backend_swap_test)

if(WIN32)
    add_executable(ui_cli_determinism_test
        ui_cli_determinism_test.cpp
    )

    set_target_properties(ui_cli_determinism_test PROPERTIES
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    add_dependencies(ui_cli_determinism_test dominium-ui-editor)

    set(UI_CLI_TEST_ROOT ${CMAKE_CURRENT_BINARY_DIR}/ui_cli_tests)

    add_test(NAME test_ui_apply_determinism_launcher
        COMMAND ui_cli_determinism_test
            --mode apply_determinism
            --ui-editor $<TARGET_FILE:dominium-ui-editor>
            --script ${CMAKE_SOURCE_DIR}/tools/launcher/ui/scripts/minecraft_launcher_v1.ops.json
            --doc-basename launcher_ui_doc
            --work-dir ${UI_CLI_TEST_ROOT}/launcher_apply
    )

    add_test(NAME test_ui_apply_determinism_setup
        COMMAND ui_cli_determinism_test
            --mode apply_determinism
            --ui-editor $<TARGET_FILE:dominium-ui-editor>
            --script ${CMAKE_SOURCE_DIR}/tools/setup/ui/scripts/minecraft_setup_v1.ops.json
            --doc-basename setup_ui_doc
            --work-dir ${UI_CLI_TEST_ROOT}/setup_apply
    )

    add_test(NAME test_ui_codegen_determinism_launcher
        COMMAND ui_cli_determinism_test
            --mode codegen_determinism
            --ui-editor $<TARGET_FILE:dominium-ui-editor>
            --doc ${CMAKE_SOURCE_DIR}/tools/launcher/ui/doc/launcher_ui_doc.tlv
            --docname launcher_ui
            --work-dir ${UI_CLI_TEST_ROOT}/launcher_codegen
    )

    add_test(NAME test_ui_codegen_determinism_setup
        COMMAND ui_cli_determinism_test
            --mode codegen_determinism
            --ui-editor $<TARGET_FILE:dominium-ui-editor>
            --doc ${CMAKE_SOURCE_DIR}/tools/setup/ui/doc/setup_ui_doc.tlv
            --docname setup_ui
            --work-dir ${UI_CLI_TEST_ROOT}/setup_codegen
    )

    add_test(NAME test_ui_registry_stability
        COMMAND ui_cli_determinism_test
            --mode registry_stability
            --ui-editor $<TARGET_FILE:dominium-ui-editor>
            --work-dir ${UI_CLI_TEST_ROOT}/registry
    )

    add_test(NAME test_ui_index_determinism
        COMMAND ui_cli_determinism_test
            --mode scan_determinism
            --ui-editor $<TARGET_FILE:dominium-ui-editor>
            --work-dir ${UI_CLI_TEST_ROOT}/scan
    )
    set_tests_properties(test_ui_index_determinism PROPERTIES
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    )
endif()

add_executable(dgfx_demo
    ../../tests/domino_gfx/dgfx_demo.c
)

target_include_directories(dgfx_demo PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(dgfx_demo
    PRIVATE domino_core
)

if(WIN32 AND DOM_BACKEND_DX9)
    target_link_libraries(dgfx_demo PRIVATE d3d9)
endif()

set_target_properties(dgfx_demo PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)

if(WIN32)
    function(setup2_copy_winpthread target)
        get_filename_component(DSK_COMPILER_DIR "${CMAKE_CXX_COMPILER}" DIRECTORY)
        set(DSK_RUNTIME_DLLS
            "${DSK_COMPILER_DIR}/libwinpthread-1.dll"
            "${DSK_COMPILER_DIR}/libstdc++-6.dll"
            "${DSK_COMPILER_DIR}/libgcc_s_seh-1.dll"
            "${DSK_COMPILER_DIR}/libgcc_s_dw2-1.dll"
            "${DSK_COMPILER_DIR}/libgcc_s_sjlj-1.dll"
            "${DSK_COMPILER_DIR}/libatomic-1.dll"
        )
        foreach(dll IN LISTS DSK_RUNTIME_DLLS)
            if(EXISTS "${dll}")
                add_custom_command(TARGET ${target} POST_BUILD
                    COMMAND ${CMAKE_COMMAND} -E copy_if_different
                        "${dll}"
                        $<TARGET_FILE_DIR:${target}>
                )
            endif()
        endforeach()
    endfunction()
endif()

add_executable(setup2_kernel_tests
    ../../tests/setup2/setup2_kernel_tests.cpp
)

target_include_directories(setup2_kernel_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
)

target_link_libraries(setup2_kernel_tests
    PRIVATE dsk_kernel dss_services
)

set_target_properties(setup2_kernel_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dominium_bundle_runtime(setup2_kernel_tests)
if(WIN32)
    setup2_copy_winpthread(setup2_kernel_tests)
endif()

add_test(NAME test_tlv_roundtrip_known_fields COMMAND setup2_kernel_tests tlv_roundtrip_known_fields)
add_test(NAME test_tlv_skip_unknown COMMAND setup2_kernel_tests tlv_skip_unknown)
add_test(NAME test_manifest_validate_missing_required COMMAND setup2_kernel_tests manifest_validate_missing_required)
add_test(NAME test_request_validate_missing_required COMMAND setup2_kernel_tests request_validate_missing_required)
add_test(NAME test_kernel_emits_audit_on_failure COMMAND setup2_kernel_tests kernel_emits_audit_on_failure)
add_test(NAME test_splat_selection_deterministic COMMAND setup2_kernel_tests splat_selection_deterministic)

add_executable(setup2_services_fs_tests
    ../../tests/setup2/test_services_fs_sandbox.cpp
)

target_include_directories(setup2_services_fs_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
)

target_link_libraries(setup2_services_fs_tests
    PRIVATE dss_services
)

set_target_properties(setup2_services_fs_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dominium_bundle_runtime(setup2_services_fs_tests)
if(WIN32)
    setup2_copy_winpthread(setup2_services_fs_tests)
endif()

add_test(NAME test_services_fs_rejects_escape COMMAND setup2_services_fs_tests services_fs_rejects_escape)
add_test(NAME test_services_fs_atomic_write COMMAND setup2_services_fs_tests services_fs_atomic_write)
add_test(NAME test_services_fs_canonicalize COMMAND setup2_services_fs_tests services_fs_canonicalize)

add_executable(setup2_services_platform_tests
    ../../tests/setup2/test_services_platform_fake.cpp
)

target_include_directories(setup2_services_platform_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
)

target_link_libraries(setup2_services_platform_tests
    PRIVATE dss_services
)

set_target_properties(setup2_services_platform_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dominium_bundle_runtime(setup2_services_platform_tests)
if(WIN32)
    setup2_copy_winpthread(setup2_services_platform_tests)
endif()

add_test(NAME test_services_platform_fake COMMAND setup2_services_platform_tests services_platform_fake)

add_executable(setup2_kernel_services_tests
    ../../tests/setup2/test_kernel_uses_services_platform.cpp
)

target_include_directories(setup2_kernel_services_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
)

target_link_libraries(setup2_kernel_services_tests
    PRIVATE dsk_kernel dss_services
)

set_target_properties(setup2_kernel_services_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dominium_bundle_runtime(setup2_kernel_services_tests)
if(WIN32)
    setup2_copy_winpthread(setup2_kernel_services_tests)
endif()

add_test(NAME test_kernel_uses_services_platform COMMAND setup2_kernel_services_tests kernel_uses_services_platform)

add_executable(setup2_splat_tests
    ../../tests/setup2/test_splat_selection.cpp
)

target_include_directories(setup2_splat_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
)

target_link_libraries(setup2_splat_tests
    PRIVATE dsk_kernel dss_services
)

set_target_properties(setup2_splat_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dominium_bundle_runtime(setup2_splat_tests)
if(WIN32)
    setup2_copy_winpthread(setup2_splat_tests)
endif()

add_test(NAME test_splat_registry_sorted COMMAND setup2_splat_tests splat_registry_sorted)
add_test(NAME test_splat_select_requested_id_success COMMAND setup2_splat_tests splat_select_requested_id_success)
add_test(NAME test_splat_select_requested_id_not_found COMMAND setup2_splat_tests splat_select_requested_id_not_found)
add_test(NAME test_splat_select_filters_by_platform COMMAND setup2_splat_tests splat_select_filters_by_platform)
add_test(NAME test_splat_select_filters_by_scope COMMAND setup2_splat_tests splat_select_filters_by_scope)
add_test(NAME test_splat_select_filters_by_ui_mode COMMAND setup2_splat_tests splat_select_filters_by_ui_mode)
add_test(NAME test_splat_select_no_compatible_emits_rejections_and_audit COMMAND setup2_splat_tests splat_select_no_compatible_emits_rejections_and_audit)
add_test(NAME test_splat_select_deterministic_choice_first_compatible COMMAND setup2_splat_tests splat_select_deterministic_choice_first_compatible)

add_executable(setup2_plan_tests
    ../../tests/setup2/test_plan.cpp
)

target_include_directories(setup2_plan_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/src/plan
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
)

target_compile_definitions(setup2_plan_tests PRIVATE
    SETUP2_TESTS_SOURCE_DIR=\"${CMAKE_SOURCE_DIR}/tests/setup2\"
)

target_link_libraries(setup2_plan_tests
    PRIVATE dsk_kernel
)

set_target_properties(setup2_plan_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dominium_bundle_runtime(setup2_plan_tests)
if(WIN32)
    setup2_copy_winpthread(setup2_plan_tests)
endif()

add_test(NAME test_resolve_default_components COMMAND setup2_plan_tests resolve_default_components)
add_test(NAME test_resolve_explicit_components COMMAND setup2_plan_tests resolve_explicit_components)
add_test(NAME test_resolve_dependency_closure COMMAND setup2_plan_tests resolve_dependency_closure)
add_test(NAME test_resolve_conflict_refusal COMMAND setup2_plan_tests resolve_conflict_refusal)
add_test(NAME test_resolve_platform_incompat_refusal COMMAND setup2_plan_tests resolve_platform_incompat_refusal)
add_test(NAME test_plan_byte_identical_repeat COMMAND setup2_plan_tests plan_byte_identical_repeat)
add_test(NAME test_plan_digest_stable COMMAND setup2_plan_tests plan_digest_stable)
add_test(NAME test_plan_validate_rejects_corrupt_header COMMAND setup2_plan_tests plan_validate_rejects_corrupt_header)
add_test(NAME test_plan_lists_canonically_sorted COMMAND setup2_plan_tests plan_lists_canonically_sorted)
add_test(NAME test_plan_golden_default COMMAND setup2_plan_tests plan_golden_default)
add_test(NAME test_plan_golden_custom COMMAND setup2_plan_tests plan_golden_custom)

add_executable(setup2_apply_tests
    ../../tests/setup2/test_apply.cpp
)

target_include_directories(setup2_apply_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/src/plan
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
)

target_compile_definitions(setup2_apply_tests PRIVATE
    SETUP2_TESTS_SANDBOX_ROOT=\"${CMAKE_SOURCE_DIR}/setup2_fs_sandbox\"
)

target_link_libraries(setup2_apply_tests
    PRIVATE dsk_kernel dss_services
)

set_target_properties(setup2_apply_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dominium_bundle_runtime(setup2_apply_tests)
if(WIN32)
    setup2_copy_winpthread(setup2_apply_tests)
endif()

add_test(NAME test_apply_fresh_install_succeeds COMMAND setup2_apply_tests apply_fresh_install_succeeds)
add_test(NAME test_fail_mid_commit_then_rollback_restores_pristine COMMAND setup2_apply_tests fail_mid_commit_then_rollback_restores_pristine)
add_test(NAME test_fail_mid_commit_then_resume_completes COMMAND setup2_apply_tests fail_mid_commit_then_resume_completes)
add_test(NAME test_crash_during_stage_then_resume COMMAND setup2_apply_tests crash_during_stage_then_resume)
add_test(NAME test_no_in_place_mutation COMMAND setup2_apply_tests no_in_place_mutation)
add_test(NAME test_deterministic_journals COMMAND setup2_apply_tests deterministic_journals)

if(WIN32)
    add_test(NAME setup2_kernel_purity_check
        COMMAND ${CMAKE_SOURCE_DIR}/scripts/setup2/check_kernel_purity.bat
    )
else()
    add_test(NAME setup2_kernel_purity_check
        COMMAND sh ${CMAKE_SOURCE_DIR}/scripts/setup2/check_kernel_purity.sh
    )
endif()
