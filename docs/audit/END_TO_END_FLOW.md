Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# IRC-0 Phase 5: End-to-End Flow Check

## Scope

- Objective: orchestration correctness only (no gameplay semantics).
- Flow required:
  - setup initializes layout
  - launcher inspects instances
  - server starts headless authority path
  - client runs connect/smoke path
  - tool validates same environment

## Executed Flow

1. Setup initialize
   - Command: `build/msvc-base/bin/setup.exe prepare --root tmp/irc0_e2e`
   - Result: PASS (`setup_prepare=ok`; expected directory tree emitted)

2. Launcher instance discovery
   - Command: `build/msvc-base/bin/launcher.exe instances list`
   - Result: PASS (`result: ok`, `instances: []`)

3. Server headless authority loop
   - Command: `build/msvc-base/bin/server.exe --headless --ticks 1`
   - Result: PASS (exit code 0; no refusal)

4. Client connect/smoke path
   - Command: `build/msvc-base/bin/client.exe --mp0-connect=local`
   - Result: PASS (`MP0 client local hash: 16976973710109906564`)

5. Tool validation against environment
   - Command: `out/build/vs2026/verify/bin/tools.exe validate --format json`
   - Result: PASS (`validate_status: ok`, compatibility payload emitted)

## Outcome

- PASS: minimal real orchestration path is executable end-to-end.
- PASS: outputs/refusals are explicit and machine-readable where expected.
- NOTE: `tools.exe` is present in `out/build/vs2026/verify/bin` rather than `build/msvc-base/bin`; this is a build-layout difference, not a runtime mismatch.
