Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Acceptance Checkpoints (CHK0)

Status: binding.
Scope: explicit pass/fail checkpoints for product acceptance.

## Checkpoint 1: Product shell confidence

Required behaviors:
- Product shell contracts exist and are enforced by TestX.
- Setup succeeds for minimal, maximal, offline, uninstall, repair, rollback.
- Launcher shows installs/instances/profiles and generates compat_report.
- Client boots with zero assets and exposes CLI/TUI/GUI parity.
- Server runs headless-first and emits logs and replays.
- Tools are read-only by default and include replay inspection.

Forbidden behaviors:
- Setup silently mutates installs or assumes content.
- Launcher hides refusals or bypasses compat_report.
- Client requires packs to reach the main menu.
- Tools mutate state by default.

Manual test (human):
1) Perform minimal and maximal installs without network access.
2) Launch the client with zero packs and reach the main menu.
3) Attempt a launch with missing packs and confirm explicit refusals.
4) Start the server headless and verify logs/replay outputs.
5) Use tools to inspect a replay without mutation.

TestX (automated):
- `tests/contract/product_shell/product_shell_contract_tests.py`
- `tests/contract/refusal_code_stability.py`
- `tests/contract/no_raw_file_paths_lint.py`

## Checkpoint 2: Exploration baseline (future)

Required behaviors:
- Baseline exploration flows are available without content packs.
- Inspect mode provides read-only visibility of world state.
- CLI/TUI/GUI parity holds for exploration actions.

Forbidden behaviors:
- Exploration relies on GUI-only controls.
- Inspect mode mutates state or bypasses authority.

Manual test (human):
1) Start a baseline world and navigate using camera/movement.
2) Inspect world state and verify read-only behavior.

TestX (automated):
- Placeholder: add exploration parity and inspect-mode invariants.

## Checkpoint 3: Interaction baseline (future)

Required behaviors:
- Baseline interaction intents are deterministic and lawful.
- Refusals are visible and use canonical codes.

Forbidden behaviors:
- Interaction mutates state outside Process execution.
- UI-only interaction paths exist.

Manual test (human):
1) Submit baseline intents and verify deterministic outcomes.
2) Trigger a refusal and verify visibility and payload shape.

TestX (automated):
- Placeholder: add interaction intent parity and refusal invariants.