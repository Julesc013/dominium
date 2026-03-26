Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.06f2c33736385885`

- Symbol: `_write_canonical_json`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/worldgen/worldgen_lock_common.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/mvp/baseline_universe_common.py`
- `tools/mvp/ecosystem_verify_common.py`
- `tools/mvp/gameplay_loop_common.py`
- `tools/mvp/update_sim_common.py`
- `tools/release/offline_archive_common.py`
- `tools/security/trust_strict_common.py`
- `tools/worldgen/worldgen_lock_common.py`

## Scorecard

- `tools/worldgen/worldgen_lock_common.py` disposition=`canonical` rank=`1` total_score=`85.24` risk=`HIGH`
- `tools/mvp/baseline_universe_common.py` disposition=`quarantine` rank=`2` total_score=`84.64` risk=`HIGH`
- `tools/mvp/ecosystem_verify_common.py` disposition=`quarantine` rank=`3` total_score=`84.11` risk=`HIGH`
- `tools/release/offline_archive_common.py` disposition=`quarantine` rank=`4` total_score=`83.04` risk=`HIGH`
- `tools/mvp/gameplay_loop_common.py` disposition=`quarantine` rank=`5` total_score=`82.26` risk=`HIGH`
- `tools/security/trust_strict_common.py` disposition=`quarantine` rank=`6` total_score=`77.8` risk=`HIGH`
- `tools/mvp/update_sim_common.py` disposition=`merge` rank=`7` total_score=`70.14` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/ARCHITECTURE.md, docs/STATUS_NOW.md, docs/appshell/CLI_REFERENCE.md, docs/appshell/TOOL_REFERENCE.md, docs/architecture/CANON_INDEX.md, docs/architecture/REPO_INTENT.md, docs/architecture/lockfile.md, docs/architecture/registry_compile.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/security/tool_run_trust_strict_suite.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
