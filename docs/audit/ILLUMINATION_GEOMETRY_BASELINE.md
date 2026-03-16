Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# SOL-1 Illumination Geometry Baseline

## Scope

SOL-1 establishes a single deterministic illumination geometry layer for emitter/receiver/viewer relationships.

- Stars are emitters through `emitter.star`.
- Planets and moons are receivers through `receiver.planet` and `receiver.moon`.
- Moon phase is derived from illumination geometry and is not stored as truth state.
- Occlusion remains `occlusion.none_stub` in MVP and keeps eclipse expansion on a deterministic interface.

## Emitter / Receiver Model

- Emitter inputs: `position_ref`, `luminosity_proxy`, optional spectrum stub.
- Receiver inputs: `position_ref`, `radius`, `albedo_proxy`.
- Viewer input: `position_ref`.
- Derived artifact: `illumination_view_artifact`.

The visible illumination fraction uses the receiver-centered phase angle between:

- `receiver -> emitter`
- `receiver -> viewer`

The receiver is spherical in MVP. No standalone lunar phase variable is persisted.

## Fixed-Point Trig Approach

- Runtime math is integer/fixed-point only.
- Direction comparison uses integer dot products and integer magnitude reduction.
- `cos_phase_permille` is clamped to `[-1000, 1000]`.
- `phase_angle` is derived through the stable `_PHASE_ANGLE_BY_COS_PERMILLE` lookup table.
- `illumination_fraction` uses the canonical spherical phase rule:
  - `(1000 + cos_phase_permille) // 2`
- `occlusion_fraction` is `1000` under `occlusion.none_stub`.

This keeps phase derivation deterministic across thread counts and host platforms.

## Integrations

- EARTH-4 sky now derives Moon illumination through `src/astro/illumination/illumination_geometry_engine.py`.
- EARTH-5 lighting consumes the sky-provided illumination artifact and no longer relies on a direct phase shortcut.
- Inspect panels expose:
  - `phase_angle`
  - `illumination_fraction`
  - `occlusion_fraction`
  - `eclipse-ready: yes (occlusion stub)`
- Replay/proof tooling is available through `tools/astro/tool_replay_illumination_view.py`.

## Deterministic Baseline

Validated local baseline on March 13, 2026:

- `EARTH-4 sky hash`: `7d55f1aaf5d417f1c14e2ad353f2e77c96ff78941cf4dd6648393762a0797c1d`
- `EARTH-5 lighting hash`: `cf1331bff313ae1549772db29b90fd7add8f6b5a31e335338d58837c0b98d978`
- `Night geometry fingerprint (tick 8)`: `0b252622a31bae629a66d9c4bdeecb1ff27348c4ac2633c649ac76d2fe0a1ce8`
- `Night illumination artifact fingerprint (tick 8)`: `26c21910c76552f2407800eb4c6786aa3bb204bd8db5c25a5eea4f417a8c7bd2`
- `Replay report fingerprint`: `9899c69a2590e143ad990ecf494e47df7d66a7a5af1a54d2029aa2763d7b543a`
- `Replay geometry window hash (ticks 0, 6, 8, 138)`: `217f853b386a5a48fcba79f56ed7ff9b1cc32b9ce495e3ee1c8eb1ff6dbef783`

Reference geometry window:

- `tick 0`: phase `180000`, illumination `0`, occlusion `1000`
- `tick 6`: phase `174000`, illumination `2`, occlusion `1000`
- `tick 8`: phase `168500`, illumination `10`, occlusion `1000`
- `tick 138`: phase `92941`, illumination `474`, occlusion `1000`

## Readiness

SOL-1 is ready for:

- SOL-2 orbit visualization
- future eclipse occlusion queries
- multi-star extension without changing the Earth sky/lighting contract
- later planetary reflection/albedo refinements

Deferred by design:

- real ephemerides
- shadow volume tracing
- non-stub eclipse occlusion
