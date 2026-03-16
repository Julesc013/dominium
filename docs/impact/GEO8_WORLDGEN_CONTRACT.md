Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Change:
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

GEO-8 worldgen contract for deterministic cell-key generation, generator version locking, proof surfaces, and ROI/view request integration.

Touched Paths:
- `src/geo/worldgen/worldgen_engine.py`
- `tools/xstack/sessionx/process_runtime.py`
- `tools/xstack/sessionx/creator.py`
- `tools/xstack/sessionx/runner.py`
- `tools/xstack/sessionx/script_runner.py`
- `src/geo/projection/projection_engine.py`
- `src/system/roi/system_roi_scheduler.py`
- `src/control/proof/control_proof_bundle.py`
- `src/net/policies/policy_server_authoritative.py`
- `src/net/srz/shard_coordinator.py`

Demand IDs:
- `space.interplanetary_supply_windows`
- `space.asteroid_mining_caravan`
- `space.rover_failure_forensics`

Notes:
- Supports large-scale deterministic exploration and logistics by making cell generation stable, replayable, and request-driven.
- Preserves save lineage by locking `generator_version_id` and `realism_profile_id` into `UniverseIdentity`.
