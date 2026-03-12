Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Derived from `docs/compat/DEGRADE_LADDERS.md`, `data/registries/degrade_ladder_registry.json`, `data/registries/capability_fallback_registry.json`, `src/compat/capability_negotiation.py`, and `src/compat/negotiation/degrade_enforcer.py`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Degrade Ladder Baseline

## Per-Product Ladder Summary
- `ladder.client.mvp`
  - rendered UI falls back to TUI, then CLI
  - sphere/atlas map features fall back to orthographic map lens
  - logic debug tooling may disable explicitly
  - contract mismatch may switch to read-only
- `ladder.server.mvp`
  - attach-console support may disable explicitly
  - compiled automaton preference may fall back to L1 logic evaluation
  - contract mismatch may switch to read-only
- `ladder.engine.mvp` and `ladder.game.mvp`
  - compiled automaton preference may fall back to L1 logic evaluation
- `ladder.launcher.mvp`, `ladder.setup.mvp`, `ladder.tool.mvp`
  - optional attach or presentation features degrade explicitly instead of silently

## Capability Fallback Map
- `cap.ui.rendered -> cap.ui.tui -> cap.ui.cli`
- `cap.logic.debug_analyzer -> disable_feature`
- `cap.geo.atlas_unwrap -> cap.geo.ortho_map_lens`
- `cap.logic.compiled_automaton -> cap.logic.l1_eval`
- `cap.logic.protocol_layer -> disable_feature` for advanced sniffing/bus tooling

## Runtime Enforcement
- Negotiation records now include disabled and substituted capability rows.
- Client local-singleplayer orchestration derives an effective UI mode from the negotiated record.
- Logic analyzer tooling refuses deterministically when its negotiated capability is disabled.
- Server console exposes `compat_status` for operator inspection.

## Readiness
This baseline is ready for CAP-NEG-4 stress work and PACK-COMPAT follow-up tasks because degradation is now explicit, recorded, and enforceable instead of being only advisory.
