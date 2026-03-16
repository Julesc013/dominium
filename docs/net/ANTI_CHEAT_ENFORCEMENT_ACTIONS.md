Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to anti-cheat policy registry action tables and refusal contract.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Anti-Cheat Enforcement Actions

## Purpose
Define explicit anti-cheat action semantics. No hidden ban paths are permitted.

## Canonical Actions
1. `action.audit_only`
   - Runtime action token: `audit`
   - Behavior: record event only.
2. `action.refuse_intent`
   - Runtime action token: `refuse`
   - Behavior: inject deterministic refusal and drop envelope.
3. `action.throttle_peer`
   - Runtime action token: `throttle`
   - Behavior: deterministic non-terminal drop/defer behavior with action log.
4. `action.terminate_session`
   - Runtime action token: `terminate`
   - Behavior: policy-driven termination request with mandatory event/action logging.
5. `action.require_attestation` (optional)
   - Runtime action token: `require_attestation`
   - Behavior: refuse until attestation token is provided under a policy that explicitly requires it.

## Refusal Mapping
- `refusal.net.envelope_invalid`
- `refusal.net.sequence_violation`
- `refusal.net.replay_detected`
- `refusal.net.authority_violation`
- `refusal.net.resync_required`
- `refusal.ac.policy_violation`
- `refusal.ac.attestation_missing`

## Remediation Guidance
- Sequence violation: resend monotonic `deterministic_sequence_number`.
- Replay detected: issue fresh envelope id/sequence and retry.
- Authority violation: use allowed LawProfile/AuthorityContext entitlements.
- Resync required: execute policy-defined resync strategy before continuing.
- Attestation missing: provide attestation token or select policy without attestation requirement.

## Invariants
- Every terminate/refuse decision must have matching event + action artifacts.
- Policy tables are authoritative; no hidden branches.
- Action outcomes are deterministic for identical event streams.

## Cross-References
- `docs/net/ANTI_CHEAT_MODULES.md`
- `docs/net/ANTI_CHEAT_POLICY_FRAMEWORK.md`
- `docs/contracts/refusal_contract.md`
- `src/net/anti_cheat/anti_cheat_engine.py`
