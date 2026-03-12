Status: CANONICAL
Last Reviewed: 2026-03-03
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# SIG7 Retro Consistency Audit

## Scope
Audit target for final SIG hardening:
- `src/signals/transport/*`
- `src/signals/aggregation/*`
- `src/signals/institutions/*`
- `src/signals/trust/*`
- proof and replay hooks under `src/control/proof/*`, `tools/net/*`, `tools/mobility/*`

## Findings

### 1) Remaining ad-hoc message processing loops
- `src/signals/institutions/bulletin_engine.py`
  - Per-institution send loop directly invokes `process_signal_send`.
- `src/signals/institutions/dispatch_engine.py`
  - Per-update loop generates control intents and dispatch report envelope directly.
- `src/signals/institutions/standards_engine.py`
  - Per-request issue + report send loop directly invokes `process_signal_send`.

Assessment:
- Process-only mutation is preserved.
- Deterministic ordering is preserved.
- Missing a shared SIG envelope budget/degradation orchestrator.

### 2) Non-budgeted aggregation paths
- `src/signals/aggregation/aggregation_engine.py`
  - `process_signal_aggregation_tick` does not expose explicit cost envelope inputs.
  - All due policies run in one tick if scheduled.

Assessment:
- Deterministic but not explicitly budget-governed for MMO-scale runs.

### 3) Silent drop surface audit
- `src/signals/transport/channel_executor.py`
  - Queue deferrals are explicit.
  - Delivery state is explicit (`delivered|lost|corrupted`) and logged via `message_delivery_event`.
- `src/signals/transport/transport_engine.py`
  - Lost/corrupted states are emitted through transport tick outputs.

Assessment:
- No transport-layer silent drop observed.
- Need enforcement guard to keep this invariant locked.

### 4) Trust update logging audit
- `src/signals/trust/trust_engine.py`
  - `process_trust_update` emits `decision.trust_update.*` entries.
  - Verification flow can route through trust update process.

Assessment:
- Logged trust update path exists and is deterministic.
- Need explicit enforcement smell detector for bypass attempts.

## Migration / Hardening Plan
1. Add deterministic SIG stress scenario generator tool.
2. Add SIG stress harness with budget envelope and deterministic fingerprint reporting.
3. Introduce explicit SIG degradation order process (budgeted, logged, deterministic).
4. Extend control proof bundle with SIG hash-chain surfaces.
5. Add replay-window verification tool for signal history stability.
6. Add SIG regression lock baseline with required update tag.
7. Add RepoX + AuditX enforcement rules for budgeting, silent drop prevention, and trust-update logging.
8. Add TestX for determinism, degradation order, proof chains, replay verification, and silent-drop protection.

## Invariants Referenced
- A1 Determinism is primary
- A2 Process-only mutation
- A6 Provenance is mandatory
- A10 Explicit degradation and refusal
- E2 Deterministic ordering
- E6 Replay equivalence
