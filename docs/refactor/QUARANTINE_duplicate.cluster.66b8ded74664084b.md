Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.66b8ded74664084b`

- Symbol: `sha256_file`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/lib/content_store.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/lib/bundle/bundle_manifest.py`
- `tools/bugreport/bugreport_cli.py`
- `tools/lib/content_store.py`
- `tools/share/share_cli.py`

## Scorecard

- `tools/lib/content_store.py` disposition=`canonical` rank=`1` total_score=`81.31` risk=`HIGH`
- `src/lib/bundle/bundle_manifest.py` disposition=`quarantine` rank=`2` total_score=`74.94` risk=`HIGH`
- `tools/share/share_cli.py` disposition=`merge` rank=`3` total_score=`52.38` risk=`HIGH`
- `tools/bugreport/bugreport_cli.py` disposition=`merge` rank=`4` total_score=`37.86` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/EXPORT_IMPORT_BASELINE.md, docs/audit/RELEASE0_RETRO_AUDIT.md, docs/lib/EXPORT_IMPORT_FORMAT.md`

## Tests Involved

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
