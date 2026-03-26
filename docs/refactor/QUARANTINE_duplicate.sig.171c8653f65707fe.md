Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.171c8653f65707fe`

- Symbol: `sizeof`
- Cluster Kind: `exact`
- Cluster Resolution: `merge`
- Risk Level: `MED`
- Canonical Candidate: `launcher/cli/launcher_cli_main.c`
- Quarantine Reasons: `builtin_or_entrypoint_collision, cross_domain_helper_collision, cross_product_surface, file_scope_ambiguity, phase_boundary_deferred, requires_medium_risk_batch_gate, secondary_file_active_in_default_build`
- Planned Action Kinds: `merge, rewire, deprecate`

## Competing Files

- `client/app/main_client.c`
- `launcher/cli/launcher_cli_main.c`
- `tools/tools_host_main.c`

## Scorecard

- `launcher/cli/launcher_cli_main.c` disposition=`canonical` rank=`1` total_score=`74.15` risk=`MED`
- `tools/tools_host_main.c` disposition=`merge` rank=`2` total_score=`69.52` risk=`LOW`
- `client/app/main_client.c` disposition=`merge` rank=`3` total_score=`65.0` risk=`MED`

## Usage Sites

- Build Targets: `launcher_cli`
- Docs: `docs/specs/SPEC_DOMINO_GFX.md`

## Tests Involved

- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile FAST`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
