cmake_minimum_required(VERSION 3.16)

add_library(dominium_game STATIC
    dominium_game_stub.c
    core/dom_interest_set.c
    core/dom_interest_sources.c
    core/dom_interest_macro.c
    core/dom_fidelity.c
    core/dom_data_validate.c
    core/dom_epistemic.c
    core/law/law_kernel.cpp
    rules/life/ability_packages.cpp
    rules/life/control_authority.cpp
    rules/life/continuation_policy.cpp
    rules/life/controller_binding.cpp
    rules/life/life_events_stub.cpp
    rules/life/life_refusal_codes.cpp
    rules/life/death_event.cpp
    rules/life/estate.cpp
    rules/life/inheritance_scheduler.cpp
    rules/life/life_audit_log.cpp
    rules/life/death_pipeline.cpp
    rules/life/death_scene_observation_hooks.cpp
    rules/life/remains.cpp
    rules/life/remains_decay_scheduler.cpp
    rules/life/rights_post_death.cpp
    rules/life/salvage.cpp
    rules/life/birth_refusal_codes.cpp
    rules/life/birth_event.cpp
    rules/life/gestation_state.cpp
    rules/life/lineage.cpp
    rules/life/cohort_update_hooks.cpp
    rules/life/birth_pipeline.cpp
    core/orchestration/macro_due_scheduler_hooks.cpp
    core/session/mp0_session.cpp
    rules/agents/agent_goal.cpp
    rules/agents/agent_evaluator.cpp
    rules/agents/agent_planner.cpp
    rules/agents/agent_schedule.cpp
    rules/agents/agent_belief_update.cpp
    rules/agents/doctrine.cpp
    rules/agents/agent_role.cpp
    rules/agents/delegation.cpp
    rules/agents/doctrine_scheduler.cpp
    rules/agents/aggregate_beliefs.cpp
    rules/agents/aggregate_goals.cpp
    rules/agents/agent_aggregate.cpp
    rules/agents/agent_refinement.cpp
    rules/agents/agent_collapse.cpp
    mods/runtime/mod_manifest.cpp
    mods/runtime/mod_graph_resolver.cpp
    mods/runtime/mod_compat.cpp
    mods/runtime/mod_safe_mode.cpp
    mods/runtime/mod_loader.cpp
    rules/governance/jurisdiction_model.cpp
    rules/governance/legitimacy_model.cpp
    rules/governance/enforcement_capacity.cpp
    rules/governance/policy_model.cpp
    rules/governance/policy_scheduler.cpp
    rules/governance/org_governance_binding.cpp
    rules/knowledge/knowledge_refusal_codes.cpp
    rules/knowledge/knowledge_item.cpp
    rules/knowledge/institution_knowledge_binding.cpp
    rules/knowledge/secrecy_controls.cpp
    rules/knowledge/research_process.cpp
    rules/knowledge/diffusion_model.cpp
    rules/technology/tech_prerequisites.cpp
    rules/technology/tech_effects.cpp
    rules/technology/tech_activation.cpp
    rules/scale/scale_domains.cpp
    rules/scale/domain_transitions.cpp
    rules/scale/interplanetary_logistics.cpp
    rules/scale/interstellar_logistics.cpp
    rules/scale/scale_time_warp.cpp
    rules/scale/scale_interest_binding.cpp
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
    rules/war/security_force.cpp
    rules/war/military_cohort.cpp
    rules/war/readiness_state.cpp
    rules/war/morale_state.cpp
    rules/war/mobilization_pipeline.cpp
    rules/war/demobilization_pipeline.cpp
    rules/war/engagement.cpp
    rules/war/engagement_resolution.cpp
    rules/war/engagement_scheduler.cpp
    rules/war/casualty_generator.cpp
    rules/war/loss_accounting.cpp
    rules/war/territory_control.cpp
    rules/war/occupation_state.cpp
    rules/war/resistance_state.cpp
    rules/war/resistance_scheduler.cpp
    rules/war/disruption_effects.cpp
    rules/war/pacification_policies.cpp
    rules/war/route_control.cpp
    rules/war/blockade.cpp
    rules/war/convoy_security.cpp
    rules/war/interdiction.cpp
    rules/war/siege_effects.cpp
    rules/war/war_scale_scheduler.cpp
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
