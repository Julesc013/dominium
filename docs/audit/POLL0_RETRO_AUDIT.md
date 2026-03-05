# POLL-0 Retro-Consistency Audit

Date: 2026-03-05
Scope: Pollution constitution preflight for pollutant quantities, fields, transport policy tiers, and deterministic exposure hooks.

## Inputs Audited
- `tools/xstack/sessionx/process_runtime.py`
- `src/thermal/network/thermal_network_engine.py`
- `src/interior/compartment_flow_engine.py`
- `src/interior/compartment_flow_builder.py`
- `src/fields/field_engine.py`

## Findings
1. CHEM emissions hooks already exist and are process-canonical.
- `process.process_run_tick` computes deterministic `chem_process_emission_rows` and species pool updates.
- Emission rows and pool updates are sorted and fingerprinted in runtime state (no direct UI mutation path observed).

2. THERM fire/combustion pollutant hooks already exist.
- Thermal combustion carries `pollutant_emission` and generates `combustion_emission_rows`.
- Combustion emission rows are persisted as RECORD artifacts (`artifact.record.combustion_emission`) with deterministic identifiers.

3. FLUID contamination coupling exists as hook/stub pathways but not yet canonical POLL transport.
- Leak and hazard pathways can carry contaminant-like payloads.
- Dedicated pollution transport policy execution (P1 dispersion/network transport) is not yet implemented.

4. Ad-hoc smoke and visibility coupling exists outside a canonical pollution field substrate.
- Interior systems maintain `smoke_density` and smoke transfer conductance (`src/interior/compartment_flow_*`).
- Runtime derives `field.visibility` defaults directly from averaged smoke (`avg_smoke -> field.visibility`) in `process.interior_tick` orchestration.
- This should migrate to constitutive POLL -> FIELD visibility coupling derived from pollutant concentration fields/policies.

## Migration Plan
1. Standardize pollutant emission records.
- Introduce canonical `pollution_source_event` records and pollutant IDs in POLL domain registries.
- Map CHEM/THERM/FLUID emissions to POLL process events (`process.pollution_emit`) without bypass paths.

2. Preserve process-only mutation.
- Pollution mass totals and future concentration fields must mutate only through deterministic process execution.
- Disallow direct writes to pollution field layers from rendering/UI/ad-hoc runtime branches.

3. Migrate visuals to derived pollution fields.
- Replace direct smoke-to-visibility logic with model-driven visibility effects sourced from pollutant concentration fields.
- Keep existing smoke visuals as temporary compatibility overlays until POLL concentration fields are available.

4. Enforce registration and explainability.
- Pollutant IDs must resolve via pollutant registry.
- Every pollution spike and threshold crossing must provide deterministic source-chain explain traces.

## Determinism and Null-Boot Status
- Existing emission hooks are deterministic (sorted ordering + fingerprints + hash chains).
- No mandatory pollutant pack dependency detected in current boot paths.
- POLL-0 must preserve null boot behavior with explicit `poll.policy.none` and empty registries accepted.

## Risk Notes
- Existing interior smoke mechanics can create double-accounting risk if POLL concentration fields are introduced without explicit bridge policy.
- Visibility should remain a FIELD output but only via constitutive POLL coupling, not direct smoke shortcuts.
