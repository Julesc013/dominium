# Worktree Leftovers Allowlist

Purpose: when running local governance scans on a non-clean worktree, every
intentional leftover path must be documented here with a brief reason.

RepoX rule: `INV-WORKTREE-HYGIENE`

Format (one entry per line):
- `relative/path.ext`: short reason
- `relative/path.ext`|short reason

Current entries:
- `docs/audit/auditx/FINDINGS.json`: pre-existing local AuditX run artifact (kept uncommitted for iterative governance scans)
- `docs/audit/auditx/FINDINGS.md`: pre-existing local AuditX run artifact (kept uncommitted for iterative governance scans)
- `docs/audit/auditx/INVARIANT_MAP.json`: pre-existing local AuditX run artifact (kept uncommitted for iterative governance scans)
- `docs/audit/auditx/PROMOTION_CANDIDATES.json`: pre-existing local AuditX run artifact (kept uncommitted for iterative governance scans)
- `docs/audit/auditx/RUN_META.json`: pre-existing local AuditX run artifact (kept uncommitted for iterative governance scans)
- `docs/audit/auditx/SUMMARY.md`: pre-existing local AuditX run artifact (kept uncommitted for iterative governance scans)
- `docs/audit/auditx/TRENDS.json`: pre-existing local AuditX run artifact (kept uncommitted for iterative governance scans)
- `data/regression/sys_full_baseline.json`: pre-existing local regression baseline edits pending dedicated tagged update
- `schema/meta/coupling_contract.schema`: pre-existing local schema edit under active coupling review
- `data/registries/coupling_budget_registry.json`: pre-existing COUPLE-0 registry artifact pending finalize
- `data/registries/coupling_relevance_policy_registry.json`: pre-existing COUPLE-0 registry artifact pending finalize
- `docs/audit/COMPILED_MODEL_BASELINE.md`: pre-existing COMPILE-0 audit draft pending finalize
- `schema/meta/coupling_budget.schema`: pre-existing COUPLE-0 schema artifact pending finalize
- `schema/meta/coupling_evaluation_record.schema`: pre-existing COUPLE-0 schema artifact pending finalize
- `schema/meta/coupling_relevance_policy.schema`: pre-existing COUPLE-0 schema artifact pending finalize
- `data/meta/real_world_affordance_matrix.json`: GR3 FAST stabilization edit pending phase commit
- `src/process/software/pipeline_engine.py`: GR3 FAST analyzer-hygiene refactor pending phase commit
- `src/system/macro/macro_capsule_engine.py`: GR3 FAST analyzer-hygiene refactor pending phase commit
- `src/system/reliability/reliability_engine.py`: GR3 FAST analyzer-hygiene refactor pending phase commit
- `tools/xstack/sessionx/process_runtime.py`: GR3 FAST token/refusal metadata update pending phase commit
- `data/registries/action_template_registry.json`: GR3 STRICT action-family coverage fix for reverse-engineering task templates
- `tools/xstack/sessionx/process_runtime.py`: GR3 STRICT field identifier false-positive fix (`field.get` token removal)
- `docs/impact/GR3_STRICT.md`: GR3 STRICT demand linkage note pending phase commit
- `docs/impact/GR3_FAST.md`: GR3 demand linkage note pending phase commit
- `docs/audit/GR3_FAST_REFERENCE_SUITE.json`: GR3 FAST reference suite result artifact pending phase commit
- `docs/audit/GR3_FAST_COMPACTION_SANITY.json`: GR3 FAST compaction stress sanity artifact pending phase commit
- `docs/audit/GR3_FAST_COMPACTION_STATE.json`: GR3 FAST replay-from-anchor state artifact pending phase commit
- `docs/audit/GR3_FULL_SYS_SCENARIO.json`: GR3 FULL SYS stress scenario seed artifact pending phase commit
- `docs/audit/GR3_FULL_SYS_SCENARIO_RUN.json`: GR3 FULL SYS scenario runtime snapshot artifact pending phase commit
- `docs/audit/GR3_FULL_SYS_STRESS.json`: GR3 FULL SYS stress harness result artifact pending phase commit
- `docs/audit/GR3_FULL_PROC_SCENARIO.json`: GR3 FULL PROC stress scenario seed artifact pending phase commit
- `docs/audit/GR3_FULL_PROC_STATE.json`: GR3 FULL PROC scenario state snapshot artifact pending phase commit
- `docs/audit/GR3_FULL_PROC_STRESS.json`: GR3 FULL PROC stress harness result artifact pending phase commit
- `docs/audit/GR3_FULL_POLL_SCENARIO.json`: GR3 FULL POLL stress scenario seed artifact pending phase commit
- `docs/audit/GR3_FULL_POLL_STRESS.json`: GR3 FULL POLL stress harness result artifact pending phase commit
- `docs/audit/GR3_FULL_SIG_SCENARIO.json`: GR3 FULL SIG stress scenario seed artifact pending phase commit
- `docs/audit/GR3_FULL_SIG_SCENARIO_RUN.json`: GR3 FULL SIG scenario runtime snapshot artifact pending phase commit
- `docs/audit/GR3_FULL_SIG_STRESS.json`: GR3 FULL SIG stress harness result artifact pending phase commit
- `docs/audit/GR3_FULL_ELEC_SCENARIO.json`: GR3 FULL ELEC stress scenario seed artifact pending phase commit
- `docs/audit/GR3_FULL_ELEC_STRESS.json`: GR3 FULL ELEC stress harness result artifact pending phase commit
- `docs/audit/GR3_FULL_FLUID_SCENARIO.json`: GR3 FULL FLUID stress scenario seed artifact pending phase commit
- `docs/audit/GR3_FULL_THERM_SCENARIO.json`: GR3 FULL THERM stress scenario seed artifact pending phase commit
- `docs/audit/GR3_FULL_CHEM_SCENARIO.json`: GR3 FULL CHEM stress scenario seed artifact pending phase commit
- `src/meta/__init__.py`: GR3 STRICT import-cycle hardening (lazy reference evaluator exports) pending phase commit
- `tools/xstack/testx/tests/test_hidden_state_violation_detected.py`: GR3 STRICT test fixture migrated to profile-based statevec guard activation
- `docs/audit/WORKTREE_LEFTOVERS.md`: this allowlist was updated during GR3 FAST stabilization and is pending phase commit
