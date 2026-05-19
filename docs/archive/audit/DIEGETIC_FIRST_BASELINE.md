Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# DIEGETIC_FIRST_BASELINE

Status: DERIVED  
Date: 2026-02-16  
Scope: ED-3/4 strict diegetic enforcement profiles and carve-outs

## Profiles Defined

### law.player.diegetic_default
- Epistemic policy: `ep.policy.player_diegetic`
- Lenses: diegetic-only (`lens.diegetic.sensor`)
- Debug overlays: disabled (`allow_nondiegetic_overlays=false`)
- Non-diegetic/debug processes explicitly forbidden (`camera_teleport`, inspector/telemetry, time controls, lens override)

### law.spectator.limited
- Epistemic policy: `ep.policy.spectator_limited`
- Allows constrained spectator overlays through law and entitlement gates
- Truth overlays forbidden

### law.observer.truth
- Epistemic policy: `ep.policy.observer_truth`
- Observer tooling and truth overlays allowed only with explicit entitlement checks
- Watermark path required for truth-capable views

### law.admin.lab
- Broad lab/admin tooling profile
- Intended for private-relaxed governance only

## Experience/Profile Bindings
- `profile.player.default` -> `law.player.diegetic_default`
- `profile.spectator.default` -> `law.spectator.limited`
- `profile.observer.exploration` -> `law.observer.truth`
- `profile.lab.developer` remains available for dev workflows

## Workspace/Window Baseline

### Player Workspace (`workspace.player.diegetic_default`)
- Allowed windows:
  - `window.player.instrument.compass`
  - `window.player.instrument.clock`
  - `window.player.instrument.map_local`
  - `window.player.instrument.notebook`
  - `window.player.instrument.radio_text`
- Excludes non-diegetic windows (`window.tool.*`, inspector, console, freecam surfaces)

### Spectator Workspace (`workspace.spectator.limited`)
- Follow controls + limited scoreboard surface

### Observer Workspace (`workspace.observer.truth`)
- Explicit watermark panel surface

## Entitlement Matrix (Operational)
- Player default:
  - Allowed: diegetic instrument use and bounded camera controls
  - Denied by law/policy: freecam, teleport, inspector, console-equivalent debug paths
- Spectator:
  - Follow/spectator entitlements only
  - No truth overlays
- Observer:
  - Observer/truth entitlements required
  - Watermark enforced
- Admin/Lab:
  - Broad entitlements, constrained by server profile

## Ranked vs Private Governance
- `server.profile.rank_strict`:
  - Allowed laws: `law.player.diegetic_default`, `law.spectator.limited`
  - Observer/admin truth/lab laws refused at handshake
- `server.profile.private_relaxed`:
  - Allows observer/admin carve-outs by policy

## Enforcement Points
- UI host denies non-diegetic windows under diegetic player law using deterministic gating.
- Lens/view selection remains law + policy + entitlement gated.
- Handshake policy negotiation enforces allowed law-profile set per server profile.

## Validation Summary
- Added TestX coverage for:
  - player nondiegetic window exclusion
  - player observer-channel exclusion
  - ranked observer-profile refusal
  - private observer-profile acceptance
  - deterministic player workspace composition
- Added RepoX rules:
  - `INV-DIEGETIC-DEFAULT-PROFILE-PRESENT`
  - `INV-NO-PLAYER_DEBUG_SURFACES`
- Added AuditX analyzers:
  - `E26_DIEGETIC_BYPASS_SMELL`
  - `E27_HIDDEN_NONDIEGETIC_WINDOW_SMELL`

## Extension Points
- Survival-specific diegetic surfaces can layer on top of `law.player.diegetic_default` without enabling non-diegetic debug channels.
- Additional spectator overlays remain policy-gated and must avoid truth leakage.
- Future profile packs can add role-specific workspaces if they preserve law/profile gating contracts.
