Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Observation And Inspection

## Artifact Inputs
- Renderer and inspection surfaces consume epistemic artifacts only:
  - `ObservationArtifact`
  - `MemoryArtifact`
- Authoritative truth remains outside normal client presentation paths.

## Inspection Semantics
- Inspection is bounded query synthesis, not implicit micro-simulation.
- Inspection outputs are generated from:
  - macro state summaries
  - conformance summaries
  - cached internal state projections
- Outcome-critical local cases may request explicit micro execution; all others remain summarized.

## Instrument Modalities
- Instruments are bounded modalities over artifact generation, including:
  - optical (microscope/telescope)
  - thermal
  - signal
  - structural
- Instrument use increases confidence/provenance metadata only within declared capability scope.

## Three-Tier Disclosure
- Tier 1: Observation-visible (`OBSERVED_NOW`)
- Tier 2: Memory-visible (`REMEMBERED` / `INFERRED`)
- Tier 3: Tool-entitled truth disclosure (watermarked + audit logged)
- Unknown entities remain absent from client render state.

## Dependencies
- `docs/ui/RENDERING_EPISTEMICS.md`
- `docs/ui/FREECAM_MODES.md`
- `docs/architecture/EPISTEMICS_MODEL.md`
