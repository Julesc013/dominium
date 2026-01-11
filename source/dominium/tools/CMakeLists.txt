cmake_minimum_required(VERSION 3.16)

add_library(dominium_tools_common STATIC
    common/dom_content_registry.cpp
    common/dom_dui_util.cpp
    common/dom_pack_registry.cpp
    common/dom_tool_app.cpp
    common/dom_tool_cli.cpp
    common/dom_tool_controller_content.cpp
    common/dom_tool_diagnostics.cpp
    common/dom_tool_engine.cpp
    common/dom_tool_io.cpp
    common/dom_tool_ops.cpp
    common/dom_tool_registry.cpp
    common/dom_tool_tlv.cpp
    common/dom_tool_validate.cpp
    dom_tool_runtime.cpp
    ../game/runtime/dom_game_paths.c
    ../game/runtime/dom_game_handshake.cpp
    ../game/runtime/dom_universe_bundle.cpp
    ../game/runtime/dom_io_guard.cpp
)

target_include_directories(dominium_tools_common PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/domino
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(dominium_tools_common
    PUBLIC
        dominium_common
        core_tlv
        domino_core
)

set_source_files_properties(../game/runtime/dom_game_paths.c
    PROPERTIES LANGUAGE CXX
)

set_target_properties(dominium_tools_common PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_executable(dominium-modcheck
    modcheck/dom_modcheck_main.cpp
    modcheck/dom_modcheck.cpp
)

target_include_directories(dominium-modcheck PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/domino
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(dominium-modcheck
    PRIVATE
        dominium_common
        domino_core
)

set_target_properties(dominium-modcheck PROPERTIES
    OUTPUT_NAME "tool_modcheck"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dist_set_role(dominium-modcheck tools)

dominium_bundle_runtime(dominium-modcheck)

function(dominium_add_tool_exe target_name output_name)
    add_executable(${target_name} ${ARGN})
    target_include_directories(${target_name} PRIVATE
        ${DOMINIUM_INCLUDE_DIR}
        ${CMAKE_SOURCE_DIR}/source
        ${CMAKE_SOURCE_DIR}/source/domino
        ${CMAKE_SOURCE_DIR}/source/dominium/game
        ${CMAKE_SOURCE_DIR}/source/dominium/common
        ${CMAKE_CURRENT_SOURCE_DIR}
    )
    target_link_libraries(${target_name} PRIVATE dominium_tools_common)
    set_target_properties(${target_name} PROPERTIES
        OUTPUT_NAME "${output_name}"
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    dominium_bundle_runtime(${target_name})
    dist_set_role(${target_name} tools)
endfunction()

dominium_add_tool_exe(dominium-world-editor "tool_world_editor"
    world_editor/main_world_editor.cpp
    world_editor/dom_world_editor_controller.cpp
)

dominium_add_tool_exe(dominium-blueprint-editor "tool_blueprint_editor"
    blueprint_editor/main_blueprint_editor.cpp
)

dominium_add_tool_exe(dominium-tech-editor "tool_tech_editor"
    tech_editor/main_tech_editor.cpp
)

dominium_add_tool_exe(dominium-policy-editor "tool_policy_editor"
    policy_editor/main_policy_editor.cpp
)

dominium_add_tool_exe(dominium-process-editor "tool_process_editor"
    process_editor/main_process_editor.cpp
)

dominium_add_tool_exe(dominium-transport-editor "tool_transport_editor"
    transport_editor/main_transport_editor.cpp
)

dominium_add_tool_exe(dominium-struct-editor "tool_struct_editor"
    struct_editor/main_struct_editor.cpp
)

dominium_add_tool_exe(dominium-item-editor "tool_item_editor"
    item_editor/main_item_editor.cpp
)

dominium_add_tool_exe(dominium-pack-editor "tool_pack_editor"
    pack_editor/main_pack_editor.cpp
)

dominium_add_tool_exe(dominium-mod-builder "tool_mod_builder"
    mod_builder/main_mod_builder.cpp
    mod_builder/dom_mod_builder_controller.cpp
)

dominium_add_tool_exe(dominium-save-inspector "tool_save_inspector"
    save_inspector/main_save_inspector.cpp
    save_inspector/dom_save_inspector_controller.cpp
)

dominium_add_tool_exe(dominium-replay-viewer "tool_replay_viewer"
    replay_viewer/main_replay_viewer.cpp
    replay_viewer/dom_replay_viewer_controller.cpp
)

dominium_add_tool_exe(dominium-net-inspector "tool_net_inspector"
    net_inspector/main_net_inspector.cpp
    net_inspector/dom_net_inspector_controller.cpp
)

dominium_add_tool_exe(dominium-tools-demo-gen "tool_tools_demo_gen"
    demo_gen/main_tools_demo_gen.cpp
)

dominium_add_tool_exe(dominium-universe-editor "tool_universe_editor"
    universe_editor/ue_main.cpp
    universe_editor/ue_commands.cpp
    universe_editor/ue_queries.cpp
)

dominium_add_tool_exe(dominium-validator "tool_validator"
    validator/validator_main.cpp
    validator/validator_checks.cpp
)

dominium_add_tool_exe(dominium-replay-analyzer "tool_replay_analyzer"
    replay_analyzer/ra_main.cpp
    replay_analyzer/ra_parser.cpp
    replay_analyzer/ra_diff.cpp
)

target_sources(dominium-replay-analyzer PRIVATE
    ../game/runtime/dom_game_replay.cpp
)

dominium_add_tool_exe(coredata_compile "coredata_compile"
    coredata_compile/coredata_compile_main.cpp
    coredata_compile/coredata_load.cpp
    coredata_compile/coredata_validate.cpp
    coredata_compile/coredata_emit_tlv.cpp
    coredata_compile/coredata_manifest.cpp
)

target_link_libraries(coredata_compile PRIVATE core_tlv)
target_include_directories(coredata_compile PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/coredata_compile
)

dominium_add_tool_exe(coredata_validate "coredata_validate"
    coredata_validate/coredata_validate_main.cpp
    coredata_validate/coredata_validate_load.cpp
    coredata_validate/coredata_validate_checks.cpp
    coredata_validate/coredata_validate_report.cpp
    coredata_compile/coredata_load.cpp
    coredata_compile/coredata_validate.cpp
)

target_link_libraries(coredata_validate PRIVATE core_tlv)
target_include_directories(coredata_validate PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/coredata_compile
    ${CMAKE_CURRENT_SOURCE_DIR}/coredata_validate
)
