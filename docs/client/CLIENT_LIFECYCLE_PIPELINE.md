Status: DERIVED
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# Client Lifecycle Pipeline

Client session entry is command-driven and deterministic.

## Canonical Stage Order

1. `ResolveSession`
2. `AcquireWorld`
3. `VerifyWorld`
4. `WarmupSimulation`
5. `WarmupPresentation`
6. `SessionReady`
7. `SessionRunning`
8. `SuspendSession`
9. `ResumeSession`
10. `TearDownSession`

## Transition Rules

- Stage transitions happen only through canonical commands.
- Direct stage jump commands are refused with deterministic refusal codes.
- `client.session.begin` is the explicit transition from `SessionReady` to `SessionRunning`.
- Re-entry runs through the same ordered stages and returns to `SessionReady` before resume.

## Determinism Contract

- Transition order is stable and lexical command IDs are mapped to fixed stage edges.
- Refusal results are stable (`refuse.begin_requires_ready`, `refuse.invalid_transition`, `refuse.resume_requires_suspend`).
- No transition mutates simulation time; lifecycle logic is orchestration only.
