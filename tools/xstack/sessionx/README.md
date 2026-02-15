Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `schemas/session_spec.schema.json` v1.0.0 and `docs/architecture/session_lifecycle.md`.

# SessionX v1

## Purpose
Provide deterministic out-of-game session lifecycle tooling:
- SessionSpec creation
- lockfile/registry preflight binding
- Observation Kernel derivation (`TruthModel -> PerceivedModel`)
- RenderModel adapter derivation (`PerceivedModel -> RenderModel`)
- minimal headless boot/shutdown
- SRZ scheduling pipeline (`read -> propose -> resolve -> commit`)
- run-meta emission

## Commands
- `tools/xstack/session_create`
- `tools/xstack/session_boot`
- `tools/xstack/session_script_run`
- `tools/xstack/srz_status`

## Invariants
- No runtime simulation mechanics are implemented.
- Session create/boot emit deterministic refusal payloads.
- Generated save artifacts are canonical JSON.
- UniverseIdentity mutation is refused if `identity_hash` mismatch is detected.
- Lens gating is enforced by LawProfile + AuthorityContext entitlements.
- Renderer presentation payload is derived from PerceivedModel only.
- Scripted camera/time interactions mutate UniverseState only through process execution.
- Scripted process execution runs through SRZ scheduler phases and emits deterministic tick/composite hash anchors.

## Cross-References
- `docs/architecture/session_lifecycle.md`
- `docs/contracts/refusal_contract.md`
- `docs/contracts/session_spec.md`
