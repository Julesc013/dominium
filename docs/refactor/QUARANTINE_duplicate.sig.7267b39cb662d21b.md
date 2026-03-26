Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.7267b39cb662d21b`

- Symbol: `canonical_json_text`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/lib/content_store.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/lib/bundle/bundle_manifest.py`
- `src/platform/_canonical.py`
- `tools/lib/content_store.py`
- `tools/share/share_cli.py`

## Scorecard

- `tools/lib/content_store.py` disposition=`canonical` rank=`1` total_score=`86.07` risk=`HIGH`
- `src/platform/_canonical.py` disposition=`quarantine` rank=`2` total_score=`77.5` risk=`HIGH`
- `tools/share/share_cli.py` disposition=`merge` rank=`3` total_score=`60.71` risk=`HIGH`
- `src/lib/bundle/bundle_manifest.py` disposition=`merge` rank=`4` total_score=`46.76` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/VIRTUAL_PATHS.md, docs/architecture/ARTIFACT_MODEL.md, docs/architecture/BUNDLE_MODEL.md, docs/architecture/CANON_INDEX.md, docs/architecture/CONTENT_AND_STORAGE_MODEL.md, docs/architecture/INSTALL_MODEL.md, docs/architecture/INSTANCE_MODEL.md, docs/architecture/INVARIANT_REGISTRY.md`

## Tests Involved

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
