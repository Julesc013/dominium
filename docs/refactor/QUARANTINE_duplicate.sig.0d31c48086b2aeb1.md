Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.0d31c48086b2aeb1`

- Symbol: `_as_int`
- Cluster Kind: `exact`
- Cluster Resolution: `merge`
- Risk Level: `LOW`
- Canonical Candidate: `tools/xstack/registry_compile/compiler.py`
- Quarantine Reasons: `file_scope_ambiguity, phase_boundary_deferred, requires_medium_risk_batch_gate, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate`

## Competing Files

- `src/logic/eval/degradation_policy.py`
- `src/logic/signal/carrier_adapters.py`
- `src/logic/signal/observation.py`
- `src/logic/signal/signal_store.py`
- `tools/release/arch_matrix_common.py`
- `tools/xstack/registry_compile/compiler.py`

## Scorecard

- `tools/xstack/registry_compile/compiler.py` disposition=`canonical` rank=`1` total_score=`84.64` risk=`LOW`
- `tools/release/arch_matrix_common.py` disposition=`drop` rank=`2` total_score=`75.24` risk=`LOW`
- `src/logic/signal/signal_store.py` disposition=`merge` rank=`3` total_score=`67.74` risk=`HIGH`
- `src/logic/eval/degradation_policy.py` disposition=`drop` rank=`4` total_score=`61.96` risk=`MED`
- `src/logic/signal/observation.py` disposition=`drop` rank=`5` total_score=`60.95` risk=`MED`
- `src/logic/signal/carrier_adapters.py` disposition=`drop` rank=`6` total_score=`46.15` risk=`MED`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/auditx/FINDINGS.md, docs/ci/CI_ENFORCEMENT_MATRIX.md, docs/governance/REPOX_RULESETS.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile FAST`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
