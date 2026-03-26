Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.49a57c6dc3693541`

- Symbol: `sha256_file`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/lib/install/__init__.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/lib/bundle/__init__.py`
- `src/lib/bundle/bundle_manifest.py`
- `src/lib/install/__init__.py`
- `src/lib/install/install_validator.py`

## Scorecard

- `src/lib/install/__init__.py` disposition=`canonical` rank=`1` total_score=`78.45` risk=`HIGH`
- `src/lib/bundle/__init__.py` disposition=`quarantine` rank=`2` total_score=`76.37` risk=`HIGH`
- `src/lib/bundle/bundle_manifest.py` disposition=`quarantine` rank=`3` total_score=`74.94` risk=`HIGH`
- `src/lib/install/install_validator.py` disposition=`merge` rank=`4` total_score=`51.13` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/EXPORT_IMPORT_BASELINE.md, docs/audit/RELEASE0_RETRO_AUDIT.md, docs/audit/auditx/FINDINGS.md, docs/guides/BUILD_DIST.md, docs/lib/EXPORT_IMPORT_FORMAT.md, docs/release/DIST_BUNDLE_ASSEMBLY.md, docs/release/OFFLINE_ARCHIVE_MODEL_v0_0_0.md, docs/specs/launcher/TESTING.md`

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
