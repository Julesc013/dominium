Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Anti-Cheat Framework Baseline

Status: DERIVED  
Scope: MP-7/9 anti-cheat module framework

## Implemented Modules

- `ac.module.sequence_integrity`
- `ac.module.replay_protection`
- `ac.module.authority_integrity`
- `ac.module.input_integrity`
- `ac.module.state_integrity`
- `ac.module.behavioral_detection`
- `ac.module.client_attestation` (optional/stub; off by default)

Runtime engine: `src/net/anti_cheat/anti_cheat_engine.py`.

## Policy Matrix

- `policy.ac.detect_only`
  - Behavior: emit deterministic events only.
  - Default actions: `audit`.
- `policy.ac.casual_default`
  - Behavior: refuse clear integrity violations.
  - Default actions: `refuse` for core integrity modules.
- `policy.ac.rank_strict`
  - Behavior: strict deterministic enforcement for ranked.
  - Default actions: `refuse`, `terminate` (authority), `require_attestation` (module hook), `throttle` (behavioral).
  - Escalation: repeated `refusal.net.resync_required` under `ac.module.state_integrity` escalates to `terminate`.
- `policy.ac.private_relaxed`
  - Behavior: warning/audit oriented.
  - Default actions: `audit`.

Registry sources:

- `data/registries/anti_cheat_policy_registry.json`
- `data/registries/anti_cheat_module_registry.json`

## Proof Artifacts

Per-session deterministic proof stream is exported under run-meta:

- `anti_cheat.events.<run_id>.json`
- `anti_cheat.actions.<run_id>.json`
- `anti_cheat.anchor_mismatches.<run_id>.json`
- `anti_cheat.refusal_injections.<run_id>.json`
- `anti_cheat.proof_manifest.<run_id>.json`

Artifacts include:

- `pack_lock_hash`
- registry hash map
- compatibility/BII token
- deterministic fingerprints

Report tool:

- `tools/net/tool_anti_cheat_report.py`

## Determinism Guarantees

- Event processing order is deterministic: `(tick, peer_id, module_id, sequence, event_type)`.
- `anti_cheat_event.deterministic_fingerprint` and action fingerprints are canonical-hash based.
- Enforcement action selection is policy-table driven and deterministic for equal inputs.
- No wall-clock input is used in anti-cheat decisions.

## Privacy and Non-Invasive Defaults

- Framework is server-side first.
- No hidden bans; termination must be emitted as explicit policy action + refusal/event trail.
- `ac.module.client_attestation` is optional and policy-controlled.
- Default policies do not require invasive scanning.

## Extension Points

- Add new modules through `anti_cheat_module_registry`.
- Add/adjust policy tables in `anti_cheat_policy_registry` (modules, actions, escalation rules).
- Integrate external attestation providers through the attestation module interface without changing simulation semantics.
