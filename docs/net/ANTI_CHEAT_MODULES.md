Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-15
Compatibility: Bound to `schemas/net_anti_cheat_event.schema.json`, anti-cheat policy registries, and `src/net/anti_cheat/anti_cheat_engine.py`.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Anti-Cheat Modules

## Purpose
Define the modular anti-cheat execution contract used by multiplayer replication policies.

## Engine Contract
- Input stream is deterministic and ordered by:
  - `(tick, peer_id, module_id, sequence, event_type)`
- Engine consumes:
  - Intent envelope ingress events
  - Tick intent list context (lockstep)
  - Hash anchor frames
  - Perceived delta integrity signals
  - Handshake and shard-routing outcomes
- Engine produces:
  - `anti_cheat_event` artifacts
  - explicit enforcement actions
  - optional refusal injection records

## Module Set
1. `ac.module.sequence_integrity`
2. `ac.module.replay_protection`
3. `ac.module.authority_integrity`
4. `ac.module.input_integrity`
5. `ac.module.state_integrity`
6. `ac.module.behavioral_detection`
7. `ac.module.client_attestation` (optional)

## Movement Integrity Signal Sources (EB-3)
- Source processes:
  - `process.agent_move`
  - `process.agent_rotate`
- Input-integrity signals:
  - movement-envelope rate by tick window
  - malformed movement payloads
- Authority-integrity signals:
  - ownership mismatch (`controller` vs `agent.owner_peer_id`)
  - shard-target spoof for embodied movement intents
- Behavioral-detection signals:
  - displacement per tick above configured deterministic thresholds
  - repeated boundary-cross attempts without transfer permission

All movement signals are server-side and non-invasive. Client scanning remains out-of-scope.

## Determinism
- Event fingerprints use canonical hash over stable fields only.
- Module decisions are policy-driven and deterministic for identical input streams.
- Wall-clock time is excluded from enforcement decisions.
- Tick-count windows are used for rate checks and lead windows.

## Proof Surfaces
Per session run-meta artifacts include:
1. Anti-cheat events log.
2. Enforcement action log.
3. Anchor mismatch log.
4. Refusal injection log.
5. Deterministic proof manifest hash over all logs.

## Privacy and Modularity
- No invasive client scanning is permitted by default.
- Attestation is optional and disabled unless policy explicitly requires it.
- Policy/module activation comes from registries, not hardcoded flags.

## Cross-References
- `docs/net/ANTI_CHEAT_POLICY_FRAMEWORK.md`
- `docs/net/ANTI_CHEAT_ENFORCEMENT_ACTIONS.md`
- `docs/contracts/refusal_contract.md`
- `data/registries/anti_cheat_policy_registry.json`
- `data/registries/anti_cheat_module_registry.json`
- `src/net/anti_cheat/anti_cheat_engine.py`
