cmake_minimum_required(VERSION 3.16)

add_library(tools_shared STATIC
    build/host/tools_shared_stub.c
)
target_include_directories(tools_shared PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/build/host
)
target_link_libraries(tools_shared
    PUBLIC
        libs::contracts
)
set_target_properties(tools_shared PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_library(tools::shared ALIAS tools_shared)

add_executable(dominium-tools
    build/host/tools_host_main.c
    domain/scale/scale_cli.cpp
    domain/mmo/mmo_cli.cpp
    ../runtime/network/server/dom_server_protocol.cpp
    ../runtime/network/server/dom_server_runtime.cpp
    ../runtime/network/server/shard/dom_cross_shard_log.cpp
    ../runtime/network/server/shard/dom_global_id.cpp
    ../runtime/network/server/shard/dom_shard_lifecycle.cpp
    ../runtime/storage/server/persistence/dom_checkpointing.cpp
)
target_link_libraries(dominium-tools PRIVATE tools::shared)
target_link_libraries(dominium-tools PRIVATE app::runtime)
target_link_libraries(dominium-tools PRIVATE dominium_game)
target_link_libraries(dominium-tools PRIVATE domino_engine)
target_include_directories(dominium-tools PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
    ${DOMINIUM_GAME_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/runtime/network/server
    ${CMAKE_SOURCE_DIR}/runtime/network/server/shard
    ${CMAKE_SOURCE_DIR}/runtime/storage/server
    ${CMAKE_SOURCE_DIR}/runtime/storage/server/persistence
    ${CMAKE_CURRENT_SOURCE_DIR}
)
set_target_properties(dominium-tools PROPERTIES
    OUTPUT_NAME "tools"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_executable(dom_tools ALIAS dominium-tools)
dom_register_product(tools dominium-tools)

if(WIN32)
    add_executable(tools_app_win32 WIN32
        ../apps/workbench/module/tooling/host/win32/tools_app_win32.cpp
    )
    target_link_libraries(tools_app_win32 PRIVATE
        libs::appcore
        runtime_platform_win32_ui
    )
    set_target_properties(tools_app_win32 PROPERTIES
        OUTPUT_NAME "tools_app_win32"
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    if(TARGET ui_bind_phase)
        add_dependencies(tools_app_win32 ui_bind_phase)
    endif()
    if(MSVC)
        target_compile_options(tools_app_win32 PRIVATE /W4 /WX)
    endif()
endif()

add_executable(dom_tool_artifactmeta
    package/artifactmeta/tool_artifactmeta.c
)
target_link_libraries(dom_tool_artifactmeta PRIVATE libs::contracts)
target_include_directories(dom_tool_artifactmeta PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_artifactmeta PROPERTIES
    OUTPUT_NAME "dom_tool_artifactmeta"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_executable(dom_tool_terrain
    domain/terrain/terrain_cli.cpp
)
target_link_libraries(dom_tool_terrain PRIVATE domino_engine)
target_include_directories(dom_tool_terrain PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_terrain PROPERTIES
    OUTPUT_NAME "dom_tool_terrain"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_terrain PRIVATE m)
endif()

add_executable(dom_tool_geology
    validators/domain/geology/geology_cli.cpp
)
target_link_libraries(dom_tool_geology PRIVATE domino_engine)
target_include_directories(dom_tool_geology PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_geology PROPERTIES
    OUTPUT_NAME "dom_tool_geology"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_geology PRIVATE m)
endif()

add_executable(dom_tool_climate
    domain/climate/climate_cli.cpp
)
target_link_libraries(dom_tool_climate PRIVATE domino_engine)
target_include_directories(dom_tool_climate PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_climate PROPERTIES
    OUTPUT_NAME "dom_tool_climate"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_climate PRIVATE m)
endif()

add_executable(dom_tool_weather
    domain/weather/weather_cli.cpp
)
target_link_libraries(dom_tool_weather PRIVATE domino_engine)
target_include_directories(dom_tool_weather PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_weather PROPERTIES
    OUTPUT_NAME "dom_tool_weather"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_weather PRIVATE m)
endif()

add_executable(dom_tool_energy
    domain/energy/energy_cli.cpp
)
target_link_libraries(dom_tool_energy PRIVATE domino_engine)
target_include_directories(dom_tool_energy PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_energy PROPERTIES
    OUTPUT_NAME "dom_tool_energy"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_energy PRIVATE m)
endif()

add_executable(dom_tool_heat
    domain/thermal/heat/heat_cli.cpp
)
target_link_libraries(dom_tool_heat PRIVATE domino_engine)
target_include_directories(dom_tool_heat PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_heat PROPERTIES
    OUTPUT_NAME "dom_tool_heat"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_heat PRIVATE m)
endif()

add_executable(dom_tool_fluid
    domain/fluids/fluid_cli.cpp
)
target_link_libraries(dom_tool_fluid PRIVATE domino_engine)
target_include_directories(dom_tool_fluid PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_fluid PROPERTIES
    OUTPUT_NAME "dom_tool_fluid"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_fluid PRIVATE m)
endif()

add_executable(dom_tool_network
    validators/network/network_cli.cpp
)
target_link_libraries(dom_tool_network PRIVATE domino_engine)
target_include_directories(dom_tool_network PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_network PROPERTIES
    OUTPUT_NAME "dom_tool_network"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_network PRIVATE m)
endif()

add_executable(dom_tool_hazard
    domain/hazard/hazard_cli.cpp
)
target_link_libraries(dom_tool_hazard PRIVATE domino_engine)
target_include_directories(dom_tool_hazard PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_hazard PROPERTIES
    OUTPUT_NAME "dom_tool_hazard"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_hazard PRIVATE m)
endif()

add_executable(dom_tool_risk
    domain/risk/risk_cli.cpp
)
target_link_libraries(dom_tool_risk PRIVATE domino_engine)
target_include_directories(dom_tool_risk PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_risk PROPERTIES
    OUTPUT_NAME "dom_tool_risk"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_risk PRIVATE m)
endif()

add_executable(dom_tool_trust
    domain/trust/trust_cli.cpp
)
target_link_libraries(dom_tool_trust PRIVATE domino_engine)
target_include_directories(dom_tool_trust PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_trust PROPERTIES
    OUTPUT_NAME "dom_tool_trust"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_trust PRIVATE m)
endif()

add_executable(dom_tool_institution
    domain/institution/institution_cli.cpp
)
target_link_libraries(dom_tool_institution PRIVATE domino_engine)
target_include_directories(dom_tool_institution PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_institution PROPERTIES
    OUTPUT_NAME "dom_tool_institution"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_institution PRIVATE m)
endif()

add_executable(dom_tool_economy
    domain/economy/economy_cli.cpp
)
target_link_libraries(dom_tool_economy PRIVATE domino_engine)
target_include_directories(dom_tool_economy PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_economy PROPERTIES
    OUTPUT_NAME "dom_tool_economy"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_economy PRIVATE m)
endif()

add_executable(dom_tool_conflict
    domain/conflict/conflict_cli.cpp
)
target_link_libraries(dom_tool_conflict PRIVATE domino_engine)
target_include_directories(dom_tool_conflict PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_conflict PROPERTIES
    OUTPUT_NAME "dom_tool_conflict"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_conflict PRIVATE m)
endif()

add_executable(dom_tool_history
    domain/history/history_cli.cpp
)
target_link_libraries(dom_tool_history PRIVATE domino_engine)
target_include_directories(dom_tool_history PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_history PROPERTIES
    OUTPUT_NAME "dom_tool_history"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_history PRIVATE m)
endif()

add_executable(dom_tool_standard
    domain/standards/standard_cli.cpp
)
target_link_libraries(dom_tool_standard PRIVATE domino_engine)
target_include_directories(dom_tool_standard PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_standard PROPERTIES
    OUTPUT_NAME "dom_tool_standard"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_standard PRIVATE m)
endif()

add_executable(dom_tool_autonomy
    domain/autonomy/autonomy_cli.cpp
)
target_link_libraries(dom_tool_autonomy PRIVATE domino_engine)
target_include_directories(dom_tool_autonomy PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_autonomy PROPERTIES
    OUTPUT_NAME "dom_tool_autonomy"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_autonomy PRIVATE m)
endif()

add_executable(dom_tool_srz
    domain/srz/srz_cli.cpp
)
target_link_libraries(dom_tool_srz PRIVATE domino_engine)
target_include_directories(dom_tool_srz PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_srz PROPERTIES
    OUTPUT_NAME "dom_tool_srz"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_srz PRIVATE m)
endif()

add_executable(dom_tool_knowledge
    domain/knowledge/knowledge_cli.cpp
)
target_link_libraries(dom_tool_knowledge PRIVATE domino_engine)
target_include_directories(dom_tool_knowledge PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_knowledge PROPERTIES
    OUTPUT_NAME "dom_tool_knowledge"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_knowledge PRIVATE m)
endif()

add_executable(dom_tool_vegetation
    domain/vegetation/vegetation_cli.cpp
)
target_link_libraries(dom_tool_vegetation PRIVATE domino_engine)
target_include_directories(dom_tool_vegetation PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_vegetation PROPERTIES
    OUTPUT_NAME "dom_tool_vegetation"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_vegetation PRIVATE m)
endif()

add_executable(dom_tool_animal
    domain/animals/animal_cli.cpp
)
target_link_libraries(dom_tool_animal PRIVATE domino_engine)
target_include_directories(dom_tool_animal PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_animal PROPERTIES
    OUTPUT_NAME "dom_tool_animal"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_animal PRIVATE m)
endif()

add_executable(dom_tool_structure
    domain/structure/structure_cli.cpp
)
target_link_libraries(dom_tool_structure PRIVATE domino_engine)
target_include_directories(dom_tool_structure PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_structure PROPERTIES
    OUTPUT_NAME "dom_tool_structure"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_structure PRIVATE m)
endif()

add_executable(dom_tool_travel
    domain/travel/travel_cli.cpp
)
target_link_libraries(dom_tool_travel PRIVATE domino_engine)
target_include_directories(dom_tool_travel PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_travel PROPERTIES
    OUTPUT_NAME "dom_tool_travel"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_travel PRIVATE m)
endif()

add_executable(dom_tool_mining
    domain/mining/mining_cli.cpp
)
target_link_libraries(dom_tool_mining PRIVATE domino_engine)
target_include_directories(dom_tool_mining PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_mining PROPERTIES
    OUTPUT_NAME "dom_tool_mining"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_mining PRIVATE m)
endif()

add_executable(dom_tool_crafting
    domain/crafting/crafting_cli.cpp
)
target_link_libraries(dom_tool_crafting PRIVATE domino_engine)
target_include_directories(dom_tool_crafting PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dom_tool_crafting PROPERTIES
    OUTPUT_NAME "dom_tool_crafting"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if(NOT WIN32)
    target_link_libraries(dom_tool_crafting PRIVATE m)
endif()
add_executable(coredata_compile
    codegen/content/coredata_compile_stub.c
)
set_target_properties(coredata_compile PROPERTIES
    OUTPUT_NAME "coredata_compile"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_executable(coredata_validate
    validators/content/coredata_validate_stub.c
)
set_target_properties(coredata_validate PROPERTIES
    OUTPUT_NAME "coredata_validate"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_executable(data_validate
    validators/content/data/data_validate_main.c
)
target_link_libraries(data_validate PRIVATE domino_engine)
set_target_properties(data_validate PROPERTIES
    OUTPUT_NAME "data_validate"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_executable(validate_all
    validators/suite/validate_all_main.cpp
    validators/suite/validator_common.cpp
    validators/suite/validator_reports.cpp
    validators/suite/validators_registry.cpp
    validators/tool_validation.cpp
    validators/policy_validation.cpp
)
target_include_directories(validate_all PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
)
set_target_properties(validate_all PROPERTIES
    OUTPUT_NAME "validate_all"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_executable(registry_dump_cli
    validators/registry_dump_cli.cpp
)
target_link_libraries(registry_dump_cli PRIVATE
    domino_engine
    libs::contracts
)
set_target_properties(registry_dump_cli PROPERTIES
    OUTPUT_NAME "registry_dump_cli"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_executable(hygiene_validate_cli
    validators/hygiene_validate_cli.cpp
)
target_link_libraries(hygiene_validate_cli PRIVATE
    domino_engine
    libs::contracts
)
set_target_properties(hygiene_validate_cli PROPERTIES
    OUTPUT_NAME "hygiene_validate_cli"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_library(dominium_tools_inspect STATIC
    ../apps/workbench/module/inspection/inspector/replay_inspector.cpp
    ../apps/workbench/module/inspection/inspector/provenance_browser.cpp
    ../apps/workbench/module/inspection/inspector/ledger_inspector.cpp
    ../apps/workbench/module/inspection/inspector/event_timeline_view.cpp
    ../apps/workbench/module/inspection/inspector/dispute_replay_inspector.cpp
)
target_include_directories(dominium_tools_inspect
    PUBLIC
        ${DOMINIUM_ENGINE_INCLUDE_DIR}
        ${CMAKE_SOURCE_DIR}/apps/workbench/module/inspection/inspector
)
set_target_properties(dominium_tools_inspect PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_library(dominium_tools_observability STATIC
    ../apps/workbench/module/observability/inspector/observation_store.cpp
    ../apps/workbench/module/observability/inspector/observability_api.cpp
    ../apps/workbench/module/observability/inspector/world_inspector.cpp
    ../apps/workbench/module/observability/inspector/agent_inspector.cpp
    ../apps/workbench/module/observability/inspector/institution_inspector.cpp
    ../apps/workbench/module/observability/inspector/history_viewer.cpp
    ../apps/workbench/module/observability/inspector/pack_inspector.cpp
    ../apps/workbench/module/observability/inspector/determinism_tools.cpp
    ../apps/workbench/module/observability/inspector/visualization_view.cpp
)
target_include_directories(dominium_tools_observability
    PUBLIC
        ${DOMINIUM_ENGINE_INCLUDE_DIR}
        ${CMAKE_SOURCE_DIR}/apps/workbench/module/observability/inspector
        ${CMAKE_SOURCE_DIR}/apps/workbench/module/inspection/inspector
)
set_target_properties(dominium_tools_observability PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_executable(dominium_tool0_inspection_tests
    test/cpp/tool0_inspection_tests.cpp
)
target_link_libraries(dominium_tool0_inspection_tests PRIVATE dominium_tools_inspect)
set_target_properties(dominium_tool0_inspection_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME dominium_tool0_inspection
    COMMAND $<TARGET_FILE:dominium_tool0_inspection_tests>
)

add_executable(dominium_vis3_observability_tests
    test/cpp/vis3_observability_tests.cpp
)
target_link_libraries(dominium_vis3_observability_tests PRIVATE dominium_tools_observability)
set_target_properties(dominium_vis3_observability_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME dominium_vis3_observability
    COMMAND $<TARGET_FILE:dominium_vis3_observability_tests>
)

add_executable(dominium_registry_tests
    test/cpp/registry_tests.cpp
)
target_link_libraries(dominium_registry_tests PRIVATE
    domino_engine
    libs::contracts
)
target_compile_definitions(dominium_registry_tests PRIVATE
    DOMINIUM_LAW_TARGETS_REGISTRY_PATH="${CMAKE_SOURCE_DIR}/contracts/registry/law_targets.registry"
)
set_target_properties(dominium_registry_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME dominium_registry
    COMMAND $<TARGET_FILE:dominium_registry_tests>
)

add_executable(mod_pack_builder
    package/modpack/mod_pack_builder.cpp
    validators/suite/validator_common.cpp
)
target_include_directories(mod_pack_builder PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GAME_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
)
target_link_libraries(mod_pack_builder PRIVATE dominium_game)
set_target_properties(mod_pack_builder PROPERTIES
    OUTPUT_NAME "mod_pack_builder"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_executable(mod_pack_validator
    package/modpack/mod_pack_validator.cpp
    validators/suite/validator_common.cpp
)
target_include_directories(mod_pack_validator PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GAME_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
)
target_link_libraries(mod_pack_validator PRIVATE dominium_game)
set_target_properties(mod_pack_validator PROPERTIES
    OUTPUT_NAME "mod_pack_validator"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_executable(tools::host ALIAS dominium-tools)
add_executable(tools::coredata_compile ALIAS coredata_compile)
add_executable(tools::coredata_validate ALIAS coredata_validate)
add_executable(tools::data_validate ALIAS data_validate)
add_executable(tools::validate_all ALIAS validate_all)

add_test(NAME dominium_validate_all_bad_fallback
    COMMAND $<TARGET_FILE:validate_all>
        --repo-root=${CMAKE_SOURCE_DIR}/tools/validators/suite/fixtures/bad_fallback
        --strict=1
)
set_tests_properties(dominium_validate_all_bad_fallback PROPERTIES WILL_FAIL TRUE)

add_test(NAME dominium_validate_all_bad_float
    COMMAND $<TARGET_FILE:validate_all>
        --repo-root=${CMAKE_SOURCE_DIR}/tools/validators/suite/fixtures/bad_float
        --strict=1
)
set_tests_properties(dominium_validate_all_bad_float PROPERTIES WILL_FAIL TRUE)

add_test(NAME dominium_validate_all_bad_unbounded
    COMMAND $<TARGET_FILE:validate_all>
        --repo-root=${CMAKE_SOURCE_DIR}/tools/validators/suite/fixtures/bad_unbounded
        --strict=1
)
set_tests_properties(dominium_validate_all_bad_unbounded PROPERTIES WILL_FAIL TRUE)

add_test(NAME dominium_validate_all_bad_fabrication
    COMMAND $<TARGET_FILE:validate_all>
        --repo-root=${CMAKE_SOURCE_DIR}/tools/validators/suite/fixtures/bad_fabrication
        --strict=1
)
set_tests_properties(dominium_validate_all_bad_fabrication PROPERTIES WILL_FAIL TRUE)

add_test(NAME dominium_validate_all_bad_ui
    COMMAND $<TARGET_FILE:validate_all>
        --repo-root=${CMAKE_SOURCE_DIR}/tools/validators/suite/fixtures/bad_ui
        --strict=1
)
set_tests_properties(dominium_validate_all_bad_ui PROPERTIES WILL_FAIL TRUE)

add_test(NAME dominium_validate_all_bad_renderer
    COMMAND $<TARGET_FILE:validate_all>
        --repo-root=${CMAKE_SOURCE_DIR}/tools/validators/suite/fixtures/bad_renderer
        --strict=1
)
set_tests_properties(dominium_validate_all_bad_renderer PROPERTIES WILL_FAIL TRUE)

add_test(NAME dominium_content1_sol_data
    COMMAND python ${CMAKE_SOURCE_DIR}/tools/validators/ci/validate_sol_data.py
        --repo-root=${CMAKE_SOURCE_DIR}
)

add_test(NAME dominium_content2_earth_data
    COMMAND python ${CMAKE_SOURCE_DIR}/tools/validators/ci/validate_earth_data.py
        --repo-root=${CMAKE_SOURCE_DIR}
)

add_test(NAME dominium_content3_milky_way_data
    COMMAND python ${CMAKE_SOURCE_DIR}/tools/validators/ci/validate_milky_way_data.py
        --repo-root=${CMAKE_SOURCE_DIR}
)

add_test(NAME dominium_world_definition
    COMMAND python ${CMAKE_SOURCE_DIR}/tools/validators/ci/validate_world_definition.py
        --repo-root=${CMAKE_SOURCE_DIR}
)

add_test(NAME dominium_tools_taxonomy_selftest
    COMMAND python ${CMAKE_SOURCE_DIR}/tools/validators/repo/check_tools_taxonomy.py
        --self-test
)

add_test(NAME dominium_tools_taxonomy
    COMMAND python ${CMAKE_SOURCE_DIR}/tools/validators/repo/check_tools_taxonomy.py
        --repo-root=${CMAKE_SOURCE_DIR}
        --strict
)

set(_dominium_tools_canonical_include_targets
    dominium-tools
    dom_tool_artifactmeta
    dom_tool_terrain
    dom_tool_geology
    dom_tool_climate
    dom_tool_weather
    dom_tool_energy
    dom_tool_heat
    dom_tool_fluid
    dom_tool_network
    dom_tool_hazard
    dom_tool_risk
    dom_tool_trust
    dom_tool_institution
    dom_tool_economy
    dom_tool_conflict
    dom_tool_history
    dom_tool_standard
    dom_tool_autonomy
    dom_tool_srz
    dom_tool_knowledge
    dom_tool_vegetation
    dom_tool_animal
    dom_tool_structure
    dom_tool_travel
    dom_tool_mining
    dom_tool_crafting
    data_validate
    dominium_tools_inspect
    dominium_tools_observability
    mod_pack_builder
    mod_pack_validator
)
foreach(_dominium_tools_target IN LISTS _dominium_tools_canonical_include_targets)
    if(TARGET ${_dominium_tools_target})
        target_include_directories(${_dominium_tools_target} PRIVATE
            ${DOMINIUM_GAME_INCLUDE_DIR}
            ${DOMINIUM_RUNTIME_INCLUDE_DIR}
        )
    endif()
endforeach()
foreach(_dominium_tools_library IN ITEMS dominium_tools_inspect dominium_tools_observability)
    if(TARGET ${_dominium_tools_library})
        target_include_directories(${_dominium_tools_library} PUBLIC
            ${DOMINIUM_GAME_INCLUDE_DIR}
            ${DOMINIUM_RUNTIME_INCLUDE_DIR}
        )
    endif()
endforeach()
