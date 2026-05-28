Status: DERIVED
Last Reviewed: 2026-05-29
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/`
Conversation Corpus Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

# Part VI - Reconciliation


## Source: `docs/archive/docs_corpus/_reconciliation/DOCS_REPO_TRUTH_CROSSWALK_v0.md`

Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/`
Conversation Corpus Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

### Docs Repo Truth Crosswalk

This crosswalk starts with current repo authority and uses archive/conversation material only as supporting historical context.

| Topic ID | Topic | Source Paths | Classification | Disposition |
| --- | --- | --- | --- | --- |
| project_identity | Project identity and purpose | README.md; docs/README.md | current_repo_truth | Use current repo orientation first; archive and conversations may only explain history. |
| canon_glossary_authority | Canon and glossary authority | docs/canon/constitution_v1.md; docs/canon/glossary_v1.md; AGENTS.md | current_repo_truth | Canon, glossary, and AGENTS outrank archive and generated outputs. |
| engine_game_runtime_product_boundaries | Engine/game/runtime/product boundaries | README.md; docs/architecture; docs/archive/conversations/_reconciliation | consistent_but_review_required | Boundary claims need current-doc support before promotion. |
| determinism_replay_provenance | Determinism, replay, and provenance | AGENTS.md; docs/canon/constitution_v1.md; docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md | current_repo_truth | Determinism and provenance constraints are binding where scoped by canon and governance. |
| process_only_mutation | Process-only mutation | AGENTS.md; docs/canon/constitution_v1.md | current_repo_truth | Authoritative truth mutation must occur through lawful deterministic Process execution. |
| law_authority_refusal_capabilities | Law, authority, refusal, and capability model | AGENTS.md; docs/canon/constitution_v1.md; docs/reference/contracts | current_repo_truth_with_review_needed | Current law and contracts govern; archive claims are advisory only. |
| pack_driven_integration | Pack-driven integration | AGENTS.md; docs/canon/constitution_v1.md | current_repo_truth | Optional content and capabilities must remain pack- and registry-driven. |
| profiles_over_modes | Profiles over runtime mode flags | AGENTS.md; docs/canon/constitution_v1.md | current_repo_truth | Hardcoded runtime mode branches remain prohibited. |
| workbench_aide_codex_tooling | Workbench/AIDE/Codex/tooling role | AGENTS.md; .aide/queue/current.toml; docs/archive/conversations/_synthesis | blocked_scope_sensitive | Tooling is active, but broad Workbench UI and native GUI work remain blocked by the queue. |
| conversation_corpus_role | Conversation corpus role | docs/archive/conversations/README.md; docs/archive/conversations/_exports | conversation_advisory_only | Conversation material is derived historical evidence, not current truth. |
| release_setup_launcher_platform | Release/setup/launcher/platform state | .aide/queue/current.toml; docs/release; docs/archive/conversations/_promotion | blocked_scope_sensitive | Release publication remains blocked unless a stronger current queue source opens it. |
| renderer_ui_native_gui_scope | Renderer/UI/native GUI scope | .aide/queue/current.toml; docs/archive/conversations/_reconciliation | blocked_by_current_queue | Renderer implementation and native GUI work remain blocked. |
| provider_package_runtime_scope | Provider/package runtime scope | .aide/queue/current.toml; docs/archive/conversations/_promotion | blocked_by_current_queue | Provider runtime, package runtime, and runtime module loading remain blocked. |
| gameplay_domain_feature_scope | Gameplay/domain feature scope | .aide/queue/current.toml; docs/archive/conversations/_synthesis | blocked_by_current_queue | Gameplay and broad domain feature implementation remain blocked. |
| timekeeping_2038 | Timekeeping and 2038 resilience | docs/archive/conversations/_wiki/topics/timekeeping.md; docs/archive/conversations/_synthesis | conversation_advisory_or_docs_candidate | Conversation/archive support exists where present; current-doc promotion requires review. |
| world_reality_civilization_worldgen | World, reality, civilization, and worldgen domains | docs/archive/conversations/_synthesis | authority_sensitive | Semantic-domain work must respect specs/reality over data/reality and current queue limits. |
| contracts_schema_reference_docs | Contracts, schema, and reference docs | docs/reference/contracts; contracts | contract_or_schema_authority | Docs may summarize, but contract/schema law remains source authority. |
| testing_validation_fast | Testing, validation, FAST, and full-gate debt | AGENTS.md; docs/testing; tools/validators | current_repo_truth_with_debt_tracking | FAST is the minimum validation floor unless explicitly exempt. |
| current_queue_blocked_areas | Current queue blocked areas | .aide/queue/current.toml; docs/repo/FOUNDATION_LOCK.md | current_repo_truth | Blocked broad feature areas remain blocked. |


## Source: `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md`

Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/`
Conversation Corpus Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

### Docs Current Project Picture

Dominium's current documentation picture is authority layered. Canon, glossary, `AGENTS.md`, contract/schema law, current queue state, and validated repo artifacts are the highest-confidence sources. Archive and conversation material can explain how earlier ideas developed, but it cannot become current truth through this docs-corpus task.

#### Current Orientation

- Project orientation: `README.md`
- Documentation taxonomy: `docs/README.md`
- Canon: `docs/canon/constitution_v1.md`
- Glossary: `docs/canon/glossary_v1.md`
- Agent governance: `AGENTS.md`
- Queue state: `.aide/queue/current.toml`
- Foundation status: `docs/repo/FOUNDATION_LOCK.md`

#### Corpus Scale

- Files represented: 5116
- Markdown files: 4671
- Archive/conversation files: 3221

#### What Is Safe To Do With This Output

- Read the docs corpus as a map.
- Use archive material for provenance and review.
- Use generated contradictions and promotion queues to plan later tasks.
- Start later live-doc patches only through explicit narrow promotion tasks.

#### What This Output Does Not Do

- It does not promote archive claims.
- It does not rewrite canon, contracts, schema, implementation, release, or queue state.
- It does not open blocked renderer, gameplay, provider runtime, package runtime, broad Workbench UI, native GUI, or release publication work.


## Source: `docs/archive/docs_corpus/_reconciliation/DOCS_CANON_ARCHITECTURE_ALIGNMENT_v0.md`

Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/`
Conversation Corpus Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

### Docs Canon Architecture Alignment

This report maps high-authority documentation families without changing them.

#### Counts

- Canon files: 2
- Architecture files: 324
- Reference contract docs: 9

#### Canon Files

| Path | Status | Stability | Binding Sources |
| --- | --- | --- | --- |
| docs/canon/constitution_v1.md | CANONICAL | stable |  |
| docs/canon/glossary_v1.md | CANONICAL | stable |  |


#### Architecture Files

| Path | Status | Freshness | Risk |
| --- | --- | --- | --- |
| docs/architecture/ADAPTER_PATTERN.md | DERIVED | current | medium |
| docs/architecture/ADOPTION_PROTOCOL.md | CANONICAL | current | medium |
| docs/architecture/AI_AND_DELEGATED_AUTONOMY_MODEL.md | DERIVED | current | medium |
| docs/architecture/AI_BUDGET_MODEL.md | CANONICAL | current | medium |
| docs/architecture/AI_INTENT_MODEL.md | CANONICAL | current | medium |
| docs/architecture/ANTI_CHEAT_AND_INTEGRITY.md | CANONICAL | current | medium |
| docs/architecture/ANTI_CHEAT_AS_LAW.md | CANONICAL | current | medium |
| docs/architecture/ANTI_ENTROPY_RULES.md | CANONICAL | current | medium |
| docs/architecture/APPLICATION_CONTRACTS.md | DERIVED | current | medium |
| docs/architecture/APP_AUTOMATION_MODEL.md | CANONICAL | current | medium |
| docs/architecture/APP_CANON0.md | CANONICAL | current | medium |
| docs/architecture/APP_CANON1.md | CANONICAL | current | medium |
| docs/architecture/ARCH0_CONSTITUTION.md | CANONICAL | current | medium |
| docs/architecture/ARCHITECTURE.md | CANONICAL | current | medium |
| docs/architecture/ARCHITECTURE_GRAPH_SPEC_v1.md | DERIVED | current | medium |
| docs/architecture/ARCHITECTURE_LAYERS.md | CANONICAL | current | medium |
| docs/architecture/ARCHIVAL_AND_PERMANENCE.md | CANONICAL | current | medium |
| docs/architecture/ARCHIVE_MANIFEST.md | CANONICAL | current | medium |
| docs/architecture/ARCH_BUILD_ENFORCEMENT.md | CANONICAL | current | medium |
| docs/architecture/ARCH_CHANGE_PROCESS.md | CANONICAL | current | medium |
| docs/architecture/ARCH_ENFORCEMENT.md | CANONICAL | current | medium |
| docs/architecture/ARCH_REPO_LAYOUT.md | CANONICAL | superseded | medium |
| docs/architecture/ARCH_SPEC_OWNERSHIP.md | CANONICAL | current | medium |
| docs/architecture/ARTIFACT_LIFECYCLE.md | DERIVED | current | medium |
| docs/architecture/ARTIFACT_MODEL.md | CANONICAL | current | medium |
| docs/architecture/AUDITABILITY_AND_DISCLOSURE.md | CANONICAL | current | medium |
| docs/architecture/AUTHORITY_AND_ENTITLEMENTS.md | CANONICAL | current | medium |
| docs/architecture/AUTHORITY_AND_OMNIPOTENCE.md | CANONICAL | current | medium |
| docs/architecture/AUTHORITY_IN_REALITY.md | CANONICAL | current | medium |
| docs/architecture/AUTHORITY_MODEL.md | CANONICAL | current | medium |
| docs/architecture/BEHAVIORAL_COMPONENTS_STANDARD.md | DERIVED | current | medium |
| docs/architecture/BOUNDARY_ENFORCEMENT.md | DERIVED | current | medium |
| docs/architecture/BUDGET_POLICY.md | DERIVED | current | medium |
| docs/architecture/BUGREPORT_MODEL.md | CANONICAL | current | medium |
| docs/architecture/BUILD_IDENTITY_MODEL.md | CANONICAL | current | medium |
| docs/architecture/BUNDLE_MODEL.md | CANONICAL | current | medium |
| docs/architecture/CANONICAL_SYSTEM_MAP.md | CANONICAL | current | medium |
| docs/architecture/CANON_CUT_LINE.md | CANONICAL | current | medium |
| docs/architecture/CANON_INDEX.md | CANONICAL | current | medium |
| docs/architecture/CAPABILITY_BASELINES.md | CANONICAL | current | medium |
| docs/architecture/CAPABILITY_ONLY_CANON.md | CANONICAL | current | medium |
| docs/architecture/CHANGELOG_ARCH.md | CANONICAL | current | medium |
| docs/architecture/CHANGE_PROTOCOL.md | CANONICAL | current | medium |
| docs/architecture/CHEATS_ARE_JUST_LAWS.md | CANONICAL | current | medium |
| docs/architecture/CHECKPOINTING_MODEL.md | CANONICAL | current | medium |
| docs/architecture/CHECKPOINTS.md | CANONICAL | current | medium |
| docs/architecture/CIVILIZATION_MODEL.md | CANONICAL | current | medium |
| docs/architecture/CODE_DATA_BOUNDARY.md | CANONICAL | current | medium |
| docs/architecture/CODE_KNOWLEDGE_BOUNDARY.md | CANONICAL | current | medium |
| docs/architecture/COLLAPSE_AND_DECAY.md | CANONICAL | current | medium |
| docs/architecture/COLLAPSE_EXPAND_CONTRACT.md | CANONICAL | current | medium |
| docs/architecture/COLLAPSE_EXPAND_SOLVERS.md | DERIVED | current | medium |
| docs/architecture/COMPATIBILITY_MODEL.md | CANONICAL | current | medium |
| docs/architecture/COMPLEXITY_AND_SCALE.md | DERIVED | current | medium |
| docs/architecture/COMPONENTS.md | CANONICAL | current | medium |
| docs/architecture/CONFLICT_AND_WAR_MODEL.md | CANONICAL | current | medium |
| docs/architecture/CONSTANT_COST_GUARANTEE.md | CANONICAL | current | medium |
| docs/architecture/CONTENT_AND_STORAGE_MODEL.md | CANONICAL | current | medium |
| docs/architecture/CONTRACTS_INDEX.md | CANONICAL | current | medium |
| docs/architecture/CONTROL_LAYERS.md | CANONICAL | current | medium |
| docs/architecture/CORE_ABSTRACTIONS.md | DERIVED | current | medium |
| docs/architecture/CRASH_RECOVERY.md | CANONICAL | current | medium |
| docs/architecture/CROSS_SHARD_LOG.md | CANONICAL | current | medium |
| docs/architecture/C_COMPATIBLE_ABI_BOUNDARY.md | DERIVED | current | medium |
| docs/architecture/DEATH_AND_CONTINUITY.md | CANONICAL | current | medium |
| docs/architecture/DECAY_EROSION_REGEN.md | CANONICAL | current | medium |
| docs/architecture/DEMO_AND_TOURIST_MODEL.md | CANONICAL | current | medium |
| docs/architecture/DEPRECATION_AND_QUARANTINE.md | DERIVED | current | medium |
| docs/architecture/DEPRECATION_LIFECYCLE.md | DERIVED | current | medium |
| docs/architecture/DETERMINISTIC_ORDERING_POLICY.md | CANONICAL | current | medium |
| docs/architecture/DETERMINISTIC_REDUCTION_RULES.md | CANONICAL | current | medium |
| docs/architecture/DEV_OPS_MODEL.md | CANONICAL | current | medium |
| docs/architecture/DIRECTORY_CONTEXT.md | DERIVED | superseded | medium |
| docs/architecture/DIRECTORY_STRUCTURE.md | DERIVED | superseded | medium |
| docs/architecture/DISTRIBUTED_SIMULATION_MODEL.md | CANONICAL | current | medium |
| docs/architecture/DISTRIBUTED_TIME_MODEL.md | CANONICAL | current | medium |
| docs/architecture/DISTRIBUTION_AND_STOREFRONTS.md | CANONICAL | current | medium |
| docs/architecture/DISTRIBUTION_LAYOUT.md | CANONICAL | current | medium |
| docs/architecture/DISTRIBUTION_PROFILES.md | CANONICAL | current | medium |
| docs/architecture/DOMAIN_JURISDICTIONS_AND_LAW.md | CANONICAL | current | medium |
| docs/architecture/DOMAIN_SHARDING_AND_STREAMING.md | CANONICAL | current | medium |
| docs/architecture/DOMAIN_VOLUMES.md | CANONICAL | current | medium |
| docs/architecture/DUPLICATION_DETECTION_RULES.md | DERIVED | current | medium |
| docs/architecture/ECONOMIC_MODEL.md | CANONICAL | current | medium |
| docs/architecture/ECONOMY_AND_LOGISTICS.md | CANONICAL | current | medium |
| docs/architecture/ENERGY_MODEL.md | CANONICAL | current | medium |
| docs/architecture/ENFORCEMENT_ESCALATION.md | CANONICAL | current | medium |
| docs/architecture/EPISTEMICS_AND_SCALED_MMO.md | CANONICAL | current | medium |
| docs/architecture/EPISTEMICS_MODEL.md | CANONICAL | current | medium |
| docs/architecture/EXECUTION_MODEL.md | CANONICAL | current | medium |
| docs/architecture/EXECUTION_REORDERING_POLICY.md | CANONICAL | current | medium |
| docs/architecture/EXECUTION_SUBSTRATE_AUDIT.md | CANONICAL | current | medium |
| docs/architecture/EXISTENCE_AND_REALITY.md | CANONICAL | current | medium |
| docs/architecture/EXISTENCE_LIFECYCLE.md | CANONICAL | current | medium |
| docs/architecture/EXOTIC_TRAVEL_AND_REALITY.md | CANONICAL | current | medium |
| docs/architecture/EXPLORATION_METRICS.md | CANONICAL | current | medium |
| docs/architecture/EXPLORATION_SCALING_PROOF.md | CANONICAL | current | medium |
| docs/architecture/EXTEND_VS_CREATE.md | CANONICAL | current | medium |
| docs/architecture/EXTENSION_MAP.md | DERIVED | current | medium |
| docs/architecture/EXTENSION_RULES.md | CANONICAL | current | medium |
| docs/architecture/FABRICATION_MODEL.md | CANONICAL | current | medium |
| docs/architecture/FLOAT_POLICY.md | CANONICAL | current | medium |
| docs/architecture/FLOWSYSTEM_STANDARD.md | DERIVED | current | medium |
| docs/architecture/FLUIDS_MODEL.md | CANONICAL | current | medium |
| docs/architecture/FORKING_AND_PROVIDES_MODEL.md | CANONICAL | current | medium |
| docs/architecture/FROZEN_CONTRACT_HASHES.json |  | unclear | medium |
| docs/architecture/FUTURE_COMPATIBILITY_AND_ARCH.md | CANONICAL | current | medium |
| docs/architecture/FUTURE_PROOFING.md | CANONICAL | current | medium |
| docs/architecture/GENERATED_CODE_POLICY.md | CANONICAL | current | medium |
| docs/architecture/GLOBAL_ID_MODEL.md | CANONICAL | current | medium |
| docs/architecture/GLOSSARY.md | CANONICAL | current | medium |
| docs/architecture/GOVERNANCE_AND_INSTITUTIONS.md | CANONICAL | current | medium |
| docs/architecture/GUI_BASELINE.md | CANONICAL | current | medium |
| docs/architecture/HARDWARE_EVOLUTION_STRATEGY.md | CANONICAL | current | medium |
| docs/architecture/HAZARDS_MODEL.md | CANONICAL | current | medium |
| docs/architecture/HISTORY_AND_CIVILIZATION_MODEL.md | DERIVED | current | medium |
| docs/architecture/IDENTITY_ACROSS_TIME.md | CANONICAL | current | medium |
| docs/architecture/IDE_AND_TOOLCHAIN_POLICY.md | CANONICAL | current | medium |
| docs/architecture/IDE_PROJECTIONS.md | DERIVED | current | medium |
| docs/architecture/ID_AND_NAMESPACE_RULES.md | CANONICAL | current | medium |
| docs/architecture/INDEXING_POLICY.md | CANONICAL | current | medium |
| docs/architecture/INFORMATION_MODEL.md | CANONICAL | current | medium |
| docs/architecture/INSTALLER_CONTRACT.md | CANONICAL | current | medium |
| docs/architecture/INSTALL_MODEL.md | CANONICAL | current | medium |
| docs/architecture/INSTANCE_MODEL.md | CANONICAL | current | medium |
| docs/architecture/INSTITUTIONS_AND_GOVERNANCE_MODEL.md | CANONICAL | current | medium |
| docs/architecture/INTEREST_MODEL.md | CANONICAL | current | medium |
| docs/architecture/INVARIANTS.md | CANONICAL | current | medium |
| docs/architecture/INVARIANTS_AND_TOLERANCES.md | CANONICAL | current | medium |
| docs/architecture/INVARIANT_REGISTRY.md | CANONICAL | current | medium |
| docs/architecture/JOIN_RESYNC_CONTRACT.md | CANONICAL | current | medium |
| docs/architecture/KNOWLEDGE_AND_SKILLS_MODEL.md | CANONICAL | current | medium |
| docs/architecture/KNOWN_BLOCKERS.md | CANONICAL | current | medium |
| docs/architecture/KNOWN_WARNINGS.md | DERIVED | current | medium |
| docs/architecture/LANGUAGE_STRATEGY.md | CANONICAL | current | medium |
| docs/architecture/LAUNCHER_CONTRACT.md | CANONICAL | current | medium |
| docs/architecture/LAW_AND_META_LAW.md | CANONICAL | current | medium |
| docs/architecture/LAW_ENFORCEMENT_POINTS.md | CANONICAL | current | medium |
| docs/architecture/LEGACY_SUPPORT_MODEL.md | CANONICAL | current | medium |
| docs/architecture/LEGACY_SUPPORT_STRATEGY.md | CANONICAL | current | medium |
| docs/architecture/LIFE_AND_POPULATION.md | CANONICAL | current | medium |
| docs/architecture/LIVE_EVOLUTION_MODEL.md | CANONICAL | current | medium |
| docs/architecture/LOCKFILES.md | CANONICAL | current | medium |
| docs/architecture/LOCKLIST.md | CANONICAL | current | medium |
| docs/architecture/LOCKLIST_OVERRIDES.json |  | unclear | medium |
| docs/architecture/MACRO_TIME_MODEL.md | CANONICAL | current | medium |
| docs/architecture/MIGRATION_TEMPLATE.md | DERIVED | current | medium |
| docs/architecture/MMO_COMPATIBILITY.md | CANONICAL | current | medium |
| docs/architecture/MMO_SAFETY_MODEL.md | CANONICAL | current | medium |
| docs/architecture/MODES_AS_PROFILES.md | DERIVED | current | medium |
| docs/architecture/MODPACK_FORMAT.md | CANONICAL | current | medium |
| docs/architecture/MODULE_BOUNDARIES_v1.md | DERIVED | current | medium |
| docs/architecture/MODULE_INDEX_v1.md | DERIVED | current | medium |
| docs/architecture/MOD_ECOSYSTEM_RULES.md | CANONICAL | current | medium |
| docs/architecture/MOVEMENT_AS_LOGISTICS.md | CANONICAL | current | medium |
| docs/architecture/NAMESPACING_RULES.md | CANONICAL | current | medium |
| docs/architecture/NETWORKGRAPH_STANDARD.md | DERIVED | current | medium |
| docs/architecture/NON_INTERFERENCE.md | CANONICAL | current | medium |
| docs/architecture/NO_MAGIC_TELEPORTS.md | CANONICAL | current | medium |
| docs/architecture/NO_TELEPORTATION_EXCEPT_BY_CONTRACT.md | CANONICAL | current | medium |
| docs/architecture/OPS_TRANSACTION_MODEL.md | CANONICAL | current | medium |
| docs/architecture/OVERVIEW_ARCHITECTURE.md | CANONICAL | current | medium |
| docs/architecture/PACK_FORMAT.md | CANONICAL | current | medium |
| docs/architecture/PERFORMANCE_METRICS.md | CANONICAL | current | medium |
| docs/architecture/PERFORMANCE_PROOF.md | CANONICAL | current | medium |
| docs/architecture/PIRACY_CONTAINMENT.md | CANONICAL | current | medium |
| docs/architecture/PLATFORM_RESPONSIBILITY.md | CANONICAL | current | medium |
| docs/architecture/POST_CLEAN_2_STATUS.md | DERIVED | current | medium |
| docs/architecture/PROCESS_ONLY_MUTATION.md | CANONICAL | current | medium |
| docs/architecture/PRODUCT_SHELL_CONTRACT.md | CANONICAL | current | medium |
| docs/architecture/PROJECTION_LIFECYCLE.md | CANONICAL | current | medium |
| docs/architecture/PROJECT_EXECUTION_BASELINE.md | CANONICAL | current | medium |
| docs/architecture/QUANTITY_BUNDLES.md | DERIVED | current | medium |
| docs/architecture/REALITY_FLOW.md | CANONICAL | current | medium |
| docs/architecture/REALITY_LAYER.md | CANONICAL | current | medium |
| docs/architecture/REALITY_MODEL.md | CANONICAL | current | medium |
| docs/architecture/REDUCTION_MODEL.md | CANONICAL | current | medium |
| docs/architecture/REFINEMENT_CONTRACTS.md | CANONICAL | current | medium |
| docs/architecture/REFRACTOR_STAGE.md | CANONICAL | current | medium |
| docs/architecture/REFUSAL_AND_EXPLANATION_MODEL.md | CANONICAL | current | medium |
| docs/architecture/REFUSAL_SEMANTICS.md | CANONICAL | current | medium |
| docs/architecture/REGISTRY_PATTERN.md | CANONICAL | current | medium |
| docs/architecture/RENDERER_RESPONSIBILITY.md | CANONICAL | current | medium |
| docs/architecture/REPLAY_AND_TIME_ASYMMETRY.md | CANONICAL | current | medium |
| docs/architecture/REPLAY_FORMAT.md | CANONICAL | current | medium |
| docs/architecture/REPORT_GAME_ARCH_DECISIONS.md | CANONICAL | current | medium |
| docs/architecture/REPOSITORY_STRUCTURE_v1.md | DERIVED | current | medium |
| docs/architecture/REPOX_AUTOMATION_MODEL.md | CANONICAL | current | medium |
| docs/architecture/REPO_INTENT.md | CANONICAL | current | medium |
| docs/architecture/REPO_NAV.md | CANONICAL | current | medium |
| docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md | CANONICAL | current | medium |
| docs/architecture/RETRO_CONSISTENCY_AUDIT_FRAMEWORK.md | DERIVED | current | medium |
| docs/architecture/RISK_AND_LIABILITY_MODEL.md | CANONICAL | current | medium |
| docs/architecture/RNG_MODEL.md | CANONICAL | current | medium |
| docs/architecture/ROLLING_UPDATES.md | CANONICAL | current | medium |
| docs/architecture/ROOT_ARCHITECTURE.md | DERIVED | current | medium |
| docs/architecture/SANDBOX_MODEL.md | CANONICAL | current | medium |
| docs/architecture/SAVE_FORMAT.md | CANONICAL | current | medium |
| docs/architecture/SAVE_MODEL.md | CANONICAL | current | medium |
| docs/architecture/SAVE_PIPELINE.md | CANONICAL | current | medium |
| docs/architecture/SCALE_AND_COMPLEXITY.md | CANONICAL | current | medium |
| docs/architecture/SCALING_COMPATIBILITY.md | CANONICAL | current | medium |
| docs/architecture/SCALING_MODEL.md | CANONICAL | current | medium |
| docs/architecture/SCHEMA_CHANGE_NOTES.md | CANONICAL | current | medium |
| docs/architecture/SCHEMA_STABILITY.md | CANONICAL | current | medium |
| docs/architecture/SEMANTIC_STABILITY_LOCK.json |  | unclear | medium |
| docs/architecture/SEMANTIC_STABILITY_POLICY.md | CANONICAL | current | medium |
| docs/architecture/SERVICES_AND_PRODUCTS.md | CANONICAL | current | medium |
| docs/architecture/SETUP_TRANSACTION_MODEL.md | CANONICAL | current | medium |
| docs/architecture/SHARD_LIFECYCLE.md | CANONICAL | current | medium |
| docs/architecture/SHIM_SUNSET_PLAN.md | DERIVED | current | medium |
| docs/architecture/SIGNAL_MODEL.md | CANONICAL | current | medium |
| docs/architecture/SKU_MATRIX.md | CANONICAL | current | medium |
| docs/architecture/SLICE_0_CONTRACT.md | CANONICAL | current | medium |
| docs/architecture/SLICE_1_CONTRACT.md | CANONICAL | current | medium |
| docs/architecture/SLICE_2_CONTRACT.md | CANONICAL | current | medium |
| docs/architecture/SOURCE_POCKET_POLICY_v1.md | DERIVED | current | medium |
| docs/architecture/SPACE_AND_BOUNDS.md | CANONICAL | current | medium |
| docs/architecture/SPACE_TIME_EXISTENCE.md | CANONICAL | current | medium |
| docs/architecture/SPECTATOR_AND_AUDIT_MODES.md | CANONICAL | current | medium |
| docs/architecture/SPECTATOR_TO_GODMODE.md | CANONICAL | current | medium |
| docs/architecture/SRZ_MODEL.md | CANONICAL | current | medium |
| docs/architecture/STANDARDS_AND_META_SYSTEMS_MODEL.md | DERIVED | current | medium |
| docs/architecture/STRUCTURAL_STABILITY_MODEL.md | CANONICAL | current | medium |
| docs/architecture/SYSTEM_TOPOLOGY_MAP.md | DERIVED | current | medium |
| docs/architecture/SYS_CAPS_AND_EXEC_POLICY.md | CANONICAL | current | medium |
| docs/architecture/TERMINOLOGY_GLOSSARY.md | DERIVED | current | medium |
| docs/architecture/TERRAIN_COORDINATES.md | CANONICAL | current | medium |
| docs/architecture/TERRAIN_FIELDS.md | CANONICAL | current | medium |
| docs/architecture/TERRAIN_MACRO_CAPSULE.md | CANONICAL | current | medium |
| docs/architecture/TERRAIN_OVERLAYS.md | CANONICAL | current | medium |
| docs/architecture/TERRAIN_PROVIDER_CHAIN.md | CANONICAL | current | medium |
| docs/architecture/TERRAIN_TRUTH_MODEL.md | CANONICAL | current | medium |
| docs/architecture/THERMAL_MODEL.md | CANONICAL | current | medium |
| docs/architecture/THREAT_MODEL.md | CANONICAL | current | medium |
| docs/architecture/TIMELINE_FORKS_AND_HISTORY.md | CANONICAL | current | medium |
| docs/architecture/TIME_DILATION_WITHOUT_TIME_WARP.md | CANONICAL | current | medium |
| docs/architecture/TIME_PERCEPTION_VS_SIMULATION.md | CANONICAL | current | medium |
| docs/architecture/TOOLS_AS_CAPABILITIES.md | CANONICAL | current | medium |
| docs/architecture/TRANSITION_PLAYBOOK.md | CANONICAL | current | medium |
| docs/architecture/TRAVEL_AND_MOVEMENT.md | CANONICAL | current | medium |
| docs/architecture/TRAVEL_CAPACITY_AND_COST.md | CANONICAL | current | medium |
| docs/architecture/TRUST_AND_LEGITIMACY_MODEL.md | CANONICAL | current | medium |
| docs/architecture/UI_BINDING_MODEL.md | CANONICAL | current | medium |
| docs/architecture/UNIT_SYSTEM_POLICY.md | CANONICAL | current | medium |
| docs/architecture/UNKNOWN_UNKNOWNS.md | CANONICAL | current | medium |
| docs/architecture/UPDATE_MODEL.md | CANONICAL | current | medium |
| docs/architecture/UPGRADE_AND_CONVERSION.md | CANONICAL | current | medium |
| docs/architecture/VALIDATION_RULES.md | CANONICAL | current | medium |
| docs/architecture/VISITABILITY_AND_REFINEMENT.md | CANONICAL | current | medium |
| docs/architecture/VISITABILITY_CONSISTENCY.md | CANONICAL | current | medium |
| docs/architecture/WHAT_THIS_IS.md | CANONICAL | current | medium |
| docs/architecture/WHAT_THIS_IS_NOT.md | CANONICAL | current | medium |
| docs/architecture/WHY_ECONOMIES_DONT_FAKE.md | CANONICAL | current | medium |
| docs/architecture/WHY_NPCS_DONT_POP.md | CANONICAL | current | medium |
| docs/architecture/WORKSPACES.md | CANONICAL | current | medium |
| docs/architecture/WORLDDEFINITION.md | CANONICAL | current | medium |
| docs/architecture/WORLDDEFINITION_CONTRACT.md | CANONICAL | current | medium |
| docs/architecture/api_abi_canon.md | DERIVED | current | medium |
| docs/architecture/app_composition_model.md | DERIVED | current | medium |
| docs/architecture/artifact_identity_law.md | DERIVED | current | medium |
| docs/architecture/astronomy_catalogs.md | DERIVED | current | medium |
| docs/architecture/barebones_client_shell.md | DERIVED | current | medium |
| docs/architecture/camera_and_navigation.md | DERIVED | current | medium |
| docs/architecture/capability_refusal_law.md | DERIVED | current | medium |
| docs/architecture/command_result_view_slice.md | DERIVED | current | medium |
| docs/architecture/command_view_event_refusal.md | DERIVED | current | medium |
| docs/architecture/composition_resolver_law.md | DERIVED | current | medium |
| docs/architecture/coordinate_model.md | DERIVED | current | medium |
| docs/architecture/dependency_direction_law.md | DERIVED | current | medium |
| docs/architecture/deterministic_packaging.md | DERIVED | current | medium |
| docs/architecture/deterministic_parallelism.md | DERIVED | current | medium |
| docs/architecture/diagnostics_and_evidence.md | DERIVED | current | medium |
| docs/architecture/document_patch_transaction.md | DERIVED | current | medium |
| docs/architecture/document_patch_transaction_runtime.md | DERIVED | current | medium |
| docs/architecture/domino_framework_boundary.md | CANONICAL | current | medium |
| docs/architecture/fidelity_policy.md | DERIVED | current | medium |
| docs/architecture/hash_anchors.md | DERIVED | current | medium |
| docs/architecture/interest_regions.md | DERIVED | current | medium |
| docs/architecture/lens_system.md | DERIVED | current | medium |
| docs/architecture/lockfile.md | DERIVED | current | medium |
| docs/architecture/lockfile_law.md | DERIVED | current | medium |
| docs/architecture/macro_capsules.md | DERIVED | current | medium |
| docs/architecture/mod_pack_trust_model.md | CANONICAL | current | medium |
| docs/architecture/module_composition_law.md | DERIVED | current | medium |
| docs/architecture/native_architecture_policy.md | CANONICAL | current | medium |
| docs/architecture/observation_kernel.md | DERIVED | current | medium |
| docs/architecture/pack_mount_model.md | DERIVED | current | medium |
| docs/architecture/pack_system.md | DERIVED | current | medium |
| docs/architecture/package_mount_slice.md | DERIVED | current | medium |
| docs/architecture/portability_matrix.md | CANONICAL | current | medium |
| docs/architecture/project_graph_impact_model.md | DERIVED | current | medium |
| docs/architecture/project_graph_service.md | DERIVED | current | medium |
| docs/architecture/provider_conformance_law.md | CANONICAL | current | medium |
| docs/architecture/provider_model.md | DERIVED | current | medium |
| docs/architecture/provider_selection_model.md | DERIVED | current | medium |
| docs/architecture/public_surface_registry.md | DERIVED | current | medium |
| docs/architecture/registry_compile.md | DERIVED | current | medium |
| docs/architecture/replacement_protocol.md | DERIVED | current | medium |
| docs/architecture/replay_proof_law.md | DERIVED | current | medium |
| docs/architecture/replay_proof_slice.md | DERIVED | current | medium |
| docs/architecture/schema_protocol_evolution.md | DERIVED | current | medium |
| docs/architecture/service_conformance_law.md | CANONICAL | current | medium |
| docs/architecture/session_lifecycle.md | DERIVED | current | medium |
| docs/architecture/setup_and_launcher.md | DERIVED | current | medium |
| docs/architecture/site_registry.md | DERIVED | current | medium |
| docs/architecture/srz_contract.md | DERIVED | current | medium |
| docs/architecture/system/EXPLICIT_STATE_VECTOR_RULE.md | CANONICAL | current | medium |
| docs/architecture/system/INTERFACE_AND_INVARIANT_RULES.md | DERIVED | current | medium |
| docs/architecture/system/MACROCAPSULE_BEHAVIOR_MODEL.md | DERIVED | current | medium |
| docs/architecture/system/SYSTEM_CERTIFICATION_MODEL.md | DERIVED | current | medium |
| docs/architecture/system/SYSTEM_COMPOSITION_CONSTITUTION.md | DERIVED | current | medium |
| docs/architecture/system/SYSTEM_FORENSICS_MODEL.md | CANONICAL | current | medium |
| docs/architecture/system/SYSTEM_RELIABILITY_MODEL.md | CANONICAL | current | medium |
| docs/architecture/system/SYSTEM_TEMPLATES.md | DERIVED | current | medium |
| docs/architecture/system/SYSTEM_TIER_AND_ROI_POLICY.md | DERIVED | current | medium |
| docs/architecture/system/SYS_SHARD_BOUNDARY_RULES.md | CANONICAL | current | medium |
| docs/architecture/time_model.md | DERIVED | current | medium |
| docs/architecture/truth_model.md | DERIVED | current | medium |
| docs/architecture/truth_perceived_render.md | DERIVED | current | medium |
| docs/architecture/ui_registry.md | DERIVED | current | medium |
| docs/architecture/versioning_and_deprecation.md | CANONICAL | current | medium |
| docs/architecture/view_action_projection_model.md | DERIVED | current | medium |
| docs/architecture/workbench_workspace_model.md | DERIVED | current | medium |


#### Reference Contract Docs

| Path | Status | Freshness | Risk |
| --- | --- | --- | --- |
| docs/reference/contracts/CAPABILITY_NEGOTIATION_CONSTITUTION.md | CANONICAL | current | high |
| docs/reference/contracts/SEMANTIC_CONTRACT_MODEL.md | CANONICAL | current | high |
| docs/reference/contracts/authority_context.md | DERIVED | current | high |
| docs/reference/contracts/experience_profile.md | DERIVED | current | high |
| docs/reference/contracts/law_profile.md | DERIVED | current | high |
| docs/reference/contracts/lens_contract.md | DERIVED | current | high |
| docs/reference/contracts/refusal_contract.md | DERIVED | current | high |
| docs/reference/contracts/session_spec.md | DERIVED | current | high |
| docs/reference/contracts/versioning_and_migration.md | DERIVED | current | high |


## Source: `docs/archive/docs_corpus/_reconciliation/DOCS_ARCHIVE_CONVERSATION_ALIGNMENT_v0.md`

Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/`
Conversation Corpus Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

### Docs Archive Conversation Alignment

Archive docs and the conversation corpus are aligned as historical/advisory evidence.

- Non-conversation archive files: 2460
- Conversation corpus files: 761
- Promotion status: not promoted

#### Alignment Rule

Archive docs can provide provenance. Conversation corpus outputs can provide design-intent summaries and review queues. Neither can override canon, contracts, schema, current queue state, or current docs in their authority scope.


## Source: `docs/archive/docs_corpus/_reconciliation/DOCS_PROMOTION_QUEUE_v0.md`

Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/`
Conversation Corpus Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

### Docs Promotion Queue

This queue records later review candidates. It does not apply any live-doc patch.

| Promotion ID | Source Path(s) | Type | Recommended Next Action | Promotion Status |
| --- | --- | --- | --- | --- |
| DOC-PROMOTE-0001 | docs/archive/audit/ULTRA_REPO_AUDIT_BUILD_RUN_TEST_MATRIX.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0002 | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__00_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0003 | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0004 | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__02_context_transfer_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0005 | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0006 | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__05_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0007 | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0008 | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__07_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0009 | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__08_future_chat_bootstrap_prompt.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0010 | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0011 | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0012 | docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__11_bundle_integrity_check.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0013 | docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__01_full_chat_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0014 | docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__03_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0015 | docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0016 | docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0017 | docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__06_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0018 | docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0019 | docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__01_full_chat_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0020 | docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__03_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0021 | docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0022 | docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0023 | docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__06_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0024 | docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0025 | docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__01_full_chat_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0026 | docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__03_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0027 | docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0028 | docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0029 | docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__06_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0030 | docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0031 | docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__01_full_chat_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0032 | docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__03_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0033 | docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0034 | docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__05_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0035 | docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__06_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0036 | docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0037 | docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__01_full_chat_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0038 | docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__03_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0039 | docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0040 | docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__05_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0041 | docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__06_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0042 | docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0043 | docs/archive/conversations/Dominium_Complete_Conversation/00_final_manifest/Dominium_Complete_Conversation_ALL_FILES_FINAL__00_readme_and_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0044 | docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__00_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0045 | docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0046 | docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__02_context_transfer_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0047 | docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0048 | docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__05_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0049 | docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__06_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0050 | docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0051 | docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__08_future_chat_bootstrap_prompt.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0052 | docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0053 | docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__00_complete_bundle_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0054 | docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0055 | docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__README_FIRST.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0056 | docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__00_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0057 | docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0058 | docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__02_context_transfer_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0059 | docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0060 | docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__05_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0061 | docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0062 | docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__07_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0063 | docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__08_future_chat_bootstrap_prompt.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0064 | docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__09_in_chat_reader.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0065 | docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0066 | docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_full_conversation_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0067 | docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_conversation_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0068 | docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_detailed_summary_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0069 | docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__11_complete_bundle_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0070 | docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__12_bundle_verification.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0071 | docs/archive/conversations/Dominium_Complete_Conversation/dominium_related_file/Dominium_Conversation_Complete_Companion_Report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0072 | docs/archive/conversations/Dominium_Complete_Conversation/existing_companion_report_package/Dominium_Complete_Conversation_Companion_Report__01_accompanying_human_readable_detailed_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0073 | docs/archive/conversations/Dominium_Complete_Conversation/existing_companion_report_package/Dominium_Complete_Conversation_Companion_Report__bundle_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0074 | docs/archive/conversations/Dominium_Complete_Conversation/existing_companion_report_package/Dominium_Complete_Conversation_Companion_Report__human_readable_detailed_summary.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0075 | docs/archive/conversations/Dominium_Complete_Conversation/existing_complete_preservation_package/Dominium_Complete_Conversation_Preservation__00_consolidated_package_index.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0076 | docs/archive/conversations/Dominium_Complete_Conversation/existing_complete_preservation_package/Dominium_Complete_Conversation_Preservation__10_accompanying_human_readable_detailed_summary_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0077 | docs/archive/conversations/Dominium_Complete_Conversation/existing_consolidated_package_artifact/Dominium_Conversation_Consolidated_File_Manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0078 | docs/archive/conversations/Dominium_Complete_Conversation/existing_consolidated_package_artifact/Dominium_Conversation_Package_Verification_Report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0079 | docs/archive/conversations/Dominium_Complete_Conversation/new_companion_report_and_bundle/Dominium_Conversation_Complete_Accompanying_Report__10_accompanying_human_readable_summary_and_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0080 | docs/archive/conversations/Dominium_Complete_Conversation/new_companion_report_and_bundle/Dominium_Conversation_Complete_Accompanying_Report__11_combined_bundle_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0081 | docs/archive/conversations/Dominium_Complete_Conversation/robotic_seed_civilisation_handoff_file/Dominium_Robotic_Seed_Civilisation_Architecture__00_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0082 | docs/archive/conversations/Dominium_Complete_Conversation/robotic_seed_civilisation_handoff_file/Dominium_Robotic_Seed_Civilisation_Architecture__01_human_readable_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0083 | docs/archive/conversations/Dominium_Complete_Conversation/robotic_seed_civilisation_handoff_file/Dominium_Robotic_Seed_Civilisation_Architecture__02_context_transfer_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0084 | docs/archive/conversations/Dominium_Complete_Conversation/robotic_seed_civilisation_handoff_file/Dominium_Robotic_Seed_Civilisation_Architecture__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0085 | docs/archive/conversations/Dominium_Complete_Conversation/robotic_seed_civilisation_handoff_file/Dominium_Robotic_Seed_Civilisation_Architecture__05_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0086 | docs/archive/conversations/Dominium_Complete_Conversation/robotic_seed_civilisation_handoff_file/Dominium_Robotic_Seed_Civilisation_Architecture__06_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0087 | docs/archive/conversations/Dominium_Complete_Conversation/robotic_seed_civilisation_handoff_file/Dominium_Robotic_Seed_Civilisation_Architecture__07_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0088 | docs/archive/conversations/Dominium_Complete_Conversation/robotic_seed_civilisation_handoff_file/Dominium_Robotic_Seed_Civilisation_Architecture__08_future_chat_bootstrap_prompt.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0089 | docs/archive/conversations/Dominium_Complete_Conversation/robotic_seed_civilisation_handoff_file/Dominium_Robotic_Seed_Civilisation_Architecture__09_in_chat_reader.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0090 | docs/archive/conversations/Domino_Dominium_Workbench/dominium_workbench_full_conversation_companion__bundle_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0091 | docs/archive/conversations/Domino_Dominium_Workbench/dominium_workbench_full_conversation_companion__human_readable_detailed_summary_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0092 | docs/archive/conversations/Domino_Dominium_Workbench/prior_preservation_files/dominium_workbench_presentation_spine_universe_explorer_planning__00_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0093 | docs/archive/conversations/Domino_Dominium_Workbench/prior_preservation_files/dominium_workbench_presentation_spine_universe_explorer_planning__01_human_readable_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0094 | docs/archive/conversations/Domino_Dominium_Workbench/prior_preservation_files/dominium_workbench_presentation_spine_universe_explorer_planning__02_context_transfer_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0095 | docs/archive/conversations/Domino_Dominium_Workbench/prior_preservation_files/dominium_workbench_presentation_spine_universe_explorer_planning__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0096 | docs/archive/conversations/Domino_Dominium_Workbench/prior_preservation_files/dominium_workbench_presentation_spine_universe_explorer_planning__05_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0097 | docs/archive/conversations/Domino_Dominium_Workbench/prior_preservation_files/dominium_workbench_presentation_spine_universe_explorer_planning__06_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0098 | docs/archive/conversations/Domino_Dominium_Workbench/prior_preservation_files/dominium_workbench_presentation_spine_universe_explorer_planning__07_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0099 | docs/archive/conversations/Domino_Dominium_Workbench/prior_preservation_files/dominium_workbench_presentation_spine_universe_explorer_planning__08_future_chat_bootstrap_prompt.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0100 | docs/archive/conversations/Domino_Dominium_Workbench/prior_preservation_files/dominium_workbench_presentation_spine_universe_explorer_planning__09_in_chat_reader.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0101 | docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__00_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0102 | docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__01_human_readable_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0103 | docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__02_context_transfer_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0104 | docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0105 | docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__05_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0106 | docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__06_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0107 | docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__07_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0108 | docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__08_future_chat_bootstrap_prompt.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0109 | docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__09_in_chat_reader.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0110 | docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__10_accompanying_detailed_summary_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0111 | docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__11_package_quality_check.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0112 | docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__00_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0113 | docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__01_human_readable_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0114 | docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__02_context_transfer_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0115 | docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0116 | docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__05_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0117 | docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__06_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0118 | docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__07_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0119 | docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__08_future_chat_bootstrap_prompt.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0120 | docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__09_in_chat_reader.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0121 | docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__10_accompanying_detailed_conversation_summary_and_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0122 | docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__11_package_integrity_check.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0123 | docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__00_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0124 | docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__01_human_readable_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0125 | docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__02_context_transfer_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0126 | docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0127 | docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__05_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0128 | docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__06_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0129 | docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__07_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0130 | docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__08_future_chat_bootstrap_prompt.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0131 | docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__09_in_chat_reader.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0132 | docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__10_accompanying_detailed_conversation_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0133 | docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__11_complete_bundle_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0134 | docs/archive/conversations/Launcher_Setup_Architecture/Dominium_Launcher_Setup_Architecture__01_full_chat_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0135 | docs/archive/conversations/Launcher_Setup_Architecture/Dominium_Launcher_Setup_Architecture__03_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0136 | docs/archive/conversations/Launcher_Setup_Architecture/Dominium_Launcher_Setup_Architecture__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0137 | docs/archive/conversations/Launcher_Setup_Architecture/Dominium_Launcher_Setup_Architecture__05_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0138 | docs/archive/conversations/Launcher_Setup_Architecture/Dominium_Launcher_Setup_Architecture__06_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0139 | docs/archive/conversations/Launcher_Setup_Architecture/Dominium_Launcher_Setup_Architecture__manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0140 | docs/archive/conversations/Modularity_AIDE_Refactorability/Dominium_Modularity_AIDE_Refactorability_Architecture__00_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0141 | docs/archive/conversations/Modularity_AIDE_Refactorability/Dominium_Modularity_AIDE_Refactorability_Architecture__01_human_readable_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0142 | docs/archive/conversations/Modularity_AIDE_Refactorability/Dominium_Modularity_AIDE_Refactorability_Architecture__02_context_transfer_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0143 | docs/archive/conversations/Modularity_AIDE_Refactorability/Dominium_Modularity_AIDE_Refactorability_Architecture__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0144 | docs/archive/conversations/Modularity_AIDE_Refactorability/Dominium_Modularity_AIDE_Refactorability_Architecture__05_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0145 | docs/archive/conversations/Modularity_AIDE_Refactorability/Dominium_Modularity_AIDE_Refactorability_Architecture__06_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0146 | docs/archive/conversations/Modularity_AIDE_Refactorability/Dominium_Modularity_AIDE_Refactorability_Architecture__07_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0147 | docs/archive/conversations/Modularity_AIDE_Refactorability/Dominium_Modularity_AIDE_Refactorability_Architecture__08_future_chat_bootstrap_prompt.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0148 | docs/archive/conversations/Modularity_AIDE_Refactorability/Dominium_Modularity_AIDE_Refactorability_Architecture__09_in_chat_reader.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0149 | docs/archive/conversations/Modularity_AIDE_Refactorability/Dominium_Modularity_AIDE_Refactorability_Architecture__10_accompanying_detailed_conversation_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0150 | docs/archive/conversations/Modularity_AIDE_Refactorability/Dominium_Modularity_AIDE_Refactorability_Architecture__11_complete_bundle_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0151 | docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__00_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0152 | docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__01_human_readable_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0153 | docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__02_context_transfer_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0154 | docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0155 | docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__05_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0156 | docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__06_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0157 | docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__07_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0158 | docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__08_future_chat_bootstrap_prompt.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0159 | docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__09_in_chat_reader.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0160 | docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__10_accompanying_detailed_summary_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0161 | docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__11_complete_bundle_verification_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0162 | docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__12_complete_companion_bundle_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0163 | docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__00_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0164 | docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__01_human_readable_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0165 | docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__02_context_transfer_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0166 | docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0167 | docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__05_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0168 | docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__06_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0169 | docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__07_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0170 | docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__08_future_chat_bootstrap_prompt.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0171 | docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__09_in_chat_reader.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0172 | docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__10_accompanying_detailed_summary_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0173 | docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__11_consolidated_bundle_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0174 | docs/archive/conversations/Refactor_Architecture/Dominium_Domino_Refactor_Architecture__01_full_chat_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0175 | docs/archive/conversations/Refactor_Architecture/Dominium_Domino_Refactor_Architecture__03_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0176 | docs/archive/conversations/Refactor_Architecture/Dominium_Domino_Refactor_Architecture__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0177 | docs/archive/conversations/Refactor_Architecture/Dominium_Domino_Refactor_Architecture__05_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0178 | docs/archive/conversations/Refactor_Architecture/Dominium_Domino_Refactor_Architecture__06_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0179 | docs/archive/conversations/Refactor_Architecture/Dominium_Domino_Refactor_Architecture__manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0180 | docs/archive/conversations/Refactor_Control_Plane/AIDE_XStack_Dominium_Refactor_Control_Plane__00_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0181 | docs/archive/conversations/Refactor_Control_Plane/AIDE_XStack_Dominium_Refactor_Control_Plane__01_human_readable_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0182 | docs/archive/conversations/Refactor_Control_Plane/AIDE_XStack_Dominium_Refactor_Control_Plane__02_context_transfer_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0183 | docs/archive/conversations/Refactor_Control_Plane/AIDE_XStack_Dominium_Refactor_Control_Plane__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0184 | docs/archive/conversations/Refactor_Control_Plane/AIDE_XStack_Dominium_Refactor_Control_Plane__05_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0185 | docs/archive/conversations/Refactor_Control_Plane/AIDE_XStack_Dominium_Refactor_Control_Plane__06_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0186 | docs/archive/conversations/Refactor_Control_Plane/AIDE_XStack_Dominium_Refactor_Control_Plane__07_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0187 | docs/archive/conversations/Refactor_Control_Plane/AIDE_XStack_Dominium_Refactor_Control_Plane__08_future_chat_bootstrap_prompt.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0188 | docs/archive/conversations/Refactor_Control_Plane/AIDE_XStack_Dominium_Refactor_Control_Plane__09_in_chat_reader.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0189 | docs/archive/conversations/Release_Identity_and_Versioning/Dominium_XStack_Release_Identity_and_Versioning__00_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0190 | docs/archive/conversations/Release_Identity_and_Versioning/Dominium_XStack_Release_Identity_and_Versioning__01_human_readable_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0191 | docs/archive/conversations/Release_Identity_and_Versioning/Dominium_XStack_Release_Identity_and_Versioning__02_context_transfer_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0192 | docs/archive/conversations/Release_Identity_and_Versioning/Dominium_XStack_Release_Identity_and_Versioning__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0193 | docs/archive/conversations/Release_Identity_and_Versioning/Dominium_XStack_Release_Identity_and_Versioning__05_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0194 | docs/archive/conversations/Release_Identity_and_Versioning/Dominium_XStack_Release_Identity_and_Versioning__06_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0195 | docs/archive/conversations/Release_Identity_and_Versioning/Dominium_XStack_Release_Identity_and_Versioning__07_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0196 | docs/archive/conversations/Release_Identity_and_Versioning/Dominium_XStack_Release_Identity_and_Versioning__08_future_chat_bootstrap_prompt.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0197 | docs/archive/conversations/Release_Identity_and_Versioning/Dominium_XStack_Release_Identity_and_Versioning__09_in_chat_reader.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0198 | docs/archive/conversations/Release_Identity_and_Versioning/Dominium_XStack_Release_Identity_and_Versioning__10_accompanying_detailed_human_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0199 | docs/archive/conversations/Release_Identity_and_Versioning/Dominium_XStack_Release_Identity_and_Versioning__11_bundle_manifest_and_verification.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0200 | docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__00_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0201 | docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__01_human_readable_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0202 | docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__02_context_transfer_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0203 | docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0204 | docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__05_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0205 | docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__06_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0206 | docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__07_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0207 | docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__08_future_chat_bootstrap_prompt.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0208 | docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__09_in_chat_reader.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0209 | docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__10_accompanying_detailed_summary_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0210 | docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__11_file_inventory_and_integrity_check.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0211 | docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__README_START_HERE.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0212 | docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__00_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0213 | docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__01_human_readable_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0214 | docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__02_context_transfer_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0215 | docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0216 | docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__05_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0217 | docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__06_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0218 | docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__07_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0219 | docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__08_future_chat_bootstrap_prompt.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0220 | docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__09_in_chat_reader.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0221 | docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__10_accompanying_human_readable_detailed_summary_and_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0222 | docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__11_package_verification_and_file_index.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0223 | docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__FULL_COMBINED_REPORT.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0224 | docs/archive/conversations/Universe_Explorer_Planning/Dominium_Universe_Explorer_Planning_Handoff__00_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0225 | docs/archive/conversations/Universe_Explorer_Planning/Dominium_Universe_Explorer_Planning_Handoff__01_human_readable_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0226 | docs/archive/conversations/Universe_Explorer_Planning/Dominium_Universe_Explorer_Planning_Handoff__02_context_transfer_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0227 | docs/archive/conversations/Universe_Explorer_Planning/Dominium_Universe_Explorer_Planning_Handoff__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0228 | docs/archive/conversations/Universe_Explorer_Planning/Dominium_Universe_Explorer_Planning_Handoff__05_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0229 | docs/archive/conversations/Universe_Explorer_Planning/Dominium_Universe_Explorer_Planning_Handoff__06_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0230 | docs/archive/conversations/Universe_Explorer_Planning/Dominium_Universe_Explorer_Planning_Handoff__07_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0231 | docs/archive/conversations/Universe_Explorer_Planning/Dominium_Universe_Explorer_Planning_Handoff__08_future_chat_bootstrap_prompt.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0232 | docs/archive/conversations/Universe_Explorer_Planning/Dominium_Universe_Explorer_Planning_Handoff__09_in_chat_reader.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0233 | docs/archive/conversations/Universe_Explorer_Planning/Dominium_Universe_Explorer_Planning_Handoff__10_accompanying_human_readable_detailed_summary.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0234 | docs/archive/conversations/Universe_Explorer_Planning/Dominium_Universe_Explorer_Planning_Handoff__11_final_bundle_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0235 | docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__00_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0236 | docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__01_human_readable_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0237 | docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__02_context_transfer_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0238 | docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0239 | docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__05_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0240 | docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__06_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0241 | docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__07_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0242 | docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__08_future_chat_bootstrap_prompt.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0243 | docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__09_in_chat_reader.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0244 | docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__10_accompanying_detailed_summary.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0245 | docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__11_refreshed_manifest_20260527.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0246 | docs/archive/conversations/World_Architecture/Dominium_World_Architecture__01_full_chat_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0247 | docs/archive/conversations/World_Architecture/Dominium_World_Architecture__03_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0248 | docs/archive/conversations/World_Architecture/Dominium_World_Architecture__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0249 | docs/archive/conversations/World_Architecture/Dominium_World_Architecture__05_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0250 | docs/archive/conversations/World_Architecture/Dominium_World_Architecture__06_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0251 | docs/archive/conversations/World_Architecture/Dominium_World_Architecture__manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0252 | docs/archive/conversations/_book/appendices/A_source_corpus_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0253 | docs/archive/conversations/_book/appendices/B_full_claim_review_matrix.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0254 | docs/archive/conversations/_book/appendices/C_full_promotion_register.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0255 | docs/archive/conversations/_book/appendices/D_full_contradiction_register.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0256 | docs/archive/conversations/_book/appendices/E_path_and_source_index.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0257 | docs/archive/conversations/_book/build/pandoc_prerequisites.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0258 | docs/archive/conversations/_book/chapters/01_orientation.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0259 | docs/archive/conversations/_book/chapters/02_project_synthesis.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0260 | docs/archive/conversations/_book/chapters/03_authority_and_reconciliation.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0261 | docs/archive/conversations/_book/chapters/04_decision_docket.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0262 | docs/archive/conversations/_book/chapters/05_promotion_review.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0263 | docs/archive/conversations/_book/chapters/06_contradictions_staleness_verification.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0264 | docs/archive/conversations/_book/chapters/07_wiki_navigation_digest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0265 | docs/archive/conversations/_book/chapters/08_conversation_reader_digest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0266 | docs/archive/conversations/advanced_simulation_infrastructure/dominium_advanced_simulation_infrastructure_architecture__01_full_chat_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0267 | docs/archive/conversations/advanced_simulation_infrastructure/dominium_advanced_simulation_infrastructure_architecture__03_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0268 | docs/archive/conversations/advanced_simulation_infrastructure/dominium_advanced_simulation_infrastructure_architecture__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0269 | docs/archive/conversations/advanced_simulation_infrastructure/dominium_advanced_simulation_infrastructure_architecture__05_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0270 | docs/archive/conversations/advanced_simulation_infrastructure/dominium_advanced_simulation_infrastructure_architecture__06_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0271 | docs/archive/conversations/advanced_simulation_infrastructure/dominium_advanced_simulation_infrastructure_architecture__manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0272 | docs/archive/conversations/app_runtime_platform_renderers/dominium_app0_runtime_platform_renderers__01_full_chat_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0273 | docs/archive/conversations/app_runtime_platform_renderers/dominium_app0_runtime_platform_renderers__03_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0274 | docs/archive/conversations/app_runtime_platform_renderers/dominium_app0_runtime_platform_renderers__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0275 | docs/archive/conversations/app_runtime_platform_renderers/dominium_app0_runtime_platform_renderers__05_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0276 | docs/archive/conversations/app_runtime_platform_renderers/dominium_app0_runtime_platform_renderers__06_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0277 | docs/archive/conversations/app_runtime_platform_renderers/dominium_app0_runtime_platform_renderers__manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0278 | docs/archive/conversations/app_testx_codehygiene/dominium_app_testx_codehygiene_handoff__01_full_chat_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0279 | docs/archive/conversations/app_testx_codehygiene/dominium_app_testx_codehygiene_handoff__03_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0280 | docs/archive/conversations/app_testx_codehygiene/dominium_app_testx_codehygiene_handoff__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0281 | docs/archive/conversations/app_testx_codehygiene/dominium_app_testx_codehygiene_handoff__05_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0282 | docs/archive/conversations/app_testx_codehygiene/dominium_app_testx_codehygiene_handoff__06_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0283 | docs/archive/conversations/app_testx_codehygiene/dominium_app_testx_codehygiene_handoff__manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0284 | docs/archive/conversations/architecture_codex_prompts/dominium_domino_architecture_codex_prompts__01_full_chat_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0285 | docs/archive/conversations/architecture_codex_prompts/dominium_domino_architecture_codex_prompts__03_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0286 | docs/archive/conversations/architecture_codex_prompts/dominium_domino_architecture_codex_prompts__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0287 | docs/archive/conversations/architecture_codex_prompts/dominium_domino_architecture_codex_prompts__05_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0288 | docs/archive/conversations/architecture_codex_prompts/dominium_domino_architecture_codex_prompts__06_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0289 | docs/archive/conversations/architecture_codex_prompts/dominium_domino_architecture_codex_prompts__manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0290 | docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__00_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0291 | docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0292 | docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__02_context_transfer_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0293 | docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0294 | docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__05_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0295 | docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__06_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0296 | docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__07_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0297 | docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__08_future_chat_bootstrap_prompt.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0298 | docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__09_in_chat_reader.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0299 | docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__10_accompanying_human_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0300 | docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__11_bundle_index_and_checksums.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0301 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_architecture_repo_foundation__00_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0302 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_architecture_repo_foundation__01_human_readable_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0303 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_architecture_repo_foundation__02_context_transfer_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0304 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_architecture_repo_foundation__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0305 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_architecture_repo_foundation__05_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0306 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_architecture_repo_foundation__06_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0307 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_architecture_repo_foundation__07_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0308 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_architecture_repo_foundation__08_future_chat_bootstrap_prompt.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0309 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_architecture_repo_foundation__09_in_chat_reader.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0310 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_architecture_repo_foundation__FULL_COMPLETE_REPORT.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0311 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_handoff.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0312 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_structure_and_framework__00_manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0313 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_structure_and_framework__01_human_readable_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0314 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_structure_and_framework__02_context_transfer_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0315 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_structure_and_framework__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0316 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_structure_and_framework__05_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0317 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_structure_and_framework__06_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0318 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_structure_and_framework__07_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0319 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_structure_and_framework__08_future_chat_bootstrap_prompt.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0320 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_structure_and_framework__09_in_chat_reader.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0321 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_structure_and_framework__10_accompanying_detailed_summary.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0322 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_structure_and_framework__10_accompanying_detailed_summary_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0323 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_structure_and_framework__11_bundle_readme.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0324 | docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_structure_and_framework__13_bundle_verification.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0325 | docs/archive/conversations/development_routes/dominium_development_routes__01_full_chat_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0326 | docs/archive/conversations/development_routes/dominium_development_routes__03_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0327 | docs/archive/conversations/development_routes/dominium_development_routes__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0328 | docs/archive/conversations/development_routes/dominium_development_routes__05_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0329 | docs/archive/conversations/development_routes/dominium_development_routes__06_verification_and_audit.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0330 | docs/archive/conversations/development_routes/dominium_development_routes__manifest.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0331 | docs/archive/conversations/documentation_standards_readme/documentation_standards_readme_handoff__01_full_chat_report.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0332 | docs/archive/conversations/documentation_standards_readme/documentation_standards_readme_handoff__03_aggregator_packet.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0333 | docs/archive/conversations/documentation_standards_readme/documentation_standards_readme_handoff__04_registers.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0334 | docs/archive/conversations/documentation_standards_readme/documentation_standards_readme_handoff__05_reader_brief.md | docs_hygiene_candidate | Add or review status/header metadata in a later allowed docs-only task. | not_promoted |
| DOC-PROMOTE-0335 | docs/archive/conversations/documentation_standards_readme/documentation

[Truncated in Omnibus source for renderability. See source path for full text.]


## Source: `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md`

Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/`
Conversation Corpus Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

### Docs Decision Docket

Decision items are review prompts. The default disposition is defer unless a later explicit task opens the scope.

| Decision ID | Source/Finding | Question | Decision Type | Risk | Recommended Default |
| --- | --- | --- | --- | --- | --- |
| DOC-DECIDE-0001 | DOC-CONTRA-0001 | Should this archive artifact remain historical or be superseded by a current doc cross-reference? | repo_authority_decision | medium | defer_until_targeted_review |
| DOC-DECIDE-0002 | DOC-CONTRA-0002 | Should this archive artifact remain historical or be superseded by a current doc cross-reference? | repo_authority_decision | medium | defer_until_targeted_review |
| DOC-DECIDE-0003 | DOC-CONTRA-0003 | Should this archive artifact remain historical or be superseded by a current doc cross-reference? | repo_authority_decision | medium | defer_until_targeted_review |
| DOC-DECIDE-0004 | DOC-CONTRA-0004 | Should this archive artifact remain historical or be superseded by a current doc cross-reference? | repo_authority_decision | medium | defer_until_targeted_review |
| DOC-DECIDE-0005 | DOC-CONTRA-0005 | Should this archive artifact remain historical or be superseded by a current doc cross-reference? | repo_authority_decision | medium | defer_until_targeted_review |
| DOC-DECIDE-0006 | DOC-CONTRA-0006 | Should this archive artifact remain historical or be superseded by a current doc cross-reference? | repo_authority_decision | medium | defer_until_targeted_review |
| DOC-DECIDE-0007 | DOC-CONTRA-0007 | Should this archive artifact remain historical or be superseded by a current doc cross-reference? | repo_authority_decision | medium | defer_until_targeted_review |
| DOC-DECIDE-0008 | DOC-CONTRA-0008 | Should this archive artifact remain historical or be superseded by a current doc cross-reference? | repo_authority_decision | medium | defer_until_targeted_review |
| DOC-DECIDE-0009 | DOC-CONTRA-0009 | Should this archive artifact remain historical or be superseded by a current doc cross-reference? | repo_authority_decision | medium | defer_until_targeted_review |
| DOC-DECIDE-0010 | DOC-CONTRA-0010 | Should this archive artifact remain historical or be superseded by a current doc cross-reference? | repo_authority_decision | medium | defer_until_targeted_review |
| DOC-DECIDE-0011 | DOC-CONTRA-0011 | Should this archive artifact remain historical or be superseded by a current doc cross-reference? | repo_authority_decision | medium | defer_until_targeted_review |
| DOC-DECIDE-0012 | DOC-CONTRA-0012 | Should this archive artifact remain historical or be superseded by a current doc cross-reference? | repo_authority_decision | medium | defer_until_targeted_review |
| DOC-DECIDE-0013 | DOC-CONTRA-0013 | Should this archive artifact remain historical or be superseded by a current doc cross-reference? | repo_authority_decision | medium | defer_until_targeted_review |
| DOC-DECIDE-0014 | DOC-CONTRA-0014 | Should this archive artifact remain historical or be superseded by a current doc cross-reference? | repo_authority_decision | medium | defer_until_targeted_review |
| DOC-DECIDE-0015 | DOC-CONTRA-0015 | Should this archive artifact remain historical or be superseded by a current doc cross-reference? | repo_authority_decision | medium | defer_until_targeted_review |
| DOC-DECIDE-0016 | DOC-CONTRA-0016 | Does the archive version contain useful historical context that should be summarized elsewhere? | future_docs_hygiene_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0017 | DOC-CONTRA-0017 | Does the archive version contain useful historical context that should be summarized elsewhere? | future_docs_hygiene_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0018 | DOC-CONTRA-0018 | Does the archive version contain useful historical context that should be summarized elsewhere? | future_docs_hygiene_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0019 | DOC-CONTRA-0019 | Does the archive version contain useful historical context that should be summarized elsewhere? | future_docs_hygiene_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0020 | DOC-CONTRA-0020 | Does the archive version contain useful historical context that should be summarized elsewhere? | future_docs_hygiene_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0021 | DOC-CONTRA-0021 | Does the archive version contain useful historical context that should be summarized elsewhere? | future_docs_hygiene_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0022 | DOC-CONTRA-0022 | Does the archive version contain useful historical context that should be summarized elsewhere? | future_docs_hygiene_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0023 | DOC-CONTRA-0023 | Does the archive version contain useful historical context that should be summarized elsewhere? | future_docs_hygiene_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0024 | DOC-CONTRA-0024 | Does the archive version contain useful historical context that should be summarized elsewhere? | future_docs_hygiene_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0025 | DOC-CONTRA-0025 | Does the archive version contain useful historical context that should be summarized elsewhere? | future_docs_hygiene_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0026 | DOC-CONTRA-0026 | Does the archive version contain useful historical context that should be summarized elsewhere? | future_docs_hygiene_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0027 | DOC-CONTRA-0027 | Does the archive version contain useful historical context that should be summarized elsewhere? | future_docs_hygiene_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0028 | DOC-CONTRA-0028 | Does the archive version contain useful historical context that should be summarized elsewhere? | future_docs_hygiene_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0029 | DOC-CONTRA-0029 | Does the archive version contain useful historical context that should be summarized elsewhere? | future_docs_hygiene_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0030 | DOC-CONTRA-0030 | Does the archive version contain useful historical context that should be summarized elsewhere? | future_docs_hygiene_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0031 | DOC-CONTRA-0031 | Does the archive version contain useful historical context that should be summarized elsewhere? | future_docs_hygiene_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0032 | DOC-CONTRA-0032 | Does the archive version contain useful historical context that should be summarized elsewhere? | future_docs_hygiene_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0033 | DOC-CONTRA-0033 | Does the archive version contain useful historical context that should be summarized elsewhere? | future_docs_hygiene_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0034 | DOC-CONTRA-0034 | Does the archive version contain useful historical context that should be summarized elsewhere? | future_docs_hygiene_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0035 | DOC-CONTRA-0035 | Does the archive version contain useful historical context that should be summarized elsewhere? | future_docs_hygiene_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0036 | DOC-CONTRA-0036 | Does the archive version contain useful historical context that should be summarized elsewhere? | future_docs_hygiene_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0037 | DOC-CONTRA-0037 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0038 | DOC-CONTRA-0038 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0039 | DOC-CONTRA-0039 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0040 | DOC-CONTRA-0040 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0041 | DOC-CONTRA-0041 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0042 | DOC-CONTRA-0042 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0043 | DOC-CONTRA-0043 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0044 | DOC-CONTRA-0044 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0045 | DOC-CONTRA-0045 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0046 | DOC-CONTRA-0046 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0047 | DOC-CONTRA-0047 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0048 | DOC-CONTRA-0048 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0049 | DOC-CONTRA-0049 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0050 | DOC-CONTRA-0050 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0051 | DOC-CONTRA-0051 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0052 | DOC-CONTRA-0052 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0053 | DOC-CONTRA-0053 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0054 | DOC-CONTRA-0054 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0055 | DOC-CONTRA-0055 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0056 | DOC-CONTRA-0056 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0057 | DOC-CONTRA-0057 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0058 | DOC-CONTRA-0058 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0059 | DOC-CONTRA-0059 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0060 | DOC-CONTRA-0060 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0061 | DOC-CONTRA-0061 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0062 | DOC-CONTRA-0062 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0063 | DOC-CONTRA-0063 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0064 | DOC-CONTRA-0064 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0065 | DOC-CONTRA-0065 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0066 | DOC-CONTRA-0066 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0067 | DOC-CONTRA-0067 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0068 | DOC-CONTRA-0068 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0069 | DOC-CONTRA-0069 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0070 | DOC-CONTRA-0070 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0071 | DOC-CONTRA-0071 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0072 | DOC-CONTRA-0072 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0073 | DOC-CONTRA-0073 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0074 | DOC-CONTRA-0074 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0075 | DOC-CONTRA-0075 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0076 | DOC-CONTRA-0076 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0077 | DOC-CONTRA-0077 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0078 | DOC-CONTRA-0078 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0079 | DOC-CONTRA-0079 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-0080 | DOC-CONTRA-0080 | Should this doc get an explicit authority/status header in a later docs-only promotion wave? | repo_authority_decision | low | defer_until_targeted_review |
| DOC-DECIDE-BLOCK-0001 | queue | Should broad Workbench UI remain closed until a later queue phase explicitly opens it? | future_queue_decision | high | defer |
| DOC-DECIDE-BLOCK-0002 | queue | Should renderer implementation remain blocked? | future_queue_decision | high | defer |
| DOC-DECIDE-BLOCK-0003 | queue | Should provider/package runtime work remain blocked? | future_queue_decision | high | defer |
| DOC-DECIDE-BLOCK-0004 | queue | Should release publication remain blocked? | future_queue_decision | high | defer |


## Source: `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md`

Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/`
Conversation Corpus Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

### Docs Blocked Scope Alignment

The current queue blocks these broad work areas. Docs-corpus outputs record them for navigation only.

| Blocked Scope | Authority Source | Matching Docs Paths | Examples | Disposition |
| --- | --- | --- | --- | --- |
| broad_workbench_ui | .aide/queue/current.toml | 1 | docs/development/workbench_module_guidelines.md | blocked_by_current_queue |
| runtime_module_loader | .aide/queue/current.toml | 0 |  | blocked_by_current_queue |
| provider_runtime | .aide/queue/current.toml | 52 | docs/architecture/TERRAIN_PROVIDER_CHAIN.md; docs/architecture/provider_conformance_law.md; docs/architecture/provider_model.md; docs/architecture/provider_selection_model.md; docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__00_manifest.md; docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__01_human_readable_report.md; docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__02_context_transfer_packet.md; docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__03_spec_sheet.yaml | blocked_by_current_queue |
| package_runtime | .aide/queue/current.toml | 0 |  | blocked_by_current_queue |
| gameplay | .aide/queue/current.toml | 11 | docs/archive/audit/MVP_GAMEPLAY0_RETRO_AUDIT.md; docs/archive/audit/MVP_GAMEPLAY_BASELINE.md; docs/archive/audit/MVP_GAMEPLAY_LOOP_RUN.md; docs/archive/audit/MVP_GAMEPLAY_VERIFY.md; docs/game/gameplay/CONSTRUCTION_MODEL.md; docs/game/gameplay/FAILURE_AND_MAINTENANCE.md; docs/game/gameplay/ITERATION_MODEL.md; docs/game/gameplay/NETWORKS.md | blocked_by_current_queue |
| renderer_implementation | .aide/queue/current.toml | 27 | docs/apps/CLIENT_RENDERER_UI.md; docs/architecture/RENDERER_RESPONSIBILITY.md; docs/archive/audit/PLATFORM_RENDERER_BACKENDS_BASELINE.md; docs/archive/audit/PLATFORM_RENDERER_MATRIX.md; docs/archive/audit/PLATFORM_RENDERER_SURFACE.md; docs/archive/audit/RENDERER_BASELINE_REPORT.md; docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md; docs/archive/conversations/_reader/by_chat/platform_renderer_api_plan.md | blocked_by_current_queue |
| native_gui | .aide/queue/current.toml | 0 |  | blocked_by_current_queue |
| release_publication | .aide/queue/current.toml | 2 | docs/release/PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES.md; docs/release/PUBLICATION_TRUST_AND_LICENSING_GATES.md | blocked_by_current_queue |
