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
