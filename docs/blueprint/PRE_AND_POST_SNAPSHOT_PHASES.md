Status: DERIVED
Last Reviewed: 2026-03-31
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PI
Replacement Target: snapshot-anchored work split after final repository remapping

# Pre and Post Snapshot Phases

## Pre-snapshot-safe

These items can be designed and documented now because they are architecture-level and do not depend on exact file boundaries.

- `SIGMA.agent_context_contract` [SIGMA]: The agent context contract is a planning artifact and should be stabilized before code work.
- `SIGMA.declarative_cutover_language` [SIGMA]: Cutover grammar is safer to design before the repo-specific wiring begins.
- `SIGMA.governance_docs` [SIGMA]: Governance vocabulary, task catalogs, and operator policy are architecture-level and do not require exact insertion points.
- `SIGMA.operator_policy_model` [SIGMA]: Policy modeling is a doctrine problem first and should guide later implementation.
- `SIGMA.task_catalogs` [SIGMA]: Task types, validation levels, and refusal expectations can be designed before the fresh snapshot arrives.
- `PHI.component_model_doctrine` [PHI]: The component model should be decided as architecture doctrine before repository-specific implementation work.
- `PHI.runtime_kernel_doctrine` [PHI]: Kernel doctrine, service boundaries, and lawful state movement can be specified before code insertion points are re-mapped.
- `PHI.state_externalization_model` [PHI]: Export/import semantics and lifecycle doctrine are design artifacts first.
- `UPSILON.rollback_and_downgrade_policy` [UPSILON]: Rollback and downgrade policy should lead implementation rather than follow it.
- `UPSILON.versioning_release_policy_docs` [UPSILON]: Versioning and release policy can be frozen ahead of repository-specific control-plane wiring.

## Post-snapshot-required

These items must wait for the fresh repository snapshot because they depend on exact module, file, build, or service insertion points.

- `XI.exact_file_and_module_move_plans` [XI]: Exact moves depend on the fresh repository snapshot and cannot be safely guessed from planning artifacts.
- `PHI.framegraph_integration_strategy` [PHI]: Render integration depends on actual runtime boundaries in the fresh snapshot.
- `PHI.module_loader_insertion_points` [PHI]: Loader insertion points must be mapped against the live codebase after convergence and freeze work.
- `UPSILON.build_graph_lock_mapping` [UPSILON]: The lock artifact must be generated from the current build graph, not an older audit snapshot.
- `UPSILON.ci_pipeline_consolidation_steps` [UPSILON]: Exact CI and pipeline steps depend on the current repo layout and tool inventory.
- `UPSILON.preset_cleanup_inventory` [UPSILON]: Preset cleanup is repository-state sensitive and must be derived from the live tree.
- `ZETA.authority_handoff_insertion_points` [ZETA]: Authority handoff cannot be planned as code without fresh runtime topology evidence.
- `ZETA.live_cutover_entrypoints` [ZETA]: Live cutovers require exact service boundaries and call sites from the live repo.
- `ZETA.replication_topology_mapping` [ZETA]: Replication topology depends on actual state partitions, services, and products.
- `ZETA.rollback_path_validation` [ZETA]: Rollback validation must be wired to the current release, replay, and trust surfaces.

