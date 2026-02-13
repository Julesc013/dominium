Status: DERIVED
Last Reviewed: 2026-02-13
Supersedes: none
Superseded By: none

# XStack Governance Reference

XStack is the governance execution stack coordinating structural policy, behavioral proof, semantic audit, compatibility, security, and throughput-aware gate planning.

## Scope

XStack coordinates:

- planning and execution (`scripts/dev/gate.py`, `tools/xstack/core/`)
- static policy enforcement (RepoX)
- behavioral verification (TestX)
- semantic audit (AuditX)
- performance/profile monitoring (PerformX)
- compatibility migration checks (CompatX)
- security/trust verification (SecureX)

## Where XStack Lives

Primary implementation:

- `scripts/dev/gate.py`
- `tools/xstack/core/impact_graph.py`
- `tools/xstack/core/merkle_tree.py`
- `tools/xstack/core/cache_store.py`
- `tools/xstack/core/plan.py`
- `tools/xstack/core/scheduler.py`
- `tools/xstack/core/runners.py`
- `tools/xstack/core/time_estimator.py`
- `tools/xstack/core/profiler.py`
- `tools/xstack/core/log.py`

Data-driven routing:

- `data/registries/gate_policy.json`
- `data/registries/testx_groups.json`
- `data/registries/auditx_groups.json`
- `data/registries/xstack_components.json`
- `data/registries/derived_artifacts.json`

## Gate Execution Profiles

`scripts/dev/gate.py` supports:

- `verify` (FAST default)
- `strict` (STRICT)
- `full` (FULL)
- `dist` (FULL dist lane)

Example commands:

```bash
python scripts/dev/gate.py verify --repo-root . --trace
python scripts/dev/gate.py strict --repo-root . --profile-report
python scripts/dev/gate.py full --repo-root .
```

Profile policy is defined by `data/registries/gate_policy.json` and described in `docs/governance/GATE_THROUGHPUT_POLICY.md`.

## RepoX

RepoX enforces static invariants and repository law.

- rulesets: `repo/repox/rulesets/`
- runner entry: `scripts/ci/check_repox_rules.py`
- architecture docs: `docs/governance/REPOX_RULESETS.md`, `docs/governance/REPOX_TOOL_RULES.md`

RepoX is typically first in gate plans to fail early on structural violations.

## TestX

TestX provides behavioral and determinism proof.

- suite registry: `data/registries/testx_suites.json`
- group mapping: `data/registries/testx_groups.json`
- grouped runner helper: `scripts/dev/run_xstack_group_tests.py`
- docs: `docs/governance/TESTX_ARCHITECTURE.md`, `docs/governance/TESTX_PROOF_MODEL.md`

XStack maps changed paths to impacted TestX groups via `tools/xstack/core/impact_graph.py`.

## AuditX

AuditX provides semantic drift and smell detection.

- tool entry: `tools/auditx/auditx.py`
- analyzers: `tools/auditx/analyzers/`
- group mapping: `data/registries/auditx_groups.json`
- docs: `docs/governance/AUDITX_MODEL.md`

Artifacts are emitted under `docs/audit/auditx/`.

## ControlX

ControlX defines orchestration semantics and prompt/gate contracts for autonomous execution.

- docs: `docs/governance/CONTROLX_MODEL.md`
- implementation area: `tools/controlx/`

Gate and policy orchestration in this repository follows the same structural contract family.

## PerformX

PerformX tracks performance/budget evidence and regression signals.

- tool entry: `tools/performx/performx.py`
- docs: `docs/governance/PERFORMX_MODEL.md`
- artifacts: `docs/audit/performance/`

## CompatX

CompatX validates schema/data compatibility and migration pathways.

- tool entry: `tools/compatx/compatx.py`
- docs: `docs/governance/COMPATX_MODEL.md`
- artifacts: `docs/audit/compat/`

## SecureX

SecureX verifies pack integrity, trust policy, and security manifests.

- tool entry: `tools/securex/securex.py`
- tool docs: `tools/securex/README.md`
- policy data: `data/registries/trust_policy.json`, `data/registries/security_roles.json`
- artifacts: `docs/audit/security/`

## Incremental Planning Model

Execution planning follows a compiler-like pipeline:

1. determine changed paths
2. build impact graph
3. compute Merkle subtree roots
4. generate deterministic plan DAG
5. execute via scheduler with content-addressed cache

Reference: `docs/governance/XSTACK_INCREMENTAL_MODEL.md`.

## Example Output (Abbreviated)

```json
{
  "gate_command": "verify",
  "profile": "FAST",
  "plan_hash": "<hash>",
  "nodes": [
    {"runner_id": "repox_runner"},
    {"runner_id": "testx.group.core.invariants"},
    {"runner_id": "auditx.group.core.policy"}
  ]
}
```

## Related Docs

- Architecture summary: `docs/ARCHITECTURE.md`
- Survival baseline: `docs/SURVIVAL_SLICE.md`
- Canon contracts: `docs/architecture/CANON_INDEX.md`
