Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Diegetic-First Enforcement

Status: Canonical policy guidance for ED-3.

## 1. Enforcement Model

Diegetic-first behavior is enforced through data contracts, not mode flags:

- `LawProfile` controls allowed processes, lenses, debug allowances, and process entitlement requirements.
- `EpistemicPolicy` controls allowed/forbidden channels and precision limits for PerceivedModel.
- Lens and view-mode registries constrain what channels can be requested.
- Server profile governance constrains which law profiles can be negotiated in multiplayer.

Player defaults must remain diegetic-first:

- No non-diegetic HUD/debug windows by default.
- No freecam, inspector, teleport, or console surfaces under player default law.
- No observer truth channels under player default policy.

## 2. Explicit Carve-Outs

Carve-outs are explicit and policy-driven:

- Spectator:
  - May use limited non-diegetic overlays when allowed by `law.spectator.limited`.
  - Must not receive observer truth channels.
- Observer:
  - May use truth overlays only when law + entitlement permit it.
  - Observer truth views require watermark signaling.
- Admin/Lab:
  - Tooling remains available for development, but only under admin/lab law and server-profile allowance.

## 3. Compliance Requirements

Required invariants:

- UI binds to PerceivedModel only; no direct TruthModel UI data binding.
- Non-diegetic windows must declare entitlement requirements and be denied by default player law.
- Lens selection must refuse forbidden channels and law-disallowed lens IDs.
- Multiplayer handshake must refuse law/profile requests not allowed by server governance data.

## 4. Deterministic Refusal Surfaces

Enforcement paths must use deterministic refusal codes and structured remediation:

- `refusal.view.mode_forbidden`
- `refusal.ep.channel_forbidden`
- `refusal.ep.entitlement_missing`
- `refusal.net.handshake_policy_not_allowed`

## 5. Non-Goals

This layer does not add gameplay mechanics. It only governs visibility/control surfaces:

- No survival progression systems.
- No crafting/inventory systems.
- No removal of developer tools; only profile-gated access.
