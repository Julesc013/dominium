Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none

Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.e790d4f0d60c4da9`

- Symbol: `ARTIFACT_KIND_PROFILE_BUNDLE`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/tools/package/libraries/artifact/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/tools/validators/compatibility/migration_lifecycle.py`
- `src/tools/package/libraries/artifact/__init__.py`
- `src/tools/package/libraries/artifact/artifact_validator.py`

## Scorecard

- `src/tools/package/libraries/artifact/__init__.py` disposition=`canonical` rank=`1` total_score=`77.44` risk=`HIGH`
- `src/tools/package/libraries/artifact/artifact_validator.py` disposition=`quarantine` rank=`2` total_score=`69.82` risk=`HIGH`
- `src/tools/validators/compatibility/migration_lifecycle.py` disposition=`quarantine` rank=`3` total_score=`68.09` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/ARCHITECTURE.md, docs/GLOSSARY.md, docs/TESTX_STAGE_MATRIX.md, docs/apps/ARTIFACT_IDENTITY.md, docs/apps/README.md, docs/runtime/shell/CLI_REFERENCE.md, docs/runtime/shell/TOOL_REFERENCE.md, docs/architecture/ARTIFACT_LIFECYCLE.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validators/suite/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
