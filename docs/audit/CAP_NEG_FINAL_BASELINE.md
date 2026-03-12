Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Derived from `docs/contracts/CAPABILITY_NEGOTIATION_CONSTITUTION.md`, `docs/compat/ENDPOINT_DESCRIPTORS.md`, `docs/compat/NEGOTIATION_HANDSHAKES.md`, `docs/compat/DEGRADE_LADDERS.md`, `tools/compat/cap_neg4_common.py`, and `data/regression/cap_neg_full_baseline.json`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# CAP-NEG Final Baseline

## Interop Matrix Summary
- Canonical matrix rows: `10`
- Deterministic seed: `41004`
- Matrix fingerprint: `2fa40b3042ce792415469e9544cd08fa130751996f201b99af48907841ac667c`
- Stress fingerprint: `537e81f08a0e645eb17bf5353badc53a7134f37928dac924519e0bb46b40b8a5`
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
- Real-descriptor rows in the regression lock are normalized to negotiated semantic outcomes.
  - build-id-sensitive descriptor hashes stay in the live stress report and replay artifacts, not in the committed lock.

## Regression Lock
- Committed lock: `data/regression/cap_neg_full_baseline.json`
- Baseline fingerprint: `3fdcdf2825a37900bd5208fbca669cf947b8664f182bf16a572ef771c5aff14a`
- Required update tag: `CAP-NEG-REGRESSION-UPDATE`
- Replay summary fingerprint: `940937de7eea180207bd0dee70faebf69ae65a45f3ecd29b51ef0a707680a2bf`

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
