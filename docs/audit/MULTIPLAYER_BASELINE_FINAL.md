Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Multiplayer Baseline Final

Status: DERIVED BASELINE  
Last Updated: 2026-02-16

## Implemented Policies
- `policy.net.lockstep` (A): deterministic tick intent ordering, per-tick anchor checks, replay resync.
- `policy.net.server_authoritative` (B): server TruthModel authority, PerceivedModel delta transport, snapshot resync.
- `policy.net.srz_hybrid` (C): deterministic shard routing/coordinator, composite hash anchors, shard resync scaffolding.

## Determinism Envelope Results
- Full-stack deterministic suites were added and pass:
  - `testx.net.mp_lockstep_full_stack`
  - `testx.net.mp_authoritative_full_stack`
  - `testx.net.mp_srz_hybrid_full_stack`
- Deterministic disorder simulation is covered by:
  - `testx.net.disorder_sim_deterministic`
- Regression lock hashes are pinned in:
  - `data/regression/multiplayer_baseline.json`

Policy baseline final composite hashes:
- `policy.net.lockstep`: `e4125db1d2db222078f4c0aa63c72f886208c98b0bfb2d5fa3e3a1cdbb9a2e75`
- `policy.net.server_authoritative`: `558eb169a19781783830d1c7eaca45ed1f775f9feffd80086c8d788644ca18f8`
- `policy.net.srz_hybrid`: `9cffe44fe9c5e6d2eaa48c5bde618efb4b38fb583829dac64d0b1beef928ce48`

## Security and Governance Coverage
- Ranked/casual/private handshake matrix checks are covered by:
  - `testx.net.handshake_matrix_ranked`
  - `testx.net.handshake_schema_version_refusal`
  - `testx.net.handshake_policy_not_allowed_refusal`
  - `testx.net.handshake_compat_matrix_report`
- Matrix artifacts:
  - `docs/audit/HANDSHAKE_COMPAT_MATRIX.md`
  - `docs/audit/HANDSHAKE_COMPAT_MATRIX.json`
- Ranked matrix hash baseline:
  - `1926e51d42b7bca86246ca523439c0674245e19f9f141662021d54394f366fb6`

## Anti-Cheat Regression Coverage
- Adversarial suites:
  - `testx.net.ac_adversarial_detect_only`
  - `testx.net.ac_adversarial_rank_strict`
- Fingerprint baselines pinned:
  - detect-only event hash: `34a73a21bd5ce366293f07ea103b6243135a6b8413a72d22d41be71509787f25`
  - rank-strict event hash: `27fbff163195f511c6954db020ebd322b8c8b7e19df88767c672ef66d6583310`
  - rank-strict action hash: `cf92fe074e9c07a526f45867534eee0bccc4c4008e24866d04e568f5c453d2cb`

## Performance Baseline Artifacts (Non-Gating)
- Multiplayer profile artifact:
  - `docs/audit/perf/multiplayer_profile_trace.json`
- Schema/determinism validation:
  - `testx.profile.multiplayer_trace_artifact`

## Known Limitations
- No client-side prediction/rollback.
- No matchmaking/NAT traversal.
- Hybrid mode is single-process authoritative shard coordination baseline; multi-machine routing remains future work.

## Extension Roadmap
- Embodiment-integrated intent streams.
- Deterministic prediction/rollback contracts for high-latency clients.
- Tournament-grade governance/attestation integration as opt-in SecureX policy extensions.
