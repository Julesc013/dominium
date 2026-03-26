Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.24f8fb0ba149dec5`

- Symbol: `_as_bool`
- Cluster Kind: `exact`
- Cluster Resolution: `keep`
- Risk Level: `MED`
- Canonical Candidate: `src/platform/platform_probe.py`
- Quarantine Reasons: `cross_domain_helper_collision, file_scope_ambiguity, source_like_surface`
- Planned Action Kinds: `rewire, deprecate`

## Competing Files

- `src/platform/platform_probe.py`
- `tools/mvp/toolchain_matrix_common.py`

## Scorecard

- `src/platform/platform_probe.py` disposition=`canonical` rank=`1` total_score=`64.76` risk=`MED`
- `tools/mvp/toolchain_matrix_common.py` disposition=`drop` rank=`2` total_score=`62.37` risk=`LOW`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/ci/HYGIENE_QUEUE.md`

## Tests Involved

- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile FAST`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
