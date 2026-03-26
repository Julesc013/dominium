Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.b7e18a17197c09e7`

- Symbol: `_semver_tuple`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/governance/tool_migration_report.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/compat/capability_negotiation.py`
- `src/compat/migration_lifecycle.py`
- `src/lib/install/install_validator.py`
- `tools/governance/tool_migration_report.py`

## Scorecard

- `tools/governance/tool_migration_report.py` disposition=`canonical` rank=`1` total_score=`68.51` risk=`HIGH`
- `src/compat/migration_lifecycle.py` disposition=`quarantine` rank=`2` total_score=`61.18` risk=`HIGH`
- `src/compat/capability_negotiation.py` disposition=`quarantine` rank=`3` total_score=`59.29` risk=`HIGH`
- `src/lib/install/install_validator.py` disposition=`merge` rank=`4` total_score=`49.06` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/ci/HYGIENE_QUEUE.md, docs/governance/GOVERNANCE_MODEL.md, docs/release/PROVISIONAL_FEATURE_LIST.md, docs/scale/DOMAIN_REGISTRY.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
