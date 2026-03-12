Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# POLL-2 Retro-Consistency Audit

Date: 2026-03-05  
Scope: Exposure accumulation, measurement epistemics, and compliance/reporting integration over POLL-1 deterministic dispersion baseline.

## Inputs Audited
- `tools/xstack/sessionx/process_runtime.py`
- `src/pollution/dispersion_engine.py`
- `src/inspection/inspection_engine.py`
- `src/signals/transport/transport_engine.py`
- `data/registries/explain_contract_registry.json`
- `data/registries/process_registry.json`

## Findings
1. Exposure updates are already process-driven.
- `process.pollution_dispersion_tick` computes exposure increments deterministically and writes `pollution_exposure_state_rows` / `pollution_hazard_hook_rows`.
- No direct UI/renderer mutation path updates exposure truth.

2. Pollution visuals remain derived, not canonical.
- Inspection/UI sections consume derived summaries (`section.pollution.*`).
- No canonical pollution field writes are performed from visual modules.

3. Measurement artifacts are not yet pollution-specialized.
- Generic OBSERVATION usage exists (`artifact.measurement`), but no dedicated pollution measurement schema/rows/process.
- Knowledge receipt integration surfaces exist in SIG (`build_knowledge_receipt`, receipt normalization), but are not yet wired for pollution measurements.

4. Institutional compliance reporting pattern exists in SIG, but not in POLL.
- REPORT artifact pattern exists via standards integration.
- POLL-specific compliance report generation and dispatch process are missing.

## Migration Plan (POLL-2)
1. Introduce pollution-specific measurement/compliance schemas and registries.
2. Add deterministic POLL exposure threshold evaluation and `health_risk_event` emission.
3. Add `process.pollution_measure` to produce OBSERVATION artifacts plus knowledge receipts (epistemic gating).
4. Add `process.pollution_compliance_tick` to produce REPORT artifacts and SIG dispatch envelopes.
5. Extend explain/proof/enforcement for exposure thresholds and compliance violations.

## Risk Notes
- Epistemic leak risk: direct concentration-map UI or unrestricted measurement results must remain forbidden.
- Deterministic degrade must be logged when exposure/compliance loops are budget-limited.
- Null boot must remain valid when no pollutant/sensor packs are present.
