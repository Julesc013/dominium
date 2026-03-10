Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Derived from `docs/contracts/CAPABILITY_NEGOTIATION_CONSTITUTION.md`, `docs/compat/ENDPOINT_DESCRIPTORS.md`, `docs/compat/NEGOTIATION_HANDSHAKES.md`, `docs/compat/DEGRADE_LADDERS.md`, `tools/compat/cap_neg4_common.py`, and `data/regression/cap_neg_full_baseline.json`.

# CAP-NEG Final Baseline

## Interop Matrix Summary
- Canonical matrix rows: `10`
- Deterministic seed: `41004`
- Matrix fingerprint: `2fa40b3042ce792415469e9544cd08fa130751996f201b99af48907841ac667c`
- Stress fingerprint: `cd1397a23e5b05271e3274cc2aadf42ffff4ff512135e17fff399f348e8d825f`
- Canonical modes:
  - `compat.full`: `2`
  - `compat.degraded`: `5`
  - `compat.read_only`: `1`
  - `compat.refuse`: `2`

## Degrade Statistics
- Most frequent disabled capabilities:
  - `cap.logic.protocol_layer`: `3`
  - `cap.ui.rendered`: `3`
  - `cap.logic.compiled_automaton`: `1`
  - `cap.pack.install`: `1`
  - `cap.unknown.synthetic_render_channel`: `1`
- Canonical degrade coverage locked in regression:
  - rendered UI degrades to CLI/TUI
  - protocol-layer tooling disables explicitly
  - compiled-automaton preference degrades to `cap.logic.l1_eval`
  - contract mismatch can force `compat.read_only`

## Refusal Statistics
- `refusal.compat.contract_mismatch`: `1`
- `refusal.compat.no_common_protocol`: `1`
- Strict mismatch behavior remains explicit:
  - no connection succeeds without negotiation
  - read-only fallback is only used when the scenario explicitly allows it

## Real Descriptor Smoke
- `client <-> server`: `compat.degraded`
  - current-build smoke still degrades rendered UI and sphere-atlas features explicitly
- `launcher <-> client`: `compat.refuse`
  - current-build smoke still refuses without a shared protocol
- `setup <-> pack verify stub`: `compat.full`
  - current-build offline verification stays fully compatible

## Regression Lock
- Committed lock: `data/regression/cap_neg_full_baseline.json`
- Baseline fingerprint: `666706c1c886e1f214bf815f7dfe47b898bcfb1ea02f1b8a9c0ea535dae811f8`
- Required update tag: `CAP-NEG-REGRESSION-UPDATE`
- Replay summary fingerprint: `701f8b973d02d70db893eeb8f1e7dd552b3480fded7d2023ec29ac46abe1ebdd`

## Readiness
CAP-NEG is ready for PACK-COMPAT follow-up and APPSHELL negotiation surfaces.

What is ready now:
- deterministic synthetic interop matrix generation
- real-descriptor smoke negotiation
- explicit degrade/refuse/read-only coverage
- replay-stable negotiation record hashing
- committed regression lock and coverage enforcement

What remains intentionally out of scope:
- historical binary execution
- new transport layers beyond the existing handshake abstraction
- network complexity beyond deterministic loopback/IPC-compatible negotiation surfaces
