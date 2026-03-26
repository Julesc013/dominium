Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.4d1320195335c0f3`

- Symbol: `canonical_sha256`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/lib/content_store.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/lib/bundle/bundle_manifest.py`
- `tools/lib/content_store.py`

## Scorecard

- `tools/lib/content_store.py` disposition=`canonical` rank=`1` total_score=`81.31` risk=`HIGH`
- `src/lib/bundle/bundle_manifest.py` disposition=`quarantine` rank=`2` total_score=`74.94` risk=`HIGH`

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

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
