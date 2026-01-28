# Live Evolution Model (OPS1)

Status: FROZEN.  
Scope: rolling updates, live evolution, and rollback safety.

## Update Model (Rolling)

Rules:
- Rolling updates are per-shard; no global downtime is required.
- Domain ownership transfer occurs at deterministic commit boundaries.
- Clients resync via snapshot + event tail after transfer.
- Every update action MUST emit a compat_report with context `update`.

## Rollback Model

Rollback is safe because:
- install_root is immutable after creation.
- Packs are content-addressed and selected by lockfiles.
- Capability baselines are explicit in compat_report.

Rules:
- Rollback MUST restore the exact previous behavior.
- Rollback actions MUST emit a compat_report and an ops transaction log entry.
- No silent fallback or partial rollback is allowed.

## Safety Notes

- Live evolution must not introduce mixed semantics inside an authoritative domain.
- If compatibility cannot be proven, the operation MUST refuse.
