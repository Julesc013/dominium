# Education and Learning Baseline (KNS0)

Status: binding for T18 baseline.  
Scope: knowledge artifacts, skill profiles, education programs, and learning events.

## What exists
**Knowledge artifacts**
- Claims with evidence and uncertainty envelopes.
- Confidence is inspectable and deterministic.

**Skill profiles**
- Variance reduction and failure-bias reduction per skill domain.
- Applies to process execution only.

**Education programs**
- Data-defined curriculum, duration, and costs.
- Instructor requirements and optional accreditation.

**Learning processes**
- Practice, study, training, and certification as event-driven processes.
- No per-tick learning or hidden mastery meters.

All values are fixed-point and unit-tagged per
`docs/architecture/UNIT_SYSTEM_POLICY.md`.

## What is NOT included yet
- No XP, levels, or tech trees.
- No instant mastery or auto-unlocks.
- No per-tick learning updates.
- No automated institution governance (T19+).

## Collapse/expand compatibility
Knowledge collapse stores:
- knowledge coverage per domain (invariant)
- confidence and skill distributions (sufficient statistics)

Expand reconstructs consistent microstate deterministically.

## Inspection and tooling
Inspection exposes:
- knowledge artifacts and claims
- confidence and uncertainty
- skill variance reduction
- education program costs and outputs

Visualization is symbolic and never authoritative.

## Maturity labels
- Knowledge artifacts: **BOUNDED** (epistemic, inspectable).
- Skill profiles: **BOUNDED** (variance-limited, deterministic).
- Education programs: **BOUNDED** (data-defined, replayable).

## See also
- `docs/architecture/KNOWLEDGE_AND_SKILLS_MODEL.md`
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/SCALING_MODEL.md`
