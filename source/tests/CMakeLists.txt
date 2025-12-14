cmake_minimum_required(VERSION 3.16)

enable_testing()

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
