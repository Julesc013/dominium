Status: CANONICAL
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none

# XStack Template Checklist

Use this checklist when bootstrapping XStack in another repository.

## Registry Checklist

- [ ] `data/registries/gate_policy.json`
- [ ] `data/registries/testx_groups.json`
- [ ] `data/registries/auditx_groups.json`
- [ ] `data/registries/xstack_components.json`
- [ ] `data/registries/derived_artifacts.json`

## Schema Checklist

- [ ] `schema/governance/derived_artifact_contract.schema`
- [ ] `schema/governance/xstack_components.schema`

## Core Module Checklist

- [ ] `tools/xstack/core/impact_graph.py`
- [ ] `tools/xstack/core/merkle_tree.py`
- [ ] `tools/xstack/core/cache_store.py`
- [ ] `tools/xstack/core/plan.py`
- [ ] `tools/xstack/core/scheduler.py`
- [ ] `tools/xstack/core/runners_base.py`
- [ ] `tools/xstack/core/runners.py`

## Gate Wiring Checklist

- [ ] `scripts/dev/gate.py` calls planner + scheduler
- [ ] FAST defaults to impacted minimal checks
- [ ] STRICT supports light/deep split
- [ ] FULL supports sharded execution
- [ ] FULL_ALL is explicit opt-in

## Determinism Checklist

- [ ] Merkle roots are deterministic
- [ ] Planner output is deterministic
- [ ] Result aggregation is deterministic
- [ ] RUN_META artifacts are excluded from canonical determinism checks

## Track/Ignore Checklist

- [ ] `verify|strict|full|doctor` do not modify tracked files
- [ ] `snapshot` is the only command allowed to write `SNAPSHOT_ONLY` artifacts
- [ ] `.xstack_cache/` and workspace temp roots are ignored by VCS
- [ ] `docs/governance/XSTACK_TRACK_IGNORE_POLICY.md` exists and is current

## Governance Checklist

- [ ] RepoX ruleset references all enforced invariants
- [ ] TestX group mappings are validated
- [ ] AuditX outputs are present and shape-validated
- [ ] artifact contract includes canonical/derived/run-meta classification

## Removability Checklist

- [ ] Runtime trees (`engine/game/client/server`) contain no `tools/xstack` imports/includes
- [ ] Runtime CMake roots contain no `tools/xstack` references
- [ ] RepoX includes `INV-RUNTIME-NO-XSTACK-IMPORTS`
- [ ] TestX includes `test_xstack_removal_builds_runtime`
