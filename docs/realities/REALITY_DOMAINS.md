Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Reality Domains

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: canonical.
Scope: alternate reality domains as content packs.
Authority: canonical. All reality packs MUST follow this.

## Binding rules
- Reality domains MUST be expressed as optional content packs.
- Reality domains MUST declare fields, processes, and model families via schemas.
- Reality domains MUST be capability-resolved; no hardcoded paths or defaults.
- Multiple realities MAY coexist; precedence MUST be explicit in refinement plans.
- Removing a reality pack MUST NOT corrupt objective truth.

## Separation of truth and belief
- Objective truth remains singular; subjective projections may diverge.
- Knowledge artifacts MAY encode belief or doctrine without changing truth.

## References
- `docs/worldgen/REALISM_IS_CONTENT.md`
- `docs/worldgen/REFINEMENT_CONTRACT.md`
- `schema/worldgen_model.schema`
- `schema/refinement_plan.schema`
