Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.0bcd68d8ef34595d`

- Symbol: `canonical_sha256`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/platform/_canonical.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/lib/bundle/__init__.py`
- `src/lib/bundle/bundle_manifest.py`
- `src/platform/_canonical.py`

## Scorecard

- `src/platform/_canonical.py` disposition=`canonical` rank=`1` total_score=`77.5` risk=`HIGH`
- `src/lib/bundle/__init__.py` disposition=`quarantine` rank=`2` total_score=`76.37` risk=`HIGH`
- `src/lib/bundle/bundle_manifest.py` disposition=`quarantine` rank=`3` total_score=`74.94` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/EXPORT_IMPORT_BASELINE.md, docs/audit/RELEASE0_RETRO_AUDIT.md, docs/distribution/PKG_MANIFEST.md, docs/guides/BUILD_DIST.md, docs/release/DIST_BUNDLE_ASSEMBLY.md, docs/release/RELEASE_IDENTITY_CONSTITUTION.md, docs/testing/xstack_profiles.md`

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
