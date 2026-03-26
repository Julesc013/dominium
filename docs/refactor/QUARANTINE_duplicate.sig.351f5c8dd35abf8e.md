Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.351f5c8dd35abf8e`

- Symbol: `mod_manifest_validate`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `game/include/dominium/mods/mod_manifest.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `game/include/dominium/mods/mod_manifest.h`
- `game/mods/runtime/mod_manifest.cpp`

## Scorecard

- `game/include/dominium/mods/mod_manifest.h` disposition=`canonical` rank=`1` total_score=`72.23` risk=`HIGH`
- `game/mods/runtime/mod_manifest.cpp` disposition=`quarantine` rank=`2` total_score=`63.33` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/ARCH_REPO_LAYOUT.md, docs/architecture/ID_AND_NAMESPACE_RULES.md, docs/archive/ci/PHASE1_AUDIT_REPORT.md, docs/audit/PROMPT_G_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/ci/CI_ENFORCEMENT_MATRIX.md, docs/ci/HYGIENE_QUEUE.md, docs/guides/MODDING_GUIDE.md`

## Tests Involved

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

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
