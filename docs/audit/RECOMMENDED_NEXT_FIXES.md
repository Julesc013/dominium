Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Recommended Next Fixes (CA-0)

Ordered, minimal, atomic fix prompts. No redesign required.

1. `DOC-CANON-ALIGN-1`
- Scope: `docs/architecture/CANON_INDEX.md`, `docs/CAPABILITY_STAGES.md`, `docs/TESTX_STAGE_MATRIX.md`.
- Action: remove runtime-normative stage semantics or mark them explicitly as non-normative historical artifacts.
- Expected result: no contradiction with `docs/architecture/CAPABILITY_ONLY_CANON.md`.

2. `CAPABILITY-ENFORCEMENT-CAMERA-1`
- Scope: `libs/appcore/command/command_registry.c`, `client/shell/client_shell.c`, `data/capabilities/app_ui_camera_blueprint.json`, related tests.
- Action: enforce mode-specific camera capabilities/entitlements (`memory`, `observer`) in canonical command metadata plus runtime checks.
- Expected result: declared capabilities are all exercised by runtime gating.

3. `REPOX-SEMANTIC-ANTI-CHEAT-1`
- Scope: `scripts/ci/check_repox_rules.py`, targeted tests.
- Action: replace token-presence checks with semantic assertions:
  - observer mode path must require entitlement in command handling path,
  - renderer ingest path must prove artifact-only input type usage.
- Expected result: anti-cheat checks fail on semantic bypasses, not only string mismatches.

4. `PROCESS-GUARD-HARDEN-1`
- Scope: `tests/invariant/process_only_mutation_tests.py`, `scripts/ci/check_repox_rules.py`, process coverage tests.
- Action: expand mutation detection and process literal scans to all relevant runtime roots and add structural guard checks.
- Expected result: stronger proof that mutation cannot occur outside registered processes.

5. `CAPABILITY-MATRIX-RUNTIME-1`
- Scope: `tests/testx/capability_suite_runner.py`, capability set tests, optional lightweight runtime harness.
- Action: move key capability matrix assertions from static parsing to runtime-executed command behavior checks.
- Expected result: capability gating regressions fail on real behavior changes.

6. `SOLVER-CONFORMANCE-RUNTIME-PROOF-1`
- Scope: runtime solver selection call path, `data/registries/solver_registry.json`, tests.
- Action: either wire solver registry into runtime selection path or explicitly document it as non-runtime metadata until wired.
- Expected result: collapse/expand claims match implementation evidence.

7. `CAPABILITY-CONFLICT-POLICY-1`
- Scope: `tools/pack/capability_inspect.py`, pack resolution policy docs/tests.
- Action: convert overlap/conflict signals from warn-only to deterministic policy outcomes where applicable.
- Expected result: pack capability resolution becomes predictable under conflicting providers.
