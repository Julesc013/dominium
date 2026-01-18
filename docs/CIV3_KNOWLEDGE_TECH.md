# CIV3 Knowledge, Research, and Technology

This document defines the CIV3 knowledge and technology substrate. Knowledge,
research, and diffusion are deterministic, event-driven, and epistemically
gated.

## Core components

- Knowledge items (`schema/knowledge/SPEC_KNOWLEDGE_ITEMS.md`)
  - Deterministic completeness (0..1000) and epistemic status.
- Research processes (`schema/knowledge/SPEC_RESEARCH_PROCESSES.md`)
  - Start and completion events scheduled in ACT time.
  - No per-tick research scans.
- Diffusion events (`schema/knowledge/SPEC_DIFFUSION.md`)
  - Scheduled delivery with deterministic ordering.
- Secrecy policies (`schema/knowledge/SPEC_SECRECY.md`)
  - Explicit gating of diffusion fidelity and access.
- Tech prerequisites (`schema/technology/SPEC_TECH_PREREQUISITES.md`)
  - Knowledge thresholds required for activation.
- Tech effects (`schema/technology/SPEC_TECH_EFFECTS.md`)
  - Unlocks recipes, policies, and research paths only.

## Event-driven research and diffusion

- Research processes expose next_due_tick and use due scheduling.
- Diffusion uses receive_act scheduling only.
- Batch vs step equivalence is required.

## Epistemic constraints

- Knowledge is not globally known.
- Diffusion and secrecy policies gate UI visibility.
- No omniscient tech trees or research completion dashboards.

## CI enforcement

The following IDs in `docs/CI_ENFORCEMENT_MATRIX.md` cover CIV3:

- CIV3-RES-DET-001
- CIV3-BATCH-001
- CIV3-DIFF-DET-001
- CIV3-SECRECY-001
- CIV3-TECH-001
- CIV3-NOGLOB-001
