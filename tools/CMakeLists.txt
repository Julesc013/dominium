cmake_minimum_required(VERSION 3.16)

add_library(tools_shared STATIC
    _shared/tools_shared_stub.c
)
target_include_directories(tools_shared PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/_shared
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
    tools_host_main.c
    scale/scale_cli.cpp
    mmo/mmo_cli.cpp
    ../server/net/dom_server_protocol.cpp
    ../server/net/dom_server_runtime.cpp
    ../server/shard/dom_cross_shard_log.cpp
    ../server/shard/dom_global_id.cpp
    ../server/shard/dom_shard_lifecycle.cpp
    ../server/persistence/dom_checkpointing.cpp
)
target_link_libraries(dominium-tools PRIVATE tools::shared)
target_link_libraries(dominium-tools PRIVATE app::runtime)
target_link_libraries(dominium-tools PRIVATE dominium_game)
target_link_libraries(dominium-tools PRIVATE domino_engine)
target_include_directories(dominium-tools PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
    ${DOMINIUM_GAME_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/server
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

add_executable(dom_tool_artifactmeta
    artifactmeta/tool_artifactmeta.c
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
    terrain/terrain_cli.cpp
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
    geology/geology_cli.cpp
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
    climate/climate_cli.cpp
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
    weather/weather_cli.cpp
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
    energy/energy_cli.cpp
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
    heat/heat_cli.cpp
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
    fluid/fluid_cli.cpp
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
    network/network_cli.cpp
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
    hazard/hazard_cli.cpp
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
    risk/risk_cli.cpp
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
    trust/trust_cli.cpp
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

add_executable(dom_tool_knowledge
    knowledge/knowledge_cli.cpp
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
    vegetation/vegetation_cli.cpp
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
    animal/animal_cli.cpp
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
    structure/structure_cli.cpp
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
    travel/travel_cli.cpp
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
    mining/mining_cli.cpp
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
    crafting/crafting_cli.cpp
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
    coredata_compile_stub.c
)
set_target_properties(coredata_compile PROPERTIES
    OUTPUT_NAME "coredata_compile"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_executable(coredata_validate
    coredata_validate_stub.c
)
set_target_properties(coredata_validate PROPERTIES
    OUTPUT_NAME "coredata_validate"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_executable(data_validate
    data_validate/data_validate_main.c
)
target_link_libraries(data_validate PRIVATE domino_engine)
set_target_properties(data_validate PROPERTIES
    OUTPUT_NAME "data_validate"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_executable(validate_all
    validation/validate_all_main.cpp
    validation/validator_common.cpp
    validation/validator_reports.cpp
    validation/validators_registry.cpp
    validate/tool_validation.cpp
    validate/policy_validation.cpp
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
    validate/registry_dump_cli.cpp
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
    validate/hygiene_validate_cli.cpp
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
    inspect/replay_inspector.cpp
    inspect/provenance_browser.cpp
    inspect/ledger_inspector.cpp
    inspect/event_timeline_view.cpp
    inspect/dispute_replay_inspector.cpp
)
target_include_directories(dominium_tools_inspect
    PUBLIC
        ${DOMINIUM_ENGINE_INCLUDE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}/inspect
)
set_target_properties(dominium_tools_inspect PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_library(dominium_tools_observability STATIC
    observability/observation_store.cpp
    observability/observability_api.cpp
    observability/world_inspector.cpp
    observability/agent_inspector.cpp
    observability/institution_inspector.cpp
    observability/history_viewer.cpp
    observability/pack_inspector.cpp
    observability/determinism_tools.cpp
    observability/visualization_view.cpp
)
target_include_directories(dominium_tools_observability
    PUBLIC
        ${DOMINIUM_ENGINE_INCLUDE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}/observability
        ${CMAKE_CURRENT_SOURCE_DIR}/inspect
)
set_target_properties(dominium_tools_observability PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_executable(dominium_tool0_inspection_tests
    tests/tool0_inspection_tests.cpp
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
    tests/vis3_observability_tests.cpp
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
    tests/registry_tests.cpp
)
target_link_libraries(dominium_registry_tests PRIVATE
    domino_engine
    libs::contracts
)
target_compile_definitions(dominium_registry_tests PRIVATE
    DOMINIUM_LAW_TARGETS_REGISTRY_PATH="${CMAKE_SOURCE_DIR}/data/registries/law_targets.registry"
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
    modpack/mod_pack_builder.cpp
    validation/validator_common.cpp
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
    modpack/mod_pack_validator.cpp
    validation/validator_common.cpp
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
        --repo-root=${CMAKE_SOURCE_DIR}/tools/validation/fixtures/bad_fallback
        --strict=1
)
set_tests_properties(dominium_validate_all_bad_fallback PROPERTIES WILL_FAIL TRUE)

add_test(NAME dominium_validate_all_bad_float
    COMMAND $<TARGET_FILE:validate_all>
        --repo-root=${CMAKE_SOURCE_DIR}/tools/validation/fixtures/bad_float
        --strict=1
)
set_tests_properties(dominium_validate_all_bad_float PROPERTIES WILL_FAIL TRUE)

add_test(NAME dominium_validate_all_bad_unbounded
    COMMAND $<TARGET_FILE:validate_all>
        --repo-root=${CMAKE_SOURCE_DIR}/tools/validation/fixtures/bad_unbounded
        --strict=1
)
set_tests_properties(dominium_validate_all_bad_unbounded PROPERTIES WILL_FAIL TRUE)

add_test(NAME dominium_validate_all_bad_fabrication
    COMMAND $<TARGET_FILE:validate_all>
        --repo-root=${CMAKE_SOURCE_DIR}/tools/validation/fixtures/bad_fabrication
        --strict=1
)
set_tests_properties(dominium_validate_all_bad_fabrication PROPERTIES WILL_FAIL TRUE)

add_test(NAME dominium_validate_all_bad_ui
    COMMAND $<TARGET_FILE:validate_all>
        --repo-root=${CMAKE_SOURCE_DIR}/tools/validation/fixtures/bad_ui
        --strict=1
)
set_tests_properties(dominium_validate_all_bad_ui PROPERTIES WILL_FAIL TRUE)

add_test(NAME dominium_validate_all_bad_renderer
    COMMAND $<TARGET_FILE:validate_all>
        --repo-root=${CMAKE_SOURCE_DIR}/tools/validation/fixtures/bad_renderer
        --strict=1
)
set_tests_properties(dominium_validate_all_bad_renderer PROPERTIES WILL_FAIL TRUE)

add_test(NAME dominium_content1_sol_data
    COMMAND python ${CMAKE_SOURCE_DIR}/tools/ci/validate_sol_data.py
        --repo-root=${CMAKE_SOURCE_DIR}
)

add_test(NAME dominium_content2_earth_data
    COMMAND python ${CMAKE_SOURCE_DIR}/tools/ci/validate_earth_data.py
        --repo-root=${CMAKE_SOURCE_DIR}
)

add_test(NAME dominium_content3_milky_way_data
    COMMAND python ${CMAKE_SOURCE_DIR}/tools/ci/validate_milky_way_data.py
        --repo-root=${CMAKE_SOURCE_DIR}
)

add_test(NAME dominium_world_definition
    COMMAND python ${CMAKE_SOURCE_DIR}/tools/ci/validate_world_definition.py
        --repo-root=${CMAKE_SOURCE_DIR}
)
