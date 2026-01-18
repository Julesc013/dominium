cmake_minimum_required(VERSION 3.16)

add_library(dominium_game STATIC
    dominium_game_stub.c
    core/dom_interest_set.c
    core/dom_interest_sources.c
    core/dom_interest_macro.c
    core/dom_fidelity.c
    core/dom_data_validate.c
    core/dom_epistemic.c
    core/life/ability_packages.cpp
    core/life/control_authority.cpp
    core/life/continuation_policy.cpp
    core/life/controller_binding.cpp
    core/life/life_events_stub.cpp
    core/life/life_refusal_codes.cpp
    core/life/death_event.cpp
    core/life/estate.cpp
    core/life/inheritance_scheduler.cpp
    core/life/life_audit_log.cpp
    core/life/death_pipeline.cpp
    core/life/death_scene_observation_hooks.cpp
    core/life/remains.cpp
    core/life/remains_decay_scheduler.cpp
    core/life/rights_post_death.cpp
    core/life/salvage.cpp
    core/life/birth_refusal_codes.cpp
    core/life/birth_event.cpp
    core/life/gestation_state.cpp
    core/life/lineage.cpp
    core/life/cohort_update_hooks.cpp
    core/life/birth_pipeline.cpp
    core/sim/macro_due_scheduler_hooks.cpp
    core/session/mp0_session.cpp
    rules/governance/jurisdiction_model.cpp
    rules/governance/legitimacy_model.cpp
    rules/governance/enforcement_capacity.cpp
    rules/governance/policy_model.cpp
    rules/governance/policy_scheduler.cpp
    rules/governance/org_governance_binding.cpp
    rules/city/city_refusal_codes.cpp
    rules/city/city_model.cpp
    rules/city/zoning_rules.cpp
    rules/city/city_services_stub.cpp
    rules/infrastructure/store_model.cpp
    rules/infrastructure/maintenance_model.cpp
    rules/infrastructure/production_chain.cpp
    rules/infrastructure/building_machine.cpp
    rules/infrastructure/machine_scheduler.cpp
    rules/logistics/transport_capacity.cpp
    rules/logistics/routing_stub.cpp
    rules/logistics/logistics_flow.cpp
    rules/survival/cohort_model.cpp
    rules/survival/needs_model.cpp
    rules/survival/consumption_scheduler.cpp
    rules/survival/survival_production_actions.cpp
    rules/survival/shelter_proxy.cpp
    rules/population/population_refusal_codes.cpp
    rules/population/cohort_types.cpp
    rules/population/demographics.cpp
    rules/population/household_model.cpp
    rules/population/migration_model.cpp
    rules/population/population_scheduler.cpp
    rules/population/population_projections.cpp
    rules/reproduction_rules.cpp
    rules/needs_constraints.cpp
)
add_custom_target(game_include_sanity
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/verify_includes_sanity.py
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Checking include boundaries for game sources"
)
add_dependencies(dominium_game game_include_sanity)
target_include_directories(dominium_game
    PUBLIC
        ${DOMINIUM_GAME_INCLUDE_DIR}
)
target_link_libraries(dominium_game
    PUBLIC
        domino_engine
)
set_target_properties(dominium_game PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_library(game::dominium ALIAS dominium_game)
