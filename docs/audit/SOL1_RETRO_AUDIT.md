Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# SOL-1 Retro Audit

## Scope

SOL-1 audits the existing EARTH-4 and EARTH-5 Moon illumination path before replacing it with a shared illumination geometry layer.

## Findings

1. Current Moon illumination is derived inside [src/worldgen/earth/sky/astronomy_proxy_engine.py](/d:/Projects/Dominium/dominium/src/worldgen/earth/sky/astronomy_proxy_engine.py).
   The `moon_direction_proxy(...)` helper currently computes `illumination_permille` directly from `lunar_phase_from_params(...)` plus `phase_cosine_proxy_permille(...)`.

2. EARTH-4 consumes the shortcut directly.
   [src/worldgen/earth/sky/sky_view_engine.py](/d:/Projects/Dominium/dominium/src/worldgen/earth/sky/sky_view_engine.py) feeds `moon_payload["illumination_permille"]` into the sky gradient model and stores `moon_illumination_permille` in the derived sky artifact.

3. EARTH-5 consumes the same shortcut indirectly.
   [src/worldgen/earth/lighting/illumination_engine.py](/d:/Projects/Dominium/dominium/src/worldgen/earth/lighting/illumination_engine.py) reads `sky_view_artifact.extensions["moon_illumination_permille"]` to derive Moon fill light.

4. No canonical TruthModel field storing Moon phase was found in the SOL/EARTH sky or lighting path.
   Current `lunar_phase` values still appear in EARTH-3 tide evaluation and derived overlay/probe outputs, but not as a canonical Earth sky or lighting truth field.

5. EARTH-4 already has the right geometry seam.
   The existing `sun_direction_proxy(...)` and `moon_direction_proxy(...)` outputs provide stable observer-relative direction proxies. SOL-1 can add a shared illumination geometry engine immediately after those direction proxies and before sky gradient / lighting evaluation.

6. Existing replay coverage already exists and can be extended instead of replaced.
   [tools/worldgen/tool_replay_illumination_view.py](/d:/Projects/Dominium/dominium/tools/worldgen/tool_replay_illumination_view.py) and [tools/worldgen/earth5_probe.py](/d:/Projects/Dominium/dominium/tools/worldgen/earth5_probe.py) already verify repeated illumination-view determinism.

7. MW-2 already provides the right body-artifact seam for albedo proxies.
   [src/worldgen/mw/mw_system_refiner_l2.py](/d:/Projects/Dominium/dominium/src/worldgen/mw/mw_system_refiner_l2.py) normalizes star luminosity proxies and planet basic artifact rows. SOL-1 can extend those rows with body albedo proxy metadata without changing simulation semantics.

## Minimal Refactor Target

- Keep orbital proxy direction generation where it is.
- Remove direct Moon phase to illumination conversion from the EARTH-4 path.
- Insert a shared fixed-point emitter/receiver/viewer illumination geometry engine between astronomy proxies and sky / lighting views.
- Preserve derived-only storage: Moon phase remains a view artifact, not truth state.
