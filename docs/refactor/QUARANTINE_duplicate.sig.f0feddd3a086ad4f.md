Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.f0feddd3a086ad4f`

- Symbol: `_legacy_main`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/server/server_main.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate, quarantine`

## Competing Files

- `src/server/server_main.py`
- `tools/launcher/launch.py`
- `tools/setup/setup_cli.py`

## Scorecard

- `src/server/server_main.py` disposition=`canonical` rank=`1` total_score=`67.5` risk=`HIGH`
- `tools/launcher/launch.py` disposition=`drop` rank=`2` total_score=`64.25` risk=`HIGH`
- `tools/setup/setup_cli.py` disposition=`quarantine` rank=`3` total_score=`61.61` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/GLOSSARY.md, docs/PROCESS_REGISTRY.md, docs/app/CLI_CONTRACTS.md, docs/app/TESTX_INVENTORY.md, docs/appshell/CLI_REFERENCE.md, docs/appshell/COMMANDS_AND_REFUSALS.md, docs/appshell/FLAG_MIGRATION.md, docs/appshell/TOOL_REFERENCE.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
