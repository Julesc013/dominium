Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# EARTH MVP Final Baseline

## Scope

EARTH-9 hardens the EARTH MVP envelope without adding new simulation features. The task composes existing EARTH-0..8 systems into a deterministic stress, proof, replay, and regression surface.

EARTH-9 keeps Earth presentation derived-view only. Derived view artifacts remained replayable from truth anchors and canonical tick buckets. No new truth-read bridge was introduced into UI or render surfaces.

## Stress Results Summary

- Scenario classes covered:
  - teleport orbit <-> surface <-> Sol <-> galaxy
  - traversal across slope, ridge, river, lake, polar, and ocean tiles
  - time warp across 1 day, 30 days, 365 days, and 10 lunar cycles
  - local trench edit followed by hydrology recompute and post-edit collision replay
  - day, twilight, and night sky/light/water/map requests
- Cross-platform determinism hash:
  - `c943c49f5879eee97336cce3d1ff1d6181f5ba76dedfa3d1212695e150c02c01`

The cross-platform determinism hash is the canonical EARTH-9 replay-lock summary for this baseline.
- Stress harness assertions locked green for:
  - deterministic scenario generation
  - view replay stability
  - physics replay stability
  - no truth leaks in views
  - lawful time-warp consistency
  - local hydrology update after geometry edits
  - collision stability after edits
  - bounded updates and deterministic degradation
  - cross-thread hash equivalence

## Determinism Verification

Time warp stayed lawful because all EARTH-9 checks derive from canonical tick progression. Derived view artifacts remained replayable from truth anchors and canonical tick buckets. EARTH-9 regression lock updates require `EARTH-REGRESSION-UPDATE`.

- View replay fingerprint:
  - `468639801eb3e8e5f40f91006acf3c45b8cfc0a7cf2ecfc973f1ada86cc45f94`
- Physics replay fingerprint:
  - `606423f411068440614eaf55b99ff46d8e96bdf5054e94d7f6adb485a12d6984`
- Stress report fingerprint:
  - `748ba4ce1fb4ae69f86ffb0e801e6517518669aa279f2d4c7e68b377b22bb03d`
- Regression baseline fingerprint:
  - `eba9d3eeaac25c0cac47b5fe4f58048363cd83ba7d2610c7ef1f5c9d9c687065`

## Regression Fingerprints

- Day sky:
  - `fa688ee7f8934265e4d75d27790aedbb42cfc21246366d3cc7da8b8837fe9c22`
- Twilight sky:
  - `4fc5835c5d45e56badcdc6458e1b1488a8d29bf01a48780b59b54b3e9669d8e1`
- Night sky:
  - `0a64c46631f42acc4b0933609b1800c08d3d843eabc3bb8dd68f43b19bbd5a53`
- Day lighting:
  - `55d9f4613ae296790bf919e93221db336a132f9b14cdafcda08950b9db37eaf1`
- Twilight lighting:
  - `695bd6e148a5cae76ee00b19439d4cb5620109348219b7a88f1c26b2da20aab4`
- Night lighting:
  - `747665a5c6d62a62a7787667b2fd70f402dd985e38bddbd634fc822e290bb792`
- Water view:
  - `2a718a93c707d3a10a60c008e7693cb0f155cb04c6a69eda98506ff12bbb74a2`
- Map view:
  - `6f1c57f39691df383d4259806556046639ce85b91698bf19d8ef901e10310104`
- Movement trace:
  - `cf106240130739c6a90c1667a1a41e42ce1dd7965f16838a4e3a97dbd34ab7fe`
- Collision final state:
  - `6dd29fabe7a214b4a1d1eefc6634eb49d0d20cd8ec5c5033c7d04f12c7f7ee18`
- Hydrology flow window:
  - `e6599106b217c2efefbe0a412252028905d5c8916d70321022bee2823b22bc72`

## Bounded Update Envelope

EARTH-9 preserves bounded update envelopes.

- Climate buckets per stress run: 12.
- Wind buckets per stress run: 8.
- Tide buckets per stress run: 6.
- Map rendered cells under deterministic downsample: 32.
- Debug view limit under `compute.default`: 2.
- Deterministic degradation remained explicit through `explain.view_downsampled`.
- Throttled debug surfaces:
  - `viewer.field_layers`
  - `viewer.geometry_layer`
  - `viewer.truth_anchor_hash`
- Hydrology local recompute region size remained 1 tile.

## Known Limitations

- Terrain remains macro-heightfield based; no micro chunk or mesh collision is present.
- Hydrology remains structural routing only; there is no water volume simulation or erosion.
- Climate, wind, tide, sky, lighting, and water remain proxy systems with bounded approximations.
- Renderer parity is limited to current null/software paths; hardware renderers remain future-compatible only through derived artifacts and shared view contracts.
- The unrelated `src/client/ui/viewer_shell.py` local `map_views` bug was not used by EARTH-9 verification; the envelope instead probes deterministic map downsampling directly through the map view surface.

## Readiness

- Ready for MW-4 because Earth traversal, teleport, time warp, and planetary view transitions now sit behind one deterministic regression lock.
- Ready for APPSHELL pre-dist work because replayable Earth view surfaces, bounded update contracts, and regression artifacts are now available for packaging and smoke-gate integration.
