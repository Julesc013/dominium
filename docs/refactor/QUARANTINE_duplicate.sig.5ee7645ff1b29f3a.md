Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.5ee7645ff1b29f3a`

- Symbol: `_server_profile_row`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/net/policies/policy_server_authoritative.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/net/policies/policy_server_authoritative.py`
- `src/net/srz/shard_coordinator.py`
- `src/server/server_boot.py`

## Scorecard

- `src/net/policies/policy_server_authoritative.py` disposition=`canonical` rank=`1` total_score=`66.07` risk=`HIGH`
- `src/server/server_boot.py` disposition=`quarantine` rank=`2` total_score=`64.46` risk=`HIGH`
- `src/net/srz/shard_coordinator.py` disposition=`merge` rank=`3` total_score=`51.83` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/UI_MODE_RESOLUTION.md, docs/architecture/ARCH_REPO_LAYOUT.md, docs/architecture/CANON_INDEX.md, docs/architecture/CONTRACTS_INDEX.md, docs/architecture/DISTRIBUTED_TIME_MODEL.md, docs/architecture/REPO_NAV.md, docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md, docs/archive/ci/PHASE1_AUDIT_REPORT.md`

## Tests Involved

- `python tools/appshell/tool_run_supervisor_hardening.py --repo-root .`
- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
