Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.849bcf350c2163cc`

- Symbol: `d_content_validate_all`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/content/d_content_validate.c`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/content/d_content.h`
- `engine/modules/content/d_content_validate.c`

## Scorecard

- `engine/modules/content/d_content_validate.c` disposition=`canonical` rank=`1` total_score=`81.55` risk=`HIGH`
- `engine/modules/content/d_content.h` disposition=`quarantine` rank=`2` total_score=`79.29` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/app/TESTX_INVENTORY.md, docs/architecture/APP_CANON0.md, docs/architecture/ARCH_REPO_LAYOUT.md, docs/architecture/BUNDLE_MODEL.md, docs/architecture/ID_AND_NAMESPACE_RULES.md, docs/architecture/PRODUCT_SHELL_CONTRACT.md, docs/archive/ci/PHASE6_SEALED.md, docs/audit/CONSISTENCY_AUDIT_REPORT.md`

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

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
