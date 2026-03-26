Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.ff69cfbfe1374d22`

- Symbol: `in`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `game/tests/tests/contract/dominium_contract_tests.cpp`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `game/tests/tests/contract/dominium_contract_tests.cpp`
- `game/tests/tests/contract/dominium_tlv_fuzz_tests.cpp`
- `game/tests/tests/setup/test_adapter_linux_wrappers.cpp`
- `game/tests/tests/setup/test_adapter_macos_pkg.cpp`
- `game/tests/tests/setup/test_adapter_wrapper_scripts.cpp`
- `game/tests/tests/setup/test_import_legacy_state.cpp`
- `game/tests/tests/setup/test_plan.cpp`
- `tools/replay_analyzer/ra_diff.cpp`

## Scorecard

- `game/tests/tests/contract/dominium_contract_tests.cpp` disposition=`canonical` rank=`1` total_score=`74.68` risk=`HIGH`
- `game/tests/tests/setup/test_plan.cpp` disposition=`quarantine` rank=`2` total_score=`72.23` risk=`HIGH`
- `game/tests/tests/setup/test_adapter_macos_pkg.cpp` disposition=`quarantine` rank=`3` total_score=`65.0` risk=`HIGH`
- `game/tests/tests/setup/test_adapter_linux_wrappers.cpp` disposition=`merge` rank=`4` total_score=`62.62` risk=`HIGH`
- `game/tests/tests/setup/test_adapter_wrapper_scripts.cpp` disposition=`merge` rank=`5` total_score=`62.62` risk=`HIGH`
- `game/tests/tests/setup/test_import_legacy_state.cpp` disposition=`merge` rank=`6` total_score=`62.19` risk=`HIGH`
- `tools/replay_analyzer/ra_diff.cpp` disposition=`drop` rank=`7` total_score=`59.91` risk=`HIGH`
- `game/tests/tests/contract/dominium_tlv_fuzz_tests.cpp` disposition=`drop` rank=`8` total_score=`52.14` risk=`HIGH`

## Usage Sites

- Build Targets: `dominium_contract_tests`
- Docs: `docs/audit/BR0_COMPLETION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/SDK_READINESS.md, docs/ci/HYGIENE_QUEUE.md, docs/guides/IMPLEMENTATION_BACKLOG_CANON.md, docs/guides/SETUP_GAPS.md, docs/guides/release/RELEASE_READINESS_CHECKLIST.md, docs/specs/AGENT_GOALS_AND_PLANNING.md`

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

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
