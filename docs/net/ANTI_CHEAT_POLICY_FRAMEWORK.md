Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-15
Compatibility: Bound to LawProfile/AuthorityContext gating, server policy registries, and refusal contract.

# Anti-Cheat Policy Framework

## Purpose
Define anti-cheat as modular, policy-driven components.
No hidden enforcement actions are allowed; all outcomes are explicit and logged.

## Module IDs

1. `ac.module.input_integrity`
2. `ac.module.sequence_integrity`
3. `ac.module.authority_integrity`
4. `ac.module.state_integrity`
5. `ac.module.replay_protection`
6. `ac.module.behavioral_detection`
7. `ac.module.client_attestation` (optional/off by default)

## Policy IDs

1. `policy.ac.detect_only`
2. `policy.ac.casual_default`
3. `policy.ac.rank_strict`
4. `policy.ac.private_relaxed`

## Policy Behavior Contract

1. Policy activation is explicit via registry + server law/profile configuration.
2. Actions are declarative:
   - `audit`
   - `refuse`
   - `terminate`
   - `throttle`
3. Singleplayer/private scenarios may choose relaxed policies by explicit policy ID.
4. Ranked/esports servers require strict policy declaration and deterministic audit trails.

## Outputs

1. `anti_cheat_event` artifact (deterministic fingerprinted evidence).
2. Refusal payload through canonical refusal contract.
3. Optional session termination request (policy-driven and logged).

## Invariants

1. Non-invasive by default:
   - `client_attestation` remains optional/off unless policy explicitly enables it.
2. No hidden bans:
   - all punitive actions must be represented as deterministic events and/or refusals.
3. Policy and module resolution is data-driven only; no hardcoded branch flags.

## Example

```json
{
  "policy_id": "policy.ac.rank_strict",
  "module_id": "ac.module.sequence_integrity",
  "severity": "violation",
  "recommended_action": "refuse"
}
```

## Cross-References

- `data/registries/anti_cheat_policy_registry.json`
- `data/registries/anti_cheat_module_registry.json`
- `schemas/net_anti_cheat_event.schema.json`
- `docs/contracts/refusal_contract.md`

## TODO

- Add adjudication workflow for tournament operations (human review handoff contract).
