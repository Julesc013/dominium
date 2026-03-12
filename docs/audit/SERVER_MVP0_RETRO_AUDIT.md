Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# SERVER-MVP-0 Retro Audit

## Scope

- Audit existing authoritative runtime and session loading surfaces.
- Confirm current AuthorityContext and loopback transport integration points.
- Identify where proof anchors and replay hashes already exist.

## Findings

- There is no dedicated `src/server/` package yet.
  - The repo already exposes deterministic authoritative runtime behavior through
    `src/net/policies/policy_server_authoritative.py`.
  - Session boot currently reaches that runtime through
    `tools/xstack/sessionx/runner.py`.
- Session and contract validation already exist and are reusable.
  - `src/universe/universe_contract_enforcer.py` enforces pinned universe
    contract bundles and semantic contract registry hashes.
  - `src/modding/mod_policy_engine.py` validates saved mod policy and conflict
    policy metadata from lock/proof surfaces.
  - `tools/xstack/sessionx/runner.py` already validates lockfile integrity and
    registry hashes before runtime startup.
- Deterministic loopback transport already exists.
  - `src/net/transport/loopback.py` provides deterministic `listen`,
    `connect`, `accept`, `send`, and `recv` semantics with stable
    `connection_id` derivation.
- Proof anchors already exist at the authoritative runtime layer.
  - `policy_server_authoritative.py` emits `hash_anchor_frames` and control
    proof bundles per deterministic network tick.
  - These can be wrapped into periodic server replay-anchor artifacts without
    changing simulation behavior.
- Existing client/session boot is not a server-facing API.
  - `tools/xstack/sessionx/runner.py` is suitable as a reference and helper
    source, but not as the public headless server surface.
  - A thin `src/server` orchestration layer is the lowest-risk integration
    point.

## Integration Direction

- Reuse `initialize_authoritative_runtime(...)`,
  `prepare_server_authoritative_baseline(...)`,
  `advance_authoritative_tick(...)`, and `join_client_midstream(...)`.
- Reuse the base loopback transport instead of implementing a second transport.
- Add a dedicated `server_config` registry to bind session template, mod
  policy, overlay conflict policy, client caps, and proof-anchor cadence.
- Keep server-side intent execution routed through the existing authoritative
  intent queue so `AuthorityContext` enforcement remains process-only.
