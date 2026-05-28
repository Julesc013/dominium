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

# Docs Repo Truth Crosswalk

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
